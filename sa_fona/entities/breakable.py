"""Breakable object entities: pots, crates, and other destructibles.

Breakable objects can be hit with the sling tap attack and drop pickups
based on economy.json drop tables.  They are spawned from level JSON
entity definitions.

Placeholder rendering:
- Pot: brown/orange rectangle
- Crate: darker brown rectangle with an 'X' pattern
"""

from __future__ import annotations

import random

import pygame

from sa_fona.entities.entity import Entity
from sa_fona.entities.pickup import Pickup, PickupType
from sa_fona.rendering.asset_loader import load_frame_strip

# Breakable dimensions (pixels).
BREAKABLE_WIDTH: int = 24
BREAKABLE_HEIGHT: int = 24

# Colors per breakable type.
_BREAKABLE_COLORS: dict[str, tuple[int, int, int]] = {
    "breakable_pot": (180, 120, 60),     # brown/orange
    "breakable_crate": (140, 90, 40),    # darker brown
}


class Breakable(Entity):
    """A destructible object that drops pickups when broken.

    Breakables are static entities that can be destroyed by the sling
    tap melee attack.  On destruction, they spawn pickup entities based
    on the economy.json drop tables.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        breakable_type: The type key (e.g. "breakable_pot", "breakable_crate").
    """

    def __init__(
        self,
        x: float,
        y: float,
        breakable_type: str = "breakable_pot",
    ) -> None:
        super().__init__(x, y, BREAKABLE_WIDTH, BREAKABLE_HEIGHT)
        self.breakable_type = breakable_type
        self._break_frames: list[pygame.Surface] = []
        self._breaking: bool = False
        self._break_timer: float = 0.0
        self._break_frame: int = 0
        self._build_sprite()

    def _build_sprite(self) -> None:
        """Load real sprites (intact and break) or create a placeholder."""
        sprite_map = {
            "breakable_pot": "assets/sprites/breakables/pot.png",
            "breakable_crate": "assets/sprites/breakables/crate.png",
        }
        break_map = {
            "breakable_pot": "assets/sprites/breakables/pot_break.png",
            "breakable_crate": "assets/sprites/breakables/crate_break.png",
        }

        # Load intact sprite.
        path = sprite_map.get(self.breakable_type)
        if path:
            frames = load_frame_strip(path, BREAKABLE_WIDTH, BREAKABLE_HEIGHT)
            if frames:
                self._sprite = frames[0]
            else:
                self._sprite = self._create_placeholder()
        else:
            self._sprite = self._create_placeholder()

        # Load break animation frames.
        break_path = break_map.get(self.breakable_type)
        if break_path:
            break_frames = load_frame_strip(
                break_path, BREAKABLE_WIDTH, BREAKABLE_HEIGHT,
            )
            if break_frames:
                self._break_frames = break_frames

    def _create_placeholder(self) -> pygame.Surface:
        """Create a fallback placeholder surface.

        Returns:
            A colored pygame Surface.
        """
        color = _BREAKABLE_COLORS.get(self.breakable_type, (140, 90, 40))
        surf = pygame.Surface((BREAKABLE_WIDTH, BREAKABLE_HEIGHT))
        surf.fill(color)

        border_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(surf, border_color, (0, 0, BREAKABLE_WIDTH, BREAKABLE_HEIGHT), 1)

        if "crate" in self.breakable_type:
            pygame.draw.line(surf, border_color, (0, 0), (BREAKABLE_WIDTH - 1, BREAKABLE_HEIGHT - 1), 1)
            pygame.draw.line(surf, border_color, (BREAKABLE_WIDTH - 1, 0), (0, BREAKABLE_HEIGHT - 1), 1)

        return surf

    # Duration each break animation frame is shown (seconds).
    _BREAK_FRAME_DURATION: float = 0.08

    def update(self, dt: float) -> None:
        """Advance the break animation if the breakable is breaking.

        Args:
            dt: Delta time in seconds.
        """
        if not self._breaking:
            return

        self._break_timer += dt
        frame_dur = self._BREAK_FRAME_DURATION
        self._break_frame = int(self._break_timer / frame_dur)

        if self._break_frame >= len(self._break_frames):
            # Animation complete -- deactivate.
            self.active = False
            return

        self._sprite = self._break_frames[self._break_frame]

    def on_hit(self, stone_yield: int) -> list[Pickup]:
        """Handle being hit by a melee attack.  Destroys the breakable
        and returns a list of pickup entities to spawn.

        If break animation frames are available, the breakable starts
        playing its break animation before disappearing.  Otherwise it
        deactivates immediately.

        Args:
            stone_yield: Number of stones to drop (from EconomySystem).

        Returns:
            A list of Pickup entities spawned at this location.
        """
        if self._break_frames:
            # Start break animation; the entity stays active briefly
            # to render the animation, but is flagged as breaking.
            self._breaking = True
            self._break_timer = 0.0
            self._break_frame = 0
            self._sprite = self._break_frames[0]
        else:
            # No break animation -- deactivate immediately.
            self.active = False

        pickups: list[Pickup] = []

        # Spawn stone pickups at slightly randomized positions.
        for i in range(stone_yield):
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-12, 0)
            pickup = Pickup(
                x=self.rect.centerx + offset_x,
                y=self.rect.top + offset_y,
                pickup_type=PickupType.STONE,
                value=1.0,
            )
            pickups.append(pickup)

        return pickups
