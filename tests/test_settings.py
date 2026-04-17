"""Tests for sa_fona.config.settings."""

from pathlib import Path

from sa_fona.config.settings import (
    ASSETS_DIR,
    BASE_HEIGHT,
    BASE_WIDTH,
    COLORS,
    DATA_DIR,
    FPS,
    GAME_TITLE,
    PACKAGE_DIR,
    SAVES_DIR,
    WINDOW_SCALE,
)


class TestWindowConstants:
    """Verify window and display constants."""

    def test_game_title(self) -> None:
        assert GAME_TITLE == "Sa Fona"

    def test_base_resolution(self) -> None:
        assert BASE_WIDTH == 384
        assert BASE_HEIGHT == 216

    def test_window_scale(self) -> None:
        assert WINDOW_SCALE == 3

    def test_fps(self) -> None:
        assert FPS == 60


class TestColors:
    """Verify the color palette."""

    def test_required_colors_present(self) -> None:
        expected_keys = {"BLACK", "WHITE", "BLUE", "RED", "GREY", "YELLOW", "GREEN"}
        assert expected_keys.issubset(COLORS.keys())

    def test_black(self) -> None:
        assert COLORS["BLACK"] == (0, 0, 0)

    def test_white(self) -> None:
        assert COLORS["WHITE"] == (255, 255, 255)

    def test_color_tuples_have_three_components(self) -> None:
        for name, rgb in COLORS.items():
            assert len(rgb) == 3, f"{name} should have 3 components"
            assert all(0 <= c <= 255 for c in rgb), f"{name} out of 0-255 range"


class TestPaths:
    """Verify filesystem path constants."""

    def test_paths_are_pathlib(self) -> None:
        assert isinstance(PACKAGE_DIR, Path)
        assert isinstance(DATA_DIR, Path)
        assert isinstance(ASSETS_DIR, Path)
        assert isinstance(SAVES_DIR, Path)

    def test_data_dir_exists(self) -> None:
        assert DATA_DIR.is_dir(), f"DATA_DIR should exist: {DATA_DIR}"

    def test_data_dir_is_child_of_package(self) -> None:
        assert DATA_DIR.parent == PACKAGE_DIR
