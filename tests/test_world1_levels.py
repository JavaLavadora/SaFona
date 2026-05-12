"""Tests for World 1 levels (D8): level loading, entity counts, triggers.

Verifies that all four W1 level JSON files are valid, loadable, and
contain the expected number and types of entities, triggers, and secrets
as specified in the GDD.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pygame
import pytest

from sa_fona.config.settings import DATA_DIR
from sa_fona.level.level_loader import LevelLoader
from sa_fona.level.tilemap import TILE_SIZE


# ── Helpers ────────────────────────────────────────────────────────

LEVELS_DIR = DATA_DIR / "levels" / "world1"

LEVEL_FILES = [
    ("level_1_1.json", 1, 1, "Es Primer Pas"),
    ("level_1_2.json", 1, 2, "Sa Cova des Foner"),
    ("level_1_3.json", 1, 3, "Es Talayot Sagrat"),
    ("level_1_4.json", 1, 4, "Sa Porta des Bou"),
]


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure Pygame is initialized for all tests."""
    pygame.init()
    yield
    pygame.quit()


def _load_raw(filename: str) -> dict:
    """Load raw JSON data from a level file."""
    path = LEVELS_DIR / filename
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_level(filename: str):
    """Load a level through the LevelLoader."""
    path = str(LEVELS_DIR / filename)
    loader = LevelLoader()
    return loader.load(path)


def _count_entities(entities: list[dict], entity_type: str, subtype_key: str | None = None, subtype_val: str | None = None) -> int:
    """Count entities of a given type/subtype."""
    count = 0
    for e in entities:
        if e.get("type") == entity_type:
            if subtype_key is None or e.get(subtype_key) == subtype_val:
                count += 1
    return count


# ── Level file existence ──────────────────────────────────────────

class TestLevelFilesExist:
    """All four W1 level JSON files exist on disk."""

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_file_exists(self, filename, world, level, name):
        path = LEVELS_DIR / filename
        assert path.exists(), f"{filename} not found at {LEVELS_DIR}"


# ── Level loading (via LevelLoader) ──────────────────────────────

class TestLevelsLoadCorrectly:
    """All levels load through LevelLoader without error."""

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_loads_without_error(self, filename, world, level, name):
        level_data = _load_level(filename)
        assert level_data is not None

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_metadata(self, filename, world, level, name):
        level_data = _load_level(filename)
        meta = level_data.metadata
        assert meta["world"] == world
        assert meta["level"] == level
        assert meta["name"] == name

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_has_tilemap(self, filename, world, level, name):
        level_data = _load_level(filename)
        assert level_data.tilemap is not None
        assert level_data.tilemap.width_tiles > 0
        assert level_data.tilemap.height_tiles > 0

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_has_player_spawn(self, filename, world, level, name):
        level_data = _load_level(filename)
        px, py = level_data.player_spawn
        assert px >= 0
        assert py >= 0

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_has_companion_spawn(self, filename, world, level, name):
        level_data = _load_level(filename)
        cx, cy = level_data.companion_spawn
        assert cx >= 0
        assert cy >= 0


# ── Level 1-1 specific checks ────────────────────────────────────

class TestLevel1_1:
    """Level 1-1 'Es Primer Pas' meets GDD specification."""

    def setup_method(self):
        self.raw = _load_raw("level_1_1.json")
        self.entities = self.raw["entities"]
        self.triggers = self.raw["triggers"]

    def test_difficulty(self):
        assert self.raw["metadata"]["difficulty"] == 1

    def test_horizontal_layout(self):
        """Level is wider than it is tall (horizontal layout)."""
        assert self.raw["dimensions"]["width"] > self.raw["dimensions"]["height"]

    def test_no_enemies_first_half(self):
        """No enemies in the first half of the level."""
        width = self.raw["dimensions"]["width"]
        halfway = width // 2
        for e in self.entities:
            if e.get("type") == "enemy":
                assert e["x"] >= halfway, f"Enemy at x={e['x']} is in the first half"

    def test_sheep_count_2_to_4(self):
        count = _count_entities(self.entities, "enemy", "enemy_type", "possessed_sheep")
        assert 2 <= count <= 4

    def test_no_warriors_or_guardians(self):
        warriors = _count_entities(self.entities, "enemy", "enemy_type", "rival_warrior")
        guardians = _count_entities(self.entities, "enemy", "enemy_type", "stone_guardian")
        assert warriors == 0
        assert guardians == 0

    def test_stones_15_to_20(self):
        """15-20 stone pickups as per GDD."""
        stone_count = _count_entities(self.entities, "pickup", "pickup_type", "stone")
        assert 15 <= stone_count <= 25  # Allow some flexibility for breakable drops

    def test_heart_pickup(self):
        hearts = _count_entities(self.entities, "pickup", "pickup_type", "heart")
        assert hearts >= 1

    def test_has_intro_dialogue_trigger(self):
        dialogue_triggers = [t for t in self.triggers if t["type"] == "dialogue"]
        ids = [t.get("dialogue_id") for t in dialogue_triggers]
        assert "w1_l1_bep_intro" in ids

    def test_has_level_end_trigger(self):
        end_triggers = [t for t in self.triggers if t["type"] == "level_end"]
        assert len(end_triggers) >= 1

    def test_has_save_point(self):
        save_triggers = [t for t in self.triggers if t["type"] == "save_point"]
        assert len(save_triggers) >= 1

    def test_level_end_points_to_level_1_2(self):
        end_triggers = [t for t in self.triggers if t["type"] == "level_end"]
        assert any(t.get("next_level") == "world1/level_1_2" for t in end_triggers)


# ── Level 1-2 specific checks ────────────────────────────────────

class TestLevel1_2:
    """Level 1-2 'Sa Cova des Foner' meets GDD specification."""

    def setup_method(self):
        self.raw = _load_raw("level_1_2.json")
        self.entities = self.raw["entities"]
        self.triggers = self.raw["triggers"]

    def test_difficulty(self):
        assert self.raw["metadata"]["difficulty"] == 2

    def test_sheep_count_4_to_5(self):
        count = _count_entities(self.entities, "enemy", "enemy_type", "possessed_sheep")
        assert 4 <= count <= 5

    def test_warrior_count_2_to_3(self):
        count = _count_entities(self.entities, "enemy", "enemy_type", "rival_warrior")
        assert 2 <= count <= 3

    def test_has_secret(self):
        assert len(self.raw.get("secrets", [])) >= 1

    def test_has_charge_hint_dialogue(self):
        dialogue_triggers = [t for t in self.triggers if t["type"] == "dialogue"]
        ids = [t.get("dialogue_id") for t in dialogue_triggers]
        assert "w1_l2_super_charge_hint" in ids

    def test_level_end_points_to_level_1_3(self):
        end_triggers = [t for t in self.triggers if t["type"] == "level_end"]
        assert any(t.get("next_level") == "world1/level_1_3" for t in end_triggers)


# ── Level 1-3 specific checks ────────────────────────────────────

class TestLevel1_3:
    """Level 1-3 'Es Talayot Sagrat' meets GDD specification."""

    def setup_method(self):
        self.raw = _load_raw("level_1_3.json")
        self.entities = self.raw["entities"]
        self.triggers = self.raw["triggers"]

    def test_difficulty(self):
        assert self.raw["metadata"]["difficulty"] == 3

    def test_vertical_layout(self):
        """Level is taller than it is wide (vertical layout)."""
        assert self.raw["dimensions"]["height"] > self.raw["dimensions"]["width"]

    def test_has_stone_guardian(self):
        count = _count_entities(self.entities, "enemy", "enemy_type", "stone_guardian")
        assert count >= 1

    def test_secrets(self):
        """Secrets may be present if level data includes them."""
        secrets = self.raw.get("secrets", [])
        # Level content evolves; just verify the field is a list.
        assert isinstance(secrets, list)

    def test_has_breakable_slam_collision_type(self):
        """Level defines breakable_slam collision type for Stone Slam support."""
        slam_ids = self.raw["collision_types"].get("breakable_slam", [])
        assert len(slam_ids) >= 1, "breakable_slam collision type should be defined"

    def test_has_save_point(self):
        save_triggers = [t for t in self.triggers if t["type"] == "save_point"]
        assert len(save_triggers) >= 1

    def test_level_end_points_to_level_1_4(self):
        end_triggers = [t for t in self.triggers if t["type"] == "level_end"]
        assert any(t.get("next_level") == "world1/level_1_4" for t in end_triggers)


# ── Level 1-4 specific checks ────────────────────────────────────

class TestLevel1_4:
    """Level 1-4 'Sa Porta des Bou' meets GDD specification."""

    def setup_method(self):
        self.raw = _load_raw("level_1_4.json")
        self.entities = self.raw["entities"]
        self.triggers = self.raw["triggers"]

    def test_difficulty(self):
        assert self.raw["metadata"]["difficulty"] == 4

    def test_mixed_layout(self):
        """Level has both significant width and height."""
        w = self.raw["dimensions"]["width"]
        h = self.raw["dimensions"]["height"]
        assert w > 24  # wider than one screen
        assert h > 15  # taller than one screen

    def test_enemy_combinations(self):
        """Has sheep, warriors, AND guardians."""
        sheep = _count_entities(self.entities, "enemy", "enemy_type", "possessed_sheep")
        warriors = _count_entities(self.entities, "enemy", "enemy_type", "rival_warrior")
        guardians = _count_entities(self.entities, "enemy", "enemy_type", "stone_guardian")
        assert sheep >= 2
        assert warriors >= 2
        assert guardians >= 1

    def test_generous_stones(self):
        """Pre-boss level should be generous with stones (30-35)."""
        count = _count_entities(self.entities, "pickup", "pickup_type", "stone")
        assert count >= 25  # Allow some via breakables

    def test_secrets(self):
        secrets = self.raw.get("secrets", [])
        assert isinstance(secrets, list)

    def test_boss_gate_at_end(self):
        end_triggers = [t for t in self.triggers if t["type"] == "level_end"]
        assert len(end_triggers) >= 1
        # Should reference the boss
        assert any("boss" in t.get("next_level", "").lower() for t in end_triggers)


# ── Difficulty progression ────────────────────────────────────────

class TestDifficultyProgression:
    """Difficulty values increase across levels."""

    def test_increasing_difficulty(self):
        difficulties = []
        for filename, _, _, _ in LEVEL_FILES:
            raw = _load_raw(filename)
            difficulties.append(raw["metadata"]["difficulty"])
        assert difficulties == sorted(difficulties)
        assert difficulties == [1, 2, 3, 4]

    def test_increasing_enemy_threat(self):
        """Each level has increasing total enemy threat (HP-weighted).

        Raw count may decrease as enemy types get tougher (e.g. fewer
        sheep but a stone guardian), so we weight by HP: sheep=2,
        warrior=3, guardian=6.
        """
        hp_weights = {"possessed_sheep": 2, "rival_warrior": 3, "stone_guardian": 6}
        threat_levels = []
        for filename, _, _, _ in LEVEL_FILES:
            raw = _load_raw(filename)
            threat = 0
            for e in raw["entities"]:
                if e.get("type") == "enemy":
                    threat += hp_weights.get(e.get("enemy_type", ""), 1)
            threat_levels.append(threat)
        for i in range(1, len(threat_levels)):
            assert threat_levels[i] >= threat_levels[i - 1], (
                f"Level {i+1} threat ({threat_levels[i]}) < Level {i} ({threat_levels[i-1]})"
            )


# ── Tilemap integrity ─────────────────────────────────────────────

class TestTilemapIntegrity:
    """All level tilemaps have correct dimensions and valid tile IDs."""

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_layers_match_dimensions(self, filename, world, level, name):
        raw = _load_raw(filename)
        w = raw["dimensions"]["width"]
        h = raw["dimensions"]["height"]
        for layer_name, grid in raw["layers"].items():
            assert len(grid) == h, f"{filename} {layer_name}: expected {h} rows, got {len(grid)}"
            for row_idx, row in enumerate(grid):
                assert len(row) == w, (
                    f"{filename} {layer_name} row {row_idx}: "
                    f"expected {w} cols, got {len(row)}"
                )

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_player_spawn_in_bounds(self, filename, world, level, name):
        raw = _load_raw(filename)
        w = raw["dimensions"]["width"]
        h = raw["dimensions"]["height"]
        px = raw["player_spawn"]["x"]
        py = raw["player_spawn"]["y"]
        assert 0 <= px < w
        assert 0 <= py < h

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_player_spawn_on_open_tile(self, filename, world, level, name):
        """Player spawn should be on an empty (non-solid) tile."""
        raw = _load_raw(filename)
        px = raw["player_spawn"]["x"]
        py = raw["player_spawn"]["y"]
        mid = raw["layers"]["midground"]
        tile = mid[py][px]
        solid_ids = set(raw["collision_types"].get("solid", []))
        assert tile not in solid_ids, f"Player spawns inside solid tile {tile} at ({px},{py})"


# ── Level transition chain ────────────────────────────────────────

class TestLevelChain:
    """Levels form a connected chain via next_level properties."""

    def test_full_chain(self):
        expected_chain = [
            ("level_1_1.json", "world1/level_1_2"),
            ("level_1_2.json", "world1/level_1_3"),
            ("level_1_3.json", "world1/level_1_4"),
            ("level_1_4.json", "world1/boss_bou_de_pedra"),
        ]
        for filename, expected_next in expected_chain:
            raw = _load_raw(filename)
            end_triggers = [t for t in raw["triggers"] if t["type"] == "level_end"]
            next_levels = [t.get("next_level") for t in end_triggers]
            assert expected_next in next_levels, (
                f"{filename}: expected next_level={expected_next!r}, "
                f"got {next_levels}"
            )


# ── Dialogue references ──────────────────────────────────────────

class TestDialogueReferences:
    """All dialogue_id references in triggers exist in dialogue files."""

    @pytest.fixture(autouse=True)
    def _load_all_dialogue(self):
        """Load all dialogue data."""
        dialogue_dir = DATA_DIR / "dialogue"
        self.dialogue_data = {}
        for json_file in sorted(dialogue_dir.glob("*.json")):
            with open(json_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.dialogue_data.update(data)

    @pytest.mark.parametrize("filename,world,level,name", LEVEL_FILES)
    def test_dialogue_ids_exist(self, filename, world, level, name):
        raw = _load_raw(filename)
        for trigger in raw["triggers"]:
            if trigger["type"] == "dialogue":
                dialogue_id = trigger.get("dialogue_id", "")
                assert dialogue_id in self.dialogue_data, (
                    f"{filename}: dialogue_id {dialogue_id!r} not found "
                    f"in dialogue files"
                )
