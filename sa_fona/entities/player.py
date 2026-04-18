"""Player entity (Ramon) with a state-machine driven moveset.

States: idle, running, jumping, falling, wall_sliding, wall_jumping.
Receives physics results from the scene integration layer.  Input is
read via InputState.  Placeholder rendering uses colored rectangles.
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from sa_fona.config.settings import (
    PLAYER_COYOTE_TIME,
    PLAYER_HEIGHT,
    PLAYER_JUMP_BUFFER,
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_STATE_COLORS,
    PLAYER_VARIABLE_JUMP_CUTOFF,
    PLAYER_WALL_JUMP_FORCE_X,
    PLAYER_WALL_JUMP_FORCE_Y,
    PLAYER_WALL_JUMP_LOCKOUT,
    PLAYER_WALL_SLIDE_SPEED,
    PLAYER_WIDTH,
)
from sa_fona.core.input_handler import InputState
from sa_fona.entities.entity import Entity


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

    The player does **not** depend on any systems package.  Physics
    integration is orchestrated by the scene (GameplayScene) which
    calls ``update_intent`` -> physics -> ``post_physics`` each frame.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self._state: PlayerState = PlayerState.IDLE

        # Timers.
        self._coyote_timer: float = 0.0
        self._jump_buffer_timer: float = 0.0
        self._wall_jump_lockout_timer: float = 0.0

        # Wall contact flags (set each frame).
        self._touching_wall_left: bool = False
        self._touching_wall_right: bool = False

        # Same-wall re-grab prevention.
        # After a wall jump, stores which side the jump came from
        # ("left" or "right").  Cleared on landing or touching the
        # opposite wall, preventing infinite same-wall climbing.
        self._wall_jump_origin_side: str | None = None

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

    @property
    def wall_jump_origin_side(self) -> str | None:
        """The wall side the player last wall-jumped from, if any.

        Returns ``"left"``, ``"right"``, or ``None``.  Used internally
        for same-wall re-grab prevention.
        """
        return self._wall_jump_origin_side

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
        """Legacy single-call update kept for Entity ABC compatibility.

        Prefer the split ``update_intent`` / ``post_physics`` flow
        orchestrated by the scene.  This default implementation only
        runs the intent step (no physics or wall contact).

        Args:
            dt: Delta time in seconds.
        """
        self.update_intent(dt)

    def update_intent(self, dt: float) -> None:
        """Process input and compute movement intent (velocity changes).

        This is the first half of the per-frame update.  After calling
        this, the scene should run physics and then call
        ``post_physics`` with the results.

        Args:
            dt: Delta time in seconds.
        """
        self._update_timers(dt)
        self._apply_input()
        self._sprite = self._surfaces[self._state]

    def post_physics(
        self,
        on_ground: bool,
        wall_left: bool,
        wall_right: bool,
    ) -> None:
        """Receive physics results and update player state accordingly.

        Called by the scene **after** the physics system has resolved
        movement and collisions.

        Args:
            on_ground: Whether the player is resting on solid ground.
            wall_left: Whether the player is touching a wall to the left.
            wall_right: Whether the player is touching a wall to the right.
        """
        was_on_ground = self.on_ground
        self.on_ground = on_ground
        self._touching_wall_left = wall_left
        self._touching_wall_right = wall_right

        # Clear same-wall re-grab lock when landing or touching the
        # opposite wall (allows wall-to-wall climbing).
        if on_ground:
            self._wall_jump_origin_side = None
        elif self._wall_jump_origin_side == "left" and wall_right:
            self._wall_jump_origin_side = None
        elif self._wall_jump_origin_side == "right" and wall_left:
            self._wall_jump_origin_side = None

        # Start coyote timer when walking off a ledge (not jumping).
        if was_on_ground and not self.on_ground and self.velocity[1] >= 0:
            self._coyote_timer = PLAYER_COYOTE_TIME

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

    def _apply_input(self) -> None:
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

        # Prevent re-grabbing the same wall after a wall jump.
        can_wall_slide = True
        if self._wall_jump_origin_side is not None:
            if (
                self._wall_jump_origin_side == "left"
                and self._touching_wall_left
                and not self._touching_wall_right
            ):
                can_wall_slide = False
            elif (
                self._wall_jump_origin_side == "right"
                and self._touching_wall_right
                and not self._touching_wall_left
            ):
                can_wall_slide = False

        if (
            not self.on_ground
            and touching_wall
            and pressing_into_wall
            and self.velocity[1] > 0
            and can_wall_slide
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
                self._wall_jump_origin_side = "left"
            else:
                self.velocity[0] = -PLAYER_WALL_JUMP_FORCE_X
                self.facing_right = False
                self._wall_jump_origin_side = "right"
            self._wall_jump_lockout_timer = PLAYER_WALL_JUMP_LOCKOUT
            self._jump_buffer_timer = 0.0

        # ── Variable jump height ───────────────────────────────
        if self._jump_released and self.velocity[1] < 0:
            self.velocity[1] *= PLAYER_VARIABLE_JUMP_CUTOFF

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

        # Same-wall re-grab prevention (mirrors check in _apply_input).
        can_wall_slide = True
        if self._wall_jump_origin_side is not None:
            if (
                self._wall_jump_origin_side == "left"
                and self._touching_wall_left
                and not self._touching_wall_right
            ):
                can_wall_slide = False
            elif (
                self._wall_jump_origin_side == "right"
                and self._touching_wall_right
                and not self._touching_wall_left
            ):
                can_wall_slide = False

        if (
            not self.on_ground
            and touching_wall
            and pressing_into_wall
            and self.velocity[1] > 0
            and can_wall_slide
        ):
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
