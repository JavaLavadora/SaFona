"""Tests for the Camera system."""

import pygame
import pytest

from sa_fona.core.camera import Camera


class TestCameraFollow:
    """Tests for camera following a target."""

    def test_follows_target(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        target = pygame.Rect(400, 200, 24, 32)

        # Simulate several frames of following.
        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        ox, oy = camera.offset
        # Camera should roughly center on the target.
        expected_x = target.centerx - camera.view_width // 2
        expected_y = target.centery - camera.view_height // 2
        assert abs(ox - expected_x) < 5, f"Camera X {ox} should be near {expected_x}"
        assert abs(oy - expected_y) < 5, f"Camera Y {oy} should be near {expected_y}"


class TestCameraClamp:
    """Tests that the camera clamps to level bounds."""

    def test_clamp_left_top(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        target = pygame.Rect(0, 0, 24, 32)

        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        ox, oy = camera.offset
        assert ox >= 0, "Camera X should not go below 0"
        assert oy >= 0, "Camera Y should not go below 0"

    def test_clamp_right_bottom(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        target = pygame.Rect(980, 480, 24, 32)

        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        ox, oy = camera.offset
        max_x = 1000 - camera.view_width
        max_y = 500 - camera.view_height
        assert ox <= max_x + 1, f"Camera X {ox} should be <= {max_x}"
        assert oy <= max_y + 1, f"Camera Y {oy} should be <= {max_y}"

    def test_small_level_clamps_to_zero(self) -> None:
        """Level smaller than viewport: camera stays at (0, 0)."""
        camera = Camera(level_width=100, level_height=100)
        target = pygame.Rect(50, 50, 24, 32)

        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        ox, oy = camera.offset
        assert ox == 0
        assert oy == 0


class TestCameraApply:
    """Tests for the apply() offset method."""

    def test_apply_offsets_rect(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        target = pygame.Rect(500, 300, 24, 32)

        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        world_rect = pygame.Rect(500, 300, 24, 32)
        screen_rect = camera.apply(world_rect)

        ox, oy = camera.offset
        assert screen_rect.x == world_rect.x - ox
        assert screen_rect.y == world_rect.y - oy
        assert screen_rect.width == world_rect.width
        assert screen_rect.height == world_rect.height


class TestScreenShake:
    """Tests for screen shake."""

    def test_shake_produces_nonzero_offset(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        # Center camera first.
        target = pygame.Rect(500, 250, 24, 32)
        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        base_offset = camera.offset

        camera.shake(intensity=20.0, duration=1.0)

        # Collect offsets over several frames.
        offsets_differ = False
        for _ in range(30):
            camera.follow(target, 0.016)
            camera.update(0.016)
            ox, oy = camera.offset
            if ox != base_offset[0] or oy != base_offset[1]:
                offsets_differ = True
                break

        assert offsets_differ, "Shake should produce non-zero offset"

    def test_shake_decays(self) -> None:
        camera = Camera(level_width=1000, level_height=500)
        target = pygame.Rect(500, 250, 24, 32)
        for _ in range(60):
            camera.follow(target, 0.016)
            camera.update(0.016)

        camera.shake(intensity=20.0, duration=0.1)

        # Advance past the shake duration.
        for _ in range(30):
            camera.follow(target, 0.016)
            camera.update(0.016)

        # After shake expires, offset should return to steady state.
        base_x = target.centerx - camera.view_width // 2
        base_y = target.centery - camera.view_height // 2
        ox, oy = camera.offset
        assert abs(ox - base_x) < 3, "Shake should have decayed"
        assert abs(oy - base_y) < 3, "Shake should have decayed"
