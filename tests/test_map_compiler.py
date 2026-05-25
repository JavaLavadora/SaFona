"""Tests for the map auto-compiler (sa_fona/level/map_compiler.py)."""

from __future__ import annotations

import json
import os
import textwrap
import time
from pathlib import Path

import pytest

from sa_fona.level.map_compiler import compile_all_maps, compile_map_file


# ── Helpers ──────────────────────────────────────────────────────────

MINIMAL_MAP = textwrap.dedent("""\
    // Test
    ..P
    ###
""")

MINIMAL_YAML = textwrap.dedent("""\
    metadata:
      world: 0
      level: 0
      name: "Test"
      name_en: "Test"
      music_slot: "none"
      difficulty: 0
      tileset: "test"
      background: "none"
    enemies: []
    pickups: []
    breakables: []
    triggers: []
    secrets: []
    parallax: {}
""")


def _write_map_yaml(tmp_path: Path, stem: str = "test_level") -> tuple[Path, Path]:
    """Write minimal .map and .yaml files and return their paths."""
    map_path = tmp_path / f"{stem}.map"
    yaml_path = tmp_path / f"{stem}.yaml"
    map_path.write_text(MINIMAL_MAP, encoding="utf-8")
    yaml_path.write_text(MINIMAL_YAML, encoding="utf-8")
    return map_path, yaml_path


# ── compile_map_file ────────────────────────────────────────────────


class TestCompileMapFile:
    """Tests for single-file compilation."""

    def test_creates_json(self, tmp_path):
        """Compiling a .map + .yaml pair creates a .json file."""
        map_path, _ = _write_map_yaml(tmp_path)
        result = compile_map_file(map_path)
        assert result is True

        json_path = map_path.with_suffix(".json")
        assert json_path.exists()

        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["metadata"]["name"] == "Test"
        assert data["dimensions"]["width"] == 3
        assert data["dimensions"]["height"] == 2

    def test_skips_when_up_to_date(self, tmp_path):
        """Does not recompile if .json is newer than sources."""
        map_path, _ = _write_map_yaml(tmp_path)
        compile_map_file(map_path)

        # Second call should skip
        result = compile_map_file(map_path)
        assert result is False

    def test_recompiles_when_map_changes(self, tmp_path):
        """Recompiles when .map is newer than .json."""
        map_path, _ = _write_map_yaml(tmp_path)
        compile_map_file(map_path)

        json_path = map_path.with_suffix(".json")

        # Touch the .map file to make it newer
        # Use a small sleep to ensure mtime is different
        time.sleep(0.05)
        map_path.write_text(MINIMAL_MAP, encoding="utf-8")

        result = compile_map_file(map_path)
        assert result is True

    def test_recompiles_when_yaml_changes(self, tmp_path):
        """Recompiles when .yaml is newer than .json."""
        map_path, yaml_path = _write_map_yaml(tmp_path)
        compile_map_file(map_path)

        # Touch the .yaml file
        time.sleep(0.05)
        yaml_path.write_text(MINIMAL_YAML, encoding="utf-8")

        result = compile_map_file(map_path)
        assert result is True

    def test_skips_missing_yaml(self, tmp_path):
        """Skips gracefully if .yaml file is missing."""
        map_path = tmp_path / "no_yaml.map"
        map_path.write_text(MINIMAL_MAP, encoding="utf-8")

        result = compile_map_file(map_path)
        assert result is False

    def test_json_content_is_valid(self, tmp_path):
        """Generated JSON has expected structural keys."""
        map_path, _ = _write_map_yaml(tmp_path)
        compile_map_file(map_path)

        json_path = map_path.with_suffix(".json")
        data = json.loads(json_path.read_text(encoding="utf-8"))

        assert "metadata" in data
        assert "dimensions" in data
        assert "layers" in data
        assert "player_spawn" in data
        assert "companion_spawn" in data
        assert "entities" in data
        assert "triggers" in data


# ── compile_all_maps ────────────────────────────────────────────────


class TestCompileAllMaps:
    """Tests for bulk compilation."""

    def test_compiles_all_map_files(self, tmp_path):
        """Compiles all .map files found in subdirectories."""
        # Create two levels in subdirectories
        (tmp_path / "world1").mkdir()
        (tmp_path / "world2").mkdir()

        map1 = tmp_path / "world1" / "level_1.map"
        yaml1 = tmp_path / "world1" / "level_1.yaml"
        map1.write_text(MINIMAL_MAP, encoding="utf-8")
        yaml1.write_text(MINIMAL_YAML, encoding="utf-8")

        map2 = tmp_path / "world2" / "level_2.map"
        yaml2 = tmp_path / "world2" / "level_2.yaml"
        map2.write_text(MINIMAL_MAP, encoding="utf-8")
        yaml2.write_text(MINIMAL_YAML, encoding="utf-8")

        count = compile_all_maps(tmp_path)
        assert count == 2

        assert (tmp_path / "world1" / "level_1.json").exists()
        assert (tmp_path / "world2" / "level_2.json").exists()

    def test_returns_zero_when_up_to_date(self, tmp_path):
        """Returns 0 when all levels are already compiled."""
        _write_map_yaml(tmp_path)
        compile_all_maps(tmp_path)

        count = compile_all_maps(tmp_path)
        assert count == 0

    def test_nonexistent_directory(self, tmp_path):
        """Returns 0 for a nonexistent directory."""
        count = compile_all_maps(tmp_path / "nonexistent")
        assert count == 0

    def test_empty_directory(self, tmp_path):
        """Returns 0 for a directory with no .map files."""
        count = compile_all_maps(tmp_path)
        assert count == 0

    def test_handles_compile_error_gracefully(self, tmp_path):
        """Continues past files with errors without crashing."""
        # Write a valid level
        _write_map_yaml(tmp_path, "good_level")

        # Write a broken .map file (no player spawn)
        bad_map = tmp_path / "bad_level.map"
        bad_yaml = tmp_path / "bad_level.yaml"
        bad_map.write_text("...\n###\n", encoding="utf-8")
        bad_yaml.write_text(MINIMAL_YAML, encoding="utf-8")

        # Should compile the good one and skip the bad one
        count = compile_all_maps(tmp_path)
        assert count == 1
        assert (tmp_path / "good_level.json").exists()
        assert not (tmp_path / "bad_level.json").exists()


# ── Frozen mode (PyInstaller) ─────────────────────────────────────


def test_compile_all_maps_skips_in_frozen_mode(tmp_path):
    """In frozen mode, compile_all_maps returns 0 immediately."""
    import sys
    from unittest.mock import patch

    # Create a fake .map file to prove it gets skipped
    levels_dir = tmp_path / "levels"
    levels_dir.mkdir()
    (levels_dir / "test.map").write_text("test")

    with patch.object(sys, 'frozen', True, create=True), \
         patch('sa_fona.level.map_compiler.compile_map_file') as mock_compile:
        result = compile_all_maps(levels_dir)

    assert result == 0
    mock_compile.assert_not_called()
