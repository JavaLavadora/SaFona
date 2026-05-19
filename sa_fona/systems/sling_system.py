"""Sling combat system: tap for melee, hold to charge ranged projectiles.

The SlingSystem reads attack input from InputState and manages the
transition between idle -> charging -> releasing.  It is decoupled
from the Player entity -- the scene passes the player reference each
frame so the system can read position and facing direction.

Charge tier thresholds and damage values are loaded from economy.json,
keeping all tuning data-driven.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.projectile import Projectile, ProjectileType
from sa_fona.level.tilemap import TILE_SIZE

if TYPE_CHECKING:
    from sa_fona.entities.player import Player


@dataclass
class ChargeTierData:
    """Parsed charge tier configuration from economy.json.

    Attributes:
        tier: Tier number (1, 2, or 3).
        min_hold: Minimum hold time in seconds to reach this tier.
        damage_multiplier: Damage multiplier for this tier.
        range_tiles: Projectile range in tiles.
    """

    tier: int
    min_hold: float
    damage_multiplier: float
    range_tiles: int


@dataclass
class MeleeHitbox:
    """A short-lived melee hitbox created by a sling tap attack.

    Attributes:
        rect: World-space bounding rectangle.
        damage: Damage dealt on overlap.
        timer: Remaining lifetime in seconds.
    """

    rect: pygame.Rect
    damage: float
    timer: float


class SlingSystem:
    """Handles Ramon's sling tap/hold/charge/release mechanics.

    The system transitions through states:

    - **idle**: Waiting for attack input.
    - **pressed**: Attack key just went down; tracking whether it's a
      tap or hold.
    - **charging**: Hold exceeded tap threshold; accumulating charge.
    - **cooldown**: Brief lockout after tap or release (prevents spam).

    Args:
        event_bus: Shared event bus for publishing combat events.
        economy_data: Parsed economy.json dict (the ``"sling"`` section).
    """

    # How long the attack key must be held before we consider it a
    # charge rather than a tap.  If released within this window, a
    # melee tap fires instead.
    TAP_THRESHOLD: float = 0.12  # seconds

    # Brief cooldown after any attack action to prevent spam.
    ATTACK_COOLDOWN: float = 0.15  # seconds

    def __init__(self, event_bus: EventBus, economy_data: dict) -> None:
        self._event_bus = event_bus
        self._load_economy(economy_data)

        # Internal state.
        self._state: str = "idle"  # idle | pressed | charging | cooldown
        self._press_timer: float = 0.0
        self._charge_timer: float = 0.0
        self._cooldown_timer: float = 0.0
        self._current_tier: int = 0

        # Active melee hitboxes (usually 0 or 1).
        self._melee_hitboxes: list[MeleeHitbox] = []

    # ── Economy loading ────────────────────────────────────────────

    def _load_economy(self, economy_data: dict) -> None:
        """Parse sling section from economy data.

        Args:
            economy_data: The full economy.json dict or the ``"sling"`` sub-dict.
        """
        sling = economy_data.get("sling", economy_data)
        thresholds = sling.get("charge_thresholds", {})

        self._tiers: list[ChargeTierData] = []
        for i, key in enumerate(["tier_1", "tier_2", "tier_3"], start=1):
            tier_data = thresholds.get(key, {})
            self._tiers.append(
                ChargeTierData(
                    tier=i,
                    min_hold=tier_data.get("min_hold", 0.3 * i),
                    damage_multiplier=tier_data.get("damage_multiplier", float(i)),
                    range_tiles=tier_data.get("range_tiles", 8 * i),
                )
            )

        self._tap_damage: float = sling.get("tap_damage", 1.0)
        self._tap_range_tiles: float = sling.get("tap_range_tiles", 1.5)
        self._projectile_speed: float = sling.get("projectile_speed", 250.0)
        self._tap_hitbox_width: int = sling.get("tap_hitbox_width", 28)
        self._tap_hitbox_height: int = sling.get("tap_hitbox_height", 20)
        self._tap_duration: float = sling.get("tap_duration", 0.1)
        self._projectile_width: int = sling.get("projectile_width", 8)
        self._projectile_height: int = sling.get("projectile_height", 8)

    # ── Public API ─────────────────────────────────────────────────

    def update(
        self,
        input_state: InputState,
        player: Player,
        dt: float,
    ) -> list[Projectile]:
        """Process sling input for one frame.

        Returns a list of newly spawned projectiles (0 or 1 per frame).
        The caller (GameplayScene) is responsible for adding them to
        the active projectile list.

        Args:
            input_state: Current frame's input snapshot.
            player: The player entity (read position/facing).
            dt: Delta time in seconds.

        Returns:
            List of newly created Projectile entities.
        """
        new_projectiles: list[Projectile] = []

        # Tick melee hitboxes.
        self._update_melee_hitboxes(dt)

        # State machine.
        if self._state == "idle":
            if input_state.attack_pressed:
                self._state = "pressed"
                self._press_timer = 0.0
                self._charge_timer = 0.0
                self._current_tier = 0

        elif self._state == "pressed":
            self._press_timer += dt
            if input_state.attack_released:
                # Released within tap threshold -> melee tap.
                self._fire_melee(player)
                self._state = "cooldown"
                self._cooldown_timer = self.ATTACK_COOLDOWN
            elif self._press_timer >= self.TAP_THRESHOLD:
                # Held past threshold -> transition to charging.
                self._state = "charging"
                self._charge_timer = self._press_timer
                self._update_charge_tier()

        elif self._state == "charging":
            self._charge_timer += dt
            self._update_charge_tier()
            if input_state.attack_released:
                proj = self._fire_projectile(player)
                if proj is not None:
                    new_projectiles.append(proj)
                self._state = "cooldown"
                self._cooldown_timer = self.ATTACK_COOLDOWN
                self._current_tier = 0

        elif self._state == "cooldown":
            self._cooldown_timer -= dt
            if self._cooldown_timer <= 0:
                self._state = "idle"
                self._cooldown_timer = 0.0

        return new_projectiles

    @property
    def is_charging(self) -> bool:
        """Whether the player is currently holding the attack button."""
        return self._state == "charging"

    @property
    def charge_tier(self) -> int:
        """Current charge tier (0=none/idle, 1-3=charging)."""
        return self._current_tier

    @property
    def charge_time(self) -> float:
        """Elapsed charge time in seconds (0 when not charging)."""
        if self._state in ("charging", "pressed"):
            return self._charge_timer
        return 0.0

    def cancel(self) -> None:
        """Cancel any in-progress sling action and return to idle.

        Called when an external event (e.g. dialogue starting) needs to
        interrupt the sling state machine.  Resets all timers so the
        system is ready for a fresh input sequence.
        """
        self._state = "idle"
        self._press_timer = 0.0
        self._charge_timer = 0.0
        self._current_tier = 0

    @property
    def state(self) -> str:
        """Current internal state name."""
        return self._state

    @property
    def melee_hitboxes(self) -> list[MeleeHitbox]:
        """Currently active melee hitboxes (for combat resolution)."""
        return self._melee_hitboxes

    # ── Private helpers ────────────────────────────────────────────

    def _update_charge_tier(self) -> None:
        """Determine the current charge tier from elapsed charge time."""
        tier = 0
        for tier_data in self._tiers:
            if self._charge_timer >= tier_data.min_hold:
                tier = tier_data.tier
        self._current_tier = tier

    def _fire_melee(self, player: Player) -> None:
        """Create a short-lived melee hitbox in front of the player.

        Args:
            player: Player entity for position and facing direction.
        """
        if player.facing_right:
            hx = player.rect.right
        else:
            hx = player.rect.left - self._tap_hitbox_width

        hy = player.rect.centery - self._tap_hitbox_height // 2

        hitbox = MeleeHitbox(
            rect=pygame.Rect(hx, hy, self._tap_hitbox_width, self._tap_hitbox_height),
            damage=self._tap_damage,
            timer=self._tap_duration,
        )
        self._melee_hitboxes.append(hitbox)
        self._event_bus.publish("sling_tap", damage=self._tap_damage)

    def _fire_projectile(self, player: Player) -> Projectile | None:
        """Spawn a projectile based on the current charge tier.

        Args:
            player: Player entity for spawn position and direction.

        Returns:
            A new Projectile entity, or None if charge tier is 0.
        """
        if self._current_tier == 0:
            # No tier reached -> fire a melee tap instead as fallback.
            self._fire_melee(player)
            return None

        tier_data = self._tiers[self._current_tier - 1]
        direction = 1.0 if player.facing_right else -1.0

        # Spawn projectile from the front of the player.
        if player.facing_right:
            px = player.rect.right + 2
        else:
            px = player.rect.left - self._projectile_width - 2

        py = player.rect.centery - self._projectile_height // 2

        damage = self._tap_damage * tier_data.damage_multiplier
        range_pixels = tier_data.range_tiles * TILE_SIZE

        proj = Projectile(
            x=px,
            y=py,
            width=self._projectile_width,
            height=self._projectile_height,
            direction=direction,
            speed=self._projectile_speed,
            damage=damage,
            charge_tier=self._current_tier,
            max_range=range_pixels,
            projectile_type=ProjectileType.BASIC_STONE,
        )

        self._event_bus.publish(
            "sling_release",
            tier=self._current_tier,
            damage=damage,
        )
        return proj

    def _update_melee_hitboxes(self, dt: float) -> None:
        """Tick down melee hitbox timers and remove expired ones.

        Args:
            dt: Delta time in seconds.
        """
        for hitbox in self._melee_hitboxes:
            hitbox.timer -= dt
        self._melee_hitboxes = [h for h in self._melee_hitboxes if h.timer > 0]
