"""Gameplay scene: loads a level, spawns the player, runs physics + camera.

This scene replaces DemoTilemapScene as the default entry point for
the game.  It wires together the Player entity, PhysicsSystem, Camera,
SlingSystem, EconomySystem, CombatSystem, TriggerSystem, HUD, Pickups,
Breakables, Enemies, and TileMap into a playable experience.
"""

from __future__ import annotations

from pathlib import Path

import pygame

from sa_fona.config.settings import (
    BASE_HEIGHT,
    BASE_WIDTH,
    DATA_DIR,
    GAMEPLAY_BG_COLOR,
    PLAYER_GRAVITY,
    PLAYER_WALL_CHECK_MARGIN,
)
from sa_fona.core.camera import Camera
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.breakable import Breakable
from sa_fona.entities.companion import Companion
from sa_fona.entities.enemy import Enemy, EnemyFactory
from sa_fona.entities.npc import NPC
from sa_fona.entities.pickup import Pickup, PickupType
from sa_fona.entities.player import Player
from sa_fona.entities.projectile import Projectile
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.level.trigger import TriggerSystem, TriggerType
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.combat import CombatSystem
from sa_fona.systems.economy import EconomySystem
from sa_fona.systems.mask_system import MaskSystem
from sa_fona.systems.physics import PhysicsSystem
from sa_fona.systems.sling_system import SlingSystem
from sa_fona.ui.charge_indicator import ChargeIndicator
from sa_fona.ui.hud import HUD

# Screen shake defaults.
_SHAKE_INTENSITY = 6.0
_SHAKE_DURATION = 0.3


class GameplayScene(BaseScene):
    """Playable level scene with player, physics, and camera.

    Loads a level JSON, creates a PhysicsSystem and Camera, spawns
    the Player entity (Ramon), and orchestrates per-frame updates.

    Args:
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
        event_bus: Shared event bus for cross-system communication.
        level_path: Path to the level JSON file. Defaults to the test level.
    """

    def __init__(
        self,
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
        event_bus: EventBus | None = None,
        level_path: str | None = None,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height

        # Store the level path for reloading on reset.
        if level_path is None:
            level_path = str(DATA_DIR / "levels" / "test" / "test_level.json")
        self._level_path = level_path

        # Load level.
        loader = LevelLoader()
        self._level_data = loader.load(self._level_path)
        self._tilemap = self._level_data.tilemap

        # Physics.
        self._physics = PhysicsSystem(self._tilemap, gravity=PLAYER_GRAVITY)

        # Camera.
        self._camera = Camera(
            self._tilemap.width_pixels,
            self._tilemap.height_pixels,
            screen_width,
            screen_height,
        )

        # Player spawn (tile coords -> pixel coords).
        spawn_x = self._level_data.player_spawn[0] * TILE_SIZE
        spawn_y = self._level_data.player_spawn[1] * TILE_SIZE
        self._player = Player(spawn_x, spawn_y)

        # Input state cache.
        self._input_state: InputState = InputState()
        self.quit_requested: bool = False

        # EventBus.
        self._event_bus = event_bus or EventBus()
        self._event_bus.subscribe("screen_shake", self._on_screen_shake)

        # Economy system (load from data/economy.json).
        self._economy = EconomySystem(self._event_bus)

        # Sling combat system (uses EconomySystem config as single source of truth).
        self._sling_system = SlingSystem(self._event_bus, self._economy.config)
        self._projectiles: list[Projectile] = []
        self._charge_indicator = ChargeIndicator()

        # HUD.
        starting_hearts = self._economy.get_starting_hearts()
        self._hud = HUD(
            self._event_bus,
            max_hearts=int(starting_hearts),
            current_hearts=starting_hearts,
            stone_count=0,
        )

        # Enemy factory and enemies.
        self._enemy_factory = EnemyFactory()
        self._enemies: list[Enemy] = []

        # Combat system.
        self._combat = CombatSystem(self._event_bus)
        self._combat.set_player_health(starting_hearts, int(starting_hearts))
        self._event_bus.subscribe("player_died", self._on_player_died)

        # Mask system.
        self._mask_system = MaskSystem(self._event_bus)

        # NPCs (spawned when save_point triggers have shop_available).
        self._npcs: list[NPC] = []

        # Pending shop push (deferred like dialogue to avoid stack issues).
        self._pending_shop: bool = False

        # Pickups and breakables (spawned from level entity definitions).
        self._pickups: list[Pickup] = []
        self._breakables: list[Breakable] = []
        self._spawn_entities()

        # Companion (Bep).
        comp_x = self._level_data.companion_spawn[0] * TILE_SIZE
        comp_y = self._level_data.companion_spawn[1] * TILE_SIZE
        self._companion = Companion(comp_x, comp_y)

        # Trigger system.
        self._trigger_system = TriggerSystem(self._event_bus)
        self._trigger_system.load_from_list(
            self._level_data.triggers, tile_size=TILE_SIZE
        )
        self._event_bus.subscribe("trigger_dialogue", self._on_trigger_dialogue)
        self._event_bus.subscribe("trigger_level_end", self._on_trigger_level_end)
        self._event_bus.subscribe("trigger_save_point", self._on_trigger_save_point)

        # Track pending dialogue scene to push (deferred to avoid stack issues).
        self._pending_dialogue_id: str | None = None

        # Track pending game over (deferred to end of update).
        self._pending_game_over: bool = False

        # Track pending level transition (deferred to end of update).
        self._pending_next_level: str | None = None

        # Scene manager reference (set externally by Game or tests).
        self._scene_manager = None

        # Save system (set externally by MainMenuScene or Game).
        self._save_system = None

    # ── Properties ─────────────────────────────────────────────────

    @property
    def player(self) -> Player:
        """The player entity (exposed for testing and future systems)."""
        return self._player

    @property
    def camera(self) -> Camera:
        """The camera (exposed for testing)."""
        return self._camera

    @property
    def physics(self) -> PhysicsSystem:
        """The physics system (exposed for testing)."""
        return self._physics

    @property
    def sling_system(self) -> SlingSystem:
        """The sling combat system (exposed for testing)."""
        return self._sling_system

    @property
    def projectiles(self) -> list[Projectile]:
        """Active projectile entities (exposed for testing)."""
        return self._projectiles

    @property
    def economy(self) -> EconomySystem:
        """The economy system (exposed for testing)."""
        return self._economy

    @property
    def hud(self) -> HUD:
        """The HUD (exposed for testing)."""
        return self._hud

    @property
    def pickups(self) -> list[Pickup]:
        """Active pickup entities (exposed for testing)."""
        return self._pickups

    @property
    def breakables(self) -> list[Breakable]:
        """Active breakable entities (exposed for testing)."""
        return self._breakables

    @property
    def enemies(self) -> list[Enemy]:
        """Active enemy entities (exposed for testing)."""
        return self._enemies

    @property
    def combat(self) -> CombatSystem:
        """The combat system (exposed for testing)."""
        return self._combat

    @property
    def mask_system(self) -> MaskSystem:
        """The mask system (exposed for testing and save integration)."""
        return self._mask_system

    @property
    def enemy_factory(self) -> EnemyFactory:
        """The enemy factory (exposed for testing)."""
        return self._enemy_factory

    @property
    def npcs(self) -> list[NPC]:
        """Active NPC entities (exposed for testing)."""
        return self._npcs

    @property
    def trigger_system(self) -> TriggerSystem:
        """The trigger system (exposed for testing)."""
        return self._trigger_system

    @property
    def companion(self) -> Companion:
        """The companion entity (Bep), exposed for testing."""
        return self._companion

    @property
    def scene_manager(self):
        """Scene manager reference for pushing overlay scenes."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value) -> None:
        self._scene_manager = value

    @property
    def save_system(self):
        """The save system (set externally by MainMenuScene or Game)."""
        return self._save_system

    @save_system.setter
    def save_system(self, value) -> None:
        self._save_system = value

    def take_level_entry_snapshot(self) -> None:
        """Record the current state as the level-entry snapshot for death rollback."""
        if self._save_system is None:
            return
        self._save_system.set_level(self._level_path)
        self._save_system.snapshot_level_entry(
            stone_count=self._economy.stone_count,
            current_hearts=self._combat.player_hearts,
            max_hearts=self._combat.player_max_hearts,
        )

    # ── Scene lifecycle ────────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered -- nothing to set up beyond __init__."""

    def on_exit(self) -> None:
        """Clean up EventBus subscriptions when the scene is removed."""
        self._event_bus.unsubscribe("screen_shake", self._on_screen_shake)
        self._event_bus.unsubscribe("trigger_dialogue", self._on_trigger_dialogue)
        self._event_bus.unsubscribe("trigger_level_end", self._on_trigger_level_end)
        self._event_bus.unsubscribe("trigger_save_point", self._on_trigger_save_point)
        try:
            self._event_bus.unsubscribe("player_died", self._on_player_died)
        except ValueError:
            pass
        self._hud.cleanup()
        self._economy.cleanup()
        self._combat.cleanup()
        self._mask_system.cleanup()

    def handle_input(self, input_state: InputState) -> None:
        """Forward input to the player and handle scene-level actions.

        Args:
            input_state: The current frame's input snapshot.
        """
        self._input_state = input_state
        self._player.handle_input(input_state)

        if input_state.pause_pressed:
            self.quit_requested = True

        if input_state.reset_pressed:
            self._reset_level()

        # NPC interaction: check if the player is near an NPC and presses interact.
        if input_state.interact_pressed:
            for npc in self._npcs:
                if npc.can_interact(self._player.rect):
                    if npc.npc_type == "shop":
                        self._pending_shop = True
                    break

    def update(self, dt: float) -> None:
        """Advance simulation by one frame.

        Orchestrates the update_intent -> physics -> post_physics
        flow so the Player never depends on PhysicsSystem directly.
        Also updates the sling system, enemies, combat, and projectiles.

        Args:
            dt: Delta time in seconds since the last frame.
        """
        # 1. Player processes input and computes movement intent.
        self._player.update_intent(dt)

        # 2. Physics system resolves movement and collisions.
        self._player.rect, self._player.velocity, on_ground = (
            self._physics.update_rect(
                self._player.rect,
                self._player.velocity,
                dt,
                self._player.on_ground,
            )
        )

        # 3. Probe for wall contact.
        wall_left, wall_right = self._check_wall_contact(self._player.rect)

        # 4. Feed physics results back to the player.
        self._player.post_physics(on_ground, wall_left, wall_right)

        # 4b. Push player out of enemy bodies (enemies have mass).
        self._resolve_enemy_push(self._player)

        # 5. Sling combat system: process input, spawn projectiles.
        new_projectiles = self._sling_system.update(
            self._input_state, self._player, dt
        )
        self._projectiles.extend(new_projectiles)

        # 6. Update projectiles (move only, no removal yet).
        for proj in self._projectiles:
            proj.update(dt)

        # 7. Update charge indicator.
        self._charge_indicator.update(self._sling_system.charge_tier, dt)

        # 8. Update enemies.
        self._update_enemies(dt)

        # 9. Combat system: resolve all damage interactions.
        #    Must run BEFORE projectile tile collision so projectiles
        #    can hit enemies they overlap this frame.
        dropped_pickups = self._combat.update(
            self._player,
            self._enemies,
            self._projectiles,
            self._sling_system.melee_hitboxes,
            dt,
        )
        self._pickups.extend(dropped_pickups)
        # Remove dead enemies.
        self._enemies = [e for e in self._enemies if e.active]

        # 10. Projectile tile collision and cleanup (after combat).
        self._check_projectile_tile_collision()

        # 11. Check pickup collection (player overlaps pickup).
        self._check_pickup_collection()

        # 12. Check breakable destruction (melee hitbox overlaps breakable).
        self._check_breakable_hits()

        # 13. Mask system: check power activation and tick cooldown.
        if self._input_state.mask_power_pressed and self._mask_system.active_mask_id:
            self._mask_system.activate_power(
                self._player.rect,
                self._tilemap,
                self._enemies,
                self._event_bus,
            )
        self._mask_system.update(dt)

        # Update HUD mask display.
        self._hud.set_mask_state(
            equipped=self._mask_system.active_mask_id is not None,
            cooldown_progress=self._mask_system.cooldown_progress,
        )

        # 14. Check triggers.
        self._trigger_system.update(self._player.rect)

        # Companion disabled — Bep is dialogue-only, not a visible follower.

        self._camera.follow(self._player.rect, dt)
        self._camera.update(dt)

        # 15. Push pending dialogue scene (deferred from trigger callback).
        if self._pending_dialogue_id is not None:
            self._push_dialogue(self._pending_dialogue_id)
            self._pending_dialogue_id = None

        # 15b. Push shop scene if NPC interaction triggered it.
        if self._pending_shop:
            self._pending_shop = False
            self._push_shop()

        # 15c. Push game over scene if player died (deferred).
        if self._pending_game_over:
            self._pending_game_over = False
            self._push_game_over()

        # 16. Transition to next level if level_end trigger fired.
        if self._pending_next_level is not None:
            next_level = self._pending_next_level
            self._pending_next_level = None
            self._load_next_level(next_level)

    def render(self, surface: pygame.Surface) -> None:
        """Draw tilemap layers, player, enemies, projectiles, pickups, and UI.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill(GAMEPLAY_BG_COLOR)
        cam_offset = self._camera.offset

        # Back-to-front layer rendering.
        self._tilemap.render_layer(surface, "background", cam_offset)
        self._tilemap.render_layer(surface, "midground", cam_offset)

        # Breakable objects.
        for breakable in self._breakables:
            breakable.render(surface, cam_offset)

        # Pickups.
        for pickup in self._pickups:
            pickup.render(surface, cam_offset)

        # Enemies.
        for enemy in self._enemies:
            enemy.render(surface, cam_offset)

        # NPCs.
        for npc in self._npcs:
            npc.render(surface, cam_offset)

        # Level-end gate visual cue.
        self._render_level_end_cues(surface, cam_offset)

        # Melee hitboxes (debug: translucent white flash).
        for hitbox in self._sling_system.melee_hitboxes:
            sx = hitbox.rect.x - cam_offset[0]
            sy = hitbox.rect.y - cam_offset[1]
            melee_surf = pygame.Surface(
                (hitbox.rect.width, hitbox.rect.height), pygame.SRCALPHA
            )
            melee_surf.fill((255, 255, 255, 120))
            surface.blit(melee_surf, (sx, sy))

        # Shockwave visual (mask system ground pound flash).
        shock_rect = self._mask_system.shockwave_rect
        if shock_rect is not None:
            shock_alpha = self._mask_system.shockwave_alpha
            sx = shock_rect.x - cam_offset[0]
            sy = shock_rect.y - cam_offset[1]
            shock_surf = pygame.Surface(
                (shock_rect.width, shock_rect.height), pygame.SRCALPHA
            )
            shock_surf.fill((255, 220, 80, shock_alpha))
            surface.blit(shock_surf, (sx, sy))

        # Projectiles.
        for proj in self._projectiles:
            proj.render(surface, cam_offset)

        # Player (respects invincibility blink from combat system).
        if self._combat.player_visible:
            self._player.render(surface, cam_offset)

        # Charge indicator (UI, world-space near player).
        self._charge_indicator.render(surface, self._player.rect, cam_offset)

        # Foreground on top.
        self._tilemap.render_layer(surface, "foreground", cam_offset)

        # HUD renders on top of everything (screen space, not camera-relative).
        self._hud.render(surface)

    def _render_level_end_cues(
        self, surface: pygame.Surface, cam_offset: tuple[int, int],
    ) -> None:
        """Draw a pulsing gate at level_end trigger locations."""
        for trigger in self._trigger_system.triggers:
            if trigger.trigger_type != TriggerType.LEVEL_END:
                continue
            sx = trigger.rect.x - cam_offset[0]
            sy = trigger.rect.y - cam_offset[1]
            w = trigger.rect.width
            h = trigger.rect.height

            gate_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            gate_surf.fill((255, 220, 80, 50))
            surface.blit(gate_surf, (sx, sy))

            pygame.draw.rect(surface, (255, 200, 50), (sx, sy, w, h), 2)

            col_w = 4
            pygame.draw.rect(
                surface, (180, 140, 40), (sx, sy, col_w, h),
            )
            pygame.draw.rect(
                surface, (180, 140, 40), (sx + w - col_w, sy, col_w, h),
            )

            try:
                if not hasattr(self, "_gate_font"):
                    self._gate_font = pygame.font.Font(None, 12)
                arrow = self._gate_font.render(">>>", False, (255, 220, 80))
                ax = sx + (w - arrow.get_width()) // 2
                ay = sy + (h - arrow.get_height()) // 2
                surface.blit(arrow, (ax, ay))
            except pygame.error:
                pass

    # ── Entity spawning ─────────────────────────────────────────────

    def _spawn_entities(self) -> None:
        """Spawn pickups, breakables, and enemies from level entity definitions."""
        for ent_def in self._level_data.entities:
            ent_type = ent_def.get("type", "")
            if ent_type == "pickup":
                self._spawn_pickup(ent_def)
            elif ent_type == "breakable":
                self._spawn_breakable(ent_def)
            elif ent_type == "enemy":
                self._spawn_enemy(ent_def)

    def _spawn_pickup(self, ent_def: dict) -> None:
        """Spawn a single pickup entity from a level definition.

        Args:
            ent_def: Dict with pickup_type, x, y, and optional value.
        """
        pt_str = ent_def.get("pickup_type", "stone")
        if pt_str == "heart":
            pickup_type = PickupType.HEART
        else:
            pickup_type = PickupType.STONE

        value = ent_def.get("value", 1.0)
        # Entity positions in level JSON are in tile coordinates.
        px = ent_def.get("x", 0) * TILE_SIZE
        py = ent_def.get("y", 0) * TILE_SIZE

        pickup = Pickup(px, py, pickup_type, value=float(value))
        self._pickups.append(pickup)

    def _spawn_breakable(self, ent_def: dict) -> None:
        """Spawn a single breakable entity from a level definition.

        Args:
            ent_def: Dict with breakable_type, x, y.
        """
        breakable_type = ent_def.get("breakable_type", "breakable_pot")
        bx = ent_def.get("x", 0) * TILE_SIZE
        by = ent_def.get("y", 0) * TILE_SIZE

        breakable = Breakable(bx, by, breakable_type)
        self._breakables.append(breakable)

    def _spawn_enemy(self, ent_def: dict) -> None:
        """Spawn a single enemy entity from a level definition.

        Args:
            ent_def: Dict with enemy_type, x, y (tile coordinates).
        """
        try:
            enemy = self._enemy_factory.create_from_entity_def(ent_def)
            self._snap_to_ground(enemy)
            self._enemies.append(enemy)
        except ValueError:
            pass  # Skip unknown enemy types gracefully.

    def _snap_to_ground(self, enemy: Enemy) -> None:
        """Align enemy feet to the top of the first solid tile below."""
        if self._tilemap is None:
            return
        start_ty = (enemy.rect.top // TILE_SIZE) + 1
        tx = enemy.rect.centerx // TILE_SIZE
        for ty in range(start_ty, self._tilemap.height_tiles):
            if self._tilemap.is_solid_at(tx, ty):
                enemy.snap_position(ty * TILE_SIZE)
                return

    # ── Enemy updates ─────────────────────────────────────────────

    def _update_enemies(self, dt: float) -> None:
        """Update all active enemies with behavior and movement.

        Args:
            dt: Delta time in seconds.
        """
        for enemy in self._enemies:
            if enemy.active:
                enemy.update_with_player(
                    self._player.rect, dt, tilemap=self._tilemap
                )

    # ── Pickup collection ─────────────────────────────────────────

    def _check_pickup_collection(self) -> None:
        """Check player overlap with pickups and trigger collection."""
        for pickup in self._pickups:
            if not pickup.active:
                continue
            if self._player.rect.colliderect(pickup.rect):
                event_type, event_data = pickup.collect()
                self._event_bus.publish(event_type, **event_data)
        # Remove collected pickups.
        self._pickups = [p for p in self._pickups if p.active]

    # ── Breakable destruction ─────────────────────────────────────

    def _check_breakable_hits(self) -> None:
        """Check melee hitbox overlap with breakables and destroy on hit."""
        for hitbox in self._sling_system.melee_hitboxes:
            for breakable in self._breakables:
                if not breakable.active:
                    continue
                if hitbox.rect.colliderect(breakable.rect):
                    stone_yield = self._economy.get_breakable_yield(
                        breakable.breakable_type
                    )
                    new_pickups = breakable.on_hit(stone_yield)
                    self._pickups.extend(new_pickups)
        # Remove destroyed breakables.
        self._breakables = [b for b in self._breakables if b.active]

    # ── Physics helpers ────────────────────────────────────────────

    def _resolve_enemy_push(self, player: Player) -> None:
        """Push the player out of overlapping enemy hitboxes."""
        pushed = False
        for enemy in self._enemies:
            if not enemy.is_alive:
                continue
            if not player.rect.colliderect(enemy.rect):
                continue
            overlap = player.rect.clip(enemy.rect)
            if overlap.width < overlap.height:
                if player.rect.centerx < enemy.rect.centerx:
                    player.rect.right = enemy.rect.left
                else:
                    player.rect.left = enemy.rect.right
            else:
                if player.rect.centery < enemy.rect.centery:
                    player.rect.bottom = enemy.rect.top
                else:
                    player.rect.top = enemy.rect.bottom
            pushed = True
        if pushed:
            self._clamp_to_solid(player.rect)

    def _clamp_to_solid(self, rect: pygame.Rect) -> None:
        """Push rect out of any overlapping solid tiles."""
        for tile_rect in self._physics.check_collision(rect, "solid"):
            overlap = rect.clip(tile_rect)
            if overlap.width < overlap.height:
                if rect.centerx < tile_rect.centerx:
                    rect.right = tile_rect.left
                else:
                    rect.left = tile_rect.right
            else:
                if rect.centery < tile_rect.centery:
                    rect.bottom = tile_rect.top
                else:
                    rect.top = tile_rect.bottom

    def _check_wall_contact(
        self, rect: pygame.Rect
    ) -> tuple[bool, bool]:
        """Probe the tilemap for wall contact on left and right sides.

        Args:
            rect: The entity's bounding box to probe around.

        Returns:
            Tuple of ``(wall_left, wall_right)`` booleans.
        """
        margin = PLAYER_WALL_CHECK_MARGIN

        left_probe = pygame.Rect(
            rect.left - margin,
            rect.top + 2,
            margin,
            rect.height - 4,
        )
        wall_left = len(self._physics.check_collision(left_probe, "solid")) > 0

        right_probe = pygame.Rect(
            rect.right,
            rect.top + 2,
            margin,
            rect.height - 4,
        )
        wall_right = len(self._physics.check_collision(right_probe, "solid")) > 0

        return wall_left, wall_right

    # ── Projectile management ─────────────────────────────────────

    def _check_projectile_tile_collision(self) -> None:
        """Check projectile-vs-tilemap collision and remove inactive."""
        for proj in self._projectiles:
            if not proj.active:
                continue
            hits = self._physics.check_collision(proj.rect, "solid")
            if hits:
                proj.on_hit_tile()
        self._projectiles = [p for p in self._projectiles if p.active]

    # ── Level reset ────────────────────────────────────────────────

    def _reset_level(self) -> None:
        """Reload the current level and respawn the player at the spawn point.

        Used for quick testing iteration (R key).  Reloads the level
        data, rebuilds physics and camera, and creates a fresh player.
        Clears projectiles and resets the sling system.
        """
        loader = LevelLoader()
        self._level_data = loader.load(self._level_path)
        self._tilemap = self._level_data.tilemap

        self._physics = PhysicsSystem(self._tilemap, gravity=PLAYER_GRAVITY)
        self._camera = Camera(
            self._tilemap.width_pixels,
            self._tilemap.height_pixels,
            self._screen_width,
            self._screen_height,
        )

        spawn_x = self._level_data.player_spawn[0] * TILE_SIZE
        spawn_y = self._level_data.player_spawn[1] * TILE_SIZE
        self._player = Player(spawn_x, spawn_y)
        self._input_state = InputState()

        # Reset combat state (reuse EconomySystem config).
        self._sling_system = SlingSystem(self._event_bus, self._economy.config)
        self._projectiles.clear()
        self._charge_indicator = ChargeIndicator()

        # Reset pickups, breakables, enemies, and NPCs from level data.
        self._pickups.clear()
        self._breakables.clear()
        self._enemies.clear()
        self._npcs.clear()
        self._spawn_entities()

        # Reset HUD to starting values (keep economy state).
        starting_hearts = self._economy.get_starting_hearts()
        self._hud.set_state(
            max_hearts=int(starting_hearts),
            current_hearts=starting_hearts,
            stone_count=self._economy.stone_count,
        )

        # Reset combat system health tracking.
        self._combat.set_player_health(starting_hearts, int(starting_hearts))

        # Reset companion.
        comp_x = self._level_data.companion_spawn[0] * TILE_SIZE
        comp_y = self._level_data.companion_spawn[1] * TILE_SIZE
        self._companion = Companion(comp_x, comp_y)

        # Reset mask cooldown (keep inventory).
        self._mask_system.update(999.0)  # Clear any remaining cooldown.

        # Reset triggers.
        self._trigger_system.reset()
        self._trigger_system.load_from_list(
            self._level_data.triggers, tile_size=TILE_SIZE
        )
        self._pending_dialogue_id = None
        self._pending_game_over = False
        self._pending_next_level = None
        self._pending_shop = False

    # ── Level progression ─────────────────────────────────────────

    def _load_next_level(self, next_level: str) -> None:
        """Load the next level by its relative path identifier.

        The ``next_level`` string is a path relative to the levels data
        directory (e.g. ``"world1/level_1_2"``).  Boss levels (paths
        containing ``"boss_"``) are loaded as BossScene instead.

        Before transitioning, updates the save system with the current
        player state and the next level path, then saves to disk.

        Args:
            next_level: Relative level identifier (without ``.json`` extension).
        """
        if self._scene_manager is None:
            return

        # Save progress before transitioning.
        level_path_for_save = str(
            DATA_DIR / "levels" / f"{next_level}.json"
        )
        if self._save_system is not None:
            self._save_system.set_level(level_path_for_save)
            self._save_system.set_player_state(
                stone_count=self._economy.stone_count,
                current_hearts=self._combat.player_hearts,
                max_hearts=self._combat.player_max_hearts,
            )
            # Save mask state.
            mask_state = self._mask_system.get_save_state()
            self._save_system.state["masks_unlocked"] = mask_state["unlocked_masks"]
            self._save_system.state["masks_equipped"] = (
                [mask_state["equipped_mask"]] if mask_state["equipped_mask"] else []
            )
            self._save_system.save()

        # Boss levels use BossScene with a boss_id extracted from the path.
        level_name = next_level.rsplit("/", 1)[-1]
        if level_name.startswith("boss_"):
            from sa_fona.scenes.boss_scene import BossScene

            boss_id = level_name[len("boss_"):]
            boss_scene = BossScene(
                boss_id=boss_id,
                screen_width=self._screen_width,
                screen_height=self._screen_height,
                event_bus=self._event_bus,
            )
            boss_scene.scene_manager = self._scene_manager
            self._scene_manager.replace(boss_scene)
            return

        level_path = str(DATA_DIR / "levels" / f"{next_level}.json")

        if not Path(level_path).is_file():
            return

        new_scene = GameplayScene(
            self._screen_width,
            self._screen_height,
            event_bus=self._event_bus,
            level_path=level_path,
        )
        new_scene.scene_manager = self._scene_manager
        # Propagate mask state to the new scene.
        new_scene.mask_system.restore_save_state(self._mask_system.get_save_state())
        if self._save_system is not None:
            new_scene.save_system = self._save_system
            new_scene.take_level_entry_snapshot()
        self._scene_manager.replace(new_scene)

    # ── Event callbacks ────────────────────────────────────────────

    def _on_screen_shake(
        self, intensity: float = 0.0, duration: float = 0.0
    ) -> None:
        """Handle screen_shake events from the EventBus.

        Args:
            intensity: Shake intensity in pixels.
            duration: Shake duration in seconds.
        """
        self._camera.shake(intensity, duration)

    def _on_trigger_dialogue(self, trigger=None) -> None:
        """Handle dialogue trigger events.

        Defers the dialogue push to the next frame to avoid modifying the
        scene stack during an update.

        Args:
            trigger: The Trigger instance that fired.
        """
        if trigger is None:
            return
        dialogue_id = trigger.properties.get("dialogue_id", "")
        if dialogue_id:
            self._pending_dialogue_id = dialogue_id

    def _on_trigger_level_end(self, trigger=None) -> None:
        """Handle level_end trigger events.

        If the trigger specifies a ``next_level`` property, defers a level
        transition to the end of the current frame.  Also publishes a
        ``level_complete`` event for any interested listeners.

        Args:
            trigger: The Trigger instance that fired.
        """
        self._event_bus.publish("level_complete")
        if trigger is not None:
            next_level = trigger.properties.get("next_level", "")
            if next_level:
                self._pending_next_level = next_level

    def _on_trigger_save_point(self, trigger=None) -> None:
        """Handle save_point trigger events.

        Publishes a save_point_reached event.  If the trigger has
        ``shop_available: true``, spawns Llorencc NPC near the save
        point (offset slightly to the right).

        Args:
            trigger: The Trigger instance that fired.
        """
        shop_available = False
        if trigger is not None:
            shop_available = trigger.properties.get("shop_available", False)

            # Spawn Llorencc NPC near the save point if shop is available.
            if shop_available:
                npc_x = trigger.rect.right + 8
                npc_y = trigger.rect.bottom - 36  # Align feet with ground.
                # Avoid duplicate spawns.
                already_spawned = any(
                    n.npc_id == "llorencc" for n in self._npcs
                )
                if not already_spawned:
                    npc = NPC(
                        npc_x, npc_y,
                        npc_id="llorencc",
                        npc_type="shop",
                        label="L",
                    )
                    self._npcs.append(npc)

        self._event_bus.publish(
            "save_point_reached", shop_available=shop_available
        )

    # ── Dialogue push ─────────────────────────────────────────────

    def _push_dialogue(self, dialogue_id: str) -> None:
        """Push a DialogueScene overlay onto the scene stack.

        Requires that ``scene_manager`` has been set on this scene.

        Args:
            dialogue_id: The dialogue sequence ID to display.
        """
        if self._scene_manager is None:
            return

        from sa_fona.scenes.dialogue import DialogueScene

        def _on_dialogue_complete() -> None:
            if self._scene_manager is not None:
                self._scene_manager.pop()

        scene = DialogueScene(
            dialogue_id=dialogue_id,
            event_bus=self._event_bus,
            on_complete=_on_dialogue_complete,
        )
        self._scene_manager.push(scene)

    # ── Shop push ─────────────────────────────────────────────────

    def _push_shop(self) -> None:
        """Push a ShopScene overlay onto the scene stack.

        Requires that ``scene_manager`` has been set on this scene.
        """
        if self._scene_manager is None:
            return

        from sa_fona.scenes.shop import ShopScene

        def _on_shop_close() -> None:
            if self._scene_manager is not None:
                self._scene_manager.pop()

        scene = ShopScene(
            event_bus=self._event_bus,
            economy=self._economy,
            mask_system=self._mask_system,
            combat_system=self._combat,
            hud=self._hud,
            current_world=1,
            on_close=_on_shop_close,
        )
        self._scene_manager.push(scene)

    # ── Player death / Game over ──────────────────────────────────

    def _on_player_died(self, **kwargs) -> None:
        """Handle player_died event: rollback economy and defer game over."""
        if self._save_system is not None:
            snap = self._save_system.rollback_to_snapshot()
            if snap is not None:
                self._economy.restore({"stone_count": snap["stone_count"]})
                self._combat.set_player_health(
                    snap["current_hearts"], snap["max_hearts"]
                )
                self._hud.set_state(
                    max_hearts=snap["max_hearts"],
                    current_hearts=snap["current_hearts"],
                    stone_count=snap["stone_count"],
                )
        self._pending_game_over = True

    def _push_game_over(self) -> None:
        """Push the GameOverScene onto the scene stack.

        When the player presses a key, the game restarts from the
        beginning of the current level.
        """
        if self._scene_manager is None:
            return

        from sa_fona.scenes.game_over import GameOverScene

        def _on_restart() -> None:
            if self._scene_manager is not None:
                self._scene_manager.pop()  # Remove GameOverScene.
                self._reset_level()
                self.take_level_entry_snapshot()

        scene = GameOverScene(on_restart=_on_restart)
        self._scene_manager.push(scene)
