"""Boss health bar rendered at the bottom of the screen.

Displays the boss name, a health bar with phase markers, and the
current phase name.  The bar smoothly transitions when the boss takes
damage and flashes during phase transitions.

This is a separate UI component from the main HUD, only active during
boss encounters.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_WIDTH


# ── Layout constants ──────────────────────────────────────────────
_BAR_MARGIN_X: int = 40
_BAR_HEIGHT: int = 8
_BAR_BORDER: int = 1

# Colors.
_BAR_BG_COLOR: tuple[int, int, int] = (30, 30, 30)
_BAR_BORDER_COLOR: tuple[int, int, int] = (80, 80, 80)
_BAR_HP_COLORS: list[tuple[int, int, int]] = [
    (220, 40, 40),    # Phase 3 (low HP) - red
    (220, 160, 40),   # Phase 2 (mid HP) - orange
    (60, 180, 60),    # Phase 1 (high HP) - green
]
_BAR_DAMAGE_COLOR: tuple[int, int, int] = (220, 220, 60)
_PHASE_MARKER_COLOR: tuple[int, int, int] = (200, 200, 200)
_TEXT_COLOR: tuple[int, int, int] = (240, 240, 240)
_TEXT_SHADOW_COLOR: tuple[int, int, int] = (20, 20, 20)


class BossHealthBar:
    """Boss health bar UI component.

    Renders at the top center of the screen.  Shows the boss name,
    a segmented health bar with phase markers, and the current phase.

    Args:
        boss_name: Display name of the boss.
        max_health: Total HP.
        phase_thresholds: List of HP fractions where phases change
            (e.g. [0.66, 0.33] for 3-phase bosses).
    """

    def __init__(
        self,
        boss_name: str,
        max_health: float,
        phase_thresholds: list[float] | None = None,
    ) -> None:
        self._boss_name = boss_name
        self._max_health = max_health
        self._current_health = max_health
        self._display_health = max_health  # Smoothly catches up.
        self._phase_thresholds = phase_thresholds or [0.66, 0.33]
        self._current_phase: int = 1
        self._phase_name: str = ""
        self._visible: bool = True

        # Smooth damage animation.
        self._damage_catch_speed: float = 40.0  # HP per second.

        # Flash timer for phase transitions.
        self._flash_timer: float = 0.0

        # Font.
        self._name_font: pygame.font.Font | None = None
        self._phase_font: pygame.font.Font | None = None
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize fonts for the boss name and phase label."""
        try:
            self._name_font = pygame.font.Font(None, 14)
            self._phase_font = pygame.font.Font(None, 12)
        except Exception:
            pass

    # ── Public API ────────────────────────────────────────────────

    @property
    def current_health(self) -> float:
        """Current boss health."""
        return self._current_health

    @property
    def max_health(self) -> float:
        """Maximum boss health."""
        return self._max_health

    @property
    def health_fraction(self) -> float:
        """Current health as a fraction (0.0 to 1.0)."""
        return max(0.0, self._current_health / self._max_health)

    @property
    def display_fraction(self) -> float:
        """Displayed health fraction (smoothly animated)."""
        return max(0.0, self._display_health / self._max_health)

    @property
    def visible(self) -> bool:
        """Whether the bar is visible."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    def set_health(self, current: float) -> None:
        """Update the current health value.

        The display bar will smoothly catch up.  Snaps to 0 on defeat
        so the bar is empty before the victory screen.

        Args:
            current: New health value.
        """
        self._current_health = max(0.0, current)
        if self._current_health <= 0:
            self._display_health = 0.0

    def set_phase(self, phase: int, phase_name: str = "") -> None:
        """Update the current phase display.

        Args:
            phase: Phase number (1-indexed).
            phase_name: Human-readable phase name.
        """
        if phase != self._current_phase:
            self._flash_timer = 0.5
        self._current_phase = phase
        self._phase_name = phase_name

    def update(self, dt: float) -> None:
        """Animate the health bar toward current health.

        Args:
            dt: Delta time in seconds.
        """
        if self._display_health > self._current_health:
            self._display_health -= self._damage_catch_speed * dt
            if self._display_health < self._current_health:
                self._display_health = self._current_health

        if self._flash_timer > 0:
            self._flash_timer -= dt

    def render(self, surface: pygame.Surface) -> None:
        """Draw the boss health bar on the screen.

        Args:
            surface: Target surface (screen space, not camera-relative).
        """
        if not self._visible:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()
        bar_width = screen_w - 2 * _BAR_MARGIN_X

        # Position from the bottom of the screen.
        bar_y = screen_h - _BAR_HEIGHT - 14
        name_y = bar_y - 12
        phase_y = bar_y + _BAR_HEIGHT + 2

        # Boss name (centered above bar).
        if self._name_font is not None:
            name_surf = self._name_font.render(
                self._boss_name, False, _TEXT_COLOR
            )
            shadow_surf = self._name_font.render(
                self._boss_name, False, _TEXT_SHADOW_COLOR
            )
            nx = (screen_w - name_surf.get_width()) // 2
            surface.blit(shadow_surf, (nx + 1, name_y + 1))
            surface.blit(name_surf, (nx, name_y))

        # Bar background.
        bar_rect = pygame.Rect(_BAR_MARGIN_X, bar_y, bar_width, _BAR_HEIGHT)
        pygame.draw.rect(surface, _BAR_BG_COLOR, bar_rect)
        pygame.draw.rect(surface, _BAR_BORDER_COLOR, bar_rect, _BAR_BORDER)

        # Damage trail (yellow, catches up to actual health).
        if self._display_health > self._current_health:
            trail_width = int(bar_width * self.display_fraction)
            trail_rect = pygame.Rect(
                _BAR_MARGIN_X + _BAR_BORDER,
                bar_y + _BAR_BORDER,
                max(0, trail_width - 2 * _BAR_BORDER),
                _BAR_HEIGHT - 2 * _BAR_BORDER,
            )
            pygame.draw.rect(surface, _BAR_DAMAGE_COLOR, trail_rect)

        # Health fill.
        if self._current_health > 0:
            hp_frac = self.health_fraction
            hp_width = int(bar_width * hp_frac)

            if hp_frac > 0.66:
                color = _BAR_HP_COLORS[2]
            elif hp_frac > 0.33:
                color = _BAR_HP_COLORS[1]
            else:
                color = _BAR_HP_COLORS[0]

            fill_rect = pygame.Rect(
                _BAR_MARGIN_X + _BAR_BORDER,
                bar_y + _BAR_BORDER,
                max(0, hp_width - 2 * _BAR_BORDER),
                _BAR_HEIGHT - 2 * _BAR_BORDER,
            )
            pygame.draw.rect(surface, color, fill_rect)

        # Phase markers (vertical lines at threshold positions).
        for threshold in self._phase_thresholds:
            marker_x = _BAR_MARGIN_X + int(bar_width * threshold)
            pygame.draw.line(
                surface,
                _PHASE_MARKER_COLOR,
                (marker_x, bar_y),
                (marker_x, bar_y + _BAR_HEIGHT),
                1,
            )

        # Phase transition flash overlay.
        if self._flash_timer > 0:
            alpha = int(120 * (self._flash_timer / 0.5))
            flash_surf = pygame.Surface(
                (bar_width, _BAR_HEIGHT), pygame.SRCALPHA
            )
            flash_surf.fill((255, 255, 255, max(0, min(255, alpha))))
            surface.blit(flash_surf, (_BAR_MARGIN_X, bar_y))

        # Phase label (below bar).
        if self._phase_font is not None and self._phase_name:
            phase_text = f"Phase {self._current_phase}: {self._phase_name}"
            phase_surf = self._phase_font.render(
                phase_text, False, _TEXT_COLOR
            )
            px = (screen_w - phase_surf.get_width()) // 2
            surface.blit(phase_surf, (px, phase_y))
