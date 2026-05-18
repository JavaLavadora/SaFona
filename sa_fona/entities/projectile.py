"""Projectile entity for sling stones and future special ammo types.

A projectile travels in a direction at a configurable speed and is
destroyed when it collides with solid tiles or exceeds its maximum
range.  Uses real sprite PNGs from assets/sprites/projectiles/ when
available.
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.config.settings import PLAYER_GRAVITY
from sa_fona.entities.entity import Entity
from sa_fona.rendering.asset_loader import load_frame_strip

_PROJECTILE_GRAVITY: float = PLAYER_GRAVITY * 0.25


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

        # Try to load a real sprite based on charge tier.
        self._sprite = self._load_projectile_sprite(
            width, height, charge_tier, projectile_type,
        )

    @staticmethod
    def _load_projectile_sprite(
        width: int,
        height: int,
        charge_tier: int,
        projectile_type: ProjectileType,
    ) -> pygame.Surface:
        """Load a projectile sprite or create a placeholder.

        Args:
            width: Sprite width.
            height: Sprite height.
            charge_tier: Charge tier (1-3) for stone projectiles.
            projectile_type: Type of projectile.

        Returns:
            A pygame Surface.
        """
        if projectile_type == ProjectileType.BASIC_STONE:
            tier = max(1, min(3, charge_tier))
            path = f"assets/sprites/projectiles/stone_tier{tier}.png"
            frames = load_frame_strip(path, width, height)
            if frames:
                return frames[0]

        # Fallback: solid color rectangle.
        color = _PROJECTILE_COLORS.get(projectile_type, (180, 160, 140))
        surf = pygame.Surface((width, height))
        surf.fill(color)
        return surf

    # ── Update ─────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        """Move the projectile with gravity and check range limit.

        Args:
            dt: Delta time in seconds.
        """
        self.velocity[1] += _PROJECTILE_GRAVITY * dt

        dx = self.velocity[0] * dt
        dy = self.velocity[1] * dt
        self.rect.x += round(dx)
        self.rect.y += round(dy)
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
