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

# Breakable dimensions (pixels).
BREAKABLE_WIDTH: int = 16
BREAKABLE_HEIGHT: int = 16

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
        self._build_sprite()

    def _build_sprite(self) -> None:
        """Create a placeholder sprite based on breakable type."""
        color = _BREAKABLE_COLORS.get(self.breakable_type, (140, 90, 40))
        surf = pygame.Surface((BREAKABLE_WIDTH, BREAKABLE_HEIGHT))
        surf.fill(color)

        # Draw a border.
        border_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(surf, border_color, (0, 0, BREAKABLE_WIDTH, BREAKABLE_HEIGHT), 1)

        # Crates get an X pattern.
        if "crate" in self.breakable_type:
            pygame.draw.line(surf, border_color, (0, 0), (BREAKABLE_WIDTH - 1, BREAKABLE_HEIGHT - 1), 1)
            pygame.draw.line(surf, border_color, (BREAKABLE_WIDTH - 1, 0), (0, BREAKABLE_HEIGHT - 1), 1)

        self._sprite = surf

    def update(self, dt: float) -> None:
        """Breakables are static -- no per-frame logic needed.

        Args:
            dt: Delta time in seconds (unused).
        """
        pass

    def on_hit(self, stone_yield: int) -> list[Pickup]:
        """Handle being hit by a melee attack.  Destroys the breakable
        and returns a list of pickup entities to spawn.

        Args:
            stone_yield: Number of stones to drop (from EconomySystem).

        Returns:
            A list of Pickup entities spawned at this location.
        """
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
