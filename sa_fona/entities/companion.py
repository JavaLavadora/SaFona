"""Companion entity (Bep): follows Ramon with simple AI.

Bep is a purely visual companion that follows the player around.
No gameplay interaction -- just visual presence and dialogue trigger.
Uses real sprite sheet when available, falls back to green rectangle.
"""

from __future__ import annotations

import pygame

from sa_fona.entities.entity import Entity
from sa_fona.rendering.asset_loader import load_frame_strip

# Companion dimensions (placeholder).
COMPANION_WIDTH = 16
COMPANION_HEIGHT = 16

# Companion colors.
COMPANION_COLOR = (50, 180, 80)  # Green
COMPANION_LABEL_COLOR = (255, 255, 255)

# Follow AI parameters.
FOLLOW_SPEED = 100.0        # px/s when catching up
FOLLOW_DISTANCE = 32.0      # desired offset from player (pixels)
CATCH_UP_DISTANCE = 80.0    # distance at which Bep starts running faster
CATCH_UP_SPEED = 180.0      # px/s when far away
TELEPORT_DISTANCE = 300.0   # distance at which Bep teleports to player
GRAVITY = 800.0             # px/s^2

# Vertical bob animation.
BOB_AMPLITUDE = 2.0
BOB_SPEED = 3.0


class Companion(Entity):
    """Bep, the myotragus companion who follows Ramon around.

    Purely visual: follows the player with simple chase/lerp AI,
    rendered as a green placeholder rectangle. Does not interact
    with gameplay systems (no collision, no combat).

    Args:
        x: Initial X position in world pixels.
        y: Initial Y position in world pixels.
    """

    def __init__(self, x: float, y: float) -> None:
        """Initialize Bep at the given world position.

        Args:
            x: X position in world pixels.
            y: Y position in world pixels.
        """
        super().__init__(x, y, COMPANION_WIDTH, COMPANION_HEIGHT)
        self._target_x: float = x
        self._target_y: float = y
        self._bob_timer: float = 0.0
        self._font: pygame.font.Font | None = None
        self._idle_frames: list[pygame.Surface] = []
        self._walk_frames: list[pygame.Surface] = []
        self._jump_frames: list[pygame.Surface] = []
        self._scared_frames: list[pygame.Surface] = []
        self._excited_frames: list[pygame.Surface] = []
        self._anim_timer: float = 0.0
        self._anim_frame: int = 0
        self._anim_speed: float = 0.25
        self._has_sprites: bool = False

        # Current state for animation selection.
        self._anim_state: str = "idle"
        self._is_moving: bool = False

        # Load all available sprite sheets.
        anim_map = {
            "_idle_frames": "idle",
            "_walk_frames": "walk",
            "_jump_frames": "jump",
            "_scared_frames": "scared",
            "_excited_frames": "excited",
        }
        for attr, name in anim_map.items():
            frames = load_frame_strip(
                f"assets/sprites/bep/{name}.png",
                COMPANION_WIDTH, COMPANION_HEIGHT,
            )
            if frames:
                setattr(self, attr, frames)
                self._has_sprites = True

    def follow(self, player_rect: pygame.Rect, dt: float) -> None:
        """Update Bep's position to follow the player.

        Uses simple chase AI: stay near the player at a comfortable offset,
        speed up when far away, teleport when extremely far.

        Args:
            player_rect: The player's bounding box.
            dt: Delta time in seconds.
        """
        # Target position: behind the player (opposite of facing direction).
        self._target_x = float(player_rect.x) - FOLLOW_DISTANCE
        self._target_y = float(player_rect.bottom) - COMPANION_HEIGHT

        dx = self._target_x - self.rect.x
        dy = self._target_y - self.rect.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > TELEPORT_DISTANCE:
            # Teleport to player when too far.
            self.rect.x = int(self._target_x)
            self.rect.y = int(self._target_y)
            return

        # Choose speed based on distance.
        if distance > CATCH_UP_DISTANCE:
            speed = CATCH_UP_SPEED
        elif distance > 4.0:
            speed = FOLLOW_SPEED
        else:
            # Close enough, don't move.
            return

        # Move toward target.
        if distance > 0:
            move_x = (dx / distance) * speed * dt
            move_y = (dy / distance) * speed * dt

            # Don't overshoot.
            if abs(move_x) > abs(dx):
                move_x = dx
            if abs(move_y) > abs(dy):
                move_y = dy

            self.rect.x += int(move_x)
            self.rect.y += int(move_y)
            self._is_moving = True
        else:
            self._is_moving = False

    def _current_frames(self) -> list[pygame.Surface]:
        """Return the frame list for the current animation state.

        Returns:
            The appropriate frame list, or an empty list when no
            sprites are loaded.
        """
        if self._anim_state == "scared" and self._scared_frames:
            return self._scared_frames
        if self._anim_state == "excited" and self._excited_frames:
            return self._excited_frames
        if self._is_moving and self._walk_frames:
            return self._walk_frames
        if self._idle_frames:
            return self._idle_frames
        return []

    def set_emotion(self, emotion: str) -> None:
        """Set Bep's emotion state for animation.

        Args:
            emotion: One of "idle", "scared", "excited".
        """
        if emotion in ("scared", "excited", "idle"):
            self._anim_state = emotion
            self._anim_frame = 0
            self._anim_timer = 0.0

    def update(self, dt: float) -> None:
        """Update the bob and sprite animation timers.

        Args:
            dt: Delta time in seconds.
        """
        self._bob_timer += dt * BOB_SPEED

        frames = self._current_frames()
        if frames:
            self._anim_timer += dt
            if self._anim_timer >= self._anim_speed:
                self._anim_timer -= self._anim_speed
                self._anim_frame = (self._anim_frame + 1) % len(frames)

    def render(self, surface: pygame.Surface, camera_offset: tuple[int, int]) -> None:
        """Draw Bep using real sprites or a green rectangle fallback.

        Args:
            surface: Target pygame Surface.
            camera_offset: ``(cam_x, cam_y)`` world-pixel camera offset.
        """
        import math

        bob_y = int(math.sin(self._bob_timer) * BOB_AMPLITUDE)

        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1] + bob_y

        frames = self._current_frames()
        if frames:
            idx = self._anim_frame % len(frames)
            surface.blit(frames[idx], (screen_x, screen_y))
            return

        # Fallback: green rectangle with "B" label.
        pygame.draw.rect(
            surface,
            COMPANION_COLOR,
            (screen_x, screen_y, COMPANION_WIDTH, COMPANION_HEIGHT),
        )

        try:
            if self._font is None:
                self._font = pygame.font.Font(None, 14)
            label = self._font.render("B", False, COMPANION_LABEL_COLOR)
            lx = screen_x + (COMPANION_WIDTH - label.get_width()) // 2
            ly = screen_y + (COMPANION_HEIGHT - label.get_height()) // 2
            surface.blit(label, (lx, ly))
        except pygame.error:
            pass
