"""Tests for the AttackEffectOverlay system on Enemy entities.

Verifies data-driven loading, activation/deactivation tied to attack
states, animation frame advancement, loop/clamp behavior, and correct
render positioning for both facing directions.
"""

from __future__ import annotations

import json
import os
import tempfile

import pygame
import pytest

from sa_fona.entities.enemy import AttackEffectOverlay, Enemy, EnemyFactory
from sa_fona.entities.enemy_behaviors import AttackState, BehaviorResult


@pytest.fixture(autouse=True)
def _init_pygame():
    """Ensure pygame is initialized for all tests."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield


def _make_effect_sprite(tmp_dir: str, name: str, frame_w: int, frame_h: int, num_frames: int) -> str:
    """Create a simple placeholder sprite strip for testing.

    Args:
        tmp_dir: Directory to write the sprite file to.
        name: Filename without extension.
        frame_w: Width of each frame.
        frame_h: Height of each frame.
        num_frames: Number of frames in the strip.

    Returns:
        The full path to the created sprite file.
    """
    effects_dir = os.path.join(tmp_dir, "assets", "sprites", "enemies", "effects")
    os.makedirs(effects_dir, exist_ok=True)
    total_w = frame_w * num_frames
    surf = pygame.Surface((total_w, frame_h), pygame.SRCALPHA)
    for i in range(num_frames):
        pygame.draw.rect(surf, (100 + i * 30, 100, 100, 200), (i * frame_w, 0, frame_w, frame_h))
    path = os.path.join(effects_dir, f"{name}.png")
    pygame.image.save(surf, path)
    return path


def _make_test_definitions(
    tmp_dir: str,
    with_effect: bool = False,
    effect_sprite_name: str = "test_effect",
    frame_w: int = 16,
    frame_h: int = 16,
    num_frames: int = 3,
    fps: float = 10.0,
    loop: bool = False,
    show_during: list[str] | None = None,
) -> str:
    """Create a temporary enemy definitions JSON file.

    Args:
        tmp_dir: Directory for the JSON file.
        with_effect: Whether to include an attack_effect block.
        effect_sprite_name: Name of the sprite for the effect.
        frame_w: Frame width for the effect.
        frame_h: Frame height for the effect.
        num_frames: Number of frames to generate in the sprite strip.
        fps: Animation speed.
        loop: Whether the animation should loop.
        show_during: List of attack state strings.

    Returns:
        Path to the JSON definitions file.
    """
    if show_during is None:
        show_during = ["attacking"]

    definition = {
        "test_enemy": {
            "display_name": "Test Enemy",
            "health": 3,
            "contact_damage": 1.0,
            "behavior": "chase",
            "behavior_params": {
                "chase_range": 6,
                "speed": 50,
                "attack_range": 1.5,
                "attack_cooldown": 1.0,
            },
            "hitbox": {"w": 16, "h": 24},
            "drops": {"stones": {"min": 1, "max": 2}, "heart_chance": 0.1},
        },
        "test_enemy_no_effect": {
            "display_name": "Test No Effect",
            "health": 2,
            "contact_damage": 0.5,
            "behavior": "patrol",
            "behavior_params": {"patrol_range": 5, "speed": 40},
            "hitbox": {"w": 16, "h": 16},
            "drops": {"stones": {"min": 1, "max": 2}, "heart_chance": 0.1},
        },
    }

    if with_effect:
        # Create the sprite file.
        _make_effect_sprite(tmp_dir, effect_sprite_name, frame_w, frame_h, num_frames)
        definition["test_enemy"]["attack_effect"] = {
            "sprite": effect_sprite_name,
            "frame_w": frame_w,
            "frame_h": frame_h,
            "offset_x": 12,
            "offset_y": -4,
            "fps": fps,
            "loop": loop,
            "show_during": show_during,
        }

    path = os.path.join(tmp_dir, "test_enemies.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(definition, fh)
    return path


def _create_enemy_with_effect(
    tmp_dir: str,
    fps: float = 10.0,
    loop: bool = False,
    show_during: list[str] | None = None,
    num_frames: int = 3,
) -> Enemy:
    """Helper to create an enemy that has an attack effect loaded.

    The function patches the project root so load_frame_strip can find
    the generated sprite file.
    """
    import sa_fona.rendering.asset_loader as al

    original_root = al._PROJECT_ROOT
    al._PROJECT_ROOT = tmp_dir
    try:
        defs_path = _make_test_definitions(
            tmp_dir,
            with_effect=True,
            fps=fps,
            loop=loop,
            show_during=show_during,
            num_frames=num_frames,
        )
        factory = EnemyFactory(defs_path)
        enemy = factory.create("test_enemy", 100, 200)
    finally:
        al._PROJECT_ROOT = original_root
    return enemy


class TestAttackEffectOverlay:
    """Tests for the AttackEffectOverlay system."""

    def test_no_attack_effect_by_default(self):
        """Enemy without attack_effect config should have None overlay."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            defs_path = _make_test_definitions(tmp_dir, with_effect=False)
            factory = EnemyFactory(defs_path)
            enemy = factory.create("test_enemy_no_effect", 100, 200)
            assert enemy.attack_effect is None

    def test_attack_effect_loaded_from_definition(self):
        """Enemy with attack_effect config should have a populated overlay."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir)
            assert enemy.attack_effect is not None
            assert isinstance(enemy.attack_effect, AttackEffectOverlay)
            assert len(enemy.attack_effect.frames) == 3
            assert enemy.attack_effect.frame_w == 16
            assert enemy.attack_effect.frame_h == 16
            assert enemy.attack_effect.offset_x == 12
            assert enemy.attack_effect.offset_y == -4
            assert AttackState.ATTACKING in enemy.attack_effect.show_during

    def test_attack_effect_inactive_when_idle(self):
        """Overlay should be inactive when enemy is in IDLE state."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir)
            # Default behavior result is IDLE.
            enemy._behavior_result = BehaviorResult()
            enemy._update_sprite(0.016)
            assert not enemy.attack_effect.active

    def test_attack_effect_active_during_show_states(self):
        """Overlay should become active when attack state matches show_during."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir, show_during=["attacking", "tell"])
            assert enemy.attack_effect is not None

            # Simulate ATTACKING state.
            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result
            enemy._update_sprite(0.016)
            assert enemy.attack_effect.active

            # Simulate TELL state.
            result2 = BehaviorResult()
            result2.attack_state = AttackState.TELL
            enemy._behavior_result = result2
            enemy._update_sprite(0.016)
            assert enemy.attack_effect.active

    def test_attack_effect_resets_on_activation(self):
        """Timer and frame_index should reset when transitioning inactive->active."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir, fps=10.0)
            overlay = enemy.attack_effect
            assert overlay is not None

            # First make it active and advance some frames.
            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result
            enemy._update_sprite(0.2)  # Should advance frame.

            # Now make it inactive.
            idle_result = BehaviorResult()
            idle_result.attack_state = AttackState.IDLE
            enemy._behavior_result = idle_result
            enemy._update_sprite(0.016)
            assert not overlay.active

            # Re-activate: should reset timer and frame_index.
            enemy._behavior_result = result
            enemy._update_sprite(0.016)
            assert overlay.active
            assert overlay.frame_index == 0
            assert overlay.timer < 0.1  # Just reset.

    def test_attack_effect_animation_advances(self):
        """Frame index should advance with time at the configured fps."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir, fps=10.0, num_frames=4)
            overlay = enemy.attack_effect
            assert overlay is not None

            # Activate.
            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result

            # First update: activation.
            enemy._update_sprite(0.0)
            assert overlay.frame_index == 0

            # At 10 fps, frame duration = 0.1s. Advance by 0.11s.
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 1

    def test_attack_effect_loop_wraps(self):
        """Looping animation should wrap back to frame 0 after the last frame."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(
                tmp_dir, fps=10.0, loop=True, num_frames=3
            )
            overlay = enemy.attack_effect
            assert overlay is not None

            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result

            # Activation.
            enemy._update_sprite(0.0)
            assert overlay.frame_index == 0

            # Advance through all 3 frames and back to 0.
            # Frame 0 -> 1 at 0.1s, 1 -> 2 at 0.2s, 2 -> 0 at 0.3s.
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 1
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 2
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 0  # Wrapped.

    def test_attack_effect_no_loop_stops(self):
        """Non-looping animation should clamp at the last frame."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(
                tmp_dir, fps=10.0, loop=False, num_frames=3
            )
            overlay = enemy.attack_effect
            assert overlay is not None

            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result

            # Activation.
            enemy._update_sprite(0.0)
            assert overlay.frame_index == 0

            # Advance to last frame.
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 1
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 2

            # Should stay at frame 2 (last frame).
            enemy._update_sprite(0.11)
            assert overlay.frame_index == 2
            enemy._update_sprite(0.5)
            assert overlay.frame_index == 2

    def test_render_attack_effect_facing_right(self):
        """Effect should render at correct position when facing right."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir)
            overlay = enemy.attack_effect
            assert overlay is not None

            # Activate.
            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result
            enemy._update_sprite(0.0)
            enemy.facing_right = True

            surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            camera_offset = (0, 0)
            shrink = Enemy._HITBOX_SHRINK
            vis_x = enemy.rect.x - shrink
            vis_y = enemy.rect.bottom - enemy._sprite_h

            # Should not crash and should blit to the surface.
            enemy._render_attack_effect(surface, camera_offset, vis_x, vis_y)

            # Verify the expected position.
            enemy_center_x = vis_x + enemy._sprite_w // 2
            expected_x = enemy_center_x + overlay.offset_x - overlay.frame_w // 2
            expected_y = vis_y + overlay.offset_y

            # Check that pixels in the expected region are not fully transparent.
            # (The placeholder sprite has non-transparent pixels.)
            pixel_color = surface.get_at((expected_x + overlay.frame_w // 2, expected_y + overlay.frame_h // 2))
            assert pixel_color.a > 0

    def test_render_attack_effect_facing_left(self):
        """Effect should render flipped at mirrored position when facing left."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir)
            overlay = enemy.attack_effect
            assert overlay is not None

            # Activate.
            result = BehaviorResult()
            result.attack_state = AttackState.ATTACKING
            enemy._behavior_result = result
            enemy._update_sprite(0.0)
            enemy.facing_right = False

            surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            camera_offset = (0, 0)
            shrink = Enemy._HITBOX_SHRINK
            vis_x = enemy.rect.x - shrink
            vis_y = enemy.rect.bottom - enemy._sprite_h

            enemy._render_attack_effect(surface, camera_offset, vis_x, vis_y)

            # When facing left, the offset_x is negated.
            enemy_center_x = vis_x + enemy._sprite_w // 2
            expected_x = enemy_center_x - overlay.offset_x - overlay.frame_w // 2
            expected_y = vis_y + overlay.offset_y

            pixel_color = surface.get_at((expected_x + overlay.frame_w // 2, expected_y + overlay.frame_h // 2))
            assert pixel_color.a > 0

    def test_render_skipped_when_no_effect(self):
        """Rendering should not crash when enemy has no attack effect."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            defs_path = _make_test_definitions(tmp_dir, with_effect=False)
            factory = EnemyFactory(defs_path)
            enemy = factory.create("test_enemy_no_effect", 100, 200)

            surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            # Should not raise.
            enemy._render_attack_effect(surface, (0, 0), 100, 180)

    def test_render_skipped_when_inactive(self):
        """No blit should happen when overlay exists but is inactive."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            enemy = _create_enemy_with_effect(tmp_dir)
            assert enemy.attack_effect is not None
            assert not enemy.attack_effect.active

            surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            surface.fill((0, 0, 0, 0))

            enemy._render_attack_effect(surface, (0, 0), 100, 180)

            # Surface should still be fully transparent (no blit occurred).
            # Check a sampling of pixels.
            for x in range(0, 400, 50):
                for y in range(0, 300, 50):
                    assert surface.get_at((x, y)).a == 0

    def test_shared_sprite_path(self):
        """Two enemies with the same sprite name should load from the same cache."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            import sa_fona.rendering.asset_loader as al

            original_root = al._PROJECT_ROOT
            al._PROJECT_ROOT = tmp_dir

            try:
                # Create sprite file.
                _make_effect_sprite(tmp_dir, "shared_effect", 16, 16, 3)

                defs = {
                    "enemy_a": {
                        "display_name": "Enemy A",
                        "health": 2,
                        "contact_damage": 1.0,
                        "behavior": "chase",
                        "behavior_params": {"chase_range": 4, "speed": 40},
                        "hitbox": {"w": 16, "h": 16},
                        "drops": {"stones": {"min": 1, "max": 1}, "heart_chance": 0.0},
                        "attack_effect": {
                            "sprite": "shared_effect",
                            "frame_w": 16,
                            "frame_h": 16,
                            "offset_x": 8,
                            "offset_y": 0,
                            "fps": 10.0,
                            "loop": False,
                            "show_during": ["attacking"],
                        },
                    },
                    "enemy_b": {
                        "display_name": "Enemy B",
                        "health": 2,
                        "contact_damage": 1.0,
                        "behavior": "chase",
                        "behavior_params": {"chase_range": 4, "speed": 40},
                        "hitbox": {"w": 16, "h": 16},
                        "drops": {"stones": {"min": 1, "max": 1}, "heart_chance": 0.0},
                        "attack_effect": {
                            "sprite": "shared_effect",
                            "frame_w": 16,
                            "frame_h": 16,
                            "offset_x": 8,
                            "offset_y": 0,
                            "fps": 10.0,
                            "loop": False,
                            "show_during": ["attacking"],
                        },
                    },
                }

                path = os.path.join(tmp_dir, "shared_test.json")
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(defs, fh)

                factory = EnemyFactory(path)
                a = factory.create("enemy_a", 0, 0)
                b = factory.create("enemy_b", 0, 0)

                assert a.attack_effect is not None
                assert b.attack_effect is not None

                # Both should have loaded from the same cache entry.
                # The frame_strip_cache uses path:WxH as key, so the
                # underlying Surface objects should be identical.
                assert a.attack_effect.frames[0] is b.attack_effect.frames[0]
            finally:
                al._PROJECT_ROOT = original_root
