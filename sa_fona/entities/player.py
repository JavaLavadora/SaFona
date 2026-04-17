"""Player entity (Ramon) with a state-machine driven moveset.

States: idle, running, jumping, falling, wall_sliding, wall_jumping.
Integrates with PhysicsSystem for gravity/collision and InputState
for controls.  Placeholder rendering uses colored rectangles.
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.config.settings import (
    PLAYER_COYOTE_TIME,
    PLAYER_GRAVITY,
    PLAYER_HEIGHT,
    PLAYER_JUMP_BUFFER,
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_STATE_COLORS,
    PLAYER_VARIABLE_JUMP_CUTOFF,
    PLAYER_WALL_CHECK_MARGIN,
    PLAYER_WALL_JUMP_FORCE_X,
    PLAYER_WALL_JUMP_FORCE_Y,
    PLAYER_WALL_JUMP_LOCKOUT,
    PLAYER_WALL_SLIDE_SPEED,
    PLAYER_WIDTH,
)
from sa_fona.core.input_handler import InputState
from sa_fona.entities.entity import Entity
from sa_fona.systems.physics import PhysicsSystem


class PlayerState(Enum):
    """Enumeration of player movement states."""

    IDLE = auto()
    RUNNING = auto()
    JUMPING = auto()
    FALLING = auto()
    WALL_SLIDING = auto()
    WALL_JUMPING = auto()


# Map enum values to string keys used in settings color dict.
_STATE_KEY: dict[PlayerState, str] = {
    PlayerState.IDLE: "idle",
    PlayerState.RUNNING: "running",
    PlayerState.JUMPING: "jumping",
    PlayerState.FALLING: "falling",
    PlayerState.WALL_SLIDING: "wall_sliding",
    PlayerState.WALL_JUMPING: "wall_jumping",
}


class Player(Entity):
    """Ramon -- the playable character.

    Extends Entity with a finite-state machine for movement,
    variable-height jumping, wall sliding, and wall jumping.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        physics: The level's physics system for collision queries.
    """

    def __init__(self, x: float, y: float, physics: PhysicsSystem) -> None:
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self._physics = physics
        self._state: PlayerState = PlayerState.IDLE

        # Timers.
        self._coyote_timer: float = 0.0
        self._jump_buffer_timer: float = 0.0
        self._wall_jump_lockout_timer: float = 0.0

        # Wall contact flags (set each frame).
        self._touching_wall_left: bool = False
        self._touching_wall_right: bool = False

        # Cached input for the current frame.
        self._input_x: float = 0.0
        self._jump_pressed: bool = False
        self._jump_held: bool = False
        self._jump_released: bool = False

        # Pre-render colored surfaces for each state.
        self._surfaces: dict[PlayerState, pygame.Surface] = {}
        self._build_surfaces()

    # ── Surface generation ─────────────────────────────────────────

    def _build_surfaces(self) -> None:
        """Create a placeholder colored rectangle for every state."""
        for state, key in _STATE_KEY.items():
            color = PLAYER_STATE_COLORS.get(key, (255, 255, 255))
            surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            surf.fill(color)
            self._surfaces[state] = surf
        self._sprite = self._surfaces[self._state]

    # ── Public API ─────────────────────────────────────────────────

    @property
    def state(self) -> PlayerState:
        """Current movement state."""
        return self._state

    @property
    def state_name(self) -> str:
        """Human-readable name of the current state."""
        return _STATE_KEY[self._state]

    @property
    def touching_wall_left(self) -> bool:
        """True if the player is touching a wall to the left."""
        return self._touching_wall_left

    @property
    def touching_wall_right(self) -> bool:
        """True if the player is touching a wall to the right."""
        return self._touching_wall_right

    def handle_input(self, input_state: InputState) -> None:
        """Cache relevant input actions for the update step.

        Args:
            input_state: The current frame's input snapshot.
        """
        self._input_x = input_state.move_x
        self._jump_pressed = input_state.jump_pressed
        self._jump_held = input_state.jump_held
        self._jump_released = input_state.jump_released

        if input_state.jump_pressed:
            self._jump_buffer_timer = PLAYER_JUMP_BUFFER

    def update(self, dt: float) -> None:
        """Run one simulation step: input -> state -> physics.

        Args:
            dt: Delta time in seconds.
        """
        self._update_timers(dt)
        self._check_wall_contact()
        self._apply_input(dt)
        self._run_physics(dt)
        self._update_state()
        self._sprite = self._surfaces[self._state]

    # ── Private helpers ────────────────────────────────────────────

    def _update_timers(self, dt: float) -> None:
        """Tick down coyote time, jump buffer, and wall-jump lockout."""
        if self._coyote_timer > 0:
            self._coyote_timer -= dt
        if self._jump_buffer_timer > 0:
            self._jump_buffer_timer -= dt
        if self._wall_jump_lockout_timer > 0:
            self._wall_jump_lockout_timer -= dt

    def _check_wall_contact(self) -> None:
        """Probe the tilemap for wall contact on left and right sides."""
        margin = PLAYER_WALL_CHECK_MARGIN

        # Left probe: a thin rect extending from the player's left edge.
        left_probe = pygame.Rect(
            self.rect.left - margin,
            self.rect.top + 2,
            margin,
            self.rect.height - 4,
        )
        self._touching_wall_left = len(
            self._physics.check_collision(left_probe, "solid")
        ) > 0

        # Right probe: a thin rect extending from the player's right edge.
        right_probe = pygame.Rect(
            self.rect.right,
            self.rect.top + 2,
            margin,
            self.rect.height - 4,
        )
        self._touching_wall_right = len(
            self._physics.check_collision(right_probe, "solid")
        ) > 0

    def _apply_input(self, dt: float) -> None:
        """Translate cached input into velocity changes."""
        locked = self._wall_jump_lockout_timer > 0

        # ── Horizontal movement ────────────────────────────────
        if not locked:
            self.velocity[0] = self._input_x * PLAYER_MOVE_SPEED
            if self._input_x > 0:
                self.facing_right = True
            elif self._input_x < 0:
                self.facing_right = False

        # ── Wall slide ─────────────────────────────────────────
        touching_wall = self._touching_wall_left or self._touching_wall_right
        pressing_into_wall = (
            (self._touching_wall_left and self._input_x < 0)
            or (self._touching_wall_right and self._input_x > 0)
        )
        if (
            not self.on_ground
            and touching_wall
            and pressing_into_wall
            and self.velocity[1] > 0
        ):
            # Cap downward velocity to the wall-slide speed.
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)

        # ── Jumping ────────────────────────────────────────────
        can_jump_ground = self.on_ground or self._coyote_timer > 0
        want_jump = self._jump_pressed or self._jump_buffer_timer > 0

        if want_jump and can_jump_ground:
            self.velocity[1] = PLAYER_JUMP_FORCE
            self._coyote_timer = 0.0
            self._jump_buffer_timer = 0.0
        elif want_jump and not self.on_ground and touching_wall and not locked:
            # Wall jump.
            self.velocity[1] = PLAYER_WALL_JUMP_FORCE_Y
            if self._touching_wall_left:
                self.velocity[0] = PLAYER_WALL_JUMP_FORCE_X
                self.facing_right = True
            else:
                self.velocity[0] = -PLAYER_WALL_JUMP_FORCE_X
                self.facing_right = False
            self._wall_jump_lockout_timer = PLAYER_WALL_JUMP_LOCKOUT
            self._jump_buffer_timer = 0.0

        # ── Variable jump height ───────────────────────────────
        if self._jump_released and self.velocity[1] < 0:
            self.velocity[1] *= PLAYER_VARIABLE_JUMP_CUTOFF

    def _run_physics(self, dt: float) -> None:
        """Delegate movement and collision to PhysicsSystem."""
        was_on_ground = self.on_ground
        self.rect, self.velocity, self.on_ground = self._physics.update_rect(
            self.rect, self.velocity, dt, self.on_ground,
        )
        # Start coyote timer when walking off a ledge (not jumping).
        if was_on_ground and not self.on_ground and self.velocity[1] >= 0:
            self._coyote_timer = PLAYER_COYOTE_TIME

    def _update_state(self) -> None:
        """Determine the correct state from velocity and flags."""
        if self._wall_jump_lockout_timer > 0:
            self._state = PlayerState.WALL_JUMPING
            return

        touching_wall = self._touching_wall_left or self._touching_wall_right
        pressing_into_wall = (
            (self._touching_wall_left and self._input_x < 0)
            or (self._touching_wall_right and self._input_x > 0)
        )

        if not self.on_ground and touching_wall and pressing_into_wall and self.velocity[1] > 0:
            self._state = PlayerState.WALL_SLIDING
        elif self.on_ground:
            if abs(self.velocity[0]) > 1.0:
                self._state = PlayerState.RUNNING
            else:
                self._state = PlayerState.IDLE
        elif self.velocity[1] < 0:
            self._state = PlayerState.JUMPING
        else:
            self._state = PlayerState.FALLING
