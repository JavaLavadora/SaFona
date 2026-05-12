"""Base class for boss entities with phase management and attack patterns.

BossEntity extends Entity (not Enemy) because bosses have their own
phase system, pattern sequencing, tell/punish timers, and health bar.
They are special entities that share some traits with enemies (health,
contact damage) but have fundamentally different behavior.

Boss data is loaded from JSON files in data/bosses/.  The JSON provides
tuning parameters (timings, damage values); the code provides behavior.
"""

from __future__ import annotations

import json
import random
from abc import abstractmethod
from enum import Enum, auto
from typing import Any

import pygame

from sa_fona.config.settings import DATA_DIR
from sa_fona.core.event_bus import EventBus
from sa_fona.entities.entity import Entity
from sa_fona.rendering.asset_loader import load_frame_strip


class BossState(Enum):
    """High-level state of the boss during the fight."""

    INTRO = auto()
    IDLE = auto()
    TELL = auto()
    ATTACKING = auto()
    PUNISH = auto()
    PHASE_TRANSITION = auto()
    DEFEATED = auto()


class BossEntity(Entity):
    """Abstract base class for all boss entities.

    Provides phase management, attack pattern sequencing, tell/punish
    timers, invincibility logic, and data loading from JSON.

    Subclasses implement specific attack behaviors by overriding the
    ``_execute_attack``, ``_update_attack``, and ``_on_phase_transition``
    methods.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        definition: Boss definition dict loaded from JSON.
        event_bus: Shared event bus for publishing boss events.
    """

    def __init__(
        self,
        x: float,
        y: float,
        definition: dict,
        event_bus: EventBus,
    ) -> None:
        hitbox = definition.get("hitbox", {})
        width = hitbox.get("w", 84)
        height = hitbox.get("h", 72)
        super().__init__(x, y, width, height)

        self._event_bus = event_bus
        self._definition = definition

        # Identity.
        self.boss_id: str = definition.get("boss_id", "unknown")
        self.display_name: str = definition.get("display_name", "Boss")

        # Health.
        self.max_health: float = float(definition.get("health", 30))
        self.health: float = self.max_health
        self.contact_damage: float = float(definition.get("contact_damage", 1.0))

        # Phase management.
        self._phases: list[dict] = definition.get("phases", [])
        self._current_phase_index: int = 0
        self._phase_transitioning: bool = False
        self._transition_timer: float = 0.0
        self._transition_duration: float = 1.5  # Seconds for phase transition.

        # Attack pattern state.
        self._state: BossState = BossState.INTRO
        self._current_pattern: dict | None = None
        self._state_timer: float = 0.0
        self._idle_timer: float = 0.0
        self._idle_duration: float = 1.0  # Brief pause between attacks.
        self._last_pattern_id: str = ""

        # Idle animation cycling.
        self._idle_anim_timer: float = 0.0
        self._idle_anim_frame: int = 0
        self._idle_anim_speed: float = 0.25

        # Invincibility.
        self._invincible: bool = False
        self._invincibility_timer: float = 0.0
        self._invincibility_duration: float = 0.2  # Brief after hit.
        self._hit_flash_timer: float = 0.0

        # Weak point (Phase 3).
        self._weak_point: dict | None = None
        self._core_exposed: bool = False

        # Post-defeat data.
        self._post_defeat: dict = definition.get("post_defeat", {})

        # Set initial phase.
        if self._phases:
            phase_data = self._phases[0]
            if phase_data.get("weak_point"):
                self._weak_point = phase_data["weak_point"]
            # Check all phases for weak_point (it's on phase 3).
            for p in self._phases:
                if p.get("weak_point"):
                    self._weak_point = p["weak_point"]

        # Rendering dimensions and sprite cache.
        self._width = width
        self._height = height
        self._boss_sprites: dict[str, list[pygame.Surface]] = {}
        self._has_boss_sprites: bool = False
        self._load_boss_sprites()
        self._build_sprite()

        # Font for label (fallback only).
        self._font: pygame.font.Font | None = None

    # ── Properties ─────────────────────────────────────────────────

    @property
    def state(self) -> BossState:
        """Current boss state."""
        return self._state

    @property
    def current_phase(self) -> int:
        """Current phase number (1-indexed)."""
        return self._current_phase_index + 1

    @property
    def current_phase_data(self) -> dict:
        """Current phase definition dict."""
        if self._current_phase_index < len(self._phases):
            return self._phases[self._current_phase_index]
        return {}

    @property
    def health_fraction(self) -> float:
        """Current health as a fraction of max (0.0 to 1.0)."""
        return max(0.0, self.health / self.max_health)

    @property
    def is_alive(self) -> bool:
        """Whether the boss still has health remaining."""
        return self.health > 0 and self.active

    @property
    def is_vulnerable(self) -> bool:
        """Whether the boss can take damage right now."""
        if self._invincible or self._invincibility_timer > 0:
            return False
        if self._state == BossState.PHASE_TRANSITION:
            return False
        if self._state == BossState.DEFEATED:
            return False
        if self._state == BossState.INTRO:
            return False
        # Boss is only vulnerable during punish windows (or core exposed).
        if self._state == BossState.PUNISH:
            return True
        if self._core_exposed and self.current_phase == 3:
            return True
        return False

    @property
    def is_in_punish(self) -> bool:
        """Whether the boss is in a punish window."""
        return self._state == BossState.PUNISH

    @property
    def is_in_tell(self) -> bool:
        """Whether the boss is showing an attack tell."""
        return self._state == BossState.TELL

    @property
    def is_attacking(self) -> bool:
        """Whether the boss is currently attacking."""
        return self._state == BossState.ATTACKING

    @property
    def current_pattern(self) -> dict | None:
        """The current attack pattern definition, if any."""
        return self._current_pattern

    @property
    def core_exposed(self) -> bool:
        """Whether the Phase 3 core weak point is exposed."""
        return self._core_exposed

    # ── Damage ─────────────────────────────────────────────────────

    def take_damage(self, amount: float, charge_tier: int = 0) -> bool:
        """Apply damage to the boss.

        Respects vulnerability state and applies phase 3 weak point
        multipliers for charged shots.

        Args:
            amount: Base damage amount.
            charge_tier: Sling charge tier (0=melee, 1-3=charged).

        Returns:
            True if damage was applied, False if invulnerable.
        """
        if not self.is_vulnerable:
            return False

        # Apply weak point multipliers in Phase 3.
        actual_damage = amount
        if self._core_exposed and self._weak_point and charge_tier > 0:
            if charge_tier == 3:
                actual_damage *= self._weak_point.get("tier3_multiplier", 3.0)
            else:
                actual_damage *= self._weak_point.get("charge_multiplier", 2.0)

        self.health -= actual_damage
        self._invincibility_timer = self._invincibility_duration
        self._hit_flash_timer = 0.15

        self._event_bus.publish(
            "damage_dealt",
            target_type="boss",
            boss_id=self.boss_id,
            amount=actual_damage,
        )

        if self.health <= 0:
            self.health = 0
            self._on_defeated()
            return True

        # Check for phase transition.
        self._check_phase_transition()
        return True

    # ── Phase Management ───────────────────────────────────────────

    def _check_phase_transition(self) -> None:
        """Check if HP has dropped below the current phase threshold.

        Handles skipping phases when massive damage is dealt (e.g.,
        dropping from phase 1 directly to phase 3).
        """
        if self._current_phase_index >= len(self._phases) - 1:
            return  # Already on last phase.

        # Find the correct phase for the current HP fraction.
        target_index = self._current_phase_index
        for i in range(self._current_phase_index + 1, len(self._phases)):
            phase = self._phases[i]
            hp_range = phase.get("hp_range", [0.0, 1.0])
            threshold = hp_range[1]  # Upper bound of this phase.
            if self.health_fraction <= threshold:
                target_index = i

        if target_index > self._current_phase_index:
            self._begin_phase_transition(target_index)

    def _begin_phase_transition(self, new_phase_index: int) -> None:
        """Start a phase transition.

        Args:
            new_phase_index: Index of the new phase in the phases list.
        """
        self._state = BossState.PHASE_TRANSITION
        self._phase_transitioning = True
        self._transition_timer = self._transition_duration
        self._invincible = True
        self._current_pattern = None

        old_phase = self._current_phase_index + 1
        self._current_phase_index = new_phase_index
        new_phase = new_phase_index + 1

        # Screen shake for transition.
        self._event_bus.publish(
            "screen_shake", intensity=8.0, duration=0.6
        )
        self._event_bus.publish(
            "boss_phase_change",
            boss_id=self.boss_id,
            old_phase=old_phase,
            new_phase=new_phase,
        )

        # Enable core exposure in Phase 3.
        if new_phase == 3 and self._weak_point:
            self._core_exposed = True

        self._on_phase_transition(old_phase, new_phase)
        self._build_sprite()

    def _finish_phase_transition(self) -> None:
        """Complete a phase transition and return to idle."""
        self._phase_transitioning = False
        self._invincible = False
        self._state = BossState.IDLE
        self._idle_timer = self._idle_duration

    # ── Attack Pattern Selection ───────────────────────────────────

    def _select_next_pattern(self) -> dict | None:
        """Choose the next attack pattern based on phase and weights.

        Avoids repeating the same pattern twice in a row.

        Returns:
            A pattern definition dict, or None if no patterns available.
        """
        phase_data = self.current_phase_data
        patterns = phase_data.get("patterns", [])
        if not patterns:
            return None

        # Filter out the last used pattern to avoid repetition.
        available = [p for p in patterns if p.get("id") != self._last_pattern_id]
        if not available:
            available = patterns

        # Weighted random selection.
        weights = [p.get("weight", 1.0) for p in available]
        total = sum(weights)
        if total <= 0:
            return random.choice(available)

        roll = random.random() * total
        cumulative = 0.0
        for pattern, weight in zip(available, weights):
            cumulative += weight
            if roll <= cumulative:
                return pattern

        return available[-1]

    # ── Update ─────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        """Update boss state machine, timers, and attack logic.

        Args:
            dt: Delta time in seconds.
        """
        # Tick invincibility.
        if self._invincibility_timer > 0:
            self._invincibility_timer -= dt
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= dt

        # Tick idle animation (runs in all states for smooth cycling).
        self._idle_anim_timer += dt
        if self._idle_anim_timer >= self._idle_anim_speed:
            self._idle_anim_timer -= self._idle_anim_speed
            self._idle_anim_frame += 1

        if self._state == BossState.DEFEATED:
            return

        if self._state == BossState.INTRO:
            # Intro is handled externally (scene manages intro cutscene).
            return

        if self._state == BossState.PHASE_TRANSITION:
            self._transition_timer -= dt
            if self._transition_timer <= 0:
                self._finish_phase_transition()
            return

        if self._state == BossState.IDLE:
            self._idle_timer -= dt
            if self._idle_timer <= 0:
                pattern = self._select_next_pattern()
                if pattern is not None:
                    self._begin_tell(pattern)
            return

        if self._state == BossState.TELL:
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._begin_attack()
            return

        if self._state == BossState.ATTACKING:
            self._state_timer -= dt
            self._update_attack(dt)
            if self._state_timer <= 0:
                self._begin_punish()
            return

        if self._state == BossState.PUNISH:
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._end_punish()
            return

    def _begin_tell(self, pattern: dict) -> None:
        """Enter the tell state for an attack pattern.

        Args:
            pattern: The attack pattern definition.
        """
        self._current_pattern = pattern
        self._state = BossState.TELL
        self._state_timer = pattern.get("tell_time", 1.0)
        self._last_pattern_id = pattern.get("id", "")

        self._event_bus.publish(
            "boss_attack_tell",
            boss_id=self.boss_id,
            pattern_id=pattern.get("id", ""),
        )

    def _begin_attack(self) -> None:
        """Transition from tell to attacking state."""
        self._state = BossState.ATTACKING
        # Attack duration is set by subclass in _execute_attack.
        self._state_timer = self._get_attack_duration()
        self._execute_attack()

    def _begin_punish(self) -> None:
        """Enter the punish window after an attack ends."""
        self._state = BossState.PUNISH
        if self._current_pattern:
            self._state_timer = self._current_pattern.get("punish_window", 1.5)
        else:
            self._state_timer = 1.5

        self._event_bus.publish(
            "boss_stunned",
            boss_id=self.boss_id,
            duration=self._state_timer,
        )

    def _end_punish(self) -> None:
        """Exit punish window and return to idle."""
        self._state = BossState.IDLE
        self._idle_timer = self._idle_duration
        self._current_pattern = None

    def _on_defeated(self) -> None:
        """Handle boss death."""
        self._state = BossState.DEFEATED
        self.active = False
        self._event_bus.publish(
            "boss_defeated",
            boss_id=self.boss_id,
            post_defeat=self._post_defeat,
        )

    def start_fight(self) -> None:
        """Transition from intro to the active fight."""
        self._state = BossState.IDLE
        self._idle_timer = self._idle_duration

    # ── Abstract methods for subclasses ────────────────────────────

    @abstractmethod
    def _execute_attack(self) -> None:
        """Start executing the current attack pattern.

        Called when the tell timer expires.  The subclass should set up
        any attack-specific state (movement, hitboxes, projectiles).
        """

    @abstractmethod
    def _update_attack(self, dt: float) -> None:
        """Update the current attack each frame while attacking.

        Args:
            dt: Delta time in seconds.
        """

    @abstractmethod
    def _get_attack_duration(self) -> float:
        """Return the duration of the current attack in seconds.

        Returns:
            Attack duration. Used to set the state timer.
        """

    @abstractmethod
    def _on_phase_transition(self, old_phase: int, new_phase: int) -> None:
        """Handle phase-specific transition logic.

        Args:
            old_phase: The phase number being left (1-indexed).
            new_phase: The phase number being entered (1-indexed).
        """

    # ── Sprite loading ─────────────────────────────────────────────

    # Map boss_id -> short prefix used in asset filenames.
    _BOSS_PREFIX_MAP: dict[str, str] = {
        "bou_de_pedra": "bou",
    }

    def _load_boss_sprites(self) -> None:
        """Load boss sprite sheets from assets/sprites/boss/.

        Attempts to load sprites keyed by a short prefix derived from
        the boss_id via ``_BOSS_PREFIX_MAP``.  Falls back to using the
        full boss_id when no mapping exists.  Populates
        ``_boss_sprites`` dict with state-name -> frame list mappings.
        """
        short_prefix = self._BOSS_PREFIX_MAP.get(self.boss_id, self.boss_id)
        sprite_names = [
            "idle_p1", "idle_p2", "idle_p3",
            "rush", "headbutt", "stomp",
            "stunned", "transition", "death",
        ]
        for name in sprite_names:
            path = f"assets/sprites/boss/{short_prefix}_{name}.png"
            frames = load_frame_strip(
                path, self._width, self._height,
            )
            if frames:
                self._boss_sprites[name] = frames
                self._has_boss_sprites = True

    def _get_boss_sprite_for_state(self) -> pygame.Surface | None:
        """Get the correct sprite surface for the current boss state.

        Returns:
            A pygame Surface or None if no sprite is available.
        """
        if not self._has_boss_sprites:
            return None

        # Map boss state to sprite key.
        if self._state == BossState.DEFEATED:
            frames = self._boss_sprites.get("death")
            if frames:
                return frames[0]

        if self._state == BossState.PHASE_TRANSITION:
            frames = self._boss_sprites.get("transition")
            if frames:
                return frames[0]

        if self._state == BossState.PUNISH:
            frames = self._boss_sprites.get("stunned")
            if frames:
                return frames[0]

        # Check for attack-specific sprites.
        if self._state in (BossState.TELL, BossState.ATTACKING):
            if self._current_pattern:
                pattern_id = self._current_pattern.get("id", "")
                # Map pattern IDs to sprite names.
                pattern_sprite_map = {
                    "bull_rush": "rush",
                    "frenzy_rush": "rush",
                    "headbutt": "headbutt",
                    "ground_stomp": "stomp",
                    "core_pulse": "idle_p3",
                }
                sprite_key = pattern_sprite_map.get(pattern_id)
                if sprite_key:
                    frames = self._boss_sprites.get(sprite_key)
                    if frames:
                        return frames[0]

        # Phase-specific idle sprite with animation cycling.
        phase_key = f"idle_p{self.current_phase}"
        frames = self._boss_sprites.get(phase_key)
        if frames:
            idx = self._idle_anim_frame % len(frames)
            return frames[idx]

        # Any available idle sprite.
        for key in ("idle_p1", "idle_p2", "idle_p3"):
            frames = self._boss_sprites.get(key)
            if frames:
                idx = self._idle_anim_frame % len(frames)
                return frames[idx]

        return None

    # ── Rendering ──────────────────────────────────────────────────

    def _build_sprite(self) -> None:
        """Build the sprite for the current state.

        Uses real boss sprites when available, falling back to colored
        rectangles per phase.
        """
        boss_surf = self._get_boss_sprite_for_state()
        if boss_surf is not None:
            self._sprite = boss_surf
            return

        # Fallback: colored rectangle.
        phase_data = self.current_phase_data
        color = tuple(phase_data.get("color", [140, 140, 140]))

        surf = pygame.Surface((self._width, self._height))
        surf.fill(color)
        border = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(surf, border, (0, 0, self._width, self._height), 2)
        self._sprite = surf

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the boss with visual state indicators.

        Args:
            surface: Target pygame Surface.
            camera_offset: (cam_x, cam_y) world-pixel camera offset.
        """
        if not self.active and self._state != BossState.DEFEATED:
            return

        # Update sprite to match current state.
        if self._has_boss_sprites:
            boss_surf = self._get_boss_sprite_for_state()
            if boss_surf is not None:
                self._sprite = boss_surf

        # Hit flash: blink white briefly when damaged.
        if self._hit_flash_timer > 0:
            blink = int(self._hit_flash_timer / 0.05)
            if blink % 2 == 1:
                screen_x = self.rect.x - camera_offset[0]
                screen_y = self.rect.y - camera_offset[1]
                flash = pygame.Surface((self._width, self._height))
                flash.fill((255, 255, 255))
                surface.blit(flash, (screen_x, screen_y))
                return

        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]

        # Draw base sprite, mirrored when facing left.
        if self._sprite is not None:
            if not self.facing_right:
                flipped = pygame.transform.flip(self._sprite, True, False)
                surface.blit(flipped, (screen_x, screen_y))
            else:
                surface.blit(self._sprite, (screen_x, screen_y))

        # Overlays only when using placeholder sprites (no sprite assets).
        if not self._has_boss_sprites:
            # Tell overlay (pulsing yellow).
            if self._state == BossState.TELL:
                tell_surf = pygame.Surface(
                    (self._width, self._height), pygame.SRCALPHA
                )
                tell_surf.fill((255, 220, 50, 100))
                surface.blit(tell_surf, (screen_x, screen_y))

            # Punish overlay (blue tint = stunned).
            if self._state == BossState.PUNISH:
                punish_surf = pygame.Surface(
                    (self._width, self._height), pygame.SRCALPHA
                )
                punish_surf.fill((50, 100, 255, 80))
                surface.blit(punish_surf, (screen_x, screen_y))

            # Label.
            try:
                if self._font is None:
                    self._font = pygame.font.Font(None, 18)
                label = self._font.render("B", False, (0, 0, 0))
                lx = screen_x + (self._width - label.get_width()) // 2
                ly = screen_y + (self._height - label.get_height()) // 2
                surface.blit(label, (lx, ly))
            except (pygame.error, IndexError):
                pass

        # Phase transition overlay (bright flash) -- shown even with sprites.
        if self._state == BossState.PHASE_TRANSITION:
            flash_surf = pygame.Surface(
                (self._width, self._height), pygame.SRCALPHA
            )
            alpha = int(180 * (self._transition_timer / self._transition_duration))
            flash_surf.fill((255, 255, 255, max(0, min(255, alpha))))
            surface.blit(flash_surf, (screen_x, screen_y))

        # Core glow in Phase 3.
        if self._core_exposed:
            core_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pulse = abs(int(self._idle_timer * 4) % 2)
            glow_alpha = 180 if pulse else 120
            core_surf.fill((255, 80, 80, glow_alpha))
            core_x = screen_x + self._width // 2 - 6
            core_y = screen_y + self._height // 2 - 6
            surface.blit(core_surf, (core_x, core_y))

    # ── Static loader ──────────────────────────────────────────────

    @staticmethod
    def load_definition(boss_id: str) -> dict:
        """Load a boss definition from the data/bosses directory.

        Args:
            boss_id: The boss ID (e.g. "bou_de_pedra").

        Returns:
            The parsed JSON definition dict.

        Raises:
            FileNotFoundError: If the boss JSON does not exist.
        """
        path = DATA_DIR / "bosses" / f"boss_{boss_id}.json"
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
