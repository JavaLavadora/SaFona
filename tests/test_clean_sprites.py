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
    _AMBIGUITY_RATIO_THRESHOLD,
    add_outline,
    clean_alpha,
    clean_sprite,
    compute_stats,
    enforce_color_limit,
    main,
    parse_gpl,
    remove_stray_pixels,
    resolve_ambiguous_snaps,
    resolve_output_path,
    resolve_palette_path,
    rgb_to_lab,
    snap_to_palette,
    snap_to_palette_with_ambiguity,
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


class TestSnapToPaletteWithAmbiguity:
    """Tests for palette snapping with ambiguity data."""

    def test_returns_ambiguity_info_dict(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [255, 0, 0]
        result, info = snap_to_palette_with_ambiguity(rgba, palette)
        assert "is_ambiguous" in info
        assert "top2_indices" in info
        assert "top2_distances" in info
        assert info["is_ambiguous"].shape == (3, 3)
        assert info["top2_indices"].shape == (3, 3, 2)
        assert info["top2_distances"].shape == (3, 3, 2)

    def test_exact_palette_match_not_ambiguous(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((1, 1, 4), dtype=np.uint8)
        rgba[0, 0] = [255, 0, 0, 255]  # Exact red
        _, info = snap_to_palette_with_ambiguity(rgba, palette)
        assert not info["is_ambiguous"][0, 0]

    def test_equidistant_pixel_is_ambiguous(self) -> None:
        """A pixel equidistant between two palette colors should be ambiguous."""
        # Two palette colors fairly close, and a pixel between them
        palette = np.array([
            [200, 100, 50],   # Color A
            [180, 110, 60],   # Color B (close to A)
            [0, 0, 0],        # Black (far away)
        ], dtype=np.uint8)
        # A pixel midway between A and B
        rgba = np.zeros((1, 1, 4), dtype=np.uint8)
        rgba[0, 0] = [190, 105, 55, 255]
        _, info = snap_to_palette_with_ambiguity(rgba, palette)
        # The ratio should be high (close to 1.0) for this midpoint pixel
        assert info["is_ambiguous"][0, 0]

    def test_transparent_pixels_not_ambiguous(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((2, 2, 4), dtype=np.uint8)
        rgba[:, :, 3] = 0  # All transparent
        _, info = snap_to_palette_with_ambiguity(rgba, palette)
        assert not np.any(info["is_ambiguous"])


class TestResolveAmbiguousSnaps:
    """Tests for context-aware ambiguous snap resolution."""

    def _make_ambiguity_info(
        self,
        shape: tuple[int, int],
        ambiguous_pixels: list[tuple[int, int, int, int]],
        palette_idx_map: np.ndarray | None = None,
    ) -> dict:
        """Helper to build ambiguity_info dicts for testing.

        Args:
            shape: (H, W) of the image.
            ambiguous_pixels: list of (y, x, idx_1st, idx_2nd) tuples.
            palette_idx_map: optional full palette index map for top2_indices[:,:,0].
        """
        h, w = shape
        is_ambiguous = np.zeros((h, w), dtype=bool)
        top2_indices = np.zeros((h, w, 2), dtype=np.intp)
        top2_distances = np.zeros((h, w, 2), dtype=np.float64)

        if palette_idx_map is not None:
            top2_indices[:, :, 0] = palette_idx_map

        for y, x, idx1, idx2 in ambiguous_pixels:
            is_ambiguous[y, x] = True
            top2_indices[y, x, 0] = idx1
            top2_indices[y, x, 1] = idx2

        return {
            "is_ambiguous": is_ambiguous,
            "top2_indices": top2_indices,
            "top2_distances": top2_distances,
        }

    def test_ambiguous_pixel_resolves_to_majority_neighbor(self) -> None:
        """An ambiguous pixel surrounded by one color gets resolved to it."""
        palette = np.array([
            [200, 150, 120],  # 0: skin
            [220, 50, 50],    # 1: red sash
            [0, 0, 0],        # 2: black
        ], dtype=np.uint8)

        # 3x3 image: center pixel is ambiguous between skin(0) and red(1),
        # all 8 neighbors are skin(0).
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = palette[0]          # All skin
        rgba[1, 1, :3] = palette[1]          # Center snapped to red (wrong)

        # palette_idx_map: all are 0 (skin), center is 1 (red)
        idx_map = np.zeros((3, 3), dtype=np.intp)
        idx_map[1, 1] = 1

        info = self._make_ambiguity_info(
            (3, 3),
            ambiguous_pixels=[(1, 1, 1, 0)],  # snapped to red, 2nd choice=skin
            palette_idx_map=idx_map,
        )

        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        # Should have been resolved to skin
        np.testing.assert_array_equal(result[1, 1, :3], palette[0])
        assert count == 1

    def test_non_ambiguous_pixels_never_changed(self) -> None:
        """Pixels not marked ambiguous must remain untouched."""
        palette = np.array([
            [200, 150, 120],  # 0: skin
            [220, 50, 50],    # 1: red
            [0, 0, 0],        # 2: black
        ], dtype=np.uint8)

        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = palette[0]
        rgba[1, 1, :3] = palette[1]  # This pixel is red but NOT ambiguous

        idx_map = np.zeros((3, 3), dtype=np.intp)
        idx_map[1, 1] = 1

        info = self._make_ambiguity_info(
            (3, 3),
            ambiguous_pixels=[],  # No ambiguous pixels
            palette_idx_map=idx_map,
        )

        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        # Red pixel stays red — not ambiguous, so never touched
        np.testing.assert_array_equal(result[1, 1, :3], palette[1])
        assert count == 0

    def test_edge_pixel_fewer_neighbors(self) -> None:
        """Corner pixel with only 3 neighbors still resolves correctly."""
        palette = np.array([
            [200, 150, 120],  # 0: skin
            [220, 50, 50],    # 1: red
        ], dtype=np.uint8)

        # 2x2 image: top-left is ambiguous, other 3 are skin
        rgba = np.zeros((2, 2, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = palette[0]
        rgba[0, 0, :3] = palette[1]  # Snapped to red

        idx_map = np.zeros((2, 2), dtype=np.intp)
        idx_map[0, 0] = 1

        info = self._make_ambiguity_info(
            (2, 2),
            ambiguous_pixels=[(0, 0, 1, 0)],
            palette_idx_map=idx_map,
        )

        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        # 3 neighbors are all skin(0), so should resolve to skin
        np.testing.assert_array_equal(result[0, 0, :3], palette[0])
        assert count == 1

    def test_ambiguous_pixel_keeps_current_on_tie(self) -> None:
        """When neighbor votes are tied, the current (1st-nearest) wins."""
        palette = np.array([
            [200, 150, 120],  # 0: skin
            [220, 50, 50],    # 1: red
            [0, 0, 0],        # 2: black (filler)
        ], dtype=np.uint8)

        # 1x3 row: left=skin, center=red(ambiguous), right=skin
        # But only 2 neighbors (left, right) — one skin, but let's make it
        # a true tie: left=red, right=skin
        rgba = np.zeros((1, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[0, 0, :3] = palette[1]  # red
        rgba[0, 1, :3] = palette[1]  # red (ambiguous)
        rgba[0, 2, :3] = palette[0]  # skin

        idx_map = np.array([[1, 1, 0]], dtype=np.intp)

        info = self._make_ambiguity_info(
            (1, 3),
            ambiguous_pixels=[(0, 1, 1, 0)],  # 1st=red, 2nd=skin
            palette_idx_map=idx_map,
        )

        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        # 1 neighbor is red, 1 is skin -> tie -> keep current (red)
        np.testing.assert_array_equal(result[0, 1, :3], palette[1])
        assert count == 0

    def test_no_ambiguous_pixels_returns_unchanged(self) -> None:
        """When no pixels are ambiguous, result is identical and count is 0."""
        palette = _make_test_palette()
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = palette[0]

        info = self._make_ambiguity_info((4, 4), ambiguous_pixels=[])
        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        np.testing.assert_array_equal(result, rgba)
        assert count == 0

    def test_all_transparent_returns_unchanged(self) -> None:
        """Fully transparent image produces no changes."""
        palette = _make_test_palette()
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        info = self._make_ambiguity_info((3, 3), ambiguous_pixels=[])
        result, count = resolve_ambiguous_snaps(rgba, info, palette)
        np.testing.assert_array_equal(result, rgba)
        assert count == 0


class TestRemoveStrayPixels:
    """Tests for stray pixel cleanup."""

    def test_isolated_pixel_replaced_by_majority_neighbor(self) -> None:
        """A single pixel surrounded by uniform color gets replaced."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]  # All skin
        rgba[1, 1, :3] = [220, 50, 50]    # Center is red (stray)

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result[1, 1, :3], [200, 150, 120])
        assert count == 1

    def test_pixel_with_same_color_neighbor_left_alone(self) -> None:
        """A pixel sharing color with at least one neighbor is not stray."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]  # All skin
        # Two adjacent red pixels — neither is isolated
        rgba[1, 1, :3] = [220, 50, 50]
        rgba[1, 2, :3] = [220, 50, 50]

        result, count = remove_stray_pixels(rgba)
        # Both red pixels should remain
        np.testing.assert_array_equal(result[1, 1, :3], [220, 50, 50])
        np.testing.assert_array_equal(result[1, 2, :3], [220, 50, 50])
        assert count == 0

    def test_two_pixel_cluster_fixed_in_multiple_iterations(self) -> None:
        """A 2-pixel cluster of wrong color surrounded by another color.

        On the first pass, neither pixel is isolated (they share a neighbor).
        But once one is fixed, the other becomes isolated in the next pass.
        Actually, because they are processed from a snapshot within a pass,
        both still see each other as neighbors in pass 1. After pass 1,
        neither is fixed. We need to verify the behavior: a 2-pixel cluster
        where neither pixel is isolated won't be touched at all. This test
        verifies that a 2-pixel cluster is left alone (they are not stray).
        """
        # 5x5 image: all skin except two adjacent red pixels
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]
        rgba[2, 2, :3] = [220, 50, 50]
        rgba[2, 3, :3] = [220, 50, 50]

        result, count = remove_stray_pixels(rgba)
        # Two adjacent red pixels share a neighbor, so neither is stray
        np.testing.assert_array_equal(result[2, 2, :3], [220, 50, 50])
        np.testing.assert_array_equal(result[2, 3, :3], [220, 50, 50])
        assert count == 0

    def test_diagonal_pair_not_stray(self) -> None:
        """Two diagonally adjacent same-color pixels are not stray (8-connected)."""
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]
        rgba[1, 1, :3] = [220, 50, 50]
        rgba[2, 2, :3] = [220, 50, 50]

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result[1, 1, :3], [220, 50, 50])
        np.testing.assert_array_equal(result[2, 2, :3], [220, 50, 50])
        assert count == 0

    def test_multi_iteration_chain(self) -> None:
        """A chain of isolated single pixels, each revealed after the previous is fixed.

        Layout (5x1 row):  skin, red, blue, green, skin
        - red has neighbors skin and blue — no same-color neighbor -> stray
        - blue has neighbors red and green — no same-color neighbor -> stray
        - green has neighbors blue and skin — no same-color neighbor -> stray

        Pass 1 (from snapshot): all three are isolated.
        red -> majority of {skin, blue} = tie, pick first alphabetically by count;
        actually both have count 1, so max() returns whichever comes first.
        All three get fixed to some neighbor color.
        """
        rgba = np.zeros((1, 5, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[0, 0, :3] = [200, 150, 120]  # skin
        rgba[0, 1, :3] = [220, 50, 50]    # red (isolated)
        rgba[0, 2, :3] = [0, 0, 255]      # blue (isolated)
        rgba[0, 3, :3] = [0, 255, 0]      # green (isolated)
        rgba[0, 4, :3] = [200, 150, 120]  # skin

        result, count = remove_stray_pixels(rgba)
        # After enough iterations, all middle pixels should converge.
        # The key assertion: count > 0 (strays were fixed)
        assert count >= 3
        # All pixels should end up as some consistent color (likely skin since
        # the endpoints are skin and they anchor the chain)

    def test_border_pixel_with_fewer_neighbors(self) -> None:
        """A corner pixel with only 3 neighbors still gets fixed if isolated."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]  # All skin
        rgba[0, 0, :3] = [220, 50, 50]    # Top-left corner is red (stray)

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result[0, 0, :3], [200, 150, 120])
        assert count == 1

    def test_edge_pixel_with_fewer_neighbors(self) -> None:
        """An edge pixel (not corner) with 5 neighbors gets fixed if isolated."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]  # All skin
        rgba[0, 1, :3] = [220, 50, 50]    # Top-center edge is red (stray)

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result[0, 1, :3], [200, 150, 120])
        assert count == 1

    def test_transparent_neighbors_ignored(self) -> None:
        """Transparent neighbors are not counted — only opaque ones matter."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        # Center is opaque red, surrounded by mix of transparent and opaque skin
        rgba[1, 1] = [220, 50, 50, 255]   # Center: red, opaque
        rgba[0, 0] = [200, 150, 120, 255]  # Top-left: skin, opaque
        rgba[0, 1] = [200, 150, 120, 255]  # Top: skin, opaque
        # All other neighbors are transparent (default zeros)

        result, count = remove_stray_pixels(rgba)
        # Red pixel has only skin opaque neighbors -> isolated -> fixed
        np.testing.assert_array_equal(result[1, 1, :3], [200, 150, 120])
        assert count == 1

    def test_pixel_with_no_opaque_neighbors_unchanged(self) -> None:
        """A pixel surrounded entirely by transparent pixels is left alone."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[1, 1] = [220, 50, 50, 255]  # Only opaque pixel

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result[1, 1, :3], [220, 50, 50])
        assert count == 0

    def test_no_strays_returns_unchanged(self) -> None:
        """An image with no stray pixels is returned unchanged."""
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]  # Uniform color

        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result, rgba)
        assert count == 0

    def test_all_transparent_returns_unchanged(self) -> None:
        """Fully transparent image produces no changes."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        result, count = remove_stray_pixels(rgba)
        np.testing.assert_array_equal(result, rgba)
        assert count == 0

    def test_majority_color_wins(self) -> None:
        """When a stray pixel has mixed neighbors, the most common color wins."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        # Surround center with 5 skin pixels and 3 blue pixels
        rgba[0, :, :3] = [200, 150, 120]  # 3 skin across top
        rgba[1, 0, :3] = [200, 150, 120]  # skin left
        rgba[1, 2, :3] = [200, 150, 120]  # skin right
        rgba[2, 0, :3] = [0, 0, 255]      # blue bottom-left
        rgba[2, 1, :3] = [0, 0, 255]      # blue bottom-center
        rgba[2, 2, :3] = [0, 0, 255]      # blue bottom-right
        rgba[1, 1, :3] = [220, 50, 50]    # center is red (stray)

        result, count = remove_stray_pixels(rgba)
        # Skin has 5 neighbors vs blue's 3, so skin wins
        np.testing.assert_array_equal(result[1, 1, :3], [200, 150, 120])
        assert count == 1

    def test_max_iterations_respected(self) -> None:
        """The function does not exceed max_iterations passes."""
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[:, :, :3] = [200, 150, 120]
        rgba[1, 1, :3] = [220, 50, 50]  # Stray

        result, count = remove_stray_pixels(rgba, max_iterations=1)
        # Should fix in 1 iteration
        np.testing.assert_array_equal(result[1, 1, :3], [200, 150, 120])
        assert count == 1


class TestAddOutline:
    """Tests for the outline (contour) step."""

    def test_small_sprite_gets_outline(self) -> None:
        """A single opaque pixel gets outlined on all 4 sides."""
        palette = np.array([
            [200, 150, 120],  # Skin
            [32, 24, 16],     # Darkest
        ], dtype=np.uint8)

        # 3x3 image: only center pixel is opaque
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[1, 1] = [200, 150, 120, 255]

        result = add_outline(rgba, palette)

        # The 4-connected neighbors should now be opaque with the darkest color
        for y, x in [(0, 1), (2, 1), (1, 0), (1, 2)]:
            assert result[y, x, 3] == 255, f"Pixel ({y},{x}) should be opaque"
            np.testing.assert_array_equal(
                result[y, x, :3], [32, 24, 16],
                err_msg=f"Pixel ({y},{x}) should be darkest palette color",
            )

        # Diagonal neighbors should remain transparent (4-connected only)
        for y, x in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            assert result[y, x, 3] == 0, f"Diagonal ({y},{x}) should stay transparent"

    def test_outline_uses_darkest_palette_color(self) -> None:
        """Outline color is the one with lowest L* in CIELAB, not pure black."""
        palette = np.array([
            [255, 255, 255],  # White (high L*)
            [100, 200, 50],   # Green (mid L*)
            [40, 30, 20],     # Dark brown (lowest L*)
        ], dtype=np.uint8)

        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[1, 1] = [255, 255, 255, 255]

        result = add_outline(rgba, palette)

        # Outline should use dark brown, not pure black
        np.testing.assert_array_equal(result[0, 1, :3], [40, 30, 20])

    def test_interior_pixels_not_modified(self) -> None:
        """Opaque pixels that are not on the edge are left unchanged."""
        palette = np.array([
            [200, 150, 120],  # Skin
            [32, 24, 16],     # Darkest
        ], dtype=np.uint8)

        # 5x5 image: 3x3 block of opaque skin pixels in the center
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        for y in range(1, 4):
            for x in range(1, 4):
                rgba[y, x] = [200, 150, 120, 255]

        result = add_outline(rgba, palette)

        # Interior pixel (2,2) should still be skin
        np.testing.assert_array_equal(result[2, 2, :3], [200, 150, 120])
        assert result[2, 2, 3] == 255

        # All original opaque pixels should still be skin
        for y in range(1, 4):
            for x in range(1, 4):
                np.testing.assert_array_equal(result[y, x, :3], [200, 150, 120])

    def test_edge_of_image_pixels_outlined(self) -> None:
        """A sprite touching the image edge still gets outlined on available sides."""
        palette = np.array([
            [200, 150, 120],  # Skin
            [32, 24, 16],     # Darkest
        ], dtype=np.uint8)

        # 3x3 image: top-left pixel is opaque
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[0, 0] = [200, 150, 120, 255]

        result = add_outline(rgba, palette)

        # Only (1,0) and (0,1) are valid 4-connected transparent neighbors
        assert result[1, 0, 3] == 255
        np.testing.assert_array_equal(result[1, 0, :3], [32, 24, 16])
        assert result[0, 1, 3] == 255
        np.testing.assert_array_equal(result[0, 1, :3], [32, 24, 16])

        # Diagonal (1,1) should remain transparent
        assert result[1, 1, 3] == 0

    def test_no_outline_flag_disables_outline(self) -> None:
        """clean_sprite with outline=False produces no outline pixels."""
        palette = np.array([
            [200, 150, 120],  # Skin
            [32, 24, 16],     # Darkest
        ], dtype=np.uint8)

        # 5x5 image: center pixel is opaque
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[2, 2] = [200, 150, 120, 255]

        result_with, _, _ = clean_sprite(rgba, palette, outline=True)
        result_without, _, _ = clean_sprite(rgba, palette, outline=False)

        # With outline: should have more opaque pixels
        opaque_with = np.sum(result_with[:, :, 3] == 255)
        opaque_without = np.sum(result_without[:, :, 3] == 255)
        assert opaque_with > opaque_without
        assert opaque_without == 1  # Only the original pixel

    def test_fully_transparent_image_unchanged(self) -> None:
        """Outlining a fully transparent image produces no changes."""
        palette = np.array([[32, 24, 16], [200, 150, 120]], dtype=np.uint8)
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)

        result = add_outline(rgba, palette)
        np.testing.assert_array_equal(result, rgba)

    def test_does_not_modify_original(self) -> None:
        """add_outline returns a new array; input is not mutated."""
        palette = np.array([[200, 150, 120], [32, 24, 16]], dtype=np.uint8)
        rgba = np.zeros((3, 3, 4), dtype=np.uint8)
        rgba[1, 1] = [200, 150, 120, 255]
        original_copy = rgba.copy()

        add_outline(rgba, palette)
        np.testing.assert_array_equal(rgba, original_copy)

    def test_adjacent_opaque_pixels_share_outline(self) -> None:
        """Two adjacent opaque pixels share outline pixels between them."""
        palette = np.array([
            [200, 150, 120],  # Skin
            [32, 24, 16],     # Darkest
        ], dtype=np.uint8)

        # 5x5 image: two horizontally adjacent opaque pixels
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[2, 1] = [200, 150, 120, 255]
        rgba[2, 2] = [200, 150, 120, 255]

        result = add_outline(rgba, palette)

        # The pixel between them (2,1)-(2,2) is opaque already, not outline.
        # But above, below, left, and right of the pair should be outlined.
        for y, x in [(1, 1), (1, 2), (3, 1), (3, 2), (2, 0), (2, 3)]:
            assert result[y, x, 3] == 255, f"Pixel ({y},{x}) should be outlined"
            np.testing.assert_array_equal(result[y, x, :3], [32, 24, 16])


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
        # Row 0: semi-transparent near-red (alpha >= 128 -> opaque, color -> red)
        rgba[0, :, :] = [240, 10, 10, 200]
        # Row 1: opaque near-blue (color -> blue)
        rgba[1, :, :] = [10, 10, 240, 255]
        # Row 2: semi-transparent below threshold (alpha < 128 -> transparent)
        rgba[2, :, :] = [100, 100, 100, 50]
        # Row 3: fully transparent
        rgba[3, :, :] = [0, 0, 0, 0]

        # Test with outline disabled to verify core pipeline
        result, ambiguous_resolved, stray_fixed = clean_sprite(
            rgba, palette, outline=False,
        )

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

        assert isinstance(ambiguous_resolved, int)
        assert isinstance(stray_fixed, int)

    def test_full_pipeline_with_outline(self) -> None:
        """Full pipeline with outline enabled adds contour around opaque areas."""
        palette = np.array([
            [255, 0, 0],
            [0, 0, 255],
            [0, 0, 0],   # Darkest
        ], dtype=np.uint8)
        rgba = np.zeros((4, 4, 4), dtype=np.uint8)
        rgba[0, :, :] = [240, 10, 10, 200]   # -> opaque red
        rgba[1, :, :] = [10, 10, 240, 255]   # -> opaque blue
        rgba[2, :, :] = [100, 100, 100, 50]  # -> transparent
        rgba[3, :, :] = [0, 0, 0, 0]

        result, _, _ = clean_sprite(rgba, palette, outline=True)

        # Rows 0-1 are opaque; row 2 gets outline (adjacent to row 1)
        assert np.all(result[2, :, 3] == 255)
        np.testing.assert_array_equal(result[2, 0, :3], [0, 0, 0])

        # Row 3 stays transparent (not adjacent to opaque after outline)
        assert np.all(result[3, :, 3] == 0)

    def test_preserves_transparency(self) -> None:
        palette = _make_test_palette()
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        # Only center pixel is opaque
        rgba[2, 2] = [200, 50, 50, 255]

        # With outline disabled, only the original pixel remains opaque
        result, _, _ = clean_sprite(rgba, palette, outline=False)
        assert result[2, 2, 3] == 255
        assert np.sum(result[:, :, 3] == 255) == 1

    def test_preserves_transparency_with_outline(self) -> None:
        """With outline enabled, a single pixel gets 4 outline neighbors."""
        palette = _make_test_palette()
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[2, 2] = [200, 50, 50, 255]
        result, _, _ = clean_sprite(rgba, palette, outline=True)
        assert result[2, 2, 3] == 255
        # 1 original + 4 outline pixels (4-connected)
        assert np.sum(result[:, :, 3] == 255) == 5


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

    def test_no_outline_flag(self, tmp_path: Path) -> None:
        """--no-outline flag disables outline in CLI output."""
        # 5x5 image: single opaque pixel in the center
        rgba = np.zeros((5, 5, 4), dtype=np.uint8)
        rgba[2, 2] = [200, 50, 50, 255]
        img_path = tmp_path / "test.png"
        Image.fromarray(rgba, "RGBA").save(str(img_path))

        gpl_dir = tmp_path / "assets" / "palettes"
        gpl_dir.mkdir(parents=True)
        _make_gpl_file(gpl_dir / "test.gpl", [(255, 0, 0), (0, 0, 0)])

        import tools.clean_sprites as mod
        original_root = mod.PROJECT_ROOT
        mod.PROJECT_ROOT = tmp_path
        try:
            # With outline (default)
            out_with = tmp_path / "with_outline.png"
            main([str(img_path), "--palette", "test", "--output", str(out_with)])

            # Without outline
            out_without = tmp_path / "no_outline.png"
            main([str(img_path), "--palette", "test", "--no-outline",
                  "--output", str(out_without)])
        finally:
            mod.PROJECT_ROOT = original_root

        result_with = np.array(Image.open(out_with))
        result_without = np.array(Image.open(out_without))

        opaque_with = np.sum(result_with[:, :, 3] == 255)
        opaque_without = np.sum(result_without[:, :, 3] == 255)
        # With outline should have more opaque pixels (the outline)
        assert opaque_with > opaque_without
