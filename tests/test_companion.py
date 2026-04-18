"""Tests for the Companion entity (Bep)."""

import pygame
import pytest

from sa_fona.entities.companion import (
    CATCH_UP_DISTANCE,
    COMPANION_HEIGHT,
    COMPANION_WIDTH,
    FOLLOW_DISTANCE,
    TELEPORT_DISTANCE,
    Companion,
)


class TestCompanionInit:
    """Tests for Companion initialization."""

    def test_dimensions(self):
        bep = Companion(100, 200)
        assert bep.rect.width == COMPANION_WIDTH
        assert bep.rect.height == COMPANION_HEIGHT

    def test_initial_position(self):
        bep = Companion(100, 200)
        assert bep.rect.x == 100
        assert bep.rect.y == 200


class TestCompanionFollow:
    """Tests for follow AI behavior."""

    def test_moves_toward_player(self):
        bep = Companion(0, 100)
        player_rect = pygame.Rect(200, 100, 24, 32)
        bep.follow(player_rect, dt=0.1)
        # Bep should have moved to the right.
        assert bep.rect.x > 0

    def test_stays_close_when_near(self):
        player_rect = pygame.Rect(100, 100, 24, 32)
        # Place bep very close to target position.
        target_x = player_rect.x - FOLLOW_DISTANCE
        target_y = player_rect.bottom - COMPANION_HEIGHT
        bep = Companion(target_x + 1, target_y)
        initial_x = bep.rect.x
        bep.follow(player_rect, dt=0.1)
        # Should barely move (distance < 4 pixels, within threshold).
        assert abs(bep.rect.x - initial_x) <= 2

    def test_teleports_when_very_far(self):
        bep = Companion(0, 0)
        far_x = TELEPORT_DISTANCE + 500
        player_rect = pygame.Rect(int(far_x), 0, 24, 32)
        bep.follow(player_rect, dt=0.1)
        # Should have teleported near the player.
        assert abs(bep.rect.x - (far_x - FOLLOW_DISTANCE)) < 2

    def test_catches_up_when_far(self):
        bep = Companion(0, 100)
        # Place player far but within teleport range.
        player_rect = pygame.Rect(200, 100, 24, 32)
        bep.follow(player_rect, dt=1.0)  # 1 second, should move substantially.
        assert bep.rect.x > 50  # Should have moved a lot.


class TestCompanionUpdate:
    """Tests for companion update (bob animation)."""

    def test_update_does_not_crash(self):
        bep = Companion(100, 100)
        bep.update(0.016)  # One frame at 60fps.


class TestCompanionRender:
    """Tests for companion rendering."""

    @pytest.fixture(autouse=True)
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_mode((384, 216))
        yield
        pygame.quit()

    def test_render_does_not_crash(self):
        bep = Companion(100, 100)
        surface = pygame.Surface((384, 216))
        bep.render(surface, (0, 0))

    def test_render_with_camera_offset(self):
        bep = Companion(100, 100)
        surface = pygame.Surface((384, 216))
        bep.render(surface, (50, 30))
