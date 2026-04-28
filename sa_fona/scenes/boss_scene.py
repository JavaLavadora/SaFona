"""Boss arena scene extending GameplayScene with boss-specific logic.

The BossScene sets up the boss arena, spawns the boss entity, manages
phase transitions, boss health bar UI, boss-vs-player combat, and the
intro/outro sequences.

After the boss is defeated, pushes a CutsceneScene that handles the
Dimoni dialogue, mask acquisition, and transition to the next world.

It reuses GameplayScene's player, physics, camera, and combat systems
while adding boss-specific orchestration.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import (
    ASSETS_DIR,
    BASE_HEIGHT,
    BASE_WIDTH,
    CAMERA_ZOOM,
    DATA_DIR,
    GAMEPLAY_BG_COLOR,
    PLAYER_GRAVITY,
    PLAYER_WALL_CHECK_MARGIN,
)
from sa_fona.core.camera import Camera
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.boss_entity import BossEntity, BossState
from sa_fona.entities.bosses import get_boss_class
from sa_fona.entities.player import Player
from sa_fona.entities.projectile import Projectile
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE, TileMap
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.combat import CombatSystem
from sa_fona.systems.economy import EconomySystem
from sa_fona.systems.physics import PhysicsSystem
from sa_fona.systems.sling_system import SlingSystem
from sa_fona.ui.boss_health_bar import BossHealthBar
from sa_fona.ui.charge_indicator import ChargeIndicator
from sa_fona.ui.hud import HUD


class BossScene(BaseScene):
    """Boss arena scene for boss encounters.

    Manages the arena layout, boss entity, phase transitions, boss
    health bar, and integrates with the existing combat and physics
    systems. After defeat, pushes a CutsceneScene for the post-boss
    sequence.

    Args:
        boss_id: The boss identifier (e.g. "bou_de_pedra").
        screen_width: Viewport width in pixels.
        screen_height: Viewport height in pixels.
        event_bus: Shared event bus.
        level_path: Optional path to a level JSON for the arena.
            If None, a procedural arena is generated.
        cutscene_id: Cutscene definition ID to play after boss defeat.
            If None, the default "VICTORY!" overlay is shown instead.
        on_load_level: Callback for level loading from the cutscene.
            Receives the level_path string as argument.
    """

    def __init__(
        self,
        boss_id: str = "bou_de_pedra",
        screen_width: int = BASE_WIDTH,
        screen_height: int = BASE_HEIGHT,
        event_bus: EventBus | None = None,
        level_path: str | None = None,
        cutscene_id: str | None = "post_boss_w1",
        on_load_level: callable | None = None,
    ) -> None:
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._event_bus = event_bus or EventBus()
        self._boss_id = boss_id

        # Load boss definition.
        self._boss_def = BossEntity.load_definition(boss_id)
        arena_data = self._boss_def.get("arena", {})
        arena_w = arena_data.get("width", 25)
        arena_h = arena_data.get("height", 14)

        # Load tileset surface for the arena (if specified).
        tileset_id = arena_data.get("tileset", "")
        tileset_surface = None
        if tileset_id:
            tileset_path = ASSETS_DIR / "tilesets" / tileset_id / "tileset.png"
            if tileset_path.is_file():
                try:
                    tileset_surface = pygame.image.load(str(tileset_path)).convert_alpha()
                except pygame.error:
                    tileset_surface = None

        # Load background image for the arena (if specified).
        self._background: pygame.Surface | None = None
        bg_id = arena_data.get("background", "")
        if bg_id:
            base_name = bg_id
            if base_name.endswith("_bg"):
                base_name = base_name[:-3]
            bg_path = ASSETS_DIR / "backgrounds" / f"{base_name}.png"
            if bg_path.is_file():
                try:
                    self._background = pygame.image.load(str(bg_path)).convert()
                except pygame.error:
                    self._background = None

        # Build arena tilemap (procedural if no level_path).
        if level_path is not None:
            loader = LevelLoader()
            level_data = loader.load(level_path)
            self._tilemap = level_data.tilemap
        else:
            self._tilemap = self._build_arena_tilemap(
                arena_w, arena_h,
                tileset_id=tileset_id,
                tileset_surface=tileset_surface,
            )

        # Physics.
        self._physics = PhysicsSystem(self._tilemap, gravity=PLAYER_GRAVITY)

        # Camera.
        self._camera = Camera(
            self._tilemap.width_pixels,
            self._tilemap.height_pixels,
            screen_width,
            screen_height,
            zoom=CAMERA_ZOOM,
        )

        # Player spawn.
        player_spawn = arena_data.get("player_spawn", {"x": 2, "y": 11})
        spawn_x = player_spawn.get("x", 2) * TILE_SIZE
        spawn_y = player_spawn.get("y", 11) * TILE_SIZE
        self._player = Player(spawn_x, spawn_y)
        # Snap player feet to the floor (top of floor row = (arena_h - 2) * TILE_SIZE).
        self._player.rect.bottom = (arena_h - 2) * TILE_SIZE

        # Snap camera to player immediately (avoid lerp snap on first frame).
        self._camera.snap_to(self._player.rect)

        # Zoom surface for camera zoom rendering pipeline.
        zoom = self._camera.zoom
        if zoom != 1.0:
            zoom_w = int(self._screen_width / zoom)
            zoom_h = int(self._screen_height / zoom)
            self._zoom_surface: pygame.Surface | None = pygame.Surface(
                (zoom_w, zoom_h)
            )
        else:
            self._zoom_surface = None

        # Input state.
        self._input_state = InputState()
        self.quit_requested: bool = False

        # Event bus subscriptions.
        self._event_bus.subscribe("screen_shake", self._on_screen_shake)
        self._event_bus.subscribe("boss_phase_change", self._on_boss_phase_change)
        self._event_bus.subscribe("boss_defeated", self._on_boss_defeated)
        self._event_bus.subscribe("player_died", self._on_player_died)

        # Economy and sling.
        self._economy = EconomySystem(self._event_bus)
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

        # Combat system.
        self._combat = CombatSystem(self._event_bus)
        self._combat.set_player_health(starting_hearts, int(starting_hearts))

        # Boss entity.
        boss_spawn = arena_data.get("boss_spawn", {"x": 20, "y": 9})
        boss_x = boss_spawn.get("x", 20) * TILE_SIZE
        boss_y = boss_spawn.get("y", 9) * TILE_SIZE
        arena_bounds = (0, 0, arena_w * TILE_SIZE, arena_h * TILE_SIZE)

        boss_cls = get_boss_class(boss_id)
        self._boss: BossEntity = boss_cls(
            boss_x, boss_y, self._boss_def, self._event_bus, arena_bounds
        )
        # Snap boss feet to the floor.
        self._boss.rect.bottom = (arena_h - 2) * TILE_SIZE

        # Setup pillars.
        pillar_positions = arena_data.get("pillar_positions", [])
        self._boss.setup_pillars(pillar_positions)

        # Boss health bar.
        phase_thresholds = [0.66, 0.33]
        self._boss_health_bar = BossHealthBar(
            boss_name=self._boss.display_name,
            max_health=self._boss.max_health,
            phase_thresholds=phase_thresholds,
        )
        if self._boss_def.get("phases"):
            phase_name = self._boss_def["phases"][0].get("name", "")
            self._boss_health_bar.set_phase(1, phase_name)

        # Intro state.
        self._intro_active: bool = True
        self._intro_timer: float = 2.0  # Brief intro before fight starts.
        self._intro_skippable: bool = False  # Skippable on retry.
        self._fight_started: bool = False

        # Defeat state.
        self._boss_defeated: bool = False
        self._defeat_timer: float = 0.0
        self._defeat_duration: float = 3.0
        self._cutscene_pushed: bool = False
        self._cutscene_completed: bool = False

        # Cutscene configuration.
        self._cutscene_id: str | None = cutscene_id
        self._on_load_level = on_load_level
        self._pending_level_load: str | None = None
        self._is_retry: bool = False  # Set to True after first death+restart.

        # Game over state.
        self._pending_game_over: bool = False

        # Scene manager.
        self._scene_manager = None

    # ── Properties ─────────────────────────────────────────────────

    @property
    def player(self) -> Player:
        """The player entity."""
        return self._player

    @property
    def boss(self) -> BossEntity:
        """The boss entity."""
        return self._boss

    @property
    def camera(self) -> Camera:
        """The camera."""
        return self._camera

    @property
    def boss_health_bar(self) -> BossHealthBar:
        """The boss health bar UI."""
        return self._boss_health_bar

    @property
    def combat(self) -> CombatSystem:
        """The combat system."""
        return self._combat

    @property
    def scene_manager(self):
        """Scene manager reference."""
        return self._scene_manager

    @scene_manager.setter
    def scene_manager(self, value) -> None:
        self._scene_manager = value

    @property
    def fight_started(self) -> bool:
        """Whether the boss fight has started."""
        return self._fight_started

    # ── Scene lifecycle ────────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered."""

    def on_resume(self) -> None:
        """Called when the cutscene pops off the stack.

        If a level load was requested during the cutscene (via load_level
        step), executes the transition now that the cutscene has cleanly
        popped from the scene stack.
        """
        if self._cutscene_pushed:
            self._cutscene_completed = True
        if self._pending_level_load and self._on_load_level:
            self._on_load_level(self._pending_level_load)
            self._pending_level_load = None

    def on_exit(self) -> None:
        """Clean up subscriptions."""
        self._event_bus.unsubscribe("screen_shake", self._on_screen_shake)
        self._event_bus.unsubscribe("boss_phase_change", self._on_boss_phase_change)
        self._event_bus.unsubscribe("boss_defeated", self._on_boss_defeated)
        try:
            self._event_bus.unsubscribe("player_died", self._on_player_died)
        except ValueError:
            pass
        self._hud.cleanup()
        self._economy.cleanup()
        self._combat.cleanup()

    def handle_input(self, input_state: InputState) -> None:
        """Process input.

        Args:
            input_state: Current frame input snapshot.
        """
        self._input_state = input_state

        # Skip intro on any key press during intro.
        if self._intro_active and (
            input_state.jump_pressed or input_state.attack_pressed
        ):
            if self._intro_skippable or self._intro_timer < 1.0:
                self._end_intro()

        if input_state.pause_pressed:
            self.quit_requested = True

        if input_state.reset_pressed:
            self._reset_fight()

        if not self._intro_active and not self._boss_defeated:
            self._player.handle_input(input_state)

    def update(self, dt: float) -> None:
        """Update the boss scene.

        Args:
            dt: Delta time in seconds.
        """
        # Intro countdown.
        if self._intro_active:
            self._intro_timer -= dt
            if self._intro_timer <= 0:
                self._end_intro()
            self._camera.follow(self._boss.rect, dt)
            self._camera.update(dt)
            return

        # Defeat sequence.
        if self._boss_defeated:
            if not self._cutscene_completed:
                self._defeat_timer += dt
            self._camera.update(dt)
            # After a brief defeat flash, push the cutscene.
            if (
                not self._cutscene_pushed
                and self._defeat_timer >= 1.5
                and self._cutscene_id is not None
            ):
                self._push_cutscene()
            return

        # 1. Player intent.
        self._player.update_intent(dt)

        # 2. Physics.
        self._player.rect, self._player.velocity, on_ground = (
            self._physics.update_rect(
                self._player.rect,
                self._player.velocity,
                dt,
                self._player.on_ground,
            )
        )

        # 3. Wall contact.
        wall_left, wall_right = self._check_wall_contact(self._player.rect)

        # 3b. Pillar collision (before post_physics so on_ground is correct).
        on_ground = self._resolve_pillar_collision(on_ground)

        # 4. Post-physics.
        self._player.post_physics(on_ground, wall_left, wall_right)

        # 4b. Boss push-back (physical mass).
        self._resolve_boss_push()

        # 5. Sling system.
        new_projectiles = self._sling_system.update(
            self._input_state, self._player, dt
        )
        self._projectiles.extend(new_projectiles)

        # 5b. Sync sling animation state to the player sprite.
        # Map all four SlingSystem states to player animation states:
        #   idle     -> "none"      (no sling activity)
        #   pressed  -> "charging"  (player starting to wind up)
        #   charging -> "charging"  (actively charging the sling)
        #   cooldown -> "releasing" (release pose, unconditional)
        sling_st = self._sling_system.state
        if sling_st == "idle":
            self._player.sling_anim_state = "none"
        elif sling_st in ("pressed", "charging"):
            self._player.sling_anim_state = "charging"
        elif sling_st == "cooldown":
            self._player.sling_anim_state = "releasing"

        # 6. Update projectiles.
        for proj in self._projectiles:
            proj.update(dt)

        # 7. Charge indicator.
        self._charge_indicator.update(self._sling_system.charge_tier, dt)

        # 8. Update boss.
        self._boss.update_with_player(self._player.rect, dt)

        # 9. Boss damage resolution (player attacks -> boss).
        self._resolve_player_attacks_on_boss()

        # 10. Boss attacks -> player.
        self._resolve_boss_attacks_on_player()

        # 11. Projectile tile collision.
        self._check_projectile_tile_collision()

        # 12. Tick combat timers (invincibility, blink).
        self._combat.tick(dt)

        # 13. Update boss health bar.
        self._boss_health_bar.set_health(self._boss.health)
        self._boss_health_bar.update(dt)

        # 14. Camera.
        self._camera.follow(self._player.rect, dt)
        self._camera.update(dt)

        # 15. Game over.
        if self._pending_game_over:
            self._pending_game_over = False
            self._push_game_over()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the boss scene.

        When camera zoom is active, the world is rendered to a smaller
        intermediate surface and then scaled up.  HUD elements render
        at native resolution on top.

        Args:
            surface: Target surface.
        """
        # Determine render target: zoom surface (smaller) or native surface.
        if self._zoom_surface is not None:
            target = self._zoom_surface
        else:
            target = surface

        self._render_background(target)
        cam_offset = self._camera.offset

        # Tilemap layers.
        self._tilemap.render_layer(target, "background", cam_offset)
        self._tilemap.render_layer(target, "midground", cam_offset)

        # Boss (includes pillars, projectiles, markers).
        self._boss.render(target, cam_offset)

        # Player projectiles.
        for proj in self._projectiles:
            proj.render(target, cam_offset)

        # Player.
        if self._combat.player_visible:
            self._player.render(target, cam_offset)

        # Charge indicator.
        self._charge_indicator.render(target, self._player.rect, cam_offset)

        # Foreground.
        self._tilemap.render_layer(target, "foreground", cam_offset)

        # Scale zoomed surface up to the native surface.
        if self._zoom_surface is not None:
            pygame.transform.scale(
                self._zoom_surface,
                (self._screen_width, self._screen_height),
                surface,
            )

        # HUD renders at native resolution.
        self._hud.render(surface)

        # Boss health bar (on top of HUD).
        self._boss_health_bar.render(surface)

        # Intro overlay.
        if self._intro_active:
            self._render_intro(surface)

        # Defeat overlay.
        if self._boss_defeated:
            self._render_defeat(surface)

    # ── Combat resolution ──────────────────────────────────────────

    def _resolve_player_attacks_on_boss(self) -> None:
        """Check player projectiles and melee against the boss."""
        if not self._boss.is_alive:
            return

        # Projectile -> Boss.
        for proj in self._projectiles:
            if not proj.active:
                continue
            if proj.rect.colliderect(self._boss.rect):
                applied = self._boss.take_damage(
                    proj.damage, charge_tier=proj.charge_tier
                )
                proj.on_hit_entity(self._boss)
                break

        # Melee -> Boss.
        for hitbox in self._sling_system.melee_hitboxes:
            if hitbox.rect.colliderect(self._boss.rect):
                self._boss.take_damage(hitbox.damage, charge_tier=0)

    def _resolve_boss_attacks_on_player(self) -> None:
        """Check boss attacks against the player."""
        if self._combat.player_invincible:
            return
        if self._combat.player_dead:
            return

        attack_rects = self._boss.get_attack_rects()
        for attack_rect, damage in attack_rects:
            # Check if a pillar blocks the attack (player hiding).
            if self._boss.blocks_rush(self._player.rect):
                continue
            if self._player.rect.colliderect(attack_rect):
                self._combat.deal_damage_to_player(damage)
                break

        # Contact damage when boss is idle/moving (non-attack contact).
        if (
            not self._combat.player_invincible
            and not self._combat.player_dead
            and self._boss.is_alive
            and self._boss.state not in (BossState.PUNISH, BossState.PHASE_TRANSITION, BossState.DEFEATED)
            and self._player.rect.colliderect(self._boss.rect)
        ):
            self._combat.deal_damage_to_player(self._boss.contact_damage)

    def _resolve_pillar_collision(self, on_ground: bool) -> bool:
        """Push the player out of active pillars (solid obstacles).

        Returns updated on_ground (True if player landed on a pillar top).
        """
        for pillar in self._boss.active_pillars:
            if not self._player.rect.colliderect(pillar.rect):
                continue
            overlap = self._player.rect.clip(pillar.rect)
            if overlap.width < overlap.height:
                if self._player.rect.centerx < pillar.rect.centerx:
                    self._player.rect.right = pillar.rect.left
                else:
                    self._player.rect.left = pillar.rect.right
            else:
                if self._player.rect.centery < pillar.rect.centery:
                    self._player.rect.bottom = pillar.rect.top
                    self._player.velocity.y = 0
                    on_ground = True
                else:
                    self._player.rect.top = pillar.rect.bottom
                    if self._player.velocity.y < 0:
                        self._player.velocity.y = 0
        return on_ground

    def _resolve_boss_push(self) -> None:
        """Push the player out of the boss hitbox (physical mass)."""
        if not self._boss.is_alive:
            return
        if not self._player.rect.colliderect(self._boss.rect):
            return
        overlap = self._player.rect.clip(self._boss.rect)
        if overlap.width < overlap.height:
            if self._player.rect.centerx < self._boss.rect.centerx:
                self._player.rect.right = self._boss.rect.left
            else:
                self._player.rect.left = self._boss.rect.right
        else:
            if self._player.rect.centery < self._boss.rect.centery:
                self._player.rect.bottom = self._boss.rect.top
            else:
                self._player.rect.top = self._boss.rect.bottom
        self._clamp_to_solid(self._player.rect)

    def _clamp_to_solid(self, rect: pygame.Rect) -> None:
        """Push rect out of any overlapping solid tiles after push."""
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

    # ── Physics helpers ────────────────────────────────────────────

    def _check_wall_contact(
        self, rect: pygame.Rect
    ) -> tuple[bool, bool]:
        """Probe for wall contact.

        Args:
            rect: Entity bounding box.

        Returns:
            (wall_left, wall_right) booleans.
        """
        margin = PLAYER_WALL_CHECK_MARGIN

        left_probe = pygame.Rect(
            rect.left - margin, rect.top + 2, margin, rect.height - 4
        )
        wall_left = len(self._physics.check_collision(left_probe, "solid")) > 0

        right_probe = pygame.Rect(
            rect.right, rect.top + 2, margin, rect.height - 4
        )
        wall_right = len(self._physics.check_collision(right_probe, "solid")) > 0

        return wall_left, wall_right

    def _check_projectile_tile_collision(self) -> None:
        """Check player projectiles against the tilemap."""
        for proj in self._projectiles:
            if not proj.active:
                continue
            hits = self._physics.check_collision(proj.rect, "solid")
            if hits:
                proj.on_hit_tile()
        self._projectiles = [p for p in self._projectiles if p.active]

    # ── Arena generation ───────────────────────────────────────────

    def _build_arena_tilemap(
        self,
        width: int,
        height: int,
        tileset_id: str = "",
        tileset_surface: pygame.Surface | None = None,
    ) -> TileMap:
        """Build a procedural boss arena tilemap.

        Creates a flat arena with walls on the sides and a floor.

        Args:
            width: Arena width in tiles.
            height: Arena height in tiles.
            tileset_id: Tileset identifier for metadata (e.g. "world1_cave").
            tileset_surface: Optional tileset image for real rendering.

        Returns:
            A TileMap for the boss arena.
        """
        # Build tile data: solid border, empty interior.
        midground = []
        for row in range(height):
            tile_row = []
            for col in range(width):
                if row == 0 or row >= height - 2:
                    tile_row.append(1)  # Floor/ceiling.
                elif col == 0 or col == width - 1:
                    tile_row.append(1)  # Walls.
                else:
                    tile_row.append(0)  # Empty.
            midground.append(tile_row)

        # Create empty background and foreground layers.
        empty_layer = [[0] * width for _ in range(height)]

        tilemap_data = {
            "dimensions": {
                "width": width,
                "height": height,
            },
            "tile_size": TILE_SIZE,
            "layers": {
                "background": empty_layer,
                "midground": midground,
                "foreground": empty_layer,
            },
            "collision_types": {
                "solid": [1],
                "one_way": [],
                "hazard": [],
                "breakable_slam": [],
            },
            "metadata": {"tileset": tileset_id},
        }

        return TileMap(tilemap_data, tileset_surface=tileset_surface)

    # ── Cutscene push ─────────────────────────────────────────────

    def _push_cutscene(self) -> None:
        """Push the post-boss CutsceneScene onto the scene stack.

        Loads the cutscene definition and creates a CutsceneScene overlay.
        On retry (after the player died and restarted), enables fast-forward
        mode to skip dialogue.

        The cutscene's load_level callback is intercepted: instead of firing
        the external callback directly (which would modify the scene stack
        while the cutscene is still on top), the level path is stored as
        pending.  After the cutscene auto-pops, ``on_resume`` executes the
        actual transition.
        """
        if self._scene_manager is None:
            return

        from sa_fona.scenes.cutscene import CutsceneScene

        def _deferred_load_level(level_path: str) -> None:
            self._pending_level_load = level_path

        cutscene_data = CutsceneScene.load_cutscene_data(self._cutscene_id)
        scene = CutsceneScene(
            cutscene_data=cutscene_data,
            event_bus=self._event_bus,
            on_load_level=_deferred_load_level,
            fast_forward=self._is_retry,
        )
        scene.scene_manager = self._scene_manager
        self._scene_manager.push(scene)
        self._cutscene_pushed = True

    # ── Background rendering ─────────────────────────────────────────

    # Boss arenas are interior levels; use a subtle parallax factor.
    _PARALLAX_FACTOR: float = 0.15
    # Dim overlay alpha (~60% brightness) so tiles stay readable.
    _BG_DIM_ALPHA: int = 102

    def _render_background(self, surface: pygame.Surface) -> None:
        """Draw the arena background with parallax scrolling and dim overlay.

        If a background image was loaded from the boss definition, it is
        scaled to cover the full parallax scroll range and shifted by
        the camera position.  Otherwise falls back to the solid
        GAMEPLAY_BG_COLOR fill.

        A semi-transparent dim overlay is drawn on top to keep tiles
        readable, matching the GameplayScene pattern.

        Args:
            surface: Target surface (may be the zoom surface).
        """
        if self._background is not None:
            vp_w, vp_h = surface.get_size()
            level_px_w = self._tilemap.width_pixels

            # Background must be wide enough so that at maximum camera
            # scroll the parallax-shifted image still covers the viewport.
            required_w = max(
                vp_w,
                int(vp_w + (level_px_w - vp_w) * self._PARALLAX_FACTOR),
            )

            # Cache the scaled background to avoid per-frame scaling.
            if (
                not hasattr(self, "_bg_cache")
                or self._bg_cache.get_size() != (required_w, vp_h)
            ):
                self._bg_cache = pygame.transform.scale(
                    self._background, (required_w, vp_h)
                )

            cam_x = self._camera.offset[0]
            shift = -(cam_x * self._PARALLAX_FACTOR)
            # Clamp so edges never go past the viewport.
            shift = min(shift, 0)
            shift = max(shift, -(required_w - vp_w))
            surface.blit(self._bg_cache, (int(shift), 0))
        else:
            surface.fill(GAMEPLAY_BG_COLOR)

        # Dim overlay so gameplay tiles stand out.
        vp_w, vp_h = surface.get_size()
        if (
            not hasattr(self, "_dim_cache")
            or self._dim_cache.get_size() != (vp_w, vp_h)
        ):
            self._dim_cache = pygame.Surface((vp_w, vp_h), pygame.SRCALPHA)
            self._dim_cache.fill((0, 0, 0, self._BG_DIM_ALPHA))
        surface.blit(self._dim_cache, (0, 0))

    # ── Intro / Defeat sequences ───────────────────────────────────

    def _end_intro(self) -> None:
        """End the intro and start the fight."""
        self._intro_active = False
        self._fight_started = True
        self._boss.start_fight()
        # Screen shake as the boss activates.
        self._event_bus.publish("screen_shake", intensity=4.0, duration=0.3)

    def _render_intro(self, surface: pygame.Surface) -> None:
        """Render the intro overlay.

        Args:
            surface: Target surface.
        """
        # Semi-transparent dark overlay.
        overlay = pygame.Surface(
            (self._screen_width, self._screen_height), pygame.SRCALPHA
        )
        alpha = max(0, min(180, int(120 * (self._intro_timer / 2.0))))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

        # Boss name text.
        try:
            font = pygame.font.Font(None, 24)
            text = font.render(self._boss.display_name, False, (255, 255, 255))
            tx = (self._screen_width - text.get_width()) // 2
            ty = self._screen_height // 3
            surface.blit(text, (tx, ty))
        except pygame.error:
            pass

    def _render_defeat(self, surface: pygame.Surface) -> None:
        """Render the defeat overlay.

        Shows a white flash effect during the defeat sequence. After the
        post-boss cutscene completes, shows a dim overlay with VICTORY
        text and exit instructions.

        Args:
            surface: Target surface.
        """
        if self._cutscene_completed:
            overlay = pygame.Surface(
                (self._screen_width, self._screen_height), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))
            try:
                font = pygame.font.Font(None, 24)
                text = font.render("VICTORY!", False, (255, 220, 50))
                tx = (self._screen_width - text.get_width()) // 2
                ty = self._screen_height // 2 - 16
                surface.blit(text, (tx, ty))
                small = pygame.font.Font(None, 16)
                hint = small.render("Press ESC to continue", False, (200, 200, 200))
                hx = (self._screen_width - hint.get_width()) // 2
                surface.blit(hint, (hx, ty + 24))
            except pygame.error:
                pass
            return

        alpha = min(200, int(self._defeat_timer * 80))
        overlay = pygame.Surface(
            (self._screen_width, self._screen_height), pygame.SRCALPHA
        )
        overlay.fill((255, 255, 255, alpha))
        surface.blit(overlay, (0, 0))

        if self._cutscene_id is None and self._defeat_timer > 1.0:
            try:
                font = pygame.font.Font(None, 20)
                text = font.render("VICTORY!", False, (255, 220, 50))
                tx = (self._screen_width - text.get_width()) // 2
                ty = self._screen_height // 2 - 10
                surface.blit(text, (tx, ty))
            except pygame.error:
                pass

    # ── Reset ──────────────────────────────────────────────────────

    def _reset_fight(self) -> None:
        """Reset the boss fight from the beginning."""
        arena_data = self._boss_def.get("arena", {})

        # Reset player.
        player_spawn = arena_data.get("player_spawn", {"x": 2, "y": 11})
        spawn_x = player_spawn.get("x", 2) * TILE_SIZE
        spawn_y = player_spawn.get("y", 11) * TILE_SIZE
        self._player = Player(spawn_x, spawn_y)
        arena_h = arena_data.get("height", 14)
        self._player.rect.bottom = (arena_h - 2) * TILE_SIZE

        # Snap camera to player immediately (avoid lerp snap on respawn).
        self._camera.snap_to(self._player.rect)

        # Reset boss.
        boss_spawn = arena_data.get("boss_spawn", {"x": 20, "y": 9})
        boss_x = boss_spawn.get("x", 20) * TILE_SIZE
        boss_y = boss_spawn.get("y", 9) * TILE_SIZE
        arena_w = arena_data.get("width", 25)
        arena_h = arena_data.get("height", 14)
        arena_bounds = (0, 0, arena_w * TILE_SIZE, arena_h * TILE_SIZE)

        boss_cls = get_boss_class(self._boss_id)
        self._boss = boss_cls(
            boss_x, boss_y, self._boss_def, self._event_bus, arena_bounds
        )
        self._boss.rect.bottom = (arena_h - 2) * TILE_SIZE
        pillar_positions = arena_data.get("pillar_positions", [])
        self._boss.setup_pillars(pillar_positions)

        # Reset combat.
        self._sling_system = SlingSystem(self._event_bus, self._economy.config)
        self._projectiles.clear()
        self._charge_indicator = ChargeIndicator()

        starting_hearts = self._economy.get_starting_hearts()
        self._hud.set_state(
            max_hearts=int(starting_hearts),
            current_hearts=starting_hearts,
            stone_count=self._economy.stone_count,
        )
        self._combat.set_player_health(starting_hearts, int(starting_hearts))

        # Reset boss health bar.
        self._boss_health_bar = BossHealthBar(
            boss_name=self._boss.display_name,
            max_health=self._boss.max_health,
            phase_thresholds=[0.66, 0.33],
        )
        if self._boss_def.get("phases"):
            phase_name = self._boss_def["phases"][0].get("name", "")
            self._boss_health_bar.set_phase(1, phase_name)

        # Reset state.
        self._intro_active = True
        self._intro_timer = 1.0  # Shorter on retry.
        self._intro_skippable = True  # Can skip on retry.
        self._fight_started = False
        self._boss_defeated = False
        self._defeat_timer = 0.0
        self._cutscene_pushed = False
        self._cutscene_completed = False
        self._is_retry = True  # Fast-forward cutscene on retry.
        self._pending_game_over = False
        self._pending_level_load = None
        self._input_state = InputState()

    # ── Event handlers ─────────────────────────────────────────────

    def _on_screen_shake(
        self, intensity: float = 0.0, duration: float = 0.0
    ) -> None:
        """Handle screen_shake events.

        Args:
            intensity: Shake intensity.
            duration: Shake duration.
        """
        self._camera.shake(intensity, duration)

    def _on_boss_phase_change(self, **kwargs) -> None:
        """Handle boss_phase_change events."""
        new_phase = kwargs.get("new_phase", 1)
        # Update health bar phase display.
        phase_name = ""
        if new_phase - 1 < len(self._boss_def.get("phases", [])):
            phase_name = self._boss_def["phases"][new_phase - 1].get("name", "")
        self._boss_health_bar.set_phase(new_phase, phase_name)

    def _on_boss_defeated(self, **kwargs) -> None:
        """Handle boss_defeated events."""
        self._boss_defeated = True
        self._defeat_timer = 0.0
        self._event_bus.publish("screen_shake", intensity=10.0, duration=1.0)

    def _on_player_died(self, **kwargs) -> None:
        """Handle player death during boss fight."""
        self._pending_game_over = True

    def _push_game_over(self) -> None:
        """Push the game over scene."""
        if self._scene_manager is None:
            return

        from sa_fona.scenes.game_over import GameOverScene

        def _on_restart() -> None:
            if self._scene_manager is not None:
                self._scene_manager.pop()
                self._reset_fight()

        scene = GameOverScene(on_restart=_on_restart)
        self._scene_manager.push(scene)
