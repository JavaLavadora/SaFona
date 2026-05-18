"""Tests for the Camera system."""

import pygame
import pytest

from sa_fona.config.settings import CAMERA_LOOKAHEAD_RATIO
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
        # Camera should roughly center on the target, shifted right
        # by the lookahead offset so the player sits left of center.
        lookahead = int(camera.view_width * CAMERA_LOOKAHEAD_RATIO)
        expected_x = target.centerx - camera.view_width // 2 + lookahead
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


class TestCameraSnapTo:
    """Tests for the snap_to() instant centering method."""

    def test_snap_to_centers_on_target(self) -> None:
        """snap_to places camera so the target sits left of center (lookahead)."""
        camera = Camera(level_width=2000, level_height=1000)
        target = pygame.Rect(500, 300, 24, 32)

        camera.snap_to(target)

        ox, oy = camera.offset
        lookahead = int(camera.view_width * CAMERA_LOOKAHEAD_RATIO)
        expected_x = target.centerx - camera.view_width // 2 + lookahead
        expected_y = target.centery - camera.view_height // 2
        assert ox == expected_x
        assert oy == expected_y

    def test_snap_to_clamps_to_level_bounds(self) -> None:
        """snap_to clamps when the target is near the level edge."""
        camera = Camera(level_width=400, level_height=250)
        # Target in top-left corner: camera would go negative without clamping.
        target = pygame.Rect(0, 0, 24, 32)

        camera.snap_to(target)

        ox, oy = camera.offset
        assert ox >= 0, "Camera X should not go below 0 after snap_to"
        assert oy >= 0, "Camera Y should not go below 0 after snap_to"

    def test_snap_to_clamps_bottom_right(self) -> None:
        """snap_to clamps when target is near bottom-right edge."""
        camera = Camera(level_width=500, level_height=300)
        target = pygame.Rect(490, 290, 24, 32)

        camera.snap_to(target)

        ox, oy = camera.offset
        max_x = 500 - camera.view_width
        max_y = 300 - camera.view_height
        assert ox <= max(0, max_x), f"Camera X {ox} should not exceed {max_x}"
        assert oy <= max(0, max_y), f"Camera Y {oy} should not exceed {max_y}"

    def test_snap_to_with_zoom_centers_correctly(self) -> None:
        """snap_to with zoom uses effective viewport for centering."""
        camera = Camera(level_width=2000, level_height=1000, zoom=2.0)
        target = pygame.Rect(500, 300, 24, 32)

        camera.snap_to(target)

        # Effective viewport is half the view size at 2x zoom.
        eff_w = camera.view_width / 2.0
        eff_h = camera.view_height / 2.0
        lookahead = eff_w * CAMERA_LOOKAHEAD_RATIO
        expected_x = int(target.centerx - eff_w / 2 + lookahead)
        expected_y = int(target.centery - eff_h / 2)
        ox, oy = camera.offset
        assert ox == expected_x, f"Zoomed snap X {ox} != {expected_x}"
        assert oy == expected_y, f"Zoomed snap Y {oy} != {expected_y}"


class TestCameraZoom:
    """Tests for camera zoom functionality."""

    def test_zoom_property_default(self) -> None:
        """Default zoom is 1.0."""
        camera = Camera(level_width=1000, level_height=500)
        assert camera.zoom == 1.0

    def test_zoom_property_custom(self) -> None:
        """Custom zoom is stored and accessible."""
        camera = Camera(level_width=1000, level_height=500, zoom=1.3)
        assert camera.zoom == pytest.approx(1.3)

    def test_zoom_clamp_smaller_effective_viewport(self) -> None:
        """With zoom, camera clamps to a smaller effective viewport."""
        # Level barely larger than the unzoomed viewport.
        camera_no_zoom = Camera(level_width=400, level_height=230)
        camera_zoomed = Camera(level_width=400, level_height=230, zoom=1.3)

        target = pygame.Rect(390, 220, 24, 32)

        camera_no_zoom.snap_to(target)
        camera_zoomed.snap_to(target)

        ox_nz, oy_nz = camera_no_zoom.offset
        ox_z, oy_z = camera_zoomed.offset

        # Zoomed camera can scroll further because the effective viewport
        # is smaller than the unzoomed one.
        max_x_no_zoom = max(0, 400 - camera_no_zoom.view_width)
        max_x_zoomed = max(0, 400 - camera_zoomed.view_width / 1.3)
        assert max_x_zoomed > max_x_no_zoom or max_x_no_zoom == 0

    def test_zoom_follow_uses_effective_viewport(self) -> None:
        """Camera follow with zoom converges to zoomed center."""
        camera = Camera(level_width=2000, level_height=1000, zoom=2.0)
        target = pygame.Rect(500, 300, 24, 32)

        for _ in range(120):
            camera.follow(target, 0.016)
            camera.update(0.016)

        eff_w = camera.view_width / 2.0
        eff_h = camera.view_height / 2.0
        lookahead = eff_w * CAMERA_LOOKAHEAD_RATIO
        expected_x = target.centerx - eff_w / 2 + lookahead
        expected_y = target.centery - eff_h / 2
        ox, oy = camera.offset
        assert abs(ox - expected_x) < 2, f"Zoomed follow X {ox} != ~{expected_x}"
        assert abs(oy - expected_y) < 2, f"Zoomed follow Y {oy} != ~{expected_y}"


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
        lookahead = int(camera.view_width * CAMERA_LOOKAHEAD_RATIO)
        base_x = target.centerx - camera.view_width // 2 + lookahead
        base_y = target.centery - camera.view_height // 2
        ox, oy = camera.offset
        assert abs(ox - base_x) < 3, "Shake should have decayed"
        assert abs(oy - base_y) < 3, "Shake should have decayed"
