"""Entry point for Sa Fona.

Run with::

    python -m sa_fona.main

Optionally specify a level to load::

    python -m sa_fona.main --level world1/level_1_2
"""

from __future__ import annotations

import sys

import pygame


def main() -> None:
    """Create the Game instance and start the main loop."""
    from sa_fona.config.settings import DATA_DIR
    from sa_fona.core.game import Game

    level_path = None
    # Simple CLI: --level <relative_path>
    if "--level" in sys.argv:
        idx = sys.argv.index("--level")
        if idx + 1 < len(sys.argv):
            rel = sys.argv[idx + 1]
            # Ensure .json extension.
            if not rel.endswith(".json"):
                rel += ".json"
            level_path = str(DATA_DIR / "levels" / rel)

    game = Game(level_path=level_path)
    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
