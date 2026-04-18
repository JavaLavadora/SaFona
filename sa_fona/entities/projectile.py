"""Projectile entity for sling stones and future special ammo types.

A projectile travels in a direction at a configurable speed and is
destroyed when it collides with solid tiles or exceeds its maximum
range.  The base class is designed for extension -- subclasses can
override ``on_hit_tile`` and ``on_hit_entity`` for special ammo
behaviours (explosive, piercing, freezing).
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.entities.entity import Entity


class ProjectileType(Enum):
    """Identifies the kind of projectile for rendering and behaviour."""

    BASIC_STONE = auto()
    # Future types will be added here:
    # EXPLOSIVE_ROCK = auto()
    # PIERCING_ROCK = auto()
    # FROZEN_ROCK = auto()


# Placeholder colors per projectile type.
_PROJECTILE_COLORS: dict[ProjectileType, tuple[int, int, int]] = {
    ProjectileType.BASIC_STONE: (180, 160, 140),  # warm grey stone
}


class Projectile(Entity):
    """A sling stone that flies in a direction and interacts with the world.

    Projectiles are spawned by the SlingSystem.  They move in a straight
    line, check collision with the tilemap (destroyed on solid hit) and
    can later be checked against enemy entities by the CombatSystem.

    Attributes:
        damage: Amount of damage dealt on hit.
        charge_tier: The charge tier that spawned this projectile (1-3).
        projectile_type: Enum identifying this projectile's behaviour.
        max_range: Maximum travel distance in pixels before auto-destroy.
        distance_travelled: Pixels moved since spawning.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        width: Bounding box width.
        height: Bounding box height.
        direction: Horizontal direction (+1.0 right, -1.0 left).
        speed: Travel speed in pixels per second.
        damage: Damage dealt on impact.
        charge_tier: Charge tier (1, 2, or 3).
        max_range: Maximum range in pixels.
        projectile_type: Type of projectile.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        direction: float,
        speed: float,
        damage: float,
        charge_tier: int,
        max_range: float,
        projectile_type: ProjectileType = ProjectileType.BASIC_STONE,
    ) -> None:
        super().__init__(x, y, width, height)
        self.damage = damage
        self.charge_tier = charge_tier
        self.projectile_type = projectile_type
        self.max_range = max_range
        self.distance_travelled: float = 0.0

        # Set velocity based on direction and speed.
        self.velocity[0] = direction * speed
        self.velocity[1] = 0.0
        self.facing_right = direction > 0

        # Build placeholder sprite.
        color = _PROJECTILE_COLORS.get(projectile_type, (180, 160, 140))
        self._sprite = pygame.Surface((width, height))
        self._sprite.fill(color)

    # ── Update ─────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        """Move the projectile and check range limit.

        Note: tilemap collision is handled externally by the scene,
        which calls ``check_tile_collision`` after moving the rect.

        Args:
            dt: Delta time in seconds.
        """
        dx = self.velocity[0] * dt
        self.rect.x += round(dx)
        self.distance_travelled += abs(dx)

        if self.distance_travelled >= self.max_range:
            self.active = False

    # ── Collision hooks (override for special ammo) ────────────────

    def on_hit_tile(self) -> None:
        """Called when the projectile collides with a solid tile.

        Default behaviour: destroy the projectile.  Override in
        subclasses for special effects (e.g., explosive rock creates
        an AOE, piercing rock continues).
        """
        self.active = False

    def on_hit_entity(self, entity: Entity) -> None:
        """Called when the projectile collides with an entity.

        Default behaviour: destroy the projectile.  Override for
        special effects (e.g., piercing rock does not destroy,
        frozen rock applies freeze status).

        Args:
            entity: The entity that was hit.
        """
        self.active = False
