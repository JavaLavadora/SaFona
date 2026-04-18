"""Gameplay scene: loads a level, spawns the player, runs physics + camera.

This scene replaces DemoTilemapScene as the default entry point for
the game.  It wires together the Player entity, PhysicsSystem, Camera,
SlingSystem, and TileMap into a playable experience.
"""

from __future__ import annotations

import json

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
from sa_fona.entities.player import Player
from sa_fona.entities.projectile import Projectile
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.scenes.base_scene import BaseScene
from sa_fona.systems.physics import PhysicsSystem
from sa_fona.systems.sling_system import SlingSystem
from sa_fona.ui.charge_indicator import ChargeIndicator

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

        # Sling combat system.
        economy_data = self._load_economy_data()
        self._sling_system = SlingSystem(self._event_bus, economy_data)
        self._projectiles: list[Projectile] = []
        self._charge_indicator = ChargeIndicator()

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

    # ── Scene lifecycle ────────────────────────────────────────────

    def on_enter(self) -> None:
        """Scene entered -- nothing to set up beyond __init__."""

    def on_exit(self) -> None:
        """Clean up EventBus subscriptions when the scene is removed."""
        self._event_bus.unsubscribe("screen_shake", self._on_screen_shake)

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

        # Debug: screen shake on interact.
        if input_state.interact_pressed:
            self._event_bus.publish(
                "screen_shake",
                intensity=_SHAKE_INTENSITY,
                duration=_SHAKE_DURATION,
            )

    def update(self, dt: float) -> None:
        """Advance simulation by one frame.

        Orchestrates the update_intent -> physics -> post_physics
        flow so the Player never depends on PhysicsSystem directly.
        Also updates the sling system and active projectiles.

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

        # 5. Sling combat system: process input, spawn projectiles.
        new_projectiles = self._sling_system.update(
            self._input_state, self._player, dt
        )
        self._projectiles.extend(new_projectiles)

        # 6. Update projectiles and check tilemap collision.
        self._update_projectiles(dt)

        # 7. Update charge indicator.
        self._charge_indicator.update(self._sling_system.charge_tier, dt)

        self._camera.follow(self._player.rect, dt)
        self._camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draw tilemap layers, player, projectiles, and UI.

        Args:
            surface: The pygame Surface to draw on.
        """
        surface.fill(GAMEPLAY_BG_COLOR)
        cam_offset = self._camera.offset

        # Back-to-front layer rendering.
        self._tilemap.render_layer(surface, "background", cam_offset)
        self._tilemap.render_layer(surface, "midground", cam_offset)

        # Melee hitboxes (debug: translucent white flash).
        for hitbox in self._sling_system.melee_hitboxes:
            sx = hitbox.rect.x - cam_offset[0]
            sy = hitbox.rect.y - cam_offset[1]
            melee_surf = pygame.Surface(
                (hitbox.rect.width, hitbox.rect.height), pygame.SRCALPHA
            )
            melee_surf.fill((255, 255, 255, 120))
            surface.blit(melee_surf, (sx, sy))

        # Projectiles.
        for proj in self._projectiles:
            proj.render(surface, cam_offset)

        # Player.
        self._player.render(surface, cam_offset)

        # Charge indicator (UI, world-space near player).
        self._charge_indicator.render(surface, self._player.rect, cam_offset)

        # Foreground on top.
        self._tilemap.render_layer(surface, "foreground", cam_offset)

    # ── Physics helpers ────────────────────────────────────────────

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

    def _update_projectiles(self, dt: float) -> None:
        """Move projectiles, check tilemap collision, remove inactive.

        Args:
            dt: Delta time in seconds.
        """
        for proj in self._projectiles:
            proj.update(dt)
            # Check solid tile collision.
            hits = self._physics.check_collision(proj.rect, "solid")
            if hits:
                proj.on_hit_tile()
        # Remove inactive projectiles.
        self._projectiles = [p for p in self._projectiles if p.active]

    # ── Economy data loading ───────────────────────────────────────

    @staticmethod
    def _load_economy_data() -> dict:
        """Load economy.json from the data directory.

        Returns:
            Parsed JSON dict with economy configuration.
        """
        economy_path = DATA_DIR / "economy.json"
        try:
            with open(economy_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return minimal defaults if file is missing.
            return {"sling": {}}

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

        # Reset combat state.
        economy_data = self._load_economy_data()
        self._sling_system = SlingSystem(self._event_bus, economy_data)
        self._projectiles.clear()
        self._charge_indicator = ChargeIndicator()

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
