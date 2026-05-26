"""Tests for environment sprite rendering (bonfire + taula gate)."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.level.trigger import Trigger, TriggerType


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()


class TestSavePointRendering:
    """Tests for bonfire sprite rendering at save points."""

    def test_activated_save_points_initialized(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        assert hasattr(scene, "_activated_save_points")
        assert isinstance(scene._activated_save_points, set)
        assert len(scene._activated_save_points) == 0

    def test_save_point_activation_tracks_trigger(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        trigger = Trigger(
            pygame.Rect(480, 192, 32, 48),
            TriggerType.SAVE_POINT,
            once=False,
            properties={"shop_available": False},
        )
        scene._on_trigger_save_point(trigger=trigger)
        assert id(trigger) in scene._activated_save_points

    def test_render_save_point_cues_does_not_crash(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        surface = pygame.Surface((384, 216))
        scene._render_save_point_cues(surface, (0, 0))
