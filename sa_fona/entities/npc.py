"""Generic NPC entity for world interactions.

NPCs are non-hostile entities placed in levels that the player can
interact with (via the Interact key).  Each NPC has a type that
determines its behaviour (e.g. ``shop`` opens the shop overlay).

Uses real sprite PNGs from assets/sprites/npcs/ when available,
falling back to coloured rectangles with initial letters.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import COLORS
from sa_fona.entities.entity import Entity
from sa_fona.rendering.asset_loader import load_frame_strip


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

    # Sprite state name mapping for NPC animations.
    _NPC_SPRITE_STATES: dict[str, dict[str, str]] = {
        "llorencc": {
            "idle": "assets/sprites/npcs/llorencc_idle.png",
            "talk": "assets/sprites/npcs/llorencc_talk.png",
            "shop": "assets/sprites/npcs/llorencc_shop.png",
        },
        "dimoni": {
            "idle": "assets/sprites/npcs/dimoni_idle.png",
            "laugh": "assets/sprites/npcs/dimoni_laugh.png",
            "grant": "assets/sprites/npcs/dimoni_grant.png",
            "angry": "assets/sprites/npcs/dimoni_angry.png",
        },
    }

    # Sprite dimensions per NPC type.
    _NPC_SPRITE_SIZES: dict[str, tuple[int, int]] = {
        "llorencc": (20, 36),
        "dimoni": (24, 40),
    }

    def __init__(
        self,
        x: float,
        y: float,
        npc_id: str = "llorencc",
        npc_type: str = "shop",
        label: str = "L",
    ) -> None:
        # Determine actual sprite size for this NPC.
        npc_base = npc_id.split("_")[0] if "_" in npc_id else npc_id
        sprite_size = self._NPC_SPRITE_SIZES.get(npc_base, (_NPC_WIDTH, _NPC_HEIGHT))
        super().__init__(x, y, sprite_size[0], sprite_size[1])
        self._npc_id = npc_id
        self._npc_base = npc_base
        self._npc_type = npc_type
        self._label = label
        self._sprite_w = sprite_size[0]
        self._sprite_h = sprite_size[1]

        # Sprite frames for different states.
        self._sprite_states: dict[str, pygame.Surface] = {}
        self._current_state: str = "idle"
        self._has_sprites: bool = False

        # Build sprite (tries real assets first).
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

    def set_sprite_state(self, state: str) -> None:
        """Change the NPC's visual state (e.g. idle, talk, shop).

        Args:
            state: State key (e.g. "idle", "talk", "shop", "laugh").
        """
        if state in self._sprite_states:
            self._current_state = state
            self._sprite = self._sprite_states[state]

    def render(
        self, surface: pygame.Surface, camera_offset: tuple[int, int],
    ) -> None:
        """Draw the NPC using sprites or a placeholder rectangle.

        Args:
            surface: Target pygame Surface.
            camera_offset: Camera world-pixel offset.
        """
        sx = self.rect.x - camera_offset[0]
        sy = self.rect.y - camera_offset[1]

        if self._has_sprites and self._sprite is not None:
            surface.blit(self._sprite, (sx, sy))
        else:
            # Fallback: green rectangle.
            pygame.draw.rect(
                surface, COLORS["GREEN"],
                (sx, sy, self.rect.width, self.rect.height),
            )
            pygame.draw.rect(
                surface, (30, 120, 50),
                (sx, sy, self.rect.width, self.rect.height), 1,
            )
            try:
                font = pygame.font.Font(None, 16)
                label_surf = font.render(self._label, False, (255, 255, 255))
                lx = sx + (self.rect.width - label_surf.get_width()) // 2
                ly = sy + (self.rect.height - label_surf.get_height()) // 2
                surface.blit(label_surf, (lx, ly))
            except pygame.error:
                pass

        # Floating type indicator above the NPC.
        try:
            font = pygame.font.Font(None, 16)
            tag = "SHOP" if self._npc_type == "shop" else self._npc_type.upper()
            tag_surf = font.render(tag, False, (255, 220, 80))
            tx = sx + (self.rect.width - tag_surf.get_width()) // 2
            ty = sy - tag_surf.get_height() - 2
            surface.blit(tag_surf, (tx, ty))
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
        """Load real NPC sprites or create a placeholder surface."""
        states = self._NPC_SPRITE_STATES.get(self._npc_base, {})
        for state_name, path in states.items():
            frames = load_frame_strip(
                path, self._sprite_w, self._sprite_h,
            )
            if frames:
                self._sprite_states[state_name] = frames[0]
                self._has_sprites = True

        if self._has_sprites:
            # Set initial sprite to idle (or first available state).
            if "idle" in self._sprite_states:
                self._sprite = self._sprite_states["idle"]
            else:
                first_key = next(iter(self._sprite_states))
                self._sprite = self._sprite_states[first_key]
        else:
            # Fallback: green rectangle.
            surf = pygame.Surface((self.rect.width, self.rect.height))
            surf.fill(COLORS["GREEN"])
            self._sprite = surf
