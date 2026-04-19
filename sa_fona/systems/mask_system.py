"""Mask system: powers obtained from boss defeats.

Manages a mask inventory, equip/unequip flow, cooldown timers, and
power activation.  Mask definitions are loaded from data/masks.json
so balance values can be tuned without touching Python code.

The first mask, Stone Slam, creates a ground-pound shockwave that
breaks ``breakable_slam`` tiles and stuns nearby grounded enemies.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pygame

from sa_fona.config.settings import DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.level.tilemap import TILE_SIZE

if TYPE_CHECKING:
    from sa_fona.entities.enemy import Enemy
    from sa_fona.level.tilemap import TileMap


class MaskSystem:
    """Manages mask inventory, equip state, cooldowns, and power activation.

    Args:
        event_bus: Shared event bus for cross-system communication.
        masks_path: Path to the masks.json definitions file.
            Defaults to the standard data directory location.
    """

    def __init__(
        self,
        event_bus: EventBus,
        masks_path: str | None = None,
    ) -> None:
        self._event_bus = event_bus
        if masks_path is None:
            masks_path = str(DATA_DIR / "masks.json")
        self._masks_path = masks_path

        # Mask definitions loaded from JSON.
        self._definitions: dict[str, dict[str, Any]] = {}
        self._load_definitions()

        # Player's unlocked masks and currently equipped mask.
        self._unlocked: set[str] = set()
        self._equipped_mask: str | None = None

        # Cooldown state.
        self._cooldown_remaining: float = 0.0
        self._cooldown_total: float = 0.0

        # Visual effect state for the shockwave flash.
        self._shockwave_timer: float = 0.0
        self._shockwave_rect: pygame.Rect | None = None

        # Subscribe to mask_acquired event (e.g. from boss defeat).
        self._event_bus.subscribe("mask_acquired", self._on_mask_acquired)

    # ── Config loading ────────────────────────────────────────────

    def _load_definitions(self) -> None:
        """Load mask definitions from the JSON file."""
        try:
            with open(self._masks_path, "r", encoding="utf-8") as fh:
                self._definitions = json.load(fh)
        except FileNotFoundError:
            self._definitions = {}

    @property
    def definitions(self) -> dict[str, dict[str, Any]]:
        """All loaded mask definitions (read-only)."""
        return self._definitions

    # ── Inventory management ──────────────────────────────────────

    @property
    def unlocked_masks(self) -> list[str]:
        """List of unlocked mask IDs."""
        return sorted(self._unlocked)

    @property
    def active_mask_id(self) -> str | None:
        """Currently equipped mask ID, or None."""
        return self._equipped_mask

    def unlock_mask(self, mask_id: str) -> bool:
        """Unlock a mask by its ID.

        Args:
            mask_id: The mask identifier (e.g. "stone_slam").

        Returns:
            True if the mask was newly unlocked, False if already unlocked
            or not a valid mask ID.
        """
        if mask_id not in self._definitions:
            return False
        if mask_id in self._unlocked:
            return False
        self._unlocked.add(mask_id)
        return True

    def equip_mask(self, mask_id: str) -> bool:
        """Equip an unlocked mask.

        Args:
            mask_id: The mask identifier to equip.

        Returns:
            True if the mask was equipped, False if not unlocked.
        """
        if mask_id not in self._unlocked:
            return False
        self._equipped_mask = mask_id
        self._cooldown_remaining = 0.0
        self._cooldown_total = 0.0
        return True

    def unequip_mask(self) -> None:
        """Remove the currently equipped mask."""
        self._equipped_mask = None
        self._cooldown_remaining = 0.0
        self._cooldown_total = 0.0

    # ── Cooldown ──────────────────────────────────────────────────

    @property
    def is_on_cooldown(self) -> bool:
        """Whether the active mask's power is on cooldown."""
        return self._cooldown_remaining > 0

    @property
    def cooldown_progress(self) -> float:
        """Cooldown progress from 0.0 (just started) to 1.0 (ready).

        Returns 1.0 when not on cooldown (ready to use).
        """
        if self._cooldown_total <= 0 or self._cooldown_remaining <= 0:
            return 1.0
        return 1.0 - (self._cooldown_remaining / self._cooldown_total)

    def update(self, dt: float) -> None:
        """Tick cooldown and visual effect timers.

        Args:
            dt: Delta time in seconds.
        """
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= dt
            if self._cooldown_remaining < 0:
                self._cooldown_remaining = 0.0

        if self._shockwave_timer > 0:
            self._shockwave_timer -= dt
            if self._shockwave_timer < 0:
                self._shockwave_timer = 0.0
                self._shockwave_rect = None

    # ── Power activation ──────────────────────────────────────────

    def activate_power(
        self,
        player_rect: pygame.Rect,
        tilemap: TileMap,
        enemies: list[Enemy],
        event_bus: EventBus,
    ) -> bool:
        """Activate the equipped mask's power.

        Checks that a mask is equipped, off cooldown, and delegates to
        the appropriate power handler based on the mask's ``power_type``.

        Args:
            player_rect: The player's bounding box.
            tilemap: The level tilemap for tile breaking.
            enemies: List of active enemy entities.
            event_bus: Event bus for publishing effects.

        Returns:
            True if the power was activated, False otherwise.
        """
        if self._equipped_mask is None:
            return False
        if self.is_on_cooldown:
            return False

        mask_def = self._definitions.get(self._equipped_mask)
        if mask_def is None:
            return False

        power_type = mask_def.get("power_type", "")
        if power_type == "ground_pound":
            self._activate_stone_slam(player_rect, tilemap, enemies, event_bus, mask_def)
        else:
            return False

        # Start cooldown.
        cooldown = float(mask_def.get("cooldown", 2.0))
        self._cooldown_remaining = cooldown
        self._cooldown_total = cooldown

        # Publish events.
        event_bus.publish(
            "mask_power_activated",
            mask_id=self._equipped_mask,
            power_type=power_type,
        )
        event_bus.publish(
            "mask_cooldown_started",
            mask_id=self._equipped_mask,
            duration=cooldown,
        )

        return True

    def _activate_stone_slam(
        self,
        player_rect: pygame.Rect,
        tilemap: TileMap,
        enemies: list[Enemy],
        event_bus: EventBus,
        mask_def: dict[str, Any],
    ) -> None:
        """Execute the Stone Slam ground pound shockwave.

        Creates a shockwave centered on the player's feet that extends
        horizontally by ``range_tiles`` tiles in each direction.

        Effects:
        - Breaks ``breakable_slam`` tiles within range.
        - Stuns grounded enemies within range for ``stun_duration`` seconds.
        - Damages enemies within range.
        - Triggers camera shake.

        Args:
            player_rect: The player's bounding box.
            tilemap: The level tilemap.
            enemies: Active enemy entities.
            event_bus: Event bus for publishing effects.
            mask_def: The mask definition dict.
        """
        range_px = int(mask_def.get("range_tiles", 3)) * TILE_SIZE
        stun_duration = float(mask_def.get("stun_duration", 1.5))
        damage = float(mask_def.get("damage", 2))

        # Shockwave area: centered on player feet, extends horizontally.
        player_cx = player_rect.centerx
        player_bottom = player_rect.bottom

        # Shockwave rect: full range left/right, one tile tall at feet level.
        shock_left = player_cx - range_px
        shock_right = player_cx + range_px
        shock_top = player_bottom - TILE_SIZE
        shock_rect = pygame.Rect(
            shock_left, shock_top,
            shock_right - shock_left, TILE_SIZE,
        )

        # Store for visual rendering.
        self._shockwave_rect = shock_rect.copy()
        self._shockwave_timer = 0.3

        # 1. Break breakable_slam tiles within range.
        self._break_slam_tiles(tilemap, shock_rect, event_bus)

        # 2. Stun and damage enemies within range.
        self._affect_enemies(enemies, shock_rect, damage, stun_duration, event_bus)

        # 3. Camera shake.
        event_bus.publish("screen_shake", intensity=6.0, duration=0.3)

    def _break_slam_tiles(
        self,
        tilemap: TileMap,
        shock_rect: pygame.Rect,
        event_bus: EventBus,
    ) -> None:
        """Break breakable_slam tiles within the shockwave area.

        Removes matching tiles from the midground layer by setting them
        to tile ID 0, then publishes a ``tile_broken`` event for each.

        Args:
            tilemap: The level tilemap.
            shock_rect: The shockwave bounding box.
            event_bus: Event bus for publishing tile_broken events.
        """
        slam_ids = tilemap._collision_types.get("breakable_slam", set())
        if not slam_ids:
            return

        midground = tilemap._layers.get("midground", [])

        # Determine tile coordinate range from the shock_rect.
        start_col = max(0, shock_rect.left // TILE_SIZE)
        end_col = min(tilemap.width_tiles, (shock_rect.right - 1) // TILE_SIZE + 1)
        start_row = max(0, shock_rect.top // TILE_SIZE)
        end_row = min(tilemap.height_tiles, (shock_rect.bottom - 1) // TILE_SIZE + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if row < len(midground) and col < len(midground[row]):
                    tid = midground[row][col]
                    if tid in slam_ids:
                        # Remove the tile.
                        tilemap.set_tile_at(col, row, "midground", 0)
                        event_bus.publish(
                            "tile_broken",
                            tile_x=col,
                            tile_y=row,
                            tile_type="breakable_slam",
                        )

    def _affect_enemies(
        self,
        enemies: list[Enemy],
        shock_rect: pygame.Rect,
        damage: float,
        stun_duration: float,
        event_bus: EventBus,
    ) -> None:
        """Stun and damage enemies within the shockwave area.

        Args:
            enemies: Active enemy entities.
            shock_rect: The shockwave bounding box.
            damage: Damage to deal to each enemy.
            stun_duration: Duration of the stun effect in seconds.
            event_bus: Event bus for publishing damage events.
        """
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            if not enemy.rect.colliderect(shock_rect):
                continue

            # Apply stun.
            enemy.stun(stun_duration)

            # Apply damage.
            applied = enemy.take_damage(damage)
            if applied:
                event_bus.publish(
                    "damage_dealt",
                    target_type="enemy",
                    enemy_type=enemy.enemy_type,
                    amount=damage,
                )
                if not enemy.is_alive:
                    event_bus.publish(
                        "enemy_killed",
                        enemy_type=enemy.enemy_type,
                    )

    # ── Visual rendering ──────────────────────────────────────────

    @property
    def shockwave_rect(self) -> pygame.Rect | None:
        """Active shockwave visual rect, or None if no effect active."""
        if self._shockwave_timer > 0:
            return self._shockwave_rect
        return None

    @property
    def shockwave_alpha(self) -> int:
        """Alpha value for the shockwave flash (fades out over time)."""
        if self._shockwave_timer <= 0:
            return 0
        # Fade from 120 alpha down to 0 over the duration.
        return int(120 * (self._shockwave_timer / 0.3))

    # ── Save/load integration ─────────────────────────────────────

    def get_save_state(self) -> dict[str, Any]:
        """Return mask state for saving.

        Returns:
            A dict with unlocked_masks list and equipped_mask string.
        """
        return {
            "unlocked_masks": sorted(self._unlocked),
            "equipped_mask": self._equipped_mask or "",
        }

    def restore_save_state(self, data: dict[str, Any]) -> None:
        """Restore mask state from save data.

        Args:
            data: Dict with unlocked_masks and equipped_mask fields.
        """
        unlocked = data.get("unlocked_masks", [])
        self._unlocked = set(unlocked)
        equipped = data.get("equipped_mask", "")
        if equipped and equipped in self._unlocked:
            self._equipped_mask = equipped
        else:
            self._equipped_mask = None
        self._cooldown_remaining = 0.0
        self._cooldown_total = 0.0

    # ── Event handlers ────────────────────────────────────────────

    def _on_mask_acquired(self, mask_id: str = "", **kwargs: Any) -> None:
        """Handle mask_acquired events (e.g. from boss defeat).

        Automatically unlocks and equips the mask.

        Args:
            mask_id: The mask identifier to unlock.
        """
        if mask_id:
            newly_unlocked = self.unlock_mask(mask_id)
            if newly_unlocked:
                self.equip_mask(mask_id)

    # ── Cleanup ───────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Unsubscribe from EventBus events."""
        try:
            self._event_bus.unsubscribe("mask_acquired", self._on_mask_acquired)
        except ValueError:
            pass
