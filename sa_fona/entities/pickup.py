"""Pickup entities: heart pickups restore health, stone pickups add currency.

Pickups are spawned from level JSON entity definitions or dropped by
breakable objects and enemies.  They sit in the world and are collected
when the player overlaps them.  Collection publishes an EventBus event
(heart_collected or stone_collected) so that the HUD, EconomySystem,
and player health can react without direct coupling.

Placeholder rendering:
- Heart pickup: red diamond shape
- Stone pickup: grey circle
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.entities.entity import Entity
from sa_fona.rendering.asset_loader import load_frame_strip


class PickupType(Enum):
    """Identifies the kind of pickup."""

    HEART = auto()
    STONE = auto()


# Pickup dimensions (pixels).
PICKUP_WIDTH: int = 18
PICKUP_HEIGHT: int = 18


class Pickup(Entity):
    """A collectible item in the game world.

    Pickups are static entities that the player collects by overlapping.
    They do not move or respond to physics -- they simply sit at their
    spawn position until collected.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        pickup_type: The kind of pickup (HEART or STONE).
        value: The amount this pickup provides (hearts or stones).
    """

    def __init__(
        self,
        x: float,
        y: float,
        pickup_type: PickupType,
        value: float = 1.0,
    ) -> None:
        super().__init__(x, y, PICKUP_WIDTH, PICKUP_HEIGHT)
        self.pickup_type = pickup_type
        self.value = value

        # Build placeholder sprite.
        self._build_sprite()

    def _build_sprite(self) -> None:
        """Load a real sprite or create a placeholder."""
        sprite_map = {
            PickupType.HEART: "assets/sprites/pickups/heart.png",
            PickupType.STONE: "assets/sprites/pickups/stone.png",
        }
        path = sprite_map.get(self.pickup_type)
        if path:
            frames = load_frame_strip(path, PICKUP_WIDTH, PICKUP_HEIGHT)
            if frames:
                self._sprite = frames[0]
                return

        surf = pygame.Surface((PICKUP_WIDTH, PICKUP_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        if self.pickup_type == PickupType.HEART:
            cx = PICKUP_WIDTH // 2
            cy = PICKUP_HEIGHT // 2
            points = [
                (cx, 0),                # top
                (PICKUP_WIDTH - 1, cy), # right
                (cx, PICKUP_HEIGHT - 1),# bottom
                (0, cy),                # left
            ]
            pygame.draw.polygon(surf, (220, 40, 40), points)
            pygame.draw.polygon(surf, (180, 30, 30), points, 1)
        elif self.pickup_type == PickupType.STONE:
            cx = PICKUP_WIDTH // 2
            cy = PICKUP_HEIGHT // 2
            radius = min(cx, cy) - 1
            pygame.draw.circle(surf, (160, 160, 160), (cx, cy), radius)
            pygame.draw.circle(surf, (120, 120, 120), (cx, cy), radius, 1)

        self._sprite = surf

    def update(self, dt: float) -> None:
        """Pickups are static -- no per-frame logic needed.

        Args:
            dt: Delta time in seconds (unused).
        """
        pass

    def collect(self) -> tuple[str, dict]:
        """Mark the pickup as collected and return the event to publish.

        Returns:
            A tuple of (event_type, event_data) for the EventBus.
            For hearts: ("heart_collected", {"amount": value})
            For stones: ("stone_collected", {"amount": int(value)})
        """
        self.active = False
        if self.pickup_type == PickupType.HEART:
            return ("heart_collected", {"amount": self.value})
        else:
            return ("stone_collected", {"amount": int(self.value)})
