"""Tests for the sprite cleanup CLI tool."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure tools/ is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.clean_sprites import (
    clean_alpha,
    clean_sprite,
    compute_stats,
    enforce_color_limit,
    main,
    parse_gpl,
    resolve_output_path,
    resolve_palette_path,
    rgb_to_lab,
    snap_to_palette,
)


def _make_test_palette() -> np.ndarray:
    """Create a small test palette with distinct colors."""
    return np.array([
        [255, 0, 0],      # Red
        [0, 255, 0],      # Green
        [0, 0, 255],      # Blue
        [255, 255, 255],  # White
        [0, 0, 0],        # Black
    ], dtype=np.uint8)


def _make_gpl_file(path: Path, colors: list[tuple[int, int, int]], names: list[str] | None = None) -> None:
    """Write a minimal GPL palette file."""
    lines = ["GIMP Palette", "Name: Test", "Columns: 3", "# test palette"]
    for i, (r, g, b) in enumerate(colors):
        name = names[i] if names else f"Color {i}"
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{name}")
    path.write_text("\n".join(lines) + "\n")


class TestParseGpl:
    """Tests for GPL palette file parsing."""

    def test_parses_valid_gpl(self, tmp_path: Path) -> None:
        gpl = tmp_path / "test.gpl"
        _make_gpl_file(gpl, [(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        colors = parse_gpl(gpl)
        assert colors.shape == (3, 3)
        assert colors.dtype == np.uint8
        np.testing.assert_array_equal(colors[0], [255, 0, 0])
        np.testing.assert_array_equal(colors[1], [0, 255, 0])

    def test_skips_comments_and_headers(self, tmp_path: Path) -> None:
        gpl = tmp_path / "test.gpl"
        gpl.write_text(
            "GIMP Palette\n"
            "Name: Test\n"
            "Columns: 4\n"
            "# This is a comment\n"
            "128 64 32\tBrown\n"
            "\n"
            "200 100 50\tOrange\n"
        )
        colors = parse_gpl(gpl)
        assert len(colors) == 2
        np.testing.assert_array_equal(colors[0], [128, 64, 32])

    def test_raises_on_missing_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            parse_gpl(Path("/nonexistent/palette.gpl"))

    def test_raises_on_empty_palette(self, tmp_path: Path) -> None:
        gpl = tmp_path / "empty.gpl"
        gpl.write_text("GIMP Palette\nName: Empty\n")
        with pytest.raises(ValueError, match="No valid color"):
            parse_gpl(gpl)

    def test_raises_on_out_of_range_rgb(self, tmp_path: Path) -> None:
        gpl = tmp_path / "bad.gpl"
        gpl.write_text("GIMP Palette\nName: Bad\n256 0 0\tTooHigh\n")
        with pytest.raises(ValueError, match="out of 0-255 range"):
            parse_gpl(gpl)

    def test_raises_on_negative_rgb(self, tmp_path: Path) -> None:
        gpl = tmp_path / "neg.gpl"
        gpl.write_text("GIMP Palette\nName: Neg\n-1 128 128\tNegative\n")
        with pytest.raises(ValueError, match="out of 0-255 range"):
            parse_gpl(gpl)

    def test_parses_ramon_palette(self) -> None:
        ramon_gpl = PROJECT_ROOT / "assets" / "palettes" / "ramon.gpl"
        if not ramon_gpl.exists():
            pytest.skip("ramon.gpl not available")
        colors = parse_gpl(ramon_gpl)
        assert len(colors) == 15
        assert colors.dtype == np.uint8


class TestRgbToLab:
    """Tests for RGB-to-CIELAB conversion."""

    def test_black_has_zero_lightness(self) -> None:
        lab = rgb_to_lab(np.array([[0, 0, 0]], dtype=np.uint8))
        assert lab[0, 0] == pytest.approx(0.0, abs=0.01)

    def test_white_has_high_lightness(self) -> None:
        lab = rgb_to_lab(np.array([[255, 255, 255]], dtype=np.uint8))
        assert lab[0, 0] == pytest.approx(100.0, abs=0.5)

    def test_pure_red_positive_a(self) -> None:
        lab = rgb_to_lab(np.array([[255, 0, 0]], dtype=np.uint8))
        assert lab[0, 1] > 0  # a* should be positive for red

    def test_batch_conversion(self) -> None:
        rgb = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
        lab = rgb_to_lab(rgb)
        assert lab.shape == (3, 3)
        # All should have different L* values
        assert not np.allclose(lab[0, 0], lab[1, 0])

    def test_2d_image_conversion(self) -> None:
        rgb = np.zeros((4, 4, 3), dtype=np.uint8)
        rgb[0, 0] = [255, 0, 0]
        rgb[1, 1] = [0, 255, 0]
        lab = rgb_to_lab(rgb)
        assert lab.shape == (4, 4, 3)


class TestCleanAlpha:
    """Tests for alpha channel cleanup."""

    def test_fully_opaque_unchanged(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        result = clean_alpha(rgba)
        assert np.all(result[:, :, 3] == 255)

    def test_fully_transparent_unchanged(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        result = clean_alpha(rgba)
        assert np.all(result[:, :, 3] == 0)

    def test_semi_transparent_above_threshold_becomes_opaque(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 200
        result = clean_alpha(rgba, threshold=128)
        assert np.all(result[:, :, 3] == 255)

    def test_semi_transparent_below_threshold_becomes_transparent(self) -> None:
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 50
        result = clean_alpha(rgba, threshold=128)
        assert np.all(result[:, :, 3] == 0)

    def test_zeros_rgb_on_transparent_pixels(self) -> None:
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, :3] = [200, 100, 50]  # Non-zero RGB
        rgba[:, :, 3] = 50  # Below threshold -> transparent
        result = clean_alpha(rgba, threshold=128)
        assert np.all(result[:, :, 3] == 0)
        # RGB should be zeroed out (no "dirty alpha")
        assert np.all(result[:, :, :3] == 0)

    def test_does_not_modify_original(self) -> None:
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 100
        original_copy = rgba.copy()
        clean_alpha(rgba)
        np.testing.assert_array_equal(rgba, original_copy)


class TestSnapToPalette:
    """Tests for palette snapping."""

    def test_exact_palette_colors_unchanged(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((2, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        for i, color in enumerate(palette):
            rgba[0, i, :3] = color
            rgba[1, i, :3] = color
        result = snap_to_palette(rgba, palette)
        for i, color in enumerate(palette):
            np.testing.assert_array_equal(result[0, i, :3], color)

    def test_near_red_snaps_to_red(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((1, 1, 4), dtype=np.uint8)
        rgba[0, 0] = [240, 10, 10, 255]  # Near red
        result = snap_to_palette(rgba, palette)
        np.testing.assert_array_equal(result[0, 0, :3], [255, 0, 0])

    def test_transparent_pixels_untouched(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, :3] = 128  # Mid gray
        rgba[:, :, 3] = 0  # All transparent
        result = snap_to_palette(rgba, palette)
        np.testing.assert_array_equal(result[:, :, :3], rgba[:, :, :3])

    def test_dark_pixels_snap_to_darkest(self) -> None:
        palette = np.array([
            [200, 100, 50],
            [30, 20, 15],   # Darkest
            [150, 80, 40],
        ], dtype=np.uint8)
        rgba = np.zeros((1, 1, 4), dtype=np.uint8)
        rgba[0, 0] = [10, 8, 5, 255]  # Very dark pixel
        result = snap_to_palette(rgba, palette)
        np.testing.assert_array_equal(result[0, 0, :3], [30, 20, 15])

    def test_all_opaque_get_palette_colors(self) -> None:
        palette = _make_test_palette()
        # Random-ish colors
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[0, :, :3] = [200, 30, 30]
        rgba[1, :, :3] = [30, 200, 30]
        rgba[2, :, :3] = [30, 30, 200]
        rgba[3, :, :3] = [128, 128, 128]
        result = snap_to_palette(rgba, palette)
        # Every opaque pixel should be a palette color
        palette_set = set(map(tuple, palette.tolist()))
        opaque = result[:, :, 3] == 255
        result_colors = set(map(tuple, result[:, :, :3][opaque].tolist()))
        assert result_colors.issubset(palette_set)


class TestEnforceColorLimit:
    """Tests for color count enforcement."""

    def test_within_limit_unchanged(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((2, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, 0, :3] = [255, 0, 0]
        rgba[:, 1, :3] = [0, 255, 0]
        rgba[:, 2, :3] = [0, 0, 255]
        result = enforce_color_limit(rgba, palette, max_colors=5)
        np.testing.assert_array_equal(result, rgba)

    def test_merges_when_exceeded(self) -> None:
        palette = _make_test_palette()
        # Create image with many slightly different colors
        rgba = np.zeros((1, 20, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        for i in range(20):
            rgba[0, i, :3] = [min(255, 200 + i), i * 3, i * 2]
        result = enforce_color_limit(rgba, palette, max_colors=3)
        opaque = result[:, :, 3] == 255
        unique = np.unique(result[:, :, :3][opaque], axis=0)
        assert len(unique) <= 3

    def test_transparent_not_counted(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((2, 3, 4), dtype=np.uint8)
        # Only 1 opaque pixel
        rgba[0, 0] = [255, 0, 0, 255]
        result = enforce_color_limit(rgba, palette, max_colors=1)
        opaque = result[:, :, 3] == 255
        unique = np.unique(result[:, :, :3][opaque], axis=0)
        assert len(unique) <= 1


class TestComputeStats:
    """Tests for stats computation."""

    def test_no_changes_zero_pixels_changed(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :] = [255, 0, 0, 255]
        stats = compute_stats(rgba, rgba, palette)
        assert stats["pixels_changed"] == 0
        assert stats["colors_before"] == 1
        assert stats["colors_after"] == 1

    def test_counts_semi_transparent(self) -> None:
        palette = _make_test_palette()
        original = np.zeros((3, 3, 4), dtype=np.uint8)
        original[:, :, 3] = 100  # Semi-transparent
        cleaned = original.copy()
        cleaned[:, :, 3] = 0  # Made fully transparent
        stats = compute_stats(original, cleaned, palette)
        assert stats["semi_transparent_fixed"] == 9


class TestCleanSprite:
    """Integration tests for the full pipeline."""

    def test_full_pipeline(self) -> None:
        palette = np.array([
            [255, 0, 0],
            [0, 0, 255],
            [0, 0, 0],
        ], dtype=np.uint8)
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        # Semi-transparent near-red
        rgba[0, :, :] = [240, 10, 10, 200]
        # Opaque near-blue
        rgba[1, :, :] = [10, 10, 240, 255]
        # Semi-transparent below threshold
        rgba[2, :, :] = [100, 100, 100, 50]
        # Fully transparent
        rgba[3, :, :] = [0, 0, 0, 0]

        result = clean_sprite(rgba, palette)

        # Row 0: was semi-transparent >= 128, snapped to opaque, color -> red
        assert np.all(result[0, :, 3] == 255)
        np.testing.assert_array_equal(result[0, 0, :3], [255, 0, 0])

        # Row 1: was opaque, color -> blue
        assert np.all(result[1, :, 3] == 255)
        np.testing.assert_array_equal(result[1, 0, :3], [0, 0, 255])

        # Row 2: was semi-transparent < 128, snapped to transparent
        assert np.all(result[2, :, 3] == 0)

        # Row 3: stays transparent
        assert np.all(result[3, :, 3] == 0)

    def test_preserves_transparency(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        # Only center pixel is opaque
        rgba[2, 2] = [200, 50, 50, 255]
        result = clean_sprite(rgba, palette)
        assert result[2, 2, 3] == 255
        assert np.sum(result[:, :, 3] == 255) == 1


class TestResolveOutputPath:
    """Tests for output path resolution."""

    def test_default_adds_cleaned_suffix(self) -> None:
        p = resolve_output_path(Path("/foo/bar/idle.png"), None)
        assert p == Path("/foo/bar/idle_cleaned.png")

    def test_explicit_output_used(self) -> None:
        p = resolve_output_path(Path("/foo/idle.png"), Path("/out/result.png"))
        assert p == Path("/out/result.png")


class TestResolvePalettePath:
    """Tests for palette path resolution."""

    def test_resolves_to_palettes_dir(self) -> None:
        p = resolve_palette_path("ramon")
        assert p.name == "ramon.gpl"
        assert "palettes" in str(p)


class TestCli:
    """Tests for the CLI entry point."""

    def test_missing_input_returns_error(self) -> None:
        exit_code = main(["nonexistent.png", "--palette", "ramon"])
        assert exit_code == 1

    def test_missing_palette_returns_error(self, tmp_path: Path) -> None:
        img_path = tmp_path / "test.png"
        img = Image.fromarray(np.zeros((4, 4, 4), dtype=np.uint8), "RGBA")
        img.save(str(img_path))
        exit_code = main([str(img_path), "--palette", "nonexistent_palette_xyz"])
        assert exit_code == 1

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        # Create a test image
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[:, :] = [200, 50, 50, 255]
        img_path = tmp_path / "test.png"
        Image.fromarray(rgba, "RGBA").save(str(img_path))

        # Create a test palette
        gpl_dir = tmp_path / "assets" / "palettes"
        gpl_dir.mkdir(parents=True)
        _make_gpl_file(gpl_dir / "test.gpl", [(255, 0, 0), (0, 0, 0)])

        # Patch PROJECT_ROOT for this test
        import tools.clean_sprites as mod
        original_root = mod.PROJECT_ROOT
        mod.PROJECT_ROOT = tmp_path
        try:
            exit_code = main([str(img_path), "--palette", "test", "--dry-run", "--verbose"])
        finally:
            mod.PROJECT_ROOT = original_root

        assert exit_code == 0
        assert not (tmp_path / "test_cleaned.png").exists()

    def test_writes_output(self, tmp_path: Path) -> None:
        # Create a test image
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[:, :] = [200, 50, 50, 255]
        img_path = tmp_path / "test.png"
        Image.fromarray(rgba, "RGBA").save(str(img_path))

        # Create a test palette
        gpl_dir = tmp_path / "assets" / "palettes"
        gpl_dir.mkdir(parents=True)
        _make_gpl_file(gpl_dir / "test.gpl", [(255, 0, 0), (0, 0, 0)])

        import tools.clean_sprites as mod
        original_root = mod.PROJECT_ROOT
        mod.PROJECT_ROOT = tmp_path
        try:
            exit_code = main([str(img_path), "--palette", "test"])
        finally:
            mod.PROJECT_ROOT = original_root

        assert exit_code == 0
        out_path = tmp_path / "test_cleaned.png"
        assert out_path.exists()
        result = np.array(Image.open(out_path))
        np.testing.assert_array_equal(result[0, 0, :3], [255, 0, 0])
