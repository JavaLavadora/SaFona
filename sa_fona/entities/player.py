"""Player entity (Ramon) with a state-machine driven moveset.

States: idle, running, jumping, falling, wall_sliding, wall_jumping.
Receives physics results from the scene integration layer.  Input is
read via InputState.  Uses real sprite sheets when available, falling
back to colored rectangles.
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
from sa_fona.rendering.sprite_renderer import load_sprite_sheet_from_file


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
        self._prev_state: PlayerState = PlayerState.IDLE

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

        # Height-tracking for same-wall climb prevention.
        # Records the player's Y position when a wall jump starts.
        # If the player touches the same wall side again (without
        # landing), wall slide/jump is only allowed if Y >= this
        # value (i.e. equal or lower on screen).  This makes it
        # physically impossible to gain height on the same wall.
        self._wall_jump_origin_y: float | None = None

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
        """Load real sprites or fall back to colored rectangles."""
        self._idle_frames: list[pygame.Surface] = []
        self._walk_frames: list[pygame.Surface] = []
        self._jump_frames: list[pygame.Surface] = []
        self._wall_slide_frames: list[pygame.Surface] = []
        self._wall_jump_frames: list[pygame.Surface] = []
        self._sling_frames: list[pygame.Surface] = []
        self._hit_frames: list[pygame.Surface] = []
        self._death_frames: list[pygame.Surface] = []
        self._anim_timer: float = 0.0
        self._anim_frame: int = 0
        self._anim_speed: float = 0.15
        self._walk_anim_speed: float = 0.1
        self._sling_anim_speed: float = 0.08

        # Sling animation state set externally by the gameplay scene.
        # Values: "none", "charging", "releasing".
        self._sling_anim_state: str = "none"

        # Hit/death animation state (set externally by gameplay/combat).
        # Values: "none", "hit", "death".
        self._damage_anim_state: str = "none"
        self._damage_anim_timer: float = 0.0

        # Load all sprite sheets.
        anim_paths = {
            "_idle_frames": "idle",
            "_walk_frames": "walk",
            "_jump_frames": "jump",
            "_wall_slide_frames": "wall_slide",
            "_wall_jump_frames": "wall_jump",
            "_sling_frames": "sling",
            "_hit_frames": "hit",
            "_death_frames": "death",
        }
        for attr, name in anim_paths.items():
            frames = load_sprite_sheet_from_file(
                f"assets/sprites/ramon/{name}.png",
                PLAYER_WIDTH, PLAYER_HEIGHT,
            )
            if frames:
                setattr(self, attr, frames)

        has_sprites = bool(
            self._idle_frames or self._walk_frames or self._jump_frames
            or self._wall_slide_frames or self._wall_jump_frames
            or self._sling_frames
        )

        for state, key in _STATE_KEY.items():
            if self._idle_frames and state == PlayerState.IDLE:
                self._surfaces[state] = self._idle_frames[0]
            elif self._walk_frames and state == PlayerState.RUNNING:
                self._surfaces[state] = self._walk_frames[0]
            elif self._jump_frames and state == PlayerState.JUMPING:
                self._surfaces[state] = self._jump_frames[0]
            elif self._jump_frames and state == PlayerState.FALLING:
                self._surfaces[state] = self._jump_frames[-1]
            elif self._wall_slide_frames and state == PlayerState.WALL_SLIDING:
                self._surfaces[state] = self._wall_slide_frames[0]
            elif self._wall_jump_frames and state == PlayerState.WALL_JUMPING:
                self._surfaces[state] = self._wall_jump_frames[0]
            elif has_sprites:
                surf = pygame.Surface(
                    (PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA,
                )
                self._surfaces[state] = surf
            else:
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

    @property
    def sling_anim_state(self) -> str:
        """The sling animation state: ``"none"``, ``"charging"``, or ``"releasing"``.

        Set by the gameplay scene based on SlingSystem state.
        """
        return self._sling_anim_state

    @sling_anim_state.setter
    def sling_anim_state(self, value: str) -> None:
        if value not in ("none", "charging", "releasing"):
            value = "none"
        if value != self._sling_anim_state:
            self._sling_anim_state = value
            # Reset sling animation frame on state change.
            if value != "none":
                self._anim_frame = 0
                self._anim_timer = 0.0

    @property
    def wall_jump_origin_y(self) -> float | None:
        """The Y position when the player last wall-jumped, if any.

        Used for height-tracking: same-wall contact is only allowed
        if the player's Y >= this value (same height or lower).
        """
        return self._wall_jump_origin_y

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
        self._update_sprite(dt)

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
            self._wall_jump_origin_y = None
        elif self._wall_jump_origin_side == "left" and wall_right:
            self._wall_jump_origin_side = None
            self._wall_jump_origin_y = None
        elif self._wall_jump_origin_side == "right" and wall_left:
            self._wall_jump_origin_side = None
            self._wall_jump_origin_y = None

        # Start coyote timer when walking off a ledge (not jumping).
        if was_on_ground and not self.on_ground and self.velocity[1] >= 0:
            self._coyote_timer = PLAYER_COYOTE_TIME

        self._update_state()
        self._update_sprite(0.0)

    # ── Private helpers ────────────────────────────────────────────

    @property
    def damage_anim_state(self) -> str:
        """Current damage animation state: "none", "hit", or "death"."""
        return self._damage_anim_state

    @damage_anim_state.setter
    def damage_anim_state(self, value: str) -> None:
        if value not in ("none", "hit", "death"):
            value = "none"
        if value != self._damage_anim_state:
            self._damage_anim_state = value
            self._damage_anim_timer = 0.0
            self._anim_frame = 0
            self._anim_timer = 0.0

    def _update_sprite(self, dt: float) -> None:
        """Select the correct sprite frame, with animation and flipping.

        Priority: death > hit > sling > movement state.
        """
        # Death animation overrides everything.
        if self._damage_anim_state == "death" and self._death_frames:
            self._damage_anim_timer += dt
            base = self._death_frames[min(
                int(self._damage_anim_timer / 0.15),
                len(self._death_frames) - 1,
            )]
            if not self.facing_right:
                self._sprite = pygame.transform.flip(base, True, False)
            else:
                self._sprite = base
            return

        # Hit animation overrides sling/movement.
        if self._damage_anim_state == "hit" and self._hit_frames:
            self._damage_anim_timer += dt
            if self._damage_anim_timer < 0.3:
                base = self._hit_frames[0]
                if not self.facing_right:
                    self._sprite = pygame.transform.flip(base, True, False)
                else:
                    self._sprite = base
                return
            # Hit animation done, revert.
            self._damage_anim_state = "none"

        # Sling animation overrides movement animation when active.
        if self._sling_anim_state != "none" and self._sling_frames:
            if self._sling_anim_state == "charging":
                # Cycle through frames 0 and 1 (wind-up, mid-rotation).
                charge_frames = self._sling_frames[:2]
                self._anim_timer += dt
                if self._anim_timer >= self._sling_anim_speed:
                    self._anim_timer -= self._sling_anim_speed
                    self._anim_frame = (self._anim_frame + 1) % len(charge_frames)
                if self._anim_frame >= len(charge_frames):
                    self._anim_frame = 0
                base = charge_frames[self._anim_frame]
            else:
                # "releasing" -- show frame 2 (release pose).
                base = self._sling_frames[-1]
                self._anim_frame = 0
                self._anim_timer = 0.0

            if not self.facing_right:
                self._sprite = pygame.transform.flip(base, True, False)
            else:
                self._sprite = base
            return

        if self._state != self._prev_state:
            self._anim_frame = 0
            self._anim_timer = 0.0
            self._prev_state = self._state

        frames: list[pygame.Surface] | None = None
        speed = self._anim_speed

        if self._state == PlayerState.IDLE and self._idle_frames:
            frames = self._idle_frames
        elif self._state == PlayerState.RUNNING and self._walk_frames:
            frames = self._walk_frames
            speed = self._walk_anim_speed
        elif self._state == PlayerState.JUMPING and self._jump_frames:
            base = self._jump_frames[0]
            self._anim_frame = 0
            self._anim_timer = 0.0
            if not self.facing_right:
                self._sprite = pygame.transform.flip(base, True, False)
            else:
                self._sprite = base
            return
        elif self._state == PlayerState.FALLING and self._jump_frames:
            base = self._jump_frames[-1]
            self._anim_frame = 0
            self._anim_timer = 0.0
            if not self.facing_right:
                self._sprite = pygame.transform.flip(base, True, False)
            else:
                self._sprite = base
            return
        elif self._state == PlayerState.WALL_SLIDING and self._wall_slide_frames:
            frames = self._wall_slide_frames
        elif self._state == PlayerState.WALL_JUMPING and self._wall_jump_frames:
            frames = self._wall_jump_frames

        if frames:
            self._anim_timer += dt
            if self._anim_timer >= speed:
                self._anim_timer -= speed
                self._anim_frame = (self._anim_frame + 1) % len(frames)
            if self._anim_frame >= len(frames):
                self._anim_frame = 0
            base = frames[self._anim_frame]
        else:
            base = self._surfaces[self._state]
            self._anim_frame = 0
            self._anim_timer = 0.0

        if not self.facing_right:
            self._sprite = pygame.transform.flip(base, True, False)
        else:
            self._sprite = base

    def _update_timers(self, dt: float) -> None:
        """Tick down coyote time, jump buffer, and wall-jump lockout."""
        if self._coyote_timer > 0:
            self._coyote_timer -= dt
        if self._jump_buffer_timer > 0:
            self._jump_buffer_timer -= dt
        if self._wall_jump_lockout_timer > 0:
            self._wall_jump_lockout_timer -= dt

    def _is_same_wall_side(self) -> bool:
        """Check whether the player is touching the same wall they jumped from."""
        if self._wall_jump_origin_side is None:
            return False
        if (
            self._wall_jump_origin_side == "left"
            and self._touching_wall_left
            and not self._touching_wall_right
        ):
            return True
        if (
            self._wall_jump_origin_side == "right"
            and self._touching_wall_right
            and not self._touching_wall_left
        ):
            return True
        return False

    def _can_wall_slide(self) -> bool:
        """Check if the player is allowed to wall slide.

        Uses height tracking: after a wall jump, wall sliding on the
        same wall is only permitted at or below the origin Y (the
        position where the wall jump started).  This prevents gaining
        height but allows sliding back down the same wall.

        Wall-to-wall sliding is always allowed because touching the
        opposite wall clears the origin tracking.
        """
        if not self._is_same_wall_side():
            return True

        # Height check: only allow slide at or below origin Y.
        if self._wall_jump_origin_y is not None:
            if self.rect.y < self._wall_jump_origin_y:
                return False

        return True

    def _can_wall_jump(self) -> bool:
        """Check if the player is allowed to wall jump.

        After a wall jump, same-wall jumping is only allowed if the
        player has slid back down to or below the previous wall jump
        origin Y.  Each successive same-wall jump updates the origin,
        ensuring net downward movement and preventing infinite climbing.

        Wall-to-wall jumping is always allowed because touching the
        opposite wall clears the origin tracking.
        """
        if not self._is_same_wall_side():
            return True

        # Height check: allow wall jump only at or below origin Y.
        if self._wall_jump_origin_y is not None:
            if self.rect.y >= self._wall_jump_origin_y:
                return True

        return False

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

        # Prevent re-grabbing / re-jumping the same wall after a
        # wall jump using side tracking + height tracking.
        can_slide = self._can_wall_slide()
        can_wj = self._can_wall_jump()

        if (
            not self.on_ground
            and touching_wall
            and pressing_into_wall
            and self.velocity[1] > 0
            and can_slide
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
        elif (
            want_jump
            and not self.on_ground
            and touching_wall
            and not locked
            and can_wj
        ):
            # Wall jump: requires pressing INTO the wall plus jump.
            # The player is already holding into the wall to maintain
            # the wall slide, so they just add jump.  If just jump is
            # pressed (no direction or away direction), the player
            # detaches and falls.
            if pressing_into_wall:
                # Wall jump.
                self.velocity[1] = PLAYER_WALL_JUMP_FORCE_Y
                self._wall_jump_origin_y = float(self.rect.y)
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
            else:
                # Detach from wall without wall jump forces (just fall).
                self.velocity[0] = 0.0
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

        # Same-wall re-grab prevention (uses height-tracking helper).
        can_slide = self._can_wall_slide()

        if (
            not self.on_ground
            and touching_wall
            and pressing_into_wall
            and self.velocity[1] > 0
            and can_slide
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
