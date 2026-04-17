"""Entry point for Sa Fona.

Run with::

    python -m sa_fona.main
"""

from __future__ import annotations

import sys

import pygame


def main() -> None:
    """Create the Game instance and start the main loop."""
    from sa_fona.core.game import Game

    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
