"""Tests for the generic AI sprite processor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure tools/ is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.process_ai_sprites import (
    assemble_sheet,
    check_facing_right,
    crop_and_clean_pose,
    detect_poses,
    ensure_facing_right,
    generate_placeholder_sheet,
    hard_threshold_alpha,
    place_in_frame,
    process_source,
    remove_green_background,
    scale_pose_to_frame,
)


def _make_green_image_with_poses(
    width: int = 400,
    height: int = 200,
    num_poses: int = 3,
    pose_w: int = 60,
    pose_h: int = 80,
    pose_color: tuple[int, int, int] = (180, 100, 80),
) -> np.ndarray:
    """Create a synthetic green-background image with colored pose rectangles.

    Args:
        width: Image width.
        height: Image height.
        num_poses: Number of poses to place.
        pose_w: Width of each pose rectangle.
        pose_h: Height of each pose rectangle.
        pose_color: RGB color for poses.

    Returns:
        RGB numpy array.
    """
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = [0, 255, 0]  # Green background

    spacing = (width - num_poses * pose_w) // (num_poses + 1)
    y_start = (height - pose_h) // 2

    for i in range(num_poses):
        x_start = spacing + i * (pose_w + spacing)
        img[y_start:y_start + pose_h, x_start:x_start + pose_w] = pose_color

    return img


class TestRemoveGreenBackground:
    """Tests for green chroma-key removal."""

    def test_pure_green_becomes_transparent(self) -> None:
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        img[:, :] = [0, 255, 0]
        rgba = remove_green_background(img)
        assert np.all(rgba[:, :, 3] == 0)

    def test_non_green_stays_opaque(self) -> None:
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        img[:, :] = [200, 100, 80]
        rgba = remove_green_background(img)
        assert np.all(rgba[:, :, 3] == 255)

    def test_handles_4_channel_input(self) -> None:
        img = np.zeros((10, 10, 4), dtype=np.uint8)
        img[:, :, :3] = [200, 100, 80]
        img[:, :, 3] = 255
        rgba = remove_green_background(img)
        assert np.all(rgba[:, :, 3] == 255)


class TestDetectPoses:
    """Tests for pose region detection."""

    def test_detects_correct_count(self) -> None:
        img = _make_green_image_with_poses(num_poses=4)
        rgba = remove_green_background(img)
        poses = detect_poses(rgba, min_area=100)
        assert len(poses) == 4

    def test_sorted_left_to_right(self) -> None:
        img = _make_green_image_with_poses(num_poses=3)
        rgba = remove_green_background(img)
        poses = detect_poses(rgba, min_area=100)
        x_starts = [p[0] for p in poses]
        assert x_starts == sorted(x_starts)

    def test_filters_small_regions(self) -> None:
        img = _make_green_image_with_poses(num_poses=2, pose_w=60, pose_h=80)
        rgba = remove_green_background(img)
        # Add a tiny 5x5 non-green region
        rgba[5:10, 5:10, :3] = [200, 100, 80]
        rgba[5:10, 5:10, 3] = 255
        poses = detect_poses(rgba, min_area=100)
        assert len(poses) == 2  # Tiny region filtered out


class TestCropAndCleanPose:
    """Tests for pose cropping and green fringe cleaning."""

    def test_crops_to_tight_bounds(self) -> None:
        rgba = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba[20:50, 30:70, :3] = [180, 100, 80]
        rgba[20:50, 30:70, 3] = 255
        crop = crop_and_clean_pose(rgba, (25, 15, 75, 55), inset=3)
        assert crop.shape[0] > 0
        assert crop.shape[1] > 0
        assert np.any(crop[:, :, 3] > 0)


class TestScalePoseToFrame:
    """Tests for the two-step scaling pipeline."""

    def test_output_fits_in_frame(self) -> None:
        pose = np.ones((60, 40, 4), dtype=np.uint8) * 200
        pose[:, :, 3] = 255
        scaled = scale_pose_to_frame(pose, 16, 16)
        assert scaled.shape[0] <= 16
        assert scaled.shape[1] <= 16

    def test_empty_pose_returns_empty(self) -> None:
        pose = np.zeros((0, 0, 4), dtype=np.uint8)
        scaled = scale_pose_to_frame(pose, 16, 16)
        assert scaled.shape == (16, 16, 4)


class TestPlaceInFrame:
    """Tests for frame placement (center-horizontal, bottom-align)."""

    def test_bottom_aligned(self) -> None:
        pose = np.ones((8, 6, 4), dtype=np.uint8) * 200
        pose[:, :, 3] = 255
        frame = place_in_frame(pose, 16, 16)
        assert frame.shape == (16, 16, 4)
        # Bottom 8 rows should have content
        assert np.any(frame[8:, :, 3] > 0)
        # Top 8 rows should be empty
        assert np.all(frame[:8, :, 3] == 0)

    def test_centered_horizontally(self) -> None:
        pose = np.ones((4, 4, 4), dtype=np.uint8) * 200
        pose[:, :, 3] = 255
        frame = place_in_frame(pose, 16, 8)
        # 4px wide in 16px frame -> offset = 6
        assert np.any(frame[:, 6:10, 3] > 0)


class TestHardThresholdAlpha:
    """Tests for alpha hard-thresholding."""

    def test_below_threshold_transparent(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 50
        result = hard_threshold_alpha(rgba, threshold=100)
        assert np.all(result[:, :, 3] == 0)

    def test_above_threshold_opaque(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 150
        result = hard_threshold_alpha(rgba, threshold=100)
        assert np.all(result[:, :, 3] == 255)


class TestCheckFacingRight:
    """Tests for facing direction detection."""

    def test_symmetric_is_right(self) -> None:
        pose = np.zeros((10, 10, 4), dtype=np.uint8)
        pose[2:8, 2:8, 3] = 255
        assert check_facing_right(pose) is True

    def test_right_heavy_is_left_facing(self) -> None:
        pose = np.zeros((10, 20, 4), dtype=np.uint8)
        # More mass on right half = likely faces left
        pose[2:8, 12:18, 3] = 255
        assert check_facing_right(pose) is False

    def test_left_heavy_is_right_facing(self) -> None:
        pose = np.zeros((10, 20, 4), dtype=np.uint8)
        # More mass on left half = faces right
        pose[2:8, 2:8, 3] = 255
        assert check_facing_right(pose) is True


class TestEnsureFacingRight:
    """Tests for the flip-if-needed function."""

    def test_flips_left_facing(self) -> None:
        pose = np.zeros((10, 20, 4), dtype=np.uint8)
        pose[2:8, 14:18, :3] = [255, 0, 0]
        pose[2:8, 14:18, 3] = 255
        result = ensure_facing_right(pose, "test")
        # After flipping, mass should be on left side
        left_mass = np.sum(result[:, :10, 3].astype(float))
        right_mass = np.sum(result[:, 10:, 3].astype(float))
        assert left_mass >= right_mass


class TestAssembleSheet:
    """Tests for horizontal sprite sheet assembly."""

    def test_correct_dimensions(self) -> None:
        frames = [np.ones((16, 16, 4), dtype=np.uint8) * 200 for _ in range(4)]
        sheet = assemble_sheet(frames)
        assert sheet.shape == (16, 64, 4)

    def test_single_frame(self) -> None:
        frame = np.ones((8, 8, 4), dtype=np.uint8) * 200
        sheet = assemble_sheet([frame])
        assert sheet.shape == (8, 8, 4)


class TestGeneratePlaceholderSheet:
    """Tests for placeholder sprite generation."""

    def test_correct_dimensions(self) -> None:
        sheet = generate_placeholder_sheet(16, 16, 3)
        assert sheet.shape == (16, 48, 4)

    def test_has_visible_content(self) -> None:
        sheet = generate_placeholder_sheet(12, 12, 2)
        assert np.any(sheet[:, :, 3] > 0)

    def test_saves_to_file(self, tmp_path: Path) -> None:
        out_path = tmp_path / "test.png"
        generate_placeholder_sheet(8, 8, 1, output_path=out_path)
        assert out_path.exists()
        img = Image.open(out_path)
        assert img.size == (8, 8)


class TestProcessSource:
    """Integration tests for the full processing pipeline."""

    def test_missing_source_generates_placeholders(self, tmp_path: Path) -> None:
        config = {
            "input": str(tmp_path / "nonexistent" / "image.png"),
            "outputs": [
                {
                    "file": str(tmp_path / "output" / "test.png"),
                    "poses": [1, 2],
                    "frame_width": 16,
                    "frame_height": 16,
                }
            ],
        }
        result = process_source(config)
        assert len(result["processed"]) == 1
        assert (tmp_path / "output" / "test.png").exists()

    def test_processes_real_source(self, tmp_path: Path) -> None:
        # Create a synthetic green-background image
        img = _make_green_image_with_poses(num_poses=3)
        input_path = tmp_path / "source" / "image.png"
        input_path.parent.mkdir(parents=True)
        Image.fromarray(img).save(str(input_path))

        config = {
            "input": str(input_path),
            "outputs": [
                {
                    "file": str(tmp_path / "out" / "idle.png"),
                    "poses": [1, 2],
                    "frame_width": 16,
                    "frame_height": 16,
                },
                {
                    "file": str(tmp_path / "out" / "jump.png"),
                    "poses": [3],
                    "frame_width": 16,
                    "frame_height": 16,
                },
            ],
        }
        result = process_source(config)
        assert len(result["processed"]) == 2
        assert (tmp_path / "out" / "idle.png").exists()
        assert (tmp_path / "out" / "jump.png").exists()

        # Verify dimensions
        idle = Image.open(str(tmp_path / "out" / "idle.png"))
        assert idle.size == (32, 16)  # 2 frames x 16w
        jump = Image.open(str(tmp_path / "out" / "jump.png"))
        assert jump.size == (16, 16)  # 1 frame x 16w

    def test_out_of_range_poses_warns(self, tmp_path: Path) -> None:
        img = _make_green_image_with_poses(num_poses=2)
        input_path = tmp_path / "source" / "image.png"
        input_path.parent.mkdir(parents=True)
        Image.fromarray(img).save(str(input_path))

        config = {
            "input": str(input_path),
            "outputs": [
                {
                    "file": str(tmp_path / "out" / "test.png"),
                    "poses": [1, 5],  # pose 5 doesn't exist
                    "frame_width": 16,
                    "frame_height": 16,
                }
            ],
        }
        result = process_source(config)
        assert len(result["processed"]) == 1
        # Should still produce output with 1 valid frame
        img_out = Image.open(str(tmp_path / "out" / "test.png"))
        assert img_out.size == (16, 16)  # Only 1 valid pose
