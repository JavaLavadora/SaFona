"""Charge indicator UI element displayed near the player during sling charge.

Shows a small visual indicator near Ramon that changes color based on
the current charge tier. Uses charge_indicator.png frame strip when
available (3 frames for tiers 1-3), falling back to colored rectangles.

- Tier 0 (not charging): hidden
- Tier 1 (faint glow): dim yellow / frame 0
- Tier 2 (bright): bright orange / frame 1
- Tier 3 (flash): pulsing white/red / frame 2

The indicator is rendered in world space (moves with the camera) above
the player's head.
"""

from __future__ import annotations

import math

import pygame

from sa_fona.rendering.asset_loader import load_ui_frame_strip


# Colors per charge tier.
_TIER_COLORS: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),           # hidden (not drawn)
    1: (180, 180, 80),      # faint yellow glow
    2: (255, 180, 50),      # bright orange
    3: (255, 255, 255),     # white (flashes to red)
}

_TIER3_FLASH_COLOR: tuple[int, int, int] = (255, 60, 60)  # red flash

# Indicator dimensions.
_INDICATOR_WIDTH: int = 12
_INDICATOR_HEIGHT: int = 4
_INDICATOR_OFFSET_Y: int = -8  # pixels above player top edge


class ChargeIndicator:
    """Visual feedback for sling charge tier, drawn near the player.

    The indicator is a small bar above the player's head.  It grows
    slightly wider and changes color as the charge tier increases.
    At Tier 3, it flashes between white and red.

    This class does not own any game state -- it reads the current
    charge tier from the SlingSystem each frame.
    """

    def __init__(self) -> None:
        self._tier: int = 0
        self._flash_timer: float = 0.0
        self._indicator_frames: list[pygame.Surface] | None = None
        self._frames_loaded: bool = False

    def update(self, tier: int, dt: float) -> None:
        """Update the indicator state.

        Args:
            tier: Current charge tier (0-3) from SlingSystem.
            dt: Delta time in seconds.
        """
        self._tier = tier
        if tier == 3:
            self._flash_timer += dt
        else:
            self._flash_timer = 0.0

    def render(
        self,
        surface: pygame.Surface,
        player_rect: pygame.Rect,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the charge indicator above the player.

        Uses charge_indicator.png frame strip when available, falling
        back to colored rectangles.

        Args:
            surface: Target surface to draw on.
            player_rect: Player's world-space bounding rect.
            camera_offset: Camera offset ``(cam_x, cam_y)``.
        """
        if self._tier == 0:
            return

        # Lazy load indicator frames.
        if not self._frames_loaded:
            self._frames_loaded = True
            self._indicator_frames = load_ui_frame_strip("charge_indicator")

        # Position above the player's head.
        screen_x = (player_rect.centerx - camera_offset[0])
        screen_y = (player_rect.top - camera_offset[1]) + _INDICATOR_OFFSET_Y

        # Try sprite frames first (tier 1=frame 0, tier 2=frame 1, tier 3=frame 2).
        frame_idx = self._tier - 1
        if (
            self._indicator_frames
            and 0 <= frame_idx < len(self._indicator_frames)
        ):
            frame = self._indicator_frames[frame_idx]
            fx = screen_x - frame.get_width() // 2
            fy = screen_y

            # Tier 3: flash by toggling visibility.
            if self._tier == 3:
                phase = math.sin(self._flash_timer * 8.0 * math.pi)
                if phase < 0:
                    return  # Flash off

            surface.blit(frame, (fx, fy))
            return

        # Fallback: colored rectangle.
        if self._tier == 3:
            phase = math.sin(self._flash_timer * 8.0 * math.pi)
            if phase > 0:
                color = _TIER_COLORS[3]
            else:
                color = _TIER3_FLASH_COLOR
        else:
            color = _TIER_COLORS.get(self._tier, _TIER_COLORS[1])

        width = _INDICATOR_WIDTH + (self._tier - 1) * 4
        height = _INDICATOR_HEIGHT

        rect_x = screen_x - width // 2
        indicator_rect = pygame.Rect(rect_x, screen_y, width, height)
        pygame.draw.rect(surface, color, indicator_rect)

        border_color = tuple(max(0, c - 60) for c in color)
        pygame.draw.rect(surface, border_color, indicator_rect, 1)
