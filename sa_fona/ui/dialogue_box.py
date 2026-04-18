"""Bottom-screen dialogue text box with character portrait and letter-by-letter reveal.

Renders a dialogue box at the bottom of the screen, showing the speaker name,
a portrait placeholder (colored square with initial), and text that reveals
letter by letter. Pressing interact advances to the next line or finishes
revealing the current line.
"""

from __future__ import annotations

import pygame

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus

# Layout constants (in base-resolution pixels).
BOX_MARGIN = 6
BOX_HEIGHT = 68
BOX_PADDING = 6
PORTRAIT_SIZE = 44
TEXT_LEFT_OFFSET = PORTRAIT_SIZE + BOX_PADDING * 2
SPEAKER_Y_OFFSET = 4
TEXT_Y_OFFSET = 18
LINE_SPACING = 14

# Letter reveal speed.
DEFAULT_CHARS_PER_SECOND = 30.0

# Colors.
BOX_BG_COLOR = (10, 8, 18, 245)
BOX_BORDER_COLOR = (200, 180, 130)
SPEAKER_COLOR = (255, 220, 100)
TEXT_COLOR = (255, 255, 255)
PORTRAIT_BG_COLOR = (60, 50, 80)
PORTRAIT_BORDER_COLOR = (200, 180, 130)

# Speaker -> portrait color mapping.
_SPEAKER_COLORS: dict[str, tuple[int, int, int]] = {
    "bep": (50, 180, 80),
    "ramon": (50, 100, 200),
    "narrator": (150, 150, 150),
}
_DEFAULT_PORTRAIT_COLOR: tuple[int, int, int] = (120, 100, 140)


def _portrait_color(speaker: str) -> tuple[int, int, int]:
    """Get the placeholder portrait color for a speaker.

    Args:
        speaker: Speaker identifier string.

    Returns:
        An (R, G, B) color tuple.
    """
    return _SPEAKER_COLORS.get(speaker.lower(), _DEFAULT_PORTRAIT_COLOR)


class DialogueBox:
    """Renders the bottom-screen dialogue text box with character portrait.

    Dialogue data is loaded externally. A dialogue sequence is a list of
    line dicts, each with ``speaker``, ``portrait``, ``text``, and optional
    ``sfx`` and ``auto_advance_ms`` fields.

    Args:
        event_bus: Shared event bus for publishing dialogue events.
        chars_per_second: Speed of letter-by-letter text reveal.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        chars_per_second: float = DEFAULT_CHARS_PER_SECOND,
    ) -> None:
        """Initialize the dialogue box.

        Args:
            event_bus: Event bus for dialogue_started/ended events.
            chars_per_second: Letter reveal speed.
        """
        self._event_bus = event_bus
        self._chars_per_second = chars_per_second

        # Dialogue state.
        self._sequence: list[dict] = []
        self._current_index: int = 0
        self._reveal_timer: float = 0.0
        self._revealed_chars: int = 0
        self._active: bool = False
        self._skippable: bool = True

        # Auto-advance timer (milliseconds converted to seconds).
        self._auto_advance_timer: float = 0.0
        self._auto_advance_duration: float = 0.0

        # Font (initialized lazily to avoid pygame.init requirement at import).
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None

    # ── Properties ─────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        """Whether a dialogue sequence is currently playing."""
        return self._active

    @property
    def skippable(self) -> bool:
        """Whether the current dialogue can be skipped entirely."""
        return self._skippable

    @property
    def current_index(self) -> int:
        """Index of the current line in the sequence."""
        return self._current_index

    @property
    def revealed_chars(self) -> int:
        """Number of characters currently revealed."""
        return self._revealed_chars

    @property
    def is_fully_revealed(self) -> bool:
        """Whether the current line's text is fully revealed."""
        if not self._active or self._current_index >= len(self._sequence):
            return True
        full_text = self._sequence[self._current_index].get("text", "")
        return self._revealed_chars >= len(full_text)

    # ── Public API ─────────────────────────────────────────────────

    def start(self, dialogue_sequence: list[dict], skippable: bool = True) -> None:
        """Begin a dialogue sequence.

        Args:
            dialogue_sequence: List of line dicts with speaker, text, etc.
            skippable: Whether the player can skip the entire dialogue.
        """
        if not dialogue_sequence:
            return

        self._sequence = dialogue_sequence
        self._current_index = 0
        self._revealed_chars = 0
        self._reveal_timer = 0.0
        self._active = True
        self._skippable = skippable

        # Check for auto-advance on the first line.
        self._setup_auto_advance()

        if self._event_bus:
            self._event_bus.publish("dialogue_started")

    def advance(self) -> bool:
        """Advance to the next line or finish revealing the current line.

        If the current line is not fully revealed, finish it immediately.
        If it is fully revealed, move to the next line. If there are no
        more lines, end the dialogue.

        Returns:
            True if the dialogue sequence is now complete.
        """
        if not self._active:
            return True

        if not self.is_fully_revealed:
            # Finish revealing the current line.
            full_text = self._sequence[self._current_index].get("text", "")
            self._revealed_chars = len(full_text)
            self._auto_advance_timer = 0.0
            self._setup_auto_advance()
            return False

        # Move to the next line.
        self._current_index += 1
        if self._current_index >= len(self._sequence):
            self._end()
            return True

        self._revealed_chars = 0
        self._reveal_timer = 0.0
        self._setup_auto_advance()
        return False

    def skip(self) -> None:
        """Skip the entire dialogue sequence (if skippable)."""
        if self._skippable:
            self._end()

    def update(self, dt: float) -> None:
        """Update letter-by-letter text reveal and auto-advance timer.

        Args:
            dt: Delta time in seconds.
        """
        if not self._active:
            return

        if self._current_index >= len(self._sequence):
            return

        # Letter-by-letter reveal.
        full_text = self._sequence[self._current_index].get("text", "")
        if self._revealed_chars < len(full_text):
            self._reveal_timer += dt
            chars_to_reveal = int(self._reveal_timer * self._chars_per_second)
            self._revealed_chars = min(chars_to_reveal, len(full_text))

        # Auto-advance.
        if self._auto_advance_duration > 0 and self.is_fully_revealed:
            self._auto_advance_timer += dt
            if self._auto_advance_timer >= self._auto_advance_duration:
                self.advance()

    def render(self, surface: pygame.Surface) -> None:
        """Draw the dialogue box, portrait, and text.

        Args:
            surface: The pygame Surface to draw on (base resolution).
        """
        if not self._active:
            return

        self._ensure_fonts()

        # Box position.
        box_x = BOX_MARGIN
        box_y = BASE_HEIGHT - BOX_HEIGHT - BOX_MARGIN
        box_w = BASE_WIDTH - BOX_MARGIN * 2

        # Draw box background with alpha.
        box_surface = pygame.Surface((box_w, BOX_HEIGHT), pygame.SRCALPHA)
        box_surface.fill(BOX_BG_COLOR)
        surface.blit(box_surface, (box_x, box_y))

        # Draw box border.
        pygame.draw.rect(
            surface,
            BOX_BORDER_COLOR,
            (box_x, box_y, box_w, BOX_HEIGHT),
            1,
        )

        if self._current_index >= len(self._sequence):
            return

        line = self._sequence[self._current_index]
        speaker = line.get("speaker", "")
        text = line.get("text", "")

        # Portrait placeholder.
        portrait_x = box_x + BOX_PADDING
        portrait_y = box_y + (BOX_HEIGHT - PORTRAIT_SIZE) // 2
        color = _portrait_color(speaker)

        pygame.draw.rect(
            surface,
            color,
            (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE),
        )
        pygame.draw.rect(
            surface,
            PORTRAIT_BORDER_COLOR,
            (portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE),
            1,
        )

        # Draw speaker initial on portrait.
        initial = speaker[0].upper() if speaker else "?"
        initial_surf = self._font.render(initial, False, (255, 255, 255))
        ix = portrait_x + (PORTRAIT_SIZE - initial_surf.get_width()) // 2
        iy = portrait_y + (PORTRAIT_SIZE - initial_surf.get_height()) // 2
        surface.blit(initial_surf, (ix, iy))

        # Speaker name.
        text_x = box_x + TEXT_LEFT_OFFSET
        name_display = speaker.capitalize() if speaker else ""
        name_surf = self._small_font.render(name_display, False, SPEAKER_COLOR)
        surface.blit(name_surf, (text_x, box_y + SPEAKER_Y_OFFSET))

        # Revealed text (letter-by-letter).
        revealed = text[: self._revealed_chars]
        self._render_wrapped_text(
            surface,
            revealed,
            text_x,
            box_y + TEXT_Y_OFFSET,
            box_w - TEXT_LEFT_OFFSET - BOX_PADDING,
        )

    # ── Private helpers ────────────────────────────────────────────

    def _end(self) -> None:
        """End the dialogue sequence."""
        self._active = False
        self._sequence = []
        self._current_index = 0
        self._revealed_chars = 0
        if self._event_bus:
            self._event_bus.publish("dialogue_ended")

    def _setup_auto_advance(self) -> None:
        """Configure auto-advance timer for the current line."""
        self._auto_advance_timer = 0.0
        self._auto_advance_duration = 0.0
        if self._current_index < len(self._sequence):
            auto_ms = self._sequence[self._current_index].get("auto_advance_ms")
            if auto_ms is not None:
                self._auto_advance_duration = auto_ms / 1000.0

    def _ensure_fonts(self) -> None:
        """Lazily initialize fonts."""
        if self._font is None:
            self._font = pygame.font.Font(None, 20)
        if self._small_font is None:
            self._small_font = pygame.font.Font(None, 18)

    def _render_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
    ) -> None:
        """Render text with simple word-wrapping.

        Args:
            surface: Target surface.
            text: Text to render.
            x: Left edge X coordinate.
            y: Top Y coordinate.
            max_width: Maximum line width in pixels.
        """
        assert self._small_font is not None

        words = text.split(" ")
        lines: list[str] = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip() if current_line else word
            test_width = self._small_font.size(test_line)[0]
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_surf = self._small_font.render(line, False, TEXT_COLOR)
            surface.blit(line_surf, (x, y + i * LINE_SPACING))
