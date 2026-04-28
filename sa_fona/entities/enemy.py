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
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from sa_fona.config.settings import DATA_DIR
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.entities.entity import Entity
from sa_fona.entities.enemy_behaviors import (
    AttackState,
    BehaviorResult,
    EnemyBehavior,
    create_behavior,
)
from sa_fona.entities.pickup import Pickup, PickupType
from sa_fona.rendering.asset_loader import load_frame_strip

if TYPE_CHECKING:
    from sa_fona.level.tilemap import TileMap

# Placeholder colors per enemy type.
_ENEMY_COLORS: dict[str, tuple[int, int, int]] = {
    "possessed_sheep": (240, 240, 240),      # white
    "rival_warrior": (139, 90, 43),           # brown
    "stone_guardian": (80, 80, 80),           # dark grey
    "legionary": (160, 50, 50),              # red (Roman)
    "war_dog": (120, 80, 40),                # dark brown
}

# Default color for unknown enemy types.
_DEFAULT_ENEMY_COLOR: tuple[int, int, int] = (200, 50, 50)

# Tell flash color (overlaid during attack tell).
_TELL_COLOR: tuple[int, int, int, int] = (255, 50, 50, 120)

# Block indicator color.
_BLOCK_COLOR: tuple[int, int, int, int] = (100, 100, 255, 120)

# Stun indicator color (yellow tint).
_STUN_COLOR: tuple[int, int, int, int] = (255, 255, 50, 100)

# Map of string names to AttackState enum values for JSON config.
_ATTACK_STATE_MAP: dict[str, AttackState] = {
    "idle": AttackState.IDLE,
    "tell": AttackState.TELL,
    "attacking": AttackState.ATTACKING,
    "recovery": AttackState.RECOVERY,
    "cooldown": AttackState.COOLDOWN,
}


@dataclass
class AttackEffectOverlay:
    """Data-driven overlay animation shown during enemy attack phases.

    Loaded from the ``attack_effect`` block in enemy JSON definitions.
    The overlay renders independently of the enemy's body sprite and
    is positioned relative to the enemy's visual center.

    Attributes:
        frames: List of pre-sliced animation frames.
        frame_w: Width of a single frame in pixels.
        frame_h: Height of a single frame in pixels.
        offset_x: Pixel offset from enemy visual center in facing direction.
        offset_y: Pixel offset from enemy visual top (negative = above).
        show_during: Set of AttackState values that activate the overlay.
        fps: Playback speed in frames per second.
        loop: Whether the animation loops or clamps at the last frame.
        timer: Internal animation timer.
        frame_index: Current frame index.
        active: Whether the overlay is currently being displayed.
        _prev_active: Previous frame's active state for edge detection.
    """

    frames: list[pygame.Surface]
    frame_w: int
    frame_h: int
    offset_x: int
    offset_y: int
    show_during: set
    fps: float
    loop: bool
    timer: float = 0.0
    frame_index: int = 0
    active: bool = False
    _prev_active: bool = False


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

    _HITBOX_SHRINK: int = 2

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str,
        definition: dict,
    ) -> None:
        sprite_w = definition.get("hitbox", {}).get("w", 16)
        sprite_h = definition.get("hitbox", {}).get("h", 16)
        shrink = self._HITBOX_SHRINK
        width = max(4, sprite_w - shrink * 2)
        height = max(4, sprite_h - shrink * 2)
        super().__init__(x + shrink, y + shrink, width, height)

        self.enemy_type: str = enemy_type
        self.display_name: str = definition.get("display_name", enemy_type)
        self.health: float = float(definition.get("health", 1))
        self.max_health: float = self.health
        self.contact_damage: float = float(definition.get("contact_damage", 0.5))
        self.attack_damage: float = float(
            definition.get("attack_damage", self.contact_damage)
        )

        # Drop table.
        drops = definition.get("drops", {})
        self._stones_min: int = drops.get("stones", {}).get("min", 1)
        self._stones_max: int = drops.get("stones", {}).get("max", 2)
        self._heart_chance: float = drops.get("heart_chance", 0.1)

        # Attack hitbox width extension (0 = body IS the hitbox).
        self._attack_hitbox_w: int = int(definition.get("attack_hitbox_w", 16))

        # Behavior component.
        behavior_type = definition.get("behavior", "patrol")
        behavior_params = definition.get("behavior_params", {})
        self.behavior: EnemyBehavior = create_behavior(behavior_type, behavior_params)
        self.behavior.reset(x + shrink)

        # Current behavior result (updated each frame).
        self._behavior_result: BehaviorResult = BehaviorResult()

        # Invincibility frames for the enemy after taking damage.
        self._invincibility_timer: float = 0.0
        self._invincibility_duration: float = 0.3  # Brief flash on hit.

        # Stun state: when stunned, the enemy can't move or attack.
        self._stun_timer: float = 0.0

        # Sub-pixel position accumulator for smooth low-speed movement.
        self._sub_x: float = float(self.rect.x)

        # Build placeholder sprite (visual size, larger than hitbox).
        self._sprite_w = sprite_w
        self._sprite_h = sprite_h
        self._base_color = _ENEMY_COLORS.get(enemy_type, _DEFAULT_ENEMY_COLOR)

        self._idle_frames: list[pygame.Surface] = []
        self._walk_frames: list[pygame.Surface] = []
        self._charge_frames: list[pygame.Surface] = []
        self._attack_frames: list[pygame.Surface] = []
        self._block_frames: list[pygame.Surface] = []
        self._hit_frames: list[pygame.Surface] = []
        self._death_frames: list[pygame.Surface] = []
        self._anim_timer: float = 0.0
        self._anim_frame: int = 0
        self._anim_speed: float = 0.2
        self._walk_anim_speed: float = 0.12
        self._has_sprites: bool = False

        # Death animation state.
        self._playing_death: bool = False
        self._death_timer: float = 0.0
        self._death_frame: int = 0

        self._build_sprite()

        # Attack effect overlay (loaded from definition if present).
        self._attack_effect: AttackEffectOverlay | None = None
        self._load_attack_effect(definition)

        # Font for label (only used when no sprites).
        self._font: pygame.font.Font | None = None

    def _build_sprite(self) -> None:
        """Load real sprites or create a placeholder colored rectangle.

        If the loaded frames don't match ``_sprite_w x _sprite_h`` (e.g.
        a rival_warrior drawn at 16x24 but intended to display at 24x32),
        each frame is scaled up to the target visual size.
        """
        # Load all available animation states.
        anim_map = {
            "_idle_frames": "idle",
            "_walk_frames": "walk",
            "_charge_frames": "charge",
            "_attack_frames": "attack",
            "_block_frames": "block",
            "_hit_frames": "hit",
            "_death_frames": "death",
        }
        for attr, suffix in anim_map.items():
            # First try loading at the target visual size.
            frames = load_frame_strip(
                f"assets/sprites/enemies/{self.enemy_type}_{suffix}.png",
                self._sprite_w, self._sprite_h,
            )
            if not frames:
                # Try loading at the file's native frame dimensions and
                # scale up to the target visual size afterwards.
                frames = self._load_and_scale_frames(
                    f"assets/sprites/enemies/{self.enemy_type}_{suffix}.png",
                )
            if frames:
                setattr(self, attr, frames)
                self._has_sprites = True

        if self._has_sprites:
            self._sprite = (self._idle_frames or self._walk_frames or [None])[0]
            if self._sprite is None:
                # Use any available frames.
                for attr in anim_map:
                    frames_list = getattr(self, attr)
                    if frames_list:
                        self._sprite = frames_list[0]
                        break
        else:
            surf = pygame.Surface((self._sprite_w, self._sprite_h))
            surf.fill(self._base_color)
            border_color = tuple(max(0, c - 40) for c in self._base_color)
            pygame.draw.rect(surf, border_color, (0, 0, self._sprite_w, self._sprite_h), 1)
            self._sprite = surf

    def _load_and_scale_frames(
        self, path: str,
    ) -> list[pygame.Surface] | None:
        """Try common frame sizes and scale results to visual size.

        Iterates over typical frame dimensions that the sprite file may
        have been authored at.  When a match is found the frames are
        scaled to ``_sprite_w x _sprite_h``.

        Args:
            path: Relative path to the sprite strip.

        Returns:
            Scaled frame list, or None.
        """
        # Common original frame sizes to try (width, height).
        # Larger sizes first to avoid cropping (e.g. 16x16 matching a 16x24 strip).
        candidates = [(24, 32), (16, 24), (24, 24), (16, 16)]
        for fw, fh in candidates:
            if fw == self._sprite_w and fh == self._sprite_h:
                continue  # Already tried at target size.
            frames = load_frame_strip(path, fw, fh)
            if frames:
                # Scale each frame to the target visual dimensions.
                scaled = [
                    pygame.transform.scale(f, (self._sprite_w, self._sprite_h))
                    for f in frames
                ]
                return scaled
        return None

    def _load_attack_effect(self, definition: dict) -> None:
        """Load an attack effect overlay from the enemy definition.

        If the definition contains an ``attack_effect`` block, loads
        the sprite strip from ``assets/sprites/enemies/effects/`` and
        constructs an :class:`AttackEffectOverlay`. If the sprite file
        is missing or no config is present, ``_attack_effect`` remains
        None.

        Args:
            definition: The full enemy definition dict from JSON.
        """
        effect_cfg = definition.get("attack_effect")
        if effect_cfg is None:
            return

        sprite_name = effect_cfg.get("sprite", "")
        frame_w = int(effect_cfg.get("frame_w", 16))
        frame_h = int(effect_cfg.get("frame_h", 16))
        sprite_path = f"assets/sprites/enemies/effects/{sprite_name}.png"

        frames = load_frame_strip(sprite_path, frame_w, frame_h)
        if not frames:
            return

        # Map string state names to AttackState enum values.
        show_during_strs = effect_cfg.get("show_during", [])
        show_during: set[AttackState] = set()
        for state_str in show_during_strs:
            state = _ATTACK_STATE_MAP.get(state_str.lower())
            if state is not None:
                show_during.add(state)

        if not show_during:
            return

        self._attack_effect = AttackEffectOverlay(
            frames=frames,
            frame_w=frame_w,
            frame_h=frame_h,
            offset_x=int(effect_cfg.get("offset_x", 0)),
            offset_y=int(effect_cfg.get("offset_y", 0)),
            show_during=show_during,
            fps=float(effect_cfg.get("fps", 10.0)),
            loop=bool(effect_cfg.get("loop", False)),
        )

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
    def is_recovering(self) -> bool:
        """Whether the enemy is in post-attack recovery."""
        return self._behavior_result.attack_state == AttackState.RECOVERY

    @property
    def is_blocking(self) -> bool:
        """Whether the enemy is currently blocking."""
        return self._behavior_result.is_blocking

    @property
    def behavior_result(self) -> BehaviorResult:
        """The current frame's behavior result."""
        return self._behavior_result

    @property
    def is_stunned(self) -> bool:
        """Whether the enemy is currently stunned."""
        return self._stun_timer > 0

    @property
    def attack_effect(self) -> AttackEffectOverlay | None:
        """The attack effect overlay, or None if not configured."""
        return self._attack_effect

    @property
    def attack_hitbox(self) -> pygame.Rect:
        """Return the active attack hitbox when the enemy is striking.

        When ``_attack_hitbox_w`` is 0 the enemy's own body rect is
        the weapon (e.g. sheep headbutt).  Otherwise the hitbox extends
        ``_attack_hitbox_w`` pixels in the direction the enemy faces.

        Only meaningful when ``is_attacking`` is True.

        Returns:
            A pygame.Rect representing the attack hitbox.
        """
        if self._attack_hitbox_w == 0:
            # Body IS the weapon (e.g. possessed sheep headbutt).
            return self.rect.copy()

        hitbox_w = self._attack_hitbox_w
        hitbox_h = self.rect.height + 4
        if self.facing_right:
            hx = self.rect.right
        else:
            hx = self.rect.left - hitbox_w
        hy = self.rect.top - 2
        return pygame.Rect(hx, hy, hitbox_w, hitbox_h)

    def stun(self, duration: float) -> None:
        """Apply a stun effect for the given duration.

        While stunned, the enemy cannot move or attack. Extends the
        stun if the new duration is longer than the remaining stun.

        Args:
            duration: Stun duration in seconds.
        """
        if duration > self._stun_timer:
            self._stun_timer = duration

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

    def snap_position(self, bottom: int) -> None:
        """Reposition the enemy vertically and sync sub-pixel tracking."""
        self.rect.bottom = bottom
        self._sub_x = float(self.rect.x)

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
        tilemap: TileMap | None = None,
    ) -> None:
        """Update behavior and apply movement.

        While stunned, the enemy skips all behavior updates and remains
        stationary.

        Args:
            player_rect: The player's bounding box.
            dt: Delta time in seconds.
            tilemap: Optional tilemap for edge detection in behaviors.
        """
        # Tick invincibility.
        if self._invincibility_timer > 0:
            self._invincibility_timer -= dt

        # Tick stun timer.
        if self._stun_timer > 0:
            self._stun_timer -= dt
            self.velocity[0] = 0.0
            return

        # Get behavior decision.
        self._behavior_result = self.behavior.update(
            self.rect, player_rect, dt, tilemap=tilemap
        )

        # Apply movement.
        move_x = self._behavior_result.move_x
        speed = self._behavior_result.speed

        if move_x != 0:
            self.velocity[0] = move_x * speed
            self.facing_right = move_x > 0
        else:
            self.velocity[0] = 0.0

        # Sub-pixel movement: accumulate float position, snap rect to int.
        self._sub_x += self.velocity[0] * dt
        self.rect.x = round(self._sub_x)

        if tilemap is not None and self.velocity[0] != 0:
            self._resolve_wall_collision(tilemap)

        self._update_sprite(dt)

    def _resolve_wall_collision(self, tilemap: TileMap) -> None:
        """Push enemy out of solid tiles after horizontal movement."""
        top_ty = self.rect.top // TILE_SIZE
        bot_ty = (self.rect.bottom - 1) // TILE_SIZE

        if self.velocity[0] > 0:
            right_tx = (self.rect.right - 1) // TILE_SIZE
            for ty in range(top_ty, bot_ty + 1):
                if tilemap.is_solid_at(right_tx, ty):
                    self.rect.right = right_tx * TILE_SIZE
                    self._sub_x = float(self.rect.x)
                    self.velocity[0] = 0
                    return
        elif self.velocity[0] < 0:
            left_tx = self.rect.left // TILE_SIZE
            for ty in range(top_ty, bot_ty + 1):
                if tilemap.is_solid_at(left_tx, ty):
                    self.rect.left = (left_tx + 1) * TILE_SIZE
                    self._sub_x = float(self.rect.x)
                    self.velocity[0] = 0
                    return

    def _update_sprite(self, dt: float) -> None:
        """Select the correct sprite frame based on combat/movement state."""
        if not self._has_sprites:
            # Still update the attack effect overlay even for placeholder enemies.
            self._update_attack_effect(dt)
            return

        # Determine which frame set to use based on state.
        frames: list[pygame.Surface] | None = None
        speed = self._anim_speed

        if self._playing_death and self._death_frames:
            frames = self._death_frames
            speed = 0.15
        elif self._invincibility_timer > 0 and self._hit_frames:
            frames = self._hit_frames
            speed = 0.15
        elif self.is_blocking and self._block_frames:
            frames = self._block_frames
            speed = self._anim_speed
        elif (self.is_attacking or self.is_in_tell or self.is_recovering) and self._attack_frames:
            frames = self._attack_frames
            speed = 0.12
        elif self.is_in_tell and self._charge_frames:
            frames = self._charge_frames
            speed = 0.12
        else:
            is_moving = abs(self.velocity[0]) > 0.5
            if is_moving and self._walk_frames:
                frames = self._walk_frames
                speed = self._walk_anim_speed
            else:
                frames = self._idle_frames

        if not frames:
            return

        self._anim_timer += dt
        if self._anim_timer >= speed:
            self._anim_timer -= speed
            self._anim_frame = (self._anim_frame + 1) % len(frames)
        if self._anim_frame >= len(frames):
            self._anim_frame = 0

        base = frames[self._anim_frame]
        if not self.facing_right:
            self._sprite = pygame.transform.flip(base, True, False)
        else:
            self._sprite = base

        # Update attack effect overlay animation.
        self._update_attack_effect(dt)

    def _update_attack_effect(self, dt: float) -> None:
        """Advance the attack effect overlay animation state.

        Checks if the current attack state is in the overlay's
        ``show_during`` set. Handles activation edge (reset timer),
        frame advancement, and loop/clamp behavior.

        Args:
            dt: Delta time in seconds.
        """
        overlay = self._attack_effect
        if overlay is None:
            return

        current_state = self._behavior_result.attack_state
        should_be_active = current_state in overlay.show_during

        # Edge detection: inactive -> active resets animation.
        if should_be_active and not overlay.active:
            overlay.timer = 0.0
            overlay.frame_index = 0

        overlay._prev_active = overlay.active
        overlay.active = should_be_active

        if not overlay.active:
            return

        # Advance timer.
        if overlay.fps > 0 and len(overlay.frames) > 1:
            frame_duration = 1.0 / overlay.fps
            overlay.timer += dt
            if overlay.timer >= frame_duration:
                overlay.timer -= frame_duration
                if overlay.loop:
                    overlay.frame_index = (overlay.frame_index + 1) % len(
                        overlay.frames
                    )
                else:
                    overlay.frame_index = min(
                        overlay.frame_index + 1, len(overlay.frames) - 1
                    )

    def _render_attack_effect(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
        vis_x: int,
        vis_y: int,
    ) -> None:
        """Draw the attack effect overlay relative to the enemy sprite.

        The overlay is positioned using ``offset_x`` (in the facing
        direction) and ``offset_y`` from the enemy's visual top-left
        corner.  When facing left the frame is flipped horizontally
        and the X offset is negated.

        Args:
            surface: Target pygame Surface.
            camera_offset: ``(cam_x, cam_y)`` world-pixel camera offset.
            vis_x: Screen X of the enemy's visual top-left corner.
            vis_y: Screen Y of the enemy's visual top-left corner.
        """
        overlay = self._attack_effect
        if overlay is None or not overlay.active:
            return

        if overlay.frame_index >= len(overlay.frames):
            return

        frame = overlay.frames[overlay.frame_index]

        # Compute position relative to enemy visual center.
        enemy_center_x = vis_x + self._sprite_w // 2

        if self.facing_right:
            eff_x = enemy_center_x + overlay.offset_x - overlay.frame_w // 2
            blit_frame = frame
        else:
            eff_x = enemy_center_x - overlay.offset_x - overlay.frame_w // 2
            blit_frame = pygame.transform.flip(frame, True, False)

        eff_y = vis_y + overlay.offset_y

        surface.blit(blit_frame, (eff_x, eff_y))

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

        # Invincibility blink: alternate visibility every 0.06 seconds.
        if self._invincibility_timer > 0:
            blink_phase = int(self._invincibility_timer / 0.06)
            if blink_phase % 2 == 1:
                return

        # Align the visual sprite so its bottom matches the hitbox bottom
        # (feet on ground) and it is horizontally centered on the hitbox.
        shrink = self._HITBOX_SHRINK
        vis_x = self.rect.x - camera_offset[0] - shrink
        vis_y = self.rect.bottom - self._sprite_h - camera_offset[1]

        if self._sprite is not None:
            surface.blit(self._sprite, (vis_x, vis_y))

        # Render attack effect overlay (data-driven, independent of body).
        self._render_attack_effect(surface, camera_offset, vis_x, vis_y)

        # State overlays are only drawn for placeholder enemies (no real
        # sprites).  When real sprites are loaded, the animation frames
        # already communicate the state (charge, attack, block, hit).
        if not self._has_sprites:
            if self.is_in_tell:
                tell_surf = pygame.Surface(
                    (self._sprite_w, self._sprite_h), pygame.SRCALPHA
                )
                tell_surf.fill(_TELL_COLOR)
                surface.blit(tell_surf, (vis_x, vis_y))

            if self.is_blocking:
                block_surf = pygame.Surface(
                    (self._sprite_w, self._sprite_h), pygame.SRCALPHA
                )
                block_surf.fill(_BLOCK_COLOR)
                surface.blit(block_surf, (vis_x, vis_y))

            if self.is_stunned:
                blink_phase = int(self._stun_timer / 0.15)
                if blink_phase % 2 == 0:
                    stun_surf = pygame.Surface(
                        (self._sprite_w, self._sprite_h), pygame.SRCALPHA
                    )
                    stun_surf.fill(_STUN_COLOR)
                    surface.blit(stun_surf, (vis_x, vis_y))

            try:
                if self._font is None:
                    self._font = pygame.font.Font(None, 14)
                label_char = self.enemy_type[0].upper()
                label = self._font.render(label_char, False, (0, 0, 0))
                lx = vis_x + (self._sprite_w - label.get_width()) // 2
                ly = vis_y + (self._sprite_h - label.get_height()) // 2
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
        use_default = definitions_path is None
        if definitions_path is None:
            definitions_path = str(
                DATA_DIR / "enemies" / "world1_enemies.json"
            )
        self._definitions: dict[str, dict] = {}
        self._load_definitions(definitions_path)
        # When using the default path, also load all other enemy definition
        # files from the same directory so that cross-world levels (e.g.
        # W2 accessed from W1 boss) can spawn any enemy type.
        if use_default:
            self._load_all_definitions()

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

    def _load_all_definitions(self) -> None:
        """Load all enemy definition files from the enemies data directory.

        Merges definitions from every ``*_enemies.json`` file found in the
        ``data/enemies/`` directory.  Existing definitions take priority
        (will not be overwritten).
        """
        enemies_dir = DATA_DIR / "enemies"
        if not enemies_dir.is_dir():
            return
        for path in sorted(enemies_dir.glob("*_enemies.json")):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    defs = json.load(fh)
                for key, value in defs.items():
                    if key not in self._definitions:
                        self._definitions[key] = value
            except (FileNotFoundError, json.JSONDecodeError):
                pass

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
        tx = entity_def.get("x", 0) * TILE_SIZE
        ty = entity_def.get("y", 0) * TILE_SIZE
        return self.create(enemy_type, tx, ty)
