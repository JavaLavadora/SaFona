"""Tests for the ASCII level editor tool (tools/map_to_json.py)."""

from __future__ import annotations

import json
import sys
import textwrap
import warnings
from pathlib import Path
from unittest import mock

import pytest

# Add tools/ to the path so we can import map_to_json
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from map_to_json import (
    CHAR_TO_TILE,
    MapParseError,
    YamlParseError,
    build_entities,
    build_level_json,
    detect_collision_types,
    load_yaml_metadata,
    main,
    make_empty_layer,
    parse_map_string,
)


# ── Grid parsing ──────────────────────────────────────────────────────


class TestParseMapString:
    """Tests for ASCII map grid parsing."""

    def test_basic_grid(self):
        """Parse a simple grid with air and solid tiles."""
        text = textwrap.dedent("""\
            ##.
            #P.
            ###
        """)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
        assert grid == [
            [1, 1, 0],
            [1, 0, 0],
            [1, 1, 1],
        ]

    def test_all_tile_types(self):
        """Parse a grid with every supported tile character."""
        text = ".#-XB\nP#-XB"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
        assert grid[0] == [0, 1, 10, 20, 30]
        assert grid[1] == [0, 1, 10, 20, 30]

    def test_spawn_detection_player(self):
        """Detect player spawn marker P."""
        text = "...\n.P.\n###"
        grid, spawns = parse_map_string(text)
        assert spawns["P"] == (1, 1)
        # P becomes air tile
        assert grid[1][1] == 0

    def test_spawn_detection_companion(self):
        """Detect companion spawn marker C."""
        text = "...\nCP.\n###"
        grid, spawns = parse_map_string(text)
        assert spawns["C"] == (0, 1)
        assert spawns["P"] == (1, 1)
        # Both become air
        assert grid[1][0] == 0
        assert grid[1][1] == 0

    def test_missing_player_spawn_raises(self):
        """Missing P marker is an error."""
        text = "...\n...\n###"
        with pytest.raises(MapParseError, match="Missing 'P'"):
            parse_map_string(text)

    def test_missing_companion_defaults(self):
        """Missing C marker defaults to 1 tile left of player with warning."""
        text = "...\n.P.\n###"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
            assert len(w) == 1
            assert "companion spawn" in str(w[0].message).lower()
        assert spawns["C"] == (0, 1)  # 1 left of (1, 1)

    def test_missing_companion_player_at_col0(self):
        """Missing C with player at column 0 clamps to 0."""
        text = "...\nP..\n###"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
        assert spawns["C"] == (0, 1)  # max(0, 0-1) = 0

    def test_comment_lines_ignored(self):
        """Lines starting with // are ignored."""
        text = "// This is a comment\n.P.\n###"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
        assert len(grid) == 2
        assert spawns["P"] == (1, 0)

    def test_leading_trailing_empty_lines_stripped(self):
        """Empty lines at start and end are stripped."""
        text = "\n\n.P.\n###\n\n"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            grid, spawns = parse_map_string(text)
        assert len(grid) == 2

    def test_mismatched_row_widths_raises(self):
        """Rows with different widths raise an error."""
        text = "##.\n#.\n###"
        with pytest.raises(MapParseError, match="Row width"):
            parse_map_string(text)

    def test_unknown_character_raises(self):
        """Unknown characters in the map raise an error."""
        text = "##Z\n...\n###"
        with pytest.raises(MapParseError, match="Unknown character 'Z'"):
            parse_map_string(text)

    def test_duplicate_player_spawn_raises(self):
        """Duplicate P markers raise an error."""
        text = "PP.\n...\n###"
        with pytest.raises(MapParseError, match="Duplicate 'P'"):
            parse_map_string(text)

    def test_empty_map_raises(self):
        """Empty map file raises an error."""
        text = "// just a comment\n\n"
        with pytest.raises(MapParseError, match="empty"):
            parse_map_string(text)

    def test_empty_line_in_middle_raises(self):
        """Empty line in the middle of grid data raises an error."""
        text = ".P.\n\n###"
        with pytest.raises(MapParseError, match="Empty line in the middle"):
            parse_map_string(text)


# ── YAML loading ──────────────────────────────────────────────────────


class TestLoadYamlMetadata:
    """Tests for YAML metadata parsing and validation."""

    def _write_yaml(self, tmp_path: Path, content: str) -> str:
        path = tmp_path / "test.yaml"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def test_valid_yaml(self, tmp_path):
        """Load a valid YAML file with all required fields."""
        yaml_content = textwrap.dedent("""\
            metadata:
              world: 1
              level: 1
              name: "Test Level"
              name_en: "Test Level EN"
              music_slot: "test_music"
              difficulty: 1
              tileset: "test_tileset"
              background: "test_bg"
            enemies: []
            pickups: []
            triggers: []
            secrets: []
            parallax: {}
        """)
        path = self._write_yaml(tmp_path, yaml_content)
        data = load_yaml_metadata(path)
        assert data["metadata"]["name"] == "Test Level"

    def test_missing_metadata_section_raises(self, tmp_path):
        """Missing metadata section raises an error."""
        path = self._write_yaml(tmp_path, "enemies: []\n")
        with pytest.raises(YamlParseError, match="Missing 'metadata'"):
            load_yaml_metadata(path)

    def test_missing_required_fields_raises(self, tmp_path):
        """Missing required metadata fields raises an error."""
        yaml_content = textwrap.dedent("""\
            metadata:
              world: 1
              level: 1
        """)
        path = self._write_yaml(tmp_path, yaml_content)
        with pytest.raises(YamlParseError, match="Missing required metadata"):
            load_yaml_metadata(path)

    def test_invalid_yaml_syntax_raises(self, tmp_path):
        """Invalid YAML syntax raises an error."""
        path = self._write_yaml(tmp_path, "  bad:\n: yaml: [{}")
        with pytest.raises(YamlParseError, match="YAML parse error"):
            load_yaml_metadata(path)

    def test_non_mapping_top_level_raises(self, tmp_path):
        """Non-dict top level raises an error."""
        path = self._write_yaml(tmp_path, "- just\n- a\n- list\n")
        with pytest.raises(YamlParseError, match="Expected a YAML mapping"):
            load_yaml_metadata(path)

    def test_optional_sections_missing(self, tmp_path):
        """Missing optional sections (enemies, pickups, etc.) are OK."""
        yaml_content = textwrap.dedent("""\
            metadata:
              world: 1
              level: 1
              name: "Test"
              name_en: "Test EN"
              music_slot: "m"
              difficulty: 1
              tileset: "t"
              background: "b"
        """)
        path = self._write_yaml(tmp_path, yaml_content)
        data = load_yaml_metadata(path)
        assert data.get("enemies") is None
        assert data.get("pickups") is None


# ── Collision types ───────────────────────────────────────────────────


class TestDetectCollisionTypes:
    """Tests for collision type detection."""

    def test_all_standard_categories_always_present(self):
        """All standard categories are included regardless of grid content."""
        grid = [[0, 0], [0, 0]]
        ct = detect_collision_types(grid)
        assert "solid" in ct
        assert "one_way" in ct
        assert "hazard" in ct
        assert "breakable_slam" in ct

    def test_solid_tiles(self):
        """Solid tile ID 1 is in the solid category."""
        grid = [[1, 0], [0, 1]]
        ct = detect_collision_types(grid)
        assert 1 in ct["solid"]


# ── Entity building ───────────────────────────────────────────────────


class TestBuildEntities:
    """Tests for entity list construction from YAML."""

    def test_pickups(self):
        """Pickups are converted to entity format."""
        yaml_data = {
            "pickups": [
                {"type": "stone", "x": 5, "y": 10, "value": 1},
                {"type": "heart", "x": 8, "y": 10, "value": 1},
            ],
            "enemies": [],
        }
        entities = build_entities(yaml_data)
        assert len(entities) == 2
        assert entities[0] == {
            "type": "pickup",
            "pickup_type": "stone",
            "x": 5,
            "y": 10,
            "value": 1,
        }

    def test_enemies(self):
        """Enemies are converted to entity format."""
        yaml_data = {
            "enemies": [{"type": "possessed_sheep", "x": 40, "y": 12}],
        }
        entities = build_entities(yaml_data)
        assert len(entities) == 1
        assert entities[0] == {
            "type": "enemy",
            "enemy_type": "possessed_sheep",
            "x": 40,
            "y": 12,
        }

    def test_breakables(self):
        """Breakables are converted to entity format."""
        yaml_data = {
            "breakables": [{"type": "breakable_pot", "x": 10, "y": 12}],
        }
        entities = build_entities(yaml_data)
        assert len(entities) == 1
        assert entities[0]["type"] == "breakable"
        assert entities[0]["breakable_type"] == "breakable_pot"

    def test_empty_sections(self):
        """Empty/missing sections produce no entities."""
        entities = build_entities({})
        assert entities == []

    def test_mixed_entities(self):
        """Mixed pickups, enemies, and breakables are all included."""
        yaml_data = {
            "pickups": [{"type": "stone", "x": 1, "y": 1, "value": 1}],
            "enemies": [{"type": "sheep", "x": 2, "y": 2}],
            "breakables": [{"type": "pot", "x": 3, "y": 3}],
        }
        entities = build_entities(yaml_data)
        assert len(entities) == 3


# ── JSON assembly ─────────────────────────────────────────────────────


class TestBuildLevelJson:
    """Tests for complete JSON structure assembly."""

    @pytest.fixture
    def basic_inputs(self):
        """Provide minimal valid inputs for level building."""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 1],
        ]
        spawns = {"P": (1, 1), "C": (0, 1)}
        yaml_data = {
            "metadata": {
                "world": 1,
                "level": 1,
                "name": "Test",
                "name_en": "Test EN",
                "music_slot": "test_music",
                "difficulty": 1,
                "tileset": "test_tileset",
                "background": "test_bg",
            },
            "enemies": [],
            "pickups": [],
            "breakables": [],
            "triggers": [],
            "secrets": [],
            "parallax": {},
        }
        return grid, spawns, yaml_data

    def test_dimensions(self, basic_inputs):
        """Dimensions match grid size."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert result["dimensions"] == {"width": 3, "height": 3}

    def test_layers_structure(self, basic_inputs):
        """Output has background, midground, and foreground layers."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert "background" in result["layers"]
        assert "midground" in result["layers"]
        assert "foreground" in result["layers"]

    def test_midground_matches_grid(self, basic_inputs):
        """Midground layer matches the input grid."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert result["layers"]["midground"] == grid

    def test_empty_layers_are_zeros(self, basic_inputs):
        """Background and foreground are all zeros."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        bg = result["layers"]["background"]
        fg = result["layers"]["foreground"]
        for row in bg:
            assert all(t == 0 for t in row)
        for row in fg:
            assert all(t == 0 for t in row)

    def test_empty_layer_dimensions(self, basic_inputs):
        """Empty layers have same dimensions as midground."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        bg = result["layers"]["background"]
        fg = result["layers"]["foreground"]
        assert len(bg) == 3
        assert len(bg[0]) == 3
        assert len(fg) == 3
        assert len(fg[0]) == 3

    def test_spawn_positions(self, basic_inputs):
        """Player and companion spawns are correctly placed."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert result["player_spawn"] == {"x": 1, "y": 1}
        assert result["companion_spawn"] == {"x": 0, "y": 1}

    def test_collision_types_present(self, basic_inputs):
        """Collision types are included in output."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert "collision_types" in result
        assert "solid" in result["collision_types"]

    def test_metadata_passthrough(self, basic_inputs):
        """Metadata is passed through correctly."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        assert result["metadata"]["name"] == "Test"
        assert result["metadata"]["world"] == 1

    def test_none_parallax_defaults_to_empty(self, basic_inputs):
        """None parallax defaults to empty dict."""
        grid, spawns, yaml_data = basic_inputs
        yaml_data["parallax"] = None
        result = build_level_json(grid, spawns, yaml_data)
        assert result["parallax"] == {}

    def test_json_serializable(self, basic_inputs):
        """Output is JSON-serializable."""
        grid, spawns, yaml_data = basic_inputs
        result = build_level_json(grid, spawns, yaml_data)
        json_str = json.dumps(result)
        assert json.loads(json_str) == result


# ── Empty layer helper ────────────────────────────────────────────────


class TestMakeEmptyLayer:
    """Tests for the empty layer generator."""

    def test_dimensions(self):
        layer = make_empty_layer(5, 3)
        assert len(layer) == 3
        assert all(len(row) == 5 for row in layer)

    def test_all_zeros(self):
        layer = make_empty_layer(4, 2)
        for row in layer:
            assert all(t == 0 for t in row)

    def test_rows_are_independent(self):
        """Rows are separate lists (not shared references)."""
        layer = make_empty_layer(3, 2)
        layer[0][0] = 99
        assert layer[1][0] == 0


# ── CLI integration ───────────────────────────────────────────────────


class TestCLI:
    """Tests for the CLI entry point."""

    @pytest.fixture
    def example_files(self):
        """Path to the example .map and .yaml files."""
        base = Path(__file__).resolve().parent.parent / "tools" / "level_examples"
        return str(base / "level_1_1.map"), str(base / "level_1_1.yaml")

    def test_validate_only(self, example_files, capsys):
        """--validate-only exits with 0 and prints summary."""
        map_file, yaml_file = example_files
        code = main([map_file, yaml_file, "--validate-only"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Validation passed" in captured.out

    def test_preview(self, example_files, capsys):
        """--preview prints the ASCII map and summary."""
        map_file, yaml_file = example_files
        code = main([map_file, yaml_file, "--preview"])
        assert code == 0
        captured = capsys.readouterr()
        assert "MAP PREVIEW" in captured.out
        assert "Dimensions:" in captured.out

    def test_stdout_output(self, example_files, capsys):
        """Default output goes to stdout as JSON."""
        map_file, yaml_file = example_files
        code = main([map_file, yaml_file])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "metadata" in data
        assert "layers" in data

    def test_file_output(self, example_files, tmp_path):
        """-o writes JSON to the specified file."""
        map_file, yaml_file = example_files
        out_path = str(tmp_path / "output.json")
        code = main([map_file, yaml_file, "-o", out_path])
        assert code == 0
        data = json.loads(Path(out_path).read_text(encoding="utf-8"))
        assert data["dimensions"]["width"] == 60

    def test_missing_map_file(self, tmp_path, capsys):
        """Missing map file returns error code 1."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("metadata:\n  world: 1\n", encoding="utf-8")
        code = main([str(tmp_path / "nonexistent.map"), str(yaml_file)])
        assert code == 1
        captured = capsys.readouterr()
        assert "ERROR" in captured.err

    def test_invalid_map_returns_error(self, tmp_path, capsys):
        """Invalid map content returns error code 1."""
        map_file = tmp_path / "bad.map"
        map_file.write_text("##Z\n...\n", encoding="utf-8")
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(textwrap.dedent("""\
            metadata:
              world: 1
              level: 1
              name: "T"
              name_en: "T"
              music_slot: "m"
              difficulty: 1
              tileset: "t"
              background: "b"
        """), encoding="utf-8")
        code = main([str(map_file), str(yaml_file)])
        assert code == 1
        captured = capsys.readouterr()
        assert "Unknown character" in captured.err


# ── Round-trip test ───────────────────────────────────────────────────


class TestRoundTrip:
    """Test that example files produce JSON matching the original level."""

    def test_level_1_1_roundtrip(self):
        """Conversion of example .map + .yaml matches original level_1_1.json."""
        base = Path(__file__).resolve().parent.parent
        original_path = (
            base / "sa_fona" / "data" / "levels" / "world1" / "level_1_1.json"
        )
        map_path = base / "tools" / "level_examples" / "level_1_1.map"
        yaml_path = base / "tools" / "level_examples" / "level_1_1.yaml"

        with open(original_path, encoding="utf-8") as f:
            original = json.load(f)

        grid, spawns = parse_map_string(
            map_path.read_text(encoding="utf-8"), source=str(map_path)
        )
        yaml_data = load_yaml_metadata(str(yaml_path))
        generated = build_level_json(grid, spawns, yaml_data)

        # Compare structural sections
        assert generated["metadata"] == original["metadata"]
        assert generated["dimensions"] == original["dimensions"]
        assert generated["collision_types"] == original["collision_types"]
        assert generated["layers"]["midground"] == original["layers"]["midground"]
        assert generated["layers"]["background"] == original["layers"]["background"]
        assert generated["layers"]["foreground"] == original["layers"]["foreground"]
        assert generated["player_spawn"] == original["player_spawn"]
        assert generated["companion_spawn"] == original["companion_spawn"]
        assert generated["triggers"] == original["triggers"]
        assert generated["secrets"] == original["secrets"]
        assert generated["parallax"] == original["parallax"]

        # Entities may be in different order, so sort both
        orig_ents = sorted(
            original["entities"],
            key=lambda e: (e["type"], e.get("x", 0), e.get("y", 0)),
        )
        gen_ents = sorted(
            generated["entities"],
            key=lambda e: (e["type"], e.get("x", 0), e.get("y", 0)),
        )
        assert gen_ents == orig_ents
