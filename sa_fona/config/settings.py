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
CAMERA_ZOOM: float = 1.3  # Camera zoom factor (1.0 = no zoom, >1 = closer)

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

# ── Player Movement ─────────────────────────────────────────────
PLAYER_WIDTH: int = 24
PLAYER_HEIGHT: int = 32
PLAYER_MOVE_SPEED: float = 120.0          # px/s horizontal
PLAYER_JUMP_FORCE: float = -330.0         # px/s upward impulse
PLAYER_VARIABLE_JUMP_CUTOFF: float = 0.5  # multiply vy when jump released early
PLAYER_WALL_SLIDE_SPEED: float = 40.0     # px/s max downward speed on wall
PLAYER_WALL_JUMP_FORCE_X: float = 160.0   # px/s horizontal push off wall
PLAYER_WALL_JUMP_FORCE_Y: float = -310.0  # px/s upward impulse on wall jump
PLAYER_WALL_JUMP_LOCKOUT: float = 0.40    # seconds of input lockout after wall jump
PLAYER_COYOTE_TIME: float = 0.06          # seconds grace after leaving ground
PLAYER_JUMP_BUFFER: float = 0.08          # seconds jump press remembered
PLAYER_GRAVITY: float = 800.0             # px/s^2
PLAYER_WALL_CHECK_MARGIN: int = 2         # pixels to probe for wall contact
PLAYER_CROUCH_HEIGHT: int = 20            # crouching hitbox height (vs 32 normal)
PLAYER_CRAWL_SPEED_FACTOR: float = 0.4    # crawl speed = 40% of normal walk
PLAYER_CROUCH_JUMP_FORCE: float = -200.0  # shorter jump while crouching

# ── Player State Colors (placeholder rendering) ────────────────
PLAYER_STATE_COLORS: dict[str, tuple[int, int, int]] = {
    "idle": (50, 100, 200),        # blue
    "running": (50, 180, 80),      # green
    "jumping": (255, 220, 50),     # yellow
    "falling": (200, 150, 50),     # orange
    "wall_sliding": (50, 200, 200),# cyan
    "wall_jumping": (200, 50, 200),# magenta
    "crouching": (100, 100, 200),  # dark blue
    "crawling": (100, 150, 200),   # blue-grey
}

# ── Combat ─────────────────────────────────────────────────────
PLAYER_INVINCIBILITY_DURATION: float = 1.0   # seconds after taking damage
PLAYER_BLINK_INTERVAL: float = 0.08          # seconds per blink toggle

# ── Scene Colors ───────────────────────────────────────────────
GAMEPLAY_BG_COLOR: tuple[int, int, int] = (30, 30, 50)

# ── Filesystem Paths ────────────────────────────────────────────
# Package root is the sa_fona/ directory.
PACKAGE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PACKAGE_DIR / "data"
ASSETS_DIR: Path = PACKAGE_DIR.parent / "assets"
SAVES_DIR: Path = PACKAGE_DIR.parent / "saves"
