"""AABB collision detection and resolution against tile geometry."""

from __future__ import annotations

import pygame

from sa_fona.level.tilemap import TileMap


class PhysicsSystem:
    """AABB collision detection and resolution.

    Applies gravity, moves entities represented as ``pygame.Rect`` objects,
    and resolves collisions against the tilemap's collision layers.  Uses
    separate X and Y resolution passes to avoid corner-case tunnelling.

    Attributes:
        gravity: Vertical acceleration in pixels per second squared.
    """

    def __init__(self, tilemap: TileMap, gravity: float = 800.0) -> None:
        """Initialise the physics system.

        Args:
            tilemap: The level's tile geometry used for collision queries.
            gravity: Downward acceleration in px/s^2. Defaults to 800.
        """
        self._tilemap = tilemap
        self._gravity = gravity

    # ── Public API ─────────────────────────────────────────────────

    def update_rect(
        self,
        rect: pygame.Rect,
        velocity: list[float],
        dt: float,
        on_ground: bool,
    ) -> tuple[pygame.Rect, list[float], bool]:
        """Apply gravity, move a rect, and resolve collisions.

        The rect is moved on the X axis first (with collision resolution),
        then on the Y axis. This two-pass approach prevents diagonal
        tunnelling.

        Args:
            rect: The entity's bounding box (will be copied, not mutated).
            velocity: ``[vx, vy]`` in pixels/second. Modified in-place.
            dt: Delta time in seconds.
            on_ground: Whether the entity was on the ground last frame.

        Returns:
            Tuple of ``(resolved_rect, resolved_velocity, new_on_ground)``.
        """
        new_rect = rect.copy()
        vx, vy = velocity[0], velocity[1]

        # Apply gravity.
        vy += self._gravity * dt

        # ── X pass ─────────────────────────────────────────────
        new_rect.x += round(vx * dt)
        vx, new_rect = self._resolve_x(new_rect, vx)

        # ── Y pass ─────────────────────────────────────────────
        prev_bottom = new_rect.bottom
        dy = round(vy * dt)
        # When resting on ground with very small accumulated vy,
        # always probe at least 1 px so ground contact is re-detected.
        if on_ground and vy > 0 and dy == 0:
            dy = 1
        new_rect.y += dy
        vy, new_rect, new_on_ground = self._resolve_y(
            new_rect, vy, prev_bottom
        )

        velocity[0] = vx
        velocity[1] = vy
        return new_rect, velocity, new_on_ground

    def check_collision(
        self, rect: pygame.Rect, layer: str = "solid"
    ) -> list[pygame.Rect]:
        """Return all tile rects of a collision type that overlap *rect*.

        Args:
            rect: The bounding box to test.
            layer: Collision category name.

        Returns:
            List of overlapping tile rects.
        """
        colliders = self._tilemap.get_collision_rects(layer)
        return [c for c in colliders if rect.colliderect(c)]

    @property
    def gravity(self) -> float:
        """Vertical acceleration in pixels per second squared."""
        return self._gravity

    # ── Private resolution helpers ─────────────────────────────────

    def _resolve_x(
        self, rect: pygame.Rect, vx: float
    ) -> tuple[float, pygame.Rect]:
        """Resolve horizontal collisions against solid tiles.

        Args:
            rect: Current bounding box (mutated in-place).
            vx: Horizontal velocity.

        Returns:
            Tuple of ``(clamped_vx, resolved_rect)``.
        """
        for tile_rect in self._tilemap.get_collision_rects("solid"):
            if not rect.colliderect(tile_rect):
                continue
            if vx > 0:
                rect.right = tile_rect.left
            elif vx < 0:
                rect.left = tile_rect.right
            vx = 0.0
        return vx, rect

    def _resolve_y(
        self,
        rect: pygame.Rect,
        vy: float,
        prev_bottom: int,
    ) -> tuple[float, pygame.Rect, bool]:
        """Resolve vertical collisions against solid and one-way tiles.

        Args:
            rect: Current bounding box (mutated in-place).
            vy: Vertical velocity.
            prev_bottom: The entity's bottom edge before the Y move,
                used for one-way platform logic.

        Returns:
            Tuple of ``(clamped_vy, resolved_rect, on_ground)``.
        """
        on_ground = False

        # Solid tiles — full resolution.
        for tile_rect in self._tilemap.get_collision_rects("solid"):
            if not rect.colliderect(tile_rect):
                continue
            if vy > 0:
                rect.bottom = tile_rect.top
                on_ground = True
            elif vy < 0:
                rect.top = tile_rect.bottom
            vy = 0.0

        # One-way platforms — only resolve when falling and entity was
        # above the platform on the previous frame.
        for tile_rect in self._tilemap.get_collision_rects("one_way"):
            if not rect.colliderect(tile_rect):
                continue
            if vy > 0 and prev_bottom <= tile_rect.top:
                rect.bottom = tile_rect.top
                vy = 0.0
                on_ground = True

        return vy, rect, on_ground
