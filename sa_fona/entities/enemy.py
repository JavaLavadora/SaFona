"""Enemy entity and EnemyFactory for JSON-driven enemy creation.

The Enemy base class extends Entity with health, contact damage, behavior
reference, and drop table.  Enemies are created by the EnemyFactory which
reads definitions from JSON files (one per world).

Placeholder rendering uses different colored rectangles per enemy type:
- Possessed sheep: white
- Rival tribal warrior: brown (139, 90, 43)
- Stone guardian: dark grey (80, 80, 80)
"""

from __future__ import annotations

import json
import random
from typing import Any

import pygame

from sa_fona.config.settings import DATA_DIR
from sa_fona.entities.entity import Entity
from sa_fona.entities.enemy_behaviors import (
    AttackState,
    BehaviorResult,
    EnemyBehavior,
    create_behavior,
)
from sa_fona.entities.pickup import Pickup, PickupType

# Tile size for converting tile units to pixels.
_TILE_SIZE = 16

# Placeholder colors per enemy type.
_ENEMY_COLORS: dict[str, tuple[int, int, int]] = {
    "possessed_sheep": (240, 240, 240),      # white
    "rival_warrior": (139, 90, 43),           # brown
    "stone_guardian": (80, 80, 80),           # dark grey
}

# Default color for unknown enemy types.
_DEFAULT_ENEMY_COLOR: tuple[int, int, int] = (200, 50, 50)

# Tell flash color (overlaid during attack tell).
_TELL_COLOR: tuple[int, int, int, int] = (255, 50, 50, 120)

# Block indicator color.
_BLOCK_COLOR: tuple[int, int, int, int] = (100, 100, 255, 120)


class Enemy(Entity):
    """An enemy entity with health, damage, behavior, and drops.

    Enemies are controlled by a behavior component that decides movement
    and attack patterns.  The combat system handles damage resolution.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        enemy_type: The type key (e.g. "possessed_sheep").
        definition: The full definition dict from the enemy JSON.
    """

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str,
        definition: dict,
    ) -> None:
        width = definition.get("hitbox", {}).get("w", 16)
        height = definition.get("hitbox", {}).get("h", 16)
        super().__init__(x, y, width, height)

        self.enemy_type: str = enemy_type
        self.display_name: str = definition.get("display_name", enemy_type)
        self.health: float = float(definition.get("health", 1))
        self.max_health: float = self.health
        self.contact_damage: float = float(definition.get("contact_damage", 0.5))

        # Drop table.
        drops = definition.get("drops", {})
        self._stones_min: int = drops.get("stones", {}).get("min", 1)
        self._stones_max: int = drops.get("stones", {}).get("max", 2)
        self._heart_chance: float = drops.get("heart_chance", 0.1)

        # Behavior component.
        behavior_type = definition.get("behavior", "patrol")
        behavior_params = definition.get("behavior_params", {})
        self.behavior: EnemyBehavior = create_behavior(behavior_type, behavior_params)
        self.behavior.reset(x)

        # Current behavior result (updated each frame).
        self._behavior_result: BehaviorResult = BehaviorResult()

        # Invincibility frames for the enemy after taking damage.
        self._invincibility_timer: float = 0.0
        self._invincibility_duration: float = 0.3  # Brief flash on hit.

        # Build placeholder sprite.
        self._width = width
        self._height = height
        self._base_color = _ENEMY_COLORS.get(enemy_type, _DEFAULT_ENEMY_COLOR)
        self._build_sprite()

        # Font for label.
        self._font: pygame.font.Font | None = None

    def _build_sprite(self) -> None:
        """Create a placeholder colored rectangle sprite."""
        surf = pygame.Surface((self._width, self._height))
        surf.fill(self._base_color)
        # Border for visibility.
        border_color = tuple(max(0, c - 40) for c in self._base_color)
        pygame.draw.rect(surf, border_color, (0, 0, self._width, self._height), 1)
        self._sprite = surf

    # ── Properties ─────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        """Whether the enemy still has health remaining."""
        return self.health > 0 and self.active

    @property
    def is_invincible(self) -> bool:
        """Whether the enemy is in invincibility frames."""
        return self._invincibility_timer > 0

    @property
    def is_attacking(self) -> bool:
        """Whether the enemy is currently in an attack state."""
        return self._behavior_result.attack_state == AttackState.ATTACKING

    @property
    def is_in_tell(self) -> bool:
        """Whether the enemy is showing an attack tell."""
        return self._behavior_result.attack_state == AttackState.TELL

    @property
    def is_blocking(self) -> bool:
        """Whether the enemy is currently blocking."""
        return self._behavior_result.is_blocking

    @property
    def behavior_result(self) -> BehaviorResult:
        """The current frame's behavior result."""
        return self._behavior_result

    @property
    def stones_min(self) -> int:
        """Minimum stone drop amount."""
        return self._stones_min

    @property
    def stones_max(self) -> int:
        """Maximum stone drop amount."""
        return self._stones_max

    @property
    def heart_chance(self) -> float:
        """Probability of dropping a heart pickup."""
        return self._heart_chance

    # ── Combat ─────────────────────────────────────────────────────

    def take_damage(self, amount: float) -> bool:
        """Apply damage to this enemy.

        Respects invincibility frames.  Returns True if damage was
        actually applied.

        Args:
            amount: Damage amount in health points.

        Returns:
            True if the damage was applied, False if blocked or invincible.
        """
        if self._invincibility_timer > 0:
            return False

        self.health -= amount
        self._invincibility_timer = self._invincibility_duration

        if self.health <= 0:
            self.health = 0
            self.active = False

        return True

    def get_drops(self) -> list[Pickup]:
        """Generate pickup drops when this enemy dies.

        Returns:
            A list of Pickup entities to spawn at the enemy's position.
        """
        pickups: list[Pickup] = []

        # Stone drops.
        stone_count = random.randint(self._stones_min, self._stones_max)
        for _ in range(stone_count):
            offset_x = random.randint(-12, 12)
            offset_y = random.randint(-16, 0)
            pickup = Pickup(
                x=self.rect.centerx + offset_x,
                y=self.rect.top + offset_y,
                pickup_type=PickupType.STONE,
                value=1.0,
            )
            pickups.append(pickup)

        # Heart drop (chance-based).
        if random.random() < self._heart_chance:
            pickup = Pickup(
                x=self.rect.centerx,
                y=self.rect.top - 8,
                pickup_type=PickupType.HEART,
                value=1.0,
            )
            pickups.append(pickup)

        return pickups

    # ── Update / Render ────────────────────────────────────────────

    def update(self, dt: float) -> None:
        """Update is a no-op; use update_with_player instead.

        Args:
            dt: Delta time in seconds.
        """
        pass

    def update_with_player(
        self,
        player_rect: pygame.Rect,
        dt: float,
    ) -> None:
        """Update behavior and apply movement.

        Args:
            player_rect: The player's bounding box.
            dt: Delta time in seconds.
        """
        # Tick invincibility.
        if self._invincibility_timer > 0:
            self._invincibility_timer -= dt

        # Get behavior decision.
        self._behavior_result = self.behavior.update(
            self.rect, player_rect, dt
        )

        # Apply movement.
        move_x = self._behavior_result.move_x
        speed = self._behavior_result.speed

        if move_x != 0:
            self.velocity[0] = move_x * speed
            self.facing_right = move_x > 0
        else:
            self.velocity[0] = 0.0

        # Move the rect (simple horizontal movement, no physics).
        dx = self.velocity[0] * dt
        self.rect.x += round(dx)

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the enemy with visual state indicators.

        Shows attack tell (red flash), blocking (blue tint), and
        invincibility blink.

        Args:
            surface: Target pygame Surface.
            camera_offset: ``(cam_x, cam_y)`` world-pixel camera offset.
        """
        if not self.active:
            return

        # Invincibility blink: skip rendering every other 0.1s.
        if self._invincibility_timer > 0:
            # Blink: alternate visibility every 0.06 seconds.
            blink_phase = int(self._invincibility_timer / 0.06)
            if blink_phase % 2 == 1:
                return

        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]

        # Draw base sprite.
        if self._sprite is not None:
            surface.blit(self._sprite, (screen_x, screen_y))

        # Attack tell overlay (red flash).
        if self.is_in_tell:
            tell_surf = pygame.Surface(
                (self._width, self._height), pygame.SRCALPHA
            )
            tell_surf.fill(_TELL_COLOR)
            surface.blit(tell_surf, (screen_x, screen_y))

        # Block indicator overlay (blue tint).
        if self.is_blocking:
            block_surf = pygame.Surface(
                (self._width, self._height), pygame.SRCALPHA
            )
            block_surf.fill(_BLOCK_COLOR)
            surface.blit(block_surf, (screen_x, screen_y))

        # Draw a label with the first letter of the enemy type.
        try:
            if self._font is None:
                self._font = pygame.font.Font(None, 14)
            label_char = self.enemy_type[0].upper()
            label = self._font.render(label_char, False, (0, 0, 0))
            lx = screen_x + (self._width - label.get_width()) // 2
            ly = screen_y + (self._height - label.get_height()) // 2
            surface.blit(label, (lx, ly))
        except (pygame.error, IndexError):
            pass


class EnemyFactory:
    """Creates enemy instances from JSON definitions.

    Enemy types are defined in data/enemies/worldN_enemies.json.
    Each definition specifies: type ID, health, damage, behavior,
    sprite, hitbox, drop table, and vulnerabilities.

    Args:
        definitions_path: Path to the enemy definitions JSON file.
            Defaults to world1_enemies.json.
    """

    def __init__(
        self,
        definitions_path: str | None = None,
    ) -> None:
        if definitions_path is None:
            definitions_path = str(
                DATA_DIR / "enemies" / "world1_enemies.json"
            )
        self._definitions: dict[str, dict] = {}
        self._load_definitions(definitions_path)

    def _load_definitions(self, path: str) -> None:
        """Load enemy definitions from a JSON file.

        Args:
            path: Path to the JSON file.
        """
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self._definitions = json.load(fh)
        except FileNotFoundError:
            self._definitions = {}

    @property
    def definitions(self) -> dict[str, dict]:
        """All loaded enemy definitions (read-only)."""
        return self._definitions

    def create(
        self,
        enemy_type: str,
        x: float,
        y: float,
    ) -> Enemy:
        """Create an enemy of the given type at the given position.

        Args:
            enemy_type: The enemy type key (e.g. "possessed_sheep").
            x: X position in world pixels.
            y: Y position in world pixels.

        Returns:
            A configured Enemy instance.

        Raises:
            ValueError: If the enemy type is not defined.
        """
        definition = self._definitions.get(enemy_type)
        if definition is None:
            raise ValueError(
                f"Unknown enemy type: {enemy_type!r}. "
                f"Available: {list(self._definitions.keys())}"
            )
        return Enemy(x, y, enemy_type, definition)

    def create_from_entity_def(self, entity_def: dict) -> Enemy:
        """Create an enemy from a level entity definition dict.

        The entity_def comes from the level JSON's entities list
        with type="enemy", enemy_type="...", x=..., y=... in tile coords.

        Args:
            entity_def: Dict with enemy_type, x, y (tile coordinates).

        Returns:
            A configured Enemy instance.
        """
        enemy_type = entity_def.get("enemy_type", "possessed_sheep")
        tx = entity_def.get("x", 0) * _TILE_SIZE
        ty = entity_def.get("y", 0) * _TILE_SIZE
        return self.create(enemy_type, tx, ty)
