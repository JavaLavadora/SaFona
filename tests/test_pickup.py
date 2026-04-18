"""Tests for Pickup entities and collection in GameplayScene."""

import pygame
import pytest

from sa_fona.config.settings import BASE_HEIGHT, BASE_WIDTH
from sa_fona.core.event_bus import EventBus
from sa_fona.core.input_handler import InputState
from sa_fona.entities.pickup import Pickup, PickupType, PICKUP_WIDTH, PICKUP_HEIGHT
from sa_fona.entities.breakable import Breakable
from sa_fona.scenes.gameplay import GameplayScene


# ── Pickup entity tests ──────────────────────────────────────────


class TestPickupEntity:
    """Tests for the Pickup entity class."""

    def test_heart_pickup_creation(self):
        p = Pickup(100, 200, PickupType.HEART, value=1.0)
        assert p.pickup_type == PickupType.HEART
        assert p.value == 1.0
        assert p.active is True
        assert p.rect.x == 100
        assert p.rect.y == 200

    def test_stone_pickup_creation(self):
        p = Pickup(50, 75, PickupType.STONE, value=3.0)
        assert p.pickup_type == PickupType.STONE
        assert p.value == 3.0

    def test_pickup_has_sprite(self):
        p = Pickup(0, 0, PickupType.HEART)
        assert p.sprite is not None
        assert p.sprite.get_width() == PICKUP_WIDTH
        assert p.sprite.get_height() == PICKUP_HEIGHT

    def test_stone_pickup_has_sprite(self):
        p = Pickup(0, 0, PickupType.STONE)
        assert p.sprite is not None

    def test_collect_heart(self):
        p = Pickup(0, 0, PickupType.HEART, value=1.0)
        event_type, event_data = p.collect()
        assert event_type == "heart_collected"
        assert event_data["amount"] == 1.0
        assert p.active is False

    def test_collect_stone(self):
        p = Pickup(0, 0, PickupType.STONE, value=3.0)
        event_type, event_data = p.collect()
        assert event_type == "stone_collected"
        assert event_data["amount"] == 3
        assert p.active is False

    def test_update_is_noop(self):
        p = Pickup(10, 20, PickupType.STONE)
        p.update(1.0)
        assert p.rect.x == 10
        assert p.rect.y == 20

    def test_render_does_not_crash(self):
        p = Pickup(0, 0, PickupType.HEART)
        surface = pygame.Surface((100, 100))
        p.render(surface, (0, 0))


# ── Breakable entity tests ───────────────────────────────────────


class TestBreakableEntity:
    """Tests for the Breakable entity class."""

    def test_breakable_creation(self):
        b = Breakable(100, 200, "breakable_pot")
        assert b.breakable_type == "breakable_pot"
        assert b.active is True

    def test_breakable_has_sprite(self):
        b = Breakable(0, 0, "breakable_crate")
        assert b.sprite is not None

    def test_on_hit_marks_inactive(self):
        b = Breakable(0, 0, "breakable_pot")
        b.on_hit(2)
        assert b.active is False

    def test_on_hit_returns_pickups(self):
        b = Breakable(100, 100, "breakable_pot")
        pickups = b.on_hit(3)
        assert len(pickups) == 3
        for p in pickups:
            assert isinstance(p, Pickup)
            assert p.pickup_type == PickupType.STONE

    def test_on_hit_zero_yield(self):
        b = Breakable(0, 0, "breakable_pot")
        pickups = b.on_hit(0)
        assert len(pickups) == 0
        assert b.active is False


# ── Pickup collection integration tests ──────────────────────────


class TestPickupCollection:
    """Tests for pickup collection in GameplayScene."""

    @pytest.fixture
    def scene(self):
        """Create a GameplayScene with the test level."""
        return GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())

    def test_pickups_spawned_from_level(self, scene):
        """Pickups should be spawned from level entity definitions."""
        assert len(scene.pickups) > 0

    def test_breakables_spawned_from_level(self, scene):
        """Breakables should be spawned from level entity definitions."""
        assert len(scene.breakables) > 0

    def test_pickup_collection_increases_stones(self, scene):
        """Collecting a stone pickup should increase stone count."""
        scene.on_enter()
        initial_stones = scene.economy.stone_count

        # Place a stone pickup directly on the player.
        pickup = Pickup(
            scene.player.rect.x,
            scene.player.rect.y,
            PickupType.STONE,
            value=5.0,
        )
        scene.pickups.append(pickup)

        # Run one update to trigger collection.
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert scene.economy.stone_count == initial_stones + 5

    def test_pickup_collection_removes_pickup(self, scene):
        """Collected pickups should be removed from the list."""
        scene.on_enter()
        pickup = Pickup(
            scene.player.rect.x,
            scene.player.rect.y,
            PickupType.STONE,
            value=1.0,
        )
        scene.pickups.append(pickup)
        initial_count = len(scene.pickups)

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        # The placed pickup should be collected (removed).
        assert len(scene.pickups) < initial_count

    def test_heart_collection_updates_hud(self, scene):
        """Collecting a heart should update the HUD hearts."""
        scene.on_enter()
        scene.hud.current_hearts = 1.0

        pickup = Pickup(
            scene.player.rect.x,
            scene.player.rect.y,
            PickupType.HEART,
            value=1.0,
        )
        scene.pickups.append(pickup)

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert scene.hud.current_hearts == 2.0

    def test_stone_collection_updates_hud(self, scene):
        """Collecting stones should update the HUD stone count."""
        scene.on_enter()
        initial_hud_stones = scene.hud.stone_count

        pickup = Pickup(
            scene.player.rect.x,
            scene.player.rect.y,
            PickupType.STONE,
            value=3.0,
        )
        scene.pickups.append(pickup)

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert scene.hud.stone_count == initial_hud_stones + 3

    def test_no_collection_without_overlap(self, scene):
        """Pickups far from the player should not be collected."""
        scene.on_enter()
        pickup = Pickup(9000, 9000, PickupType.STONE, value=1.0)
        scene.pickups.append(pickup)

        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)

        assert pickup.active is True


class TestHUDRenderedInScene:
    """Tests that the HUD is rendered as part of the scene."""

    def test_render_with_hud(self):
        """GameplayScene.render should include HUD without crashing."""
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())
        scene.on_enter()
        surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        scene.handle_input(InputState())
        scene.update(1.0 / 60.0)
        scene.render(surface)

    def test_hud_initial_state(self):
        """HUD should start with correct initial state."""
        scene = GameplayScene(BASE_WIDTH, BASE_HEIGHT, event_bus=EventBus())
        assert scene.hud.max_hearts == 3
        assert scene.hud.current_hearts == 3.0
        assert scene.hud.stone_count == 0
