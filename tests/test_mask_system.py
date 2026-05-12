"""Tests for MaskSystem: inventory, cooldowns, Stone Slam power, and save/load."""

import json
import os

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.level.tilemap import TILE_SIZE, TileMap
from sa_fona.systems.mask_system import MaskSystem


# ── Helpers ──────────────────────────────────────────────────────


def _make_masks_json(tmp_path, data=None):
    """Write a masks.json file to tmp_path and return its path."""
    if data is None:
        data = {
            "stone_slam": {
                "name": "Stone Slam",
                "description": "Ground pound shockwave",
                "power_type": "ground_pound",
                "range_tiles": 3,
                "stun_duration": 1.5,
                "damage": 2,
                "cooldown": 2.0,
                "world_origin": "world1",
            }
        }
    path = str(tmp_path / "masks.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def _make_tilemap(width=20, height=12, breakable_positions=None):
    """Create a TileMap with solid ground and optional breakable_slam tiles.

    The ground row is at row index (height - 1). Breakable positions are
    given as (col, row) tuples with tile ID 20.
    """
    midground = [[0] * width for _ in range(height)]
    # Ground row: solid tiles (ID 1).
    for col in range(width):
        midground[height - 1][col] = 1

    # Place breakable_slam tiles.
    if breakable_positions:
        for col, row in breakable_positions:
            midground[row][col] = 20

    tile_data = {
        "dimensions": {"width": width, "height": height},
        "layers": {"midground": midground},
        "collision_types": {
            "solid": [1],
            "breakable_slam": [20],
        },
    }
    return TileMap(tile_data)


def _make_enemy(x, y, health=3):
    """Create a minimal enemy at pixel position (x, y)."""
    from sa_fona.entities.enemy import Enemy

    definition = {
        "display_name": "Test Enemy",
        "health": health,
        "contact_damage": 0.5,
        "hitbox": {"w": 16, "h": 16},
        "behavior": "patrol",
        "behavior_params": {"patrol_range": 3, "speed": 40},
        "drops": {"stones": {"min": 1, "max": 1}, "heart_chance": 0.0},
    }
    return Enemy(x, y, "test_enemy", definition)


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def init_pygame():
    """Ensure pygame is initialized for Surface/Rect usage."""
    pygame.init()
    yield


@pytest.fixture
def bus():
    """Create a fresh EventBus."""
    return EventBus()


@pytest.fixture
def masks_path(tmp_path):
    """Write default masks.json and return its path."""
    return _make_masks_json(tmp_path)


@pytest.fixture
def mask_sys(bus, masks_path):
    """Create a MaskSystem with test masks."""
    return MaskSystem(bus, masks_path=masks_path)


# ── Definition loading ───────────────────────────────────────────


class TestDefinitionLoading:
    """Tests for loading mask definitions from JSON."""

    def test_loads_stone_slam_definition(self, mask_sys):
        assert "stone_slam" in mask_sys.definitions
        defn = mask_sys.definitions["stone_slam"]
        assert defn["name"] == "Stone Slam"
        assert defn["power_type"] == "ground_pound"
        assert defn["range_tiles"] == 3
        assert defn["cooldown"] == 2.0

    def test_missing_file_gives_empty_definitions(self, bus):
        sys = MaskSystem(bus, masks_path="/nonexistent/masks.json")
        assert sys.definitions == {}

    def test_multiple_masks(self, bus, tmp_path):
        data = {
            "stone_slam": {
                "name": "Stone Slam",
                "power_type": "ground_pound",
                "range_tiles": 3,
                "cooldown": 2.0,
            },
            "fire_dash": {
                "name": "Fire Dash",
                "power_type": "dash",
                "range_tiles": 5,
                "cooldown": 3.0,
            },
        }
        path = _make_masks_json(tmp_path, data)
        sys = MaskSystem(bus, masks_path=path)
        assert len(sys.definitions) == 2


# ── Inventory management ─────────────────────────────────────────


class TestInventory:
    """Tests for unlock_mask, equip_mask, unequip_mask."""

    def test_initial_state_empty(self, mask_sys):
        assert mask_sys.unlocked_masks == []
        assert mask_sys.active_mask_id is None

    def test_unlock_mask(self, mask_sys):
        result = mask_sys.unlock_mask("stone_slam")
        assert result is True
        assert "stone_slam" in mask_sys.unlocked_masks

    def test_unlock_already_unlocked(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        result = mask_sys.unlock_mask("stone_slam")
        assert result is False

    def test_unlock_invalid_mask(self, mask_sys):
        result = mask_sys.unlock_mask("nonexistent_mask")
        assert result is False

    def test_equip_mask(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        result = mask_sys.equip_mask("stone_slam")
        assert result is True
        assert mask_sys.active_mask_id == "stone_slam"

    def test_equip_locked_mask_fails(self, mask_sys):
        result = mask_sys.equip_mask("stone_slam")
        assert result is False
        assert mask_sys.active_mask_id is None

    def test_unequip_mask(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")
        mask_sys.unequip_mask()
        assert mask_sys.active_mask_id is None

    def test_equip_resets_cooldown(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")
        # Manually set cooldown state.
        mask_sys._cooldown_remaining = 1.5
        mask_sys._cooldown_total = 2.0
        # Re-equip should reset cooldown.
        mask_sys.equip_mask("stone_slam")
        assert mask_sys.is_on_cooldown is False


# ── Cooldown timing ──────────────────────────────────────────────


class TestCooldown:
    """Tests for cooldown management."""

    def test_not_on_cooldown_initially(self, mask_sys):
        assert mask_sys.is_on_cooldown is False
        assert mask_sys.cooldown_progress == 1.0

    def test_cant_activate_during_cooldown(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        # First activation should succeed.
        result = mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert result is True
        assert mask_sys.is_on_cooldown is True

        # Second activation during cooldown should fail.
        result = mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert result is False

    def test_can_activate_after_cooldown_expires(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert mask_sys.is_on_cooldown is True

        # Advance past the cooldown duration (2.0 seconds).
        mask_sys.update(2.1)
        assert mask_sys.is_on_cooldown is False

        # Now activation should succeed.
        result = mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert result is True

    def test_cooldown_progress_tracks_correctly(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert mask_sys.cooldown_progress < 0.1  # Just started.

        mask_sys.update(1.0)  # Half of 2.0s cooldown.
        assert 0.4 < mask_sys.cooldown_progress < 0.6

        mask_sys.update(1.1)  # Past cooldown.
        assert mask_sys.cooldown_progress == 1.0

    def test_cant_activate_without_equipped_mask(self, mask_sys):
        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)
        result = mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert result is False


# ── Stone Slam shockwave range ────────────────────────────────────


class TestStoneSlamRange:
    """Tests for Stone Slam shockwave enemy hit detection."""

    def test_enemy_within_range_is_hit(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        # Enemy 2 tiles away (within 3-tile range).
        enemy = _make_enemy(12 * TILE_SIZE, 10 * TILE_SIZE + 16, health=5)

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)

        # Enemy should have taken 2 damage (from 5 -> 3).
        assert enemy.health == 3.0

    def test_enemy_beyond_range_not_hit(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        # Enemy 5 tiles away (beyond 3-tile range).
        enemy = _make_enemy(10 * TILE_SIZE, 10 * TILE_SIZE + 16, health=5)

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)

        # Enemy should not have taken damage.
        assert enemy.health == 5.0

    def test_enemy_left_of_player_within_range(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        # Enemy 2 tiles to the left (within range).
        enemy = _make_enemy(8 * TILE_SIZE, 10 * TILE_SIZE + 16, health=5)

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)
        assert enemy.health == 3.0

    def test_dead_enemy_not_affected(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        enemy = _make_enemy(11 * TILE_SIZE, 10 * TILE_SIZE + 16, health=1)
        enemy.health = 0
        enemy.active = False

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)
        assert enemy.health == 0


# ── Stone Slam tile breaking ─────────────────────────────────────


class TestStoneSlamTileBreaking:
    """Tests for Stone Slam breaking breakable_slam tiles."""

    def test_breaks_tiles_within_range(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        # Place breakable_slam at row 10, col 12.
        # Player stands with feet at row 11 boundary (y = 11 * TILE_SIZE).
        # Shock rect covers from y = (11*TILE_SIZE - TILE_SIZE) to
        # y = 11*TILE_SIZE, i.e. row 10.  The breakable at row 10 is in range.
        tilemap = _make_tilemap(breakable_positions=[(12, 10)])
        assert tilemap.get_tile_at(12, 10, "midground") == 20

        # Player bottom at row 11 boundary.
        player_y = 11 * TILE_SIZE - 32  # 32 = player height
        player_rect = pygame.Rect(10 * TILE_SIZE, player_y, 24, 32)
        mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)

        # Tile should be removed (set to 0).
        assert tilemap.get_tile_at(12, 10, "midground") == 0

    def test_does_not_break_tiles_beyond_range(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        # Place a breakable_slam tile at col=15, row=11 (ground row).
        # Player at col=5, range is 3 tiles = 48px from center.
        # Player center ~= 92, tile at col=15 starts at pixel 240 => 148px away.
        tilemap = _make_tilemap(breakable_positions=[(15, 11)])
        assert tilemap.get_tile_at(15, 11, "midground") == 20

        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)
        mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)

        # Tile should remain.
        assert tilemap.get_tile_at(15, 11, "midground") == 20

    def test_publishes_tile_broken_event(self, mask_sys, bus):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap(breakable_positions=[(12, 10)])
        player_y = 11 * TILE_SIZE - 32
        player_rect = pygame.Rect(10 * TILE_SIZE, player_y, 24, 32)

        events = []
        bus.subscribe("tile_broken", lambda **kw: events.append(kw))

        mask_sys.activate_power(player_rect, tilemap, [], bus)
        assert len(events) == 1
        assert events[0]["tile_type"] == "breakable_slam"
        assert events[0]["tile_x"] == 12
        assert events[0]["tile_y"] == 10


# ── Stun application ─────────────────────────────────────────────


class TestStunApplication:
    """Tests for enemy stun behavior from Stone Slam."""

    def test_enemy_stunned_for_correct_duration(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)
        enemy = _make_enemy(11 * TILE_SIZE, 10 * TILE_SIZE + 16, health=5)

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)

        # Enemy should be stunned.
        assert enemy.is_stunned is True

        # After 1.0s, still stunned (stun_duration is 1.5s).
        enemy.update_with_player(player_rect, 1.0)
        assert enemy.is_stunned is True

        # After another 0.6s (total 1.6s), stun should expire.
        enemy.update_with_player(player_rect, 0.6)
        assert enemy.is_stunned is False

    def test_stunned_enemy_does_not_move(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)
        enemy = _make_enemy(11 * TILE_SIZE, 10 * TILE_SIZE + 16, health=5)
        original_x = enemy.rect.x

        mask_sys.activate_power(player_rect, tilemap, [enemy], mask_sys._event_bus)
        assert enemy.is_stunned

        # Update enemy multiple frames — should not move while stunned.
        for _ in range(10):
            enemy.update_with_player(player_rect, 0.016)

        assert enemy.rect.x == original_x

    def test_stun_extends_if_longer(self):
        """Applying a longer stun extends the timer."""
        enemy = _make_enemy(0, 0, health=5)
        enemy.stun(1.0)
        assert enemy.is_stunned

        # Apply a longer stun.
        enemy.stun(2.0)
        assert enemy._stun_timer == 2.0

    def test_stun_does_not_shorten(self):
        """Applying a shorter stun does not shorten the existing one."""
        enemy = _make_enemy(0, 0, health=5)
        enemy.stun(2.0)
        enemy.stun(0.5)
        assert enemy._stun_timer == 2.0


# ── Event publishing ─────────────────────────────────────────────


class TestEventPublishing:
    """Tests for mask-related event publishing."""

    def test_publishes_mask_power_activated(self, mask_sys, bus):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        events = []
        bus.subscribe("mask_power_activated", lambda **kw: events.append(kw))

        mask_sys.activate_power(player_rect, tilemap, [], bus)
        assert len(events) == 1
        assert events[0]["mask_id"] == "stone_slam"
        assert events[0]["power_type"] == "ground_pound"

    def test_publishes_mask_cooldown_started(self, mask_sys, bus):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        events = []
        bus.subscribe("mask_cooldown_started", lambda **kw: events.append(kw))

        mask_sys.activate_power(player_rect, tilemap, [], bus)
        assert len(events) == 1
        assert events[0]["duration"] == 2.0

    def test_publishes_screen_shake(self, mask_sys, bus):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)

        events = []
        bus.subscribe("screen_shake", lambda **kw: events.append(kw))

        mask_sys.activate_power(player_rect, tilemap, [], bus)
        assert len(events) == 1
        assert events[0]["intensity"] == 6.0

    def test_mask_acquired_event_unlocks_and_equips(self, bus, masks_path):
        sys = MaskSystem(bus, masks_path=masks_path)
        bus.publish("mask_acquired", mask_id="stone_slam")

        assert "stone_slam" in sys.unlocked_masks
        assert sys.active_mask_id == "stone_slam"


# ── Save / load round-trip ────────────────────────────────────────


class TestSaveLoad:
    """Tests for mask state save and restore."""

    def test_get_save_state(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        state = mask_sys.get_save_state()
        assert state["unlocked_masks"] == ["stone_slam"]
        assert state["equipped_mask"] == "stone_slam"

    def test_get_save_state_empty(self, mask_sys):
        state = mask_sys.get_save_state()
        assert state["unlocked_masks"] == []
        assert state["equipped_mask"] == ""

    def test_restore_save_state(self, mask_sys):
        save_data = {
            "unlocked_masks": ["stone_slam"],
            "equipped_mask": "stone_slam",
        }
        mask_sys.restore_save_state(save_data)

        assert "stone_slam" in mask_sys.unlocked_masks
        assert mask_sys.active_mask_id == "stone_slam"

    def test_restore_clears_cooldown(self, mask_sys):
        mask_sys.unlock_mask("stone_slam")
        mask_sys.equip_mask("stone_slam")

        # Simulate activating power to set cooldown.
        tilemap = _make_tilemap()
        player_rect = pygame.Rect(5 * TILE_SIZE, 10 * TILE_SIZE, 24, 32)
        mask_sys.activate_power(player_rect, tilemap, [], mask_sys._event_bus)
        assert mask_sys.is_on_cooldown

        # Restore should clear cooldown.
        mask_sys.restore_save_state({
            "unlocked_masks": ["stone_slam"],
            "equipped_mask": "stone_slam",
        })
        assert mask_sys.is_on_cooldown is False

    def test_restore_invalid_equipped_mask(self, mask_sys):
        """Restoring with an equipped mask not in unlocked list ignores it."""
        mask_sys.restore_save_state({
            "unlocked_masks": ["stone_slam"],
            "equipped_mask": "nonexistent_mask",
        })
        assert mask_sys.active_mask_id is None

    def test_roundtrip_via_save_system(self, bus, masks_path, tmp_path):
        """Full round-trip: mask_sys -> save_sys -> disk -> new mask_sys."""
        from sa_fona.systems.save_system import SaveSystem

        save_path = str(tmp_path / "save.json")

        # Set up mask system and unlock/equip.
        sys1 = MaskSystem(bus, masks_path=masks_path)
        sys1.unlock_mask("stone_slam")
        sys1.equip_mask("stone_slam")

        # Save via SaveSystem.
        save_sys = SaveSystem(bus, save_path=save_path)
        mask_state = sys1.get_save_state()
        save_sys.state["masks_unlocked"] = mask_state["unlocked_masks"]
        save_sys.state["masks_equipped"] = (
            [mask_state["equipped_mask"]] if mask_state["equipped_mask"] else []
        )
        save_sys.save()

        # Load into a new save system.
        save_sys2 = SaveSystem(bus, save_path=save_path)
        data = save_sys2.load()
        assert data is not None

        # Restore into a new mask system.
        sys2 = MaskSystem(bus, masks_path=masks_path)
        unlocked = data.get("masks_unlocked", [])
        equipped_list = data.get("masks_equipped", [])
        equipped = equipped_list[0] if equipped_list else ""
        sys2.restore_save_state({
            "unlocked_masks": unlocked,
            "equipped_mask": equipped,
        })

        assert sys2.unlocked_masks == ["stone_slam"]
        assert sys2.active_mask_id == "stone_slam"


# ── Cleanup ──────────────────────────────────────────────────────


class TestCleanup:
    """Tests for proper event unsubscription."""

    def test_cleanup_unsubscribes(self, bus, masks_path):
        sys = MaskSystem(bus, masks_path=masks_path)
        sys.cleanup()

        # Publishing mask_acquired after cleanup should not unlock.
        bus.publish("mask_acquired", mask_id="stone_slam")
        assert sys.unlocked_masks == []

    def test_double_cleanup_does_not_raise(self, bus, masks_path):
        sys = MaskSystem(bus, masks_path=masks_path)
        sys.cleanup()
        sys.cleanup()  # Should not raise.
