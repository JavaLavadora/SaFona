"""Global constants and configuration for Sa Fona.

Defines game window settings, color palette, and filesystem paths
used throughout the engine. All magic numbers live here so they
can be tuned in one place.
"""

from pathlib import Path

# ── Window & Display ────────────────────────────────────────────
GAME_TITLE: str = "Sa Fona"
BASE_WIDTH: int = 384
BASE_HEIGHT: int = 216
WINDOW_SCALE: int = 3
FPS: int = 60

# ── Color Palette ───────────────────────────────────────────────
COLORS: dict[str, tuple[int, int, int]] = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "BLUE": (50, 100, 200),       # Player placeholder
    "RED": (200, 50, 50),         # Enemy placeholder
    "GREY": (150, 150, 150),      # Platform placeholder
    "YELLOW": (255, 220, 50),     # Collectible placeholder
    "GREEN": (50, 180, 80),       # NPC placeholder
}

# ── Filesystem Paths ────────────────────────────────────────────
# Package root is the sa_fona/ directory.
PACKAGE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PACKAGE_DIR / "data"
ASSETS_DIR: Path = PACKAGE_DIR.parent / "assets"
SAVES_DIR: Path = PACKAGE_DIR.parent / "saves"
