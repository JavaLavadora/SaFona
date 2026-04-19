"""Entry point for Sa Fona.

Run with::

    python -m sa_fona.main

Optionally specify a level to load (bypasses main menu)::

    python -m sa_fona.main --level world1/level_1_2

Or jump directly to a boss fight::

    python -m sa_fona.main --boss bou_de_pedra
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

    god_mode = "--god" in sys.argv

    # --boss <boss_id>: skip to boss scene directly.
    if "--boss" in sys.argv:
        idx = sys.argv.index("--boss")
        boss_id = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "bou_de_pedra"

        from sa_fona.core.game import Game as _G
        game = _G(level_path=level_path, skip_menu=True)

        from sa_fona.scenes.boss_scene import BossScene
        boss_scene = BossScene(
            boss_id=boss_id,
            event_bus=game.event_bus,
        )
        boss_scene.scene_manager = game.scene_manager
        if god_mode:
            boss_scene.combat._god_mode = True
        game.scene_manager.replace(boss_scene)

        try:
            game.run()
        except KeyboardInterrupt:
            pass
        finally:
            pygame.quit()
            sys.exit(0)

    # --level flag: bypass menu, go directly to that level.
    if level_path is not None:
        game = Game(level_path=level_path, skip_menu=True)
    else:
        # Default: show main menu.
        game = Game(level_path=None, skip_menu=False)

    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
