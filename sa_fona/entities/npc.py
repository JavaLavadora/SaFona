"""Generic NPC entity for world interactions.

NPCs are non-hostile entities placed in levels that the player can
interact with (via the Interact key).  Each NPC has a type that
determines its behaviour (e.g. ``shop`` opens the shop overlay).

Placeholder rendering draws a tall coloured rectangle with the NPC's
initial letter, consistent with the project's placeholder aesthetic.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import COLORS
from sa_fona.entities.entity import Entity


# NPC placeholder dimensions (slightly taller than the player).
_NPC_WIDTH: int = 20
_NPC_HEIGHT: int = 36

# Interaction zone extends beyond the NPC's visual rect so the player
# does not need pixel-perfect overlap to trigger interaction.
_INTERACT_MARGIN_X: int = 12
_INTERACT_MARGIN_Y: int = 4


class NPC(Entity):
    """A non-player character that can be interacted with.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        npc_id: Unique identifier for this NPC instance.
        npc_type: Behaviour type (e.g. ``"shop"``).
        label: Single character displayed on the placeholder sprite.
    """

    def __init__(
        self,
        x: float,
        y: float,
        npc_id: str = "llorencc",
        npc_type: str = "shop",
        label: str = "L",
    ) -> None:
        super().__init__(x, y, _NPC_WIDTH, _NPC_HEIGHT)
        self._npc_id = npc_id
        self._npc_type = npc_type
        self._label = label

        # Build placeholder sprite.
        self._build_sprite()

        # Pre-compute the interaction rect (wider than visual).
        self._interact_rect = self.rect.inflate(
            _INTERACT_MARGIN_X * 2, _INTERACT_MARGIN_Y * 2,
        )

    # ── Properties ─────────────────────────────────────────────────

    @property
    def npc_id(self) -> str:
        """Unique NPC identifier."""
        return self._npc_id

    @property
    def npc_type(self) -> str:
        """Behaviour type of this NPC (e.g. ``"shop"``)."""
        return self._npc_type

    @property
    def interact_rect(self) -> pygame.Rect:
        """Interaction zone; larger than the visual rect for usability."""
        return self._interact_rect

    # ── Entity interface ──────────────────────────────────────────

    def update(self, dt: float) -> None:
        """NPCs are static -- nothing to update per frame.

        Args:
            dt: Delta time in seconds (unused).
        """

    def render(
        self, surface: pygame.Surface, camera_offset: tuple[int, int],
    ) -> None:
        """Draw the NPC placeholder rectangle with label.

        Args:
            surface: Target pygame Surface.
            camera_offset: Camera world-pixel offset.
        """
        sx = self.rect.x - camera_offset[0]
        sy = self.rect.y - camera_offset[1]

        # Green rectangle placeholder.
        pygame.draw.rect(
            surface, COLORS["GREEN"], (sx, sy, self.rect.width, self.rect.height),
        )
        # Outline.
        pygame.draw.rect(
            surface, (30, 120, 50), (sx, sy, self.rect.width, self.rect.height), 1,
        )

        # Label letter (centred).
        try:
            font = pygame.font.Font(None, 16)
            label_surf = font.render(self._label, False, (255, 255, 255))
            lx = sx + (self.rect.width - label_surf.get_width()) // 2
            ly = sy + (self.rect.height - label_surf.get_height()) // 2
            surface.blit(label_surf, (lx, ly))
        except pygame.error:
            pass

    def can_interact(self, player_rect: pygame.Rect) -> bool:
        """Check whether the player is close enough to interact.

        Args:
            player_rect: The player's bounding box.

        Returns:
            True if the player overlaps the interaction zone.
        """
        return self._interact_rect.colliderect(player_rect)

    # ── Private ───────────────────────────────────────────────────

    def _build_sprite(self) -> None:
        """Create the placeholder sprite surface."""
        surf = pygame.Surface((self.rect.width, self.rect.height))
        surf.fill(COLORS["GREEN"])
        self._sprite = surf
