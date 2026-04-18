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

import pygame


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
    ) -> BehaviorResult:
        """Compute movement and attack decisions for one frame.

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.

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

    @abstractmethod
    def reset(self, spawn_x: float) -> None:
        """Reset the behavior to its initial state.

        Args:
            spawn_x: The enemy's spawn X position for patrol anchoring.
        """


class PatrolBehavior(EnemyBehavior):
    """Walk back and forth within a patrol range.

    When the player enters attack range, the enemy performs an attack
    with a tell (visual warning) before striking.

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

    def update(
        self,
        enemy_rect: pygame.Rect,
        player_rect: pygame.Rect,
        dt: float,
    ) -> BehaviorResult:
        """Patrol back and forth; attack if player is in range.

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.

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

        # Attack state machine.
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
    ) -> BehaviorResult:
        """Chase the player; attack when close enough.

        Args:
            enemy_rect: The enemy's current bounding box.
            player_rect: The player's current bounding box.
            dt: Delta time in seconds.

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

        dx_to_player = player_rect.centerx - enemy_rect.centerx
        dist_to_player = abs(dx_to_player)

        # Determine facing direction toward player.
        face_dir = 1.0 if dx_to_player > 0 else -1.0

        if dist_to_player > self._chase_range:
            # Player out of range -- idle.
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
