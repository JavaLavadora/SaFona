"""Enemy behavior components: patrol, chase, and attack strategies.

Behaviors are composable components that control how an enemy moves and
attacks.  They are created by the EnemyFactory from JSON definitions and
attached to Enemy instances.  Each behavior reads the enemy's position
and the player's position to decide movement and attack actions.

Behavior types for World 1:
- PatrolBehavior: walk back and forth within a range
- ChaseBehavior: follow the player when within detection range
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from sa_fona.level.tilemap import TileMap


class AttackState(Enum):
    """Current state of an enemy's attack cycle."""

    IDLE = auto()
    TELL = auto()
    ATTACKING = auto()
    COOLDOWN = auto()


class BehaviorResult:
    """Output from a behavior's update, telling the enemy what to do.

    Attributes:
        move_x: Horizontal movement direction (-1, 0, or 1).
        speed: Movement speed in pixels per second.
        wants_attack: True if the behavior wants to initiate an attack.
        attack_state: Current attack cycle state.
        is_blocking: True if the enemy is currently blocking.
    """

    def __init__(self) -> None:
        self.move_x: float = 0.0
        self.speed: float = 0.0
        self.wants_attack: bool = False
        self.attack_state: AttackState = AttackState.IDLE
        self.is_blocking: bool = False


class EnemyBehavior(ABC):
    """Abstract base class for enemy behavior components.

    Args:
        params: Behavior-specific parameters from enemy JSON definition.
    """

    def __init__(self, params: dict) -> None:
        self._params = params

    @abstractmethod
    def update(
        self,
        enemy_rect: pygame.Rect,
        player_rect: pygame.Rect,
        dt: float,
        tilemap: TileMap | None = None,
    ) -> BehaviorResult:
        """Compute movement and attack decisions for one frame.

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.
            tilemap: Optional tilemap for ground/edge detection.

        Returns:
            A BehaviorResult describing intended actions.
        """

    def try_block(self) -> bool:
        """Attempt to enter a blocking state.

        Default implementation does nothing and returns False.
        Subclasses that support blocking (e.g. ChaseBehavior) override this.

        Returns:
            True if the enemy successfully blocks, False otherwise.
        """
        return False

    def on_damaged(self, player_x: float, player_y: float) -> None:
        """React to taking damage from the player.

        Default implementation does nothing. Subclasses can override to
        trigger aggro or other reactive behaviors.

        Args:
            player_x: The player's X position in world pixels.
            player_y: The player's Y position in world pixels.
        """

    @abstractmethod
    def reset(self, spawn_x: float) -> None:
        """Reset the behavior to its initial state.

        Args:
            spawn_x: The enemy's spawn X position for patrol anchoring.
        """


class PatrolBehavior(EnemyBehavior):
    """Walk back and forth within a patrol range.

    When the player enters attack range, the enemy performs an attack
    with a tell (visual warning) before striking.  If damaged from any
    distance, the enemy temporarily chases toward the player for a few
    seconds before resuming patrol.

    Params (from JSON):
        patrol_range: Range in tiles to patrol from spawn.
        speed: Walk speed in pixels per second.
        charge_speed: Speed during a charge attack (sheep-specific).
        charge_tell_time: Time in seconds for the attack tell.
        charge_distance: Distance in tiles for charge attacks.
        attack_range: Range in tiles to trigger an attack.
        attack_cooldown: Seconds between attacks.
        attack_tell_time: General attack tell time.
    """

    _AGGRO_DURATION: float = 3.0
    _AGGRO_SPEED_MULTIPLIER: float = 2.0
    _AGGRO_MIN_SPEED: float = 50.0
    _LEDGE_HESITATION: float = 0.6

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._patrol_range: float = params.get("patrol_range", 5) * 16  # tiles to px
        self._speed: float = params.get("speed", 40)
        self._charge_speed: float = params.get("charge_speed", 0)
        self._charge_tell_time: float = params.get("charge_tell_time", 0)
        self._charge_distance: float = params.get("charge_distance", 0) * 16
        self._attack_range: float = params.get("attack_range", 2.0) * 16
        self._attack_cooldown: float = params.get("attack_cooldown", 2.0)
        self._attack_tell_time: float = params.get(
            "attack_tell_time", self._charge_tell_time
        )

        # State.
        self._direction: float = 1.0  # 1 = right, -1 = left
        self._origin_x: float = 0.0
        self._attack_state: AttackState = AttackState.IDLE
        self._attack_timer: float = 0.0
        self._cooldown_timer: float = 0.0

        # Aggro state: when damaged, temporarily chase the player.
        self._aggro_timer: float = 0.0
        self._aggro_target_x: float = 0.0

        # Ledge retreat: hesitate, then return to origin.
        self._retreating: bool = False
        self._hesitation_timer: float = 0.0

    @property
    def aggro_timer(self) -> float:
        """Remaining aggro time in seconds (for testing)."""
        return self._aggro_timer

    def reset(self, spawn_x: float) -> None:
        """Reset patrol to initial state centered on spawn.

        Args:
            spawn_x: The enemy's spawn X position.
        """
        self._origin_x = spawn_x
        self._direction = 1.0
        self._attack_state = AttackState.IDLE
        self._attack_timer = 0.0
        self._cooldown_timer = 0.0
        self._aggro_timer = 0.0
        self._aggro_target_x = 0.0
        self._retreating = False
        self._hesitation_timer = 0.0

    def on_damaged(self, player_x: float, player_y: float) -> None:
        """React to taking damage by entering aggro state.

        If already retreating from a ledge, keep retreating — the enemy
        can't cross the gap regardless of how many times it's hit.
        Otherwise, interrupt any attack cycle and chase.

        Args:
            player_x: The player's X position in world pixels.
            player_y: The player's Y position in world pixels.
        """
        if self._retreating or self._hesitation_timer > 0:
            return
        self._aggro_timer = self._AGGRO_DURATION
        self._aggro_target_x = player_x
        self._attack_state = AttackState.IDLE
        self._attack_timer = 0.0

    def _check_edge_ahead(
        self,
        enemy_rect: pygame.Rect,
        direction: float,
        tilemap: TileMap | None,
    ) -> bool:
        """Check if there is solid ground one tile ahead of the enemy.

        Probes the tile one step ahead horizontally and one tile below
        the enemy's feet.  If no solid tile exists there, the enemy is
        at a ledge.

        Args:
            enemy_rect: The enemy's current bounding box.
            direction: Movement direction (-1.0 or 1.0).
            tilemap: The level tilemap (None skips the check).

        Returns:
            True if there is NO ground ahead (i.e., the enemy is at
            a ledge and should reverse).
        """
        if tilemap is None:
            return False

        from sa_fona.level.tilemap import TILE_SIZE

        # Tile coordinate of the enemy's leading edge.
        if direction > 0:
            probe_x_px = enemy_rect.right + 1
        else:
            probe_x_px = enemy_rect.left - 1

        # One tile below the enemy's feet.
        probe_y_px = enemy_rect.bottom

        tile_x = probe_x_px // TILE_SIZE
        tile_y = probe_y_px // TILE_SIZE

        return not tilemap.is_solid_at(tile_x, tile_y)

    def update(
        self,
        enemy_rect: pygame.Rect,
        player_rect: pygame.Rect,
        dt: float,
        tilemap: TileMap | None = None,
    ) -> BehaviorResult:
        """Patrol back and forth; attack if player is in range.

        Includes aggro response (chase on damage) and edge detection
        (reverse at ledges).

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.
            tilemap: Optional tilemap for edge detection.

        Returns:
            BehaviorResult with movement and attack data.
        """
        result = BehaviorResult()

        # Distance to player.
        dx_to_player = player_rect.centerx - enemy_rect.centerx
        dist_to_player = abs(dx_to_player)

        # Tick cooldown.
        if self._cooldown_timer > 0:
            self._cooldown_timer -= dt

        # Tick aggro timer.
        if self._aggro_timer > 0:
            self._aggro_timer -= dt

        # ── Ledge retreat (hesitate then return to origin) ─────────
        if self._hesitation_timer > 0:
            self._hesitation_timer -= dt
            result.move_x = 0.0
            result.speed = 0.0
            if self._hesitation_timer <= 0:
                self._retreating = True
            return result

        if self._retreating:
            dx_to_origin = self._origin_x - float(enemy_rect.x)
            if abs(dx_to_origin) < 4.0:
                self._retreating = False
            else:
                retreat_dir = 1.0 if dx_to_origin > 0 else -1.0
                self._direction = retreat_dir
                result.move_x = retreat_dir
                result.speed = self._speed
                return result

        # ── Aggro chase (damage response) ─────────────────────────
        if (
            self._aggro_timer > 0
            and self._attack_state == AttackState.IDLE
        ):
            chase_dir = 1.0 if dx_to_player > 0 else -1.0

            # Within attack range: let the attack state machine handle it
            # so the enemy can charge/attack instead of just trailing.
            tell_time = self._attack_tell_time or self._charge_tell_time
            if (
                dist_to_player < self._attack_range
                and self._cooldown_timer <= 0
                and tell_time > 0
            ):
                pass  # Fall through to attack state machine below.
            elif self._check_edge_ahead(enemy_rect, chase_dir, tilemap):
                self._direction = chase_dir
                self._hesitation_timer = self._LEDGE_HESITATION
                self._aggro_timer = 0.0
                result.move_x = 0.0
                result.speed = 0.0
                return result
            else:
                self._direction = chase_dir
                result.move_x = chase_dir
                result.speed = max(
                    self._speed * self._AGGRO_SPEED_MULTIPLIER,
                    self._AGGRO_MIN_SPEED,
                )
                return result

        # ── Attack state machine ──────────────────────────────────
        if self._attack_state == AttackState.IDLE:
            # Check if player is within attack range.
            tell_time = self._attack_tell_time or self._charge_tell_time
            if (
                dist_to_player < self._attack_range
                and self._cooldown_timer <= 0
                and tell_time > 0
            ):
                self._attack_state = AttackState.TELL
                self._attack_timer = tell_time
                result.move_x = 0.0
                result.speed = 0.0
                result.attack_state = AttackState.TELL
                return result

            # Normal patrol movement.
            result.move_x = self._direction
            result.speed = self._speed

            # Reverse direction at patrol boundaries.
            current_x = float(enemy_rect.x)
            if current_x > self._origin_x + self._patrol_range:
                self._direction = -1.0
                result.move_x = -1.0
            elif current_x < self._origin_x - self._patrol_range:
                self._direction = 1.0
                result.move_x = 1.0

            # Edge detection: reverse at ledges.
            if self._check_edge_ahead(enemy_rect, self._direction, tilemap):
                self._direction *= -1.0
                result.move_x = self._direction

        elif self._attack_state == AttackState.TELL:
            # Showing the attack tell (visual warning).
            self._attack_timer -= dt
            result.move_x = 0.0
            result.speed = 0.0
            result.attack_state = AttackState.TELL
            if self._attack_timer <= 0:
                self._attack_state = AttackState.ATTACKING
                # For charge attacks, rush toward the player.
                if self._charge_speed > 0:
                    self._attack_timer = self._charge_distance / max(
                        self._charge_speed, 1
                    )
                else:
                    # Stationary heavy attack.
                    self._attack_timer = 0.3
                # Face the player.
                if dx_to_player > 0:
                    self._direction = 1.0
                elif dx_to_player < 0:
                    self._direction = -1.0

        elif self._attack_state == AttackState.ATTACKING:
            self._attack_timer -= dt
            result.attack_state = AttackState.ATTACKING
            result.wants_attack = True

            if self._charge_speed > 0:
                # Charge toward player direction.
                result.move_x = self._direction
                result.speed = self._charge_speed
            else:
                # Stationary attack.
                result.move_x = 0.0
                result.speed = 0.0

            if self._attack_timer <= 0:
                self._attack_state = AttackState.COOLDOWN
                self._cooldown_timer = self._attack_cooldown

        elif self._attack_state == AttackState.COOLDOWN:
            # Wait for cooldown, resume patrol.
            result.move_x = self._direction
            result.speed = self._speed
            result.attack_state = AttackState.COOLDOWN

            # Reverse direction at patrol boundaries.
            current_x = float(enemy_rect.x)
            if current_x > self._origin_x + self._patrol_range:
                self._direction = -1.0
                result.move_x = -1.0
            elif current_x < self._origin_x - self._patrol_range:
                self._direction = 1.0
                result.move_x = 1.0

            if self._cooldown_timer <= 0:
                self._attack_state = AttackState.IDLE

        return result


class ChaseBehavior(EnemyBehavior):
    """Follow the player when within detection range.

    Includes a block mechanic: randomly blocks incoming attacks based
    on block_chance.

    Params (from JSON):
        chase_range: Detection range in tiles.
        speed: Chase speed in pixels per second.
        attack_range: Range in tiles to trigger an attack.
        attack_cooldown: Seconds between attacks.
        block_chance: Probability of blocking (0.0 to 1.0).
        block_duration: How long the block lasts in seconds.
    """

    _AGGRO_DURATION: float = 3.0

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._chase_range: float = params.get("chase_range", 6) * 16
        self._speed: float = params.get("speed", 50)
        self._attack_range: float = params.get("attack_range", 1.5) * 16
        self._attack_cooldown: float = params.get("attack_cooldown", 1.0)
        self._block_chance: float = params.get("block_chance", 0.0)
        self._block_duration: float = params.get("block_duration", 0.5)

        # State.
        self._attack_state: AttackState = AttackState.IDLE
        self._attack_timer: float = 0.0
        self._cooldown_timer: float = 0.0
        self._block_timer: float = 0.0
        self._is_blocking: bool = False

        # Aggro: temporarily extends chase range when damaged.
        self._aggro_timer: float = 0.0

    def reset(self, spawn_x: float) -> None:
        """Reset chase behavior.

        Args:
            spawn_x: Unused for chase (no patrol anchor).
        """
        self._attack_state = AttackState.IDLE
        self._attack_timer = 0.0
        self._cooldown_timer = 0.0
        self._block_timer = 0.0
        self._is_blocking = False
        self._aggro_timer = 0.0

    def on_damaged(self, player_x: float, player_y: float) -> None:
        """React to damage by extending chase range temporarily.

        Args:
            player_x: The player's X position in world pixels.
            player_y: The player's Y position in world pixels.
        """
        self._aggro_timer = self._AGGRO_DURATION
        self._attack_state = AttackState.IDLE
        self._attack_timer = 0.0

    @property
    def is_blocking(self) -> bool:
        """Whether the enemy is currently blocking."""
        return self._is_blocking

    def try_block(self) -> bool:
        """Attempt to enter a blocking state.

        Called by the combat system when the enemy is about to take damage.

        Returns:
            True if the enemy successfully blocks.
        """
        if self._is_blocking:
            return True
        if self._block_chance > 0 and random.random() < self._block_chance:
            self._is_blocking = True
            self._block_timer = self._block_duration
            return True
        return False

    def update(
        self,
        enemy_rect: pygame.Rect,
        player_rect: pygame.Rect,
        dt: float,
        tilemap: TileMap | None = None,
    ) -> BehaviorResult:
        """Chase the player; attack when close enough.

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.
            tilemap: Optional tilemap (unused by chase behavior).

        Returns:
            BehaviorResult with movement and attack data.
        """
        result = BehaviorResult()

        # Tick block timer.
        if self._is_blocking:
            self._block_timer -= dt
            if self._block_timer <= 0:
                self._is_blocking = False
            result.is_blocking = self._is_blocking

        # Tick cooldown.
        if self._cooldown_timer > 0:
            self._cooldown_timer -= dt

        # Tick aggro timer.
        if self._aggro_timer > 0:
            self._aggro_timer -= dt

        dx_to_player = player_rect.centerx - enemy_rect.centerx
        dist_to_player = abs(dx_to_player)

        # Determine facing direction toward player.
        face_dir = 1.0 if dx_to_player > 0 else -1.0

        # When aggroed, ignore chase_range limit.
        effective_range = self._chase_range if self._aggro_timer <= 0 else float("inf")
        if dist_to_player > effective_range:
            result.move_x = 0.0
            result.speed = 0.0
            return result

        # Attack state machine.
        if self._attack_state == AttackState.IDLE:
            if dist_to_player < self._attack_range and self._cooldown_timer <= 0:
                # In attack range -- attack immediately.
                self._attack_state = AttackState.ATTACKING
                self._attack_timer = 0.3  # Brief attack duration.
                result.attack_state = AttackState.ATTACKING
                result.wants_attack = True
                result.move_x = 0.0
                result.speed = 0.0
            else:
                # Chase toward player.
                result.move_x = face_dir
                result.speed = self._speed

        elif self._attack_state == AttackState.ATTACKING:
            self._attack_timer -= dt
            result.attack_state = AttackState.ATTACKING
            result.wants_attack = True
            result.move_x = 0.0
            result.speed = 0.0

            if self._attack_timer <= 0:
                self._attack_state = AttackState.COOLDOWN
                self._cooldown_timer = self._attack_cooldown

        elif self._attack_state == AttackState.COOLDOWN:
            result.attack_state = AttackState.COOLDOWN
            # Continue chasing during cooldown.
            result.move_x = face_dir
            result.speed = self._speed

            if self._cooldown_timer <= 0:
                self._attack_state = AttackState.IDLE

        return result


# ── Factory function ──────────────────────────────────────────────

_BEHAVIOR_REGISTRY: dict[str, type[EnemyBehavior]] = {
    "patrol": PatrolBehavior,
    "chase": ChaseBehavior,
}


def create_behavior(behavior_type: str, params: dict) -> EnemyBehavior:
    """Create a behavior component by type name.

    Args:
        behavior_type: The behavior type key (e.g. "patrol", "chase").
        params: Behavior-specific parameters from the enemy definition.

    Returns:
        An initialized EnemyBehavior instance.

    Raises:
        ValueError: If the behavior type is not registered.
    """
    cls = _BEHAVIOR_REGISTRY.get(behavior_type)
    if cls is None:
        raise ValueError(f"Unknown behavior type: {behavior_type!r}")
    return cls(params)
