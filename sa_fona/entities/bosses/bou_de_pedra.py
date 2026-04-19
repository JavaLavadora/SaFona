"""Es Bou de Pedra -- World 1 boss (The Stone Bull).

A massive stone bull animated by dimoni energy from a talayotic
sanctuary.  The first real test of the player's mastery of movement,
jumping, wall jumping, and sling combat.

Three phases:
  Phase 1 (100-66% HP): Bull Rush, Headbutt
  Phase 2 (66-33% HP): Faster Bull Rush, Ground Stomp, Rock Hurl
  Phase 3 (33-0% HP): Frenzy Rush, Core Pulse, Exposed Core
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from sa_fona.core.event_bus import EventBus
from sa_fona.entities.boss_entity import BossEntity, BossState
from sa_fona.level.tilemap import TILE_SIZE
from sa_fona.rendering.sprite_renderer import load_sprite_sheet_from_file

if TYPE_CHECKING:
    pass


# Pre-load boss sub-element sprites (cached at module level).
_boss_rock_sprite: pygame.Surface | None = None
_boss_shockwave_sprite: pygame.Surface | None = None
_boss_pulse_sprite: pygame.Surface | None = None
_boss_shadow_sprite: pygame.Surface | None = None
_pillar_intact_sprite: pygame.Surface | None = None
_pillar_destroyed_sprite: pygame.Surface | None = None
_boss_sprites_loaded: bool = False


def _load_boss_sub_sprites() -> None:
    """Load boss sub-element sprites once."""
    global _boss_rock_sprite, _boss_shockwave_sprite, _boss_pulse_sprite
    global _boss_shadow_sprite, _pillar_intact_sprite, _pillar_destroyed_sprite
    global _boss_sprites_loaded

    if _boss_sprites_loaded:
        return
    _boss_sprites_loaded = True

    frames = load_sprite_sheet_from_file("assets/sprites/boss/boss_rock.png", 8, 8)
    if frames:
        _boss_rock_sprite = frames[0]

    frames = load_sprite_sheet_from_file("assets/sprites/boss/boss_shockwave.png", 16, 8)
    if frames:
        _boss_shockwave_sprite = frames[0]

    frames = load_sprite_sheet_from_file("assets/sprites/boss/boss_pulse.png", 24, 16)
    if frames:
        _boss_pulse_sprite = frames[0]

    frames = load_sprite_sheet_from_file("assets/sprites/boss/boss_shadow.png", 16, 6)
    if frames:
        _boss_shadow_sprite = frames[0]

    frames = load_sprite_sheet_from_file("assets/sprites/boss/pillar_intact.png", 16, 48)
    if frames:
        _pillar_intact_sprite = frames[0]

    frames = load_sprite_sheet_from_file("assets/sprites/boss/pillar_destroyed.png", 16, 48)
    if frames:
        _pillar_destroyed_sprite = frames[0]


class BossProjectile:
    """A simple projectile spawned by boss attacks (rocks, shockwaves).

    Args:
        x: X position in world pixels.
        y: Y position in world pixels.
        width: Width in pixels.
        height: Height in pixels.
        vx: Horizontal velocity in px/s.
        vy: Vertical velocity in px/s.
        damage: Damage dealt on contact.
        lifetime: How long this projectile lives in seconds.
        proj_type: Type identifier for rendering.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: int,
        height: int,
        vx: float,
        vy: float,
        damage: float,
        lifetime: float,
        proj_type: str = "rock",
    ) -> None:
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.lifetime = lifetime
        self.timer: float = 0.0
        self.active: bool = True
        self.proj_type = proj_type
        self._sub_x: float = float(self.rect.x)
        self._sub_y: float = float(self.rect.y)

    def update(self, dt: float) -> None:
        """Move the projectile and check lifetime.

        Args:
            dt: Delta time in seconds.
        """
        self._sub_x += self.vx * dt
        self._sub_y += self.vy * dt
        self.rect.x = round(self._sub_x)
        self.rect.y = round(self._sub_y)
        self.timer += dt
        if self.timer >= self.lifetime:
            self.active = False

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the projectile using sprites or fallback shapes.

        Args:
            surface: Target surface.
            camera_offset: Camera offset.
        """
        if not self.active:
            return
        _load_boss_sub_sprites()
        sx = self.rect.x - camera_offset[0]
        sy = self.rect.y - camera_offset[1]

        if self.proj_type == "rock":
            if _boss_rock_sprite is not None:
                # Scale to match projectile rect if needed.
                if (_boss_rock_sprite.get_width() != self.rect.width
                        or _boss_rock_sprite.get_height() != self.rect.height):
                    scaled = pygame.transform.scale(
                        _boss_rock_sprite, (self.rect.width, self.rect.height),
                    )
                    surface.blit(scaled, (sx, sy))
                else:
                    surface.blit(_boss_rock_sprite, (sx, sy))
            else:
                pygame.draw.circle(
                    surface, (120, 100, 80),
                    (sx + self.rect.width // 2, sy + self.rect.height // 2),
                    self.rect.width // 2,
                )
        elif self.proj_type == "shockwave":
            if _boss_shockwave_sprite is not None:
                scaled = pygame.transform.scale(
                    _boss_shockwave_sprite, (self.rect.width, self.rect.height),
                )
                surface.blit(scaled, (sx, sy))
            else:
                shock_surf = pygame.Surface(
                    (self.rect.width, self.rect.height), pygame.SRCALPHA
                )
                shock_surf.fill((200, 180, 60, 160))
                surface.blit(shock_surf, (sx, sy))
        elif self.proj_type == "pulse":
            if _boss_pulse_sprite is not None:
                scaled = pygame.transform.scale(
                    _boss_pulse_sprite, (self.rect.width, self.rect.height),
                )
                surface.blit(scaled, (sx, sy))
            else:
                pulse_surf = pygame.Surface(
                    (self.rect.width, self.rect.height), pygame.SRCALPHA
                )
                pulse_surf.fill((255, 80, 80, 120))
                surface.blit(pulse_surf, (sx, sy))


class ShadowMarker:
    """Visual indicator showing where a rock will land.

    Args:
        x: Center X in world pixels.
        y: Y position (ground level) in world pixels.
        duration: How long the marker is visible.
    """

    def __init__(self, x: float, y: float, duration: float) -> None:
        self.x = x
        self.y = y
        self.duration = duration
        self.timer: float = 0.0
        self.active: bool = True

    def update(self, dt: float) -> None:
        """Tick the marker timer.

        Args:
            dt: Delta time.
        """
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the shadow marker using a sprite or a dark ellipse fallback.

        Args:
            surface: Target surface.
            camera_offset: Camera offset.
        """
        if not self.active:
            return
        _load_boss_sub_sprites()
        sx = int(self.x) - camera_offset[0]
        sy = int(self.y) - camera_offset[1]

        if _boss_shadow_sprite is not None:
            surface.blit(_boss_shadow_sprite, (sx - 8, sy - 3))
        else:
            marker_surf = pygame.Surface((16, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(marker_surf, (40, 40, 40, 140), (0, 0, 16, 6))
            surface.blit(marker_surf, (sx - 8, sy - 3))


class DestructiblePillar:
    """A pillar in the boss arena that can be shattered by Bull Rush.

    Pillars block the player from Bull Rush if they hide behind one.
    When shattered, the arena opens up, increasing difficulty.

    Args:
        x: X position in world pixels (tile-aligned).
        y: Y position in world pixels (tile-aligned).
    """

    def __init__(self, x: float, y: float) -> None:
        self.rect = pygame.Rect(int(x), int(y), TILE_SIZE, TILE_SIZE * 3)
        self.active: bool = True

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the pillar using a sprite or fallback rectangles.

        Args:
            surface: Target surface.
            camera_offset: Camera offset.
        """
        _load_boss_sub_sprites()
        sx = self.rect.x - camera_offset[0]
        sy = self.rect.y - camera_offset[1]

        if self.active and _pillar_intact_sprite is not None:
            surface.blit(_pillar_intact_sprite, (sx, sy))
        elif not self.active and _pillar_destroyed_sprite is not None:
            surface.blit(_pillar_destroyed_sprite, (sx, sy))
        elif self.active:
            # Fallback: drawn rectangles.
            pygame.draw.rect(surface, (100, 90, 80), (sx, sy, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, (70, 60, 50), (sx, sy, self.rect.width, self.rect.height), 2)
            pygame.draw.rect(surface, (120, 110, 100), (sx - 2, sy - 4, self.rect.width + 4, 6))


class BouDePedra(BossEntity):
    """Es Bou de Pedra -- The Stone Bull, World 1 boss.

    Implements 3-phase boss fight with charging, stomping, rock hurling,
    frenzy rushes, and core pulse attacks.

    Args:
        x: Spawn X position in world pixels.
        y: Spawn Y position in world pixels.
        definition: Boss definition dict loaded from JSON.
        event_bus: Shared event bus.
        arena_bounds: (left, top, right, bottom) of the arena in pixels.
    """

    def __init__(
        self,
        x: float,
        y: float,
        definition: dict,
        event_bus: EventBus,
        arena_bounds: tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__(x, y, definition, event_bus)

        # Arena bounds (pixel coordinates).
        if arena_bounds is None:
            arena_data = definition.get("arena", {})
            w = arena_data.get("width", 25) * TILE_SIZE
            h = arena_data.get("height", 14) * TILE_SIZE
            arena_bounds = (0, 0, w, h)
        self._arena_left = arena_bounds[0]
        self._arena_top = arena_bounds[1]
        self._arena_right = arena_bounds[2]
        self._arena_bottom = arena_bounds[3]

        # Movement.
        self._moving: bool = False
        self._move_direction: float = 0.0
        self._move_speed: float = 0.0
        self._sub_x: float = float(self.rect.x)

        # Attack-specific state.
        self._rush_bounces_remaining: int = 0
        self._rush_target_wall: int = 0  # 0=none, -1=left, 1=right

        # Boss projectiles (rocks, shockwaves).
        self.projectiles: list[BossProjectile] = []
        self.shadow_markers: list[ShadowMarker] = []

        # Destructible pillars.
        self.pillars: list[DestructiblePillar] = []

        # Player reference (set each frame for attack targeting).
        self._player_rect: pygame.Rect | None = None

        # Ground Y for shockwaves (bottom of arena minus one tile).
        self._ground_y = self._arena_bottom - TILE_SIZE

    # ── Pillar Setup ───────────────────────────────────────────────

    def setup_pillars(self, pillar_positions: list[dict]) -> None:
        """Create destructible pillars from position data.

        Args:
            pillar_positions: List of dicts with x, y in tile coords.
        """
        self.pillars.clear()
        for pos in pillar_positions:
            px = pos.get("x", 0) * TILE_SIZE
            py = (pos.get("y", 0) - 2) * TILE_SIZE  # Pillar extends upward.
            self.pillars.append(DestructiblePillar(px, py))

    @property
    def active_pillars(self) -> list[DestructiblePillar]:
        """List of pillars still standing."""
        return [p for p in self.pillars if p.active]

    # ── Update (extends base) ──────────────────────────────────────

    def update_with_player(
        self,
        player_rect: pygame.Rect,
        dt: float,
    ) -> None:
        """Update the boss with player position context.

        Args:
            player_rect: The player's bounding rect.
            dt: Delta time in seconds.
        """
        self._player_rect = player_rect
        self.update(dt)

        # Update boss projectiles.
        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.active]

        # Update shadow markers.
        for marker in self.shadow_markers:
            marker.update(dt)
        self.shadow_markers = [m for m in self.shadow_markers if m.active]

        # Apply movement.
        if self._moving:
            self._sub_x += self._move_direction * self._move_speed * dt
            self.rect.x = round(self._sub_x)

            # Check wall collision.
            if self.rect.left <= self._arena_left:
                self.rect.left = self._arena_left
                self._sub_x = float(self.rect.x)
                self._on_hit_wall(-1)
            elif self.rect.right >= self._arena_right:
                self.rect.right = self._arena_right
                self._sub_x = float(self.rect.x)
                self._on_hit_wall(1)

            # Check pillar collision during rush.
            if self._current_pattern and self._current_pattern.get("id") in (
                "bull_rush", "frenzy_rush"
            ):
                self._check_pillar_collision()

    # ── Attack Implementations ─────────────────────────────────────

    def _execute_attack(self) -> None:
        """Start executing the current attack pattern."""
        if self._current_pattern is None:
            return

        pattern_id = self._current_pattern.get("id", "")
        params = self._current_pattern.get("params", {})

        if pattern_id == "bull_rush":
            self._start_bull_rush(params)
        elif pattern_id == "headbutt":
            self._start_headbutt(params)
        elif pattern_id == "ground_stomp":
            self._start_ground_stomp(params)
        elif pattern_id == "rock_hurl":
            self._start_rock_hurl(params)
        elif pattern_id == "frenzy_rush":
            self._start_frenzy_rush(params)
        elif pattern_id == "core_pulse":
            self._start_core_pulse(params)

    def _update_attack(self, dt: float) -> None:
        """Update the current attack each frame.

        Args:
            dt: Delta time in seconds.
        """
        # Movement is handled in update_with_player.
        pass

    def _get_attack_duration(self) -> float:
        """Return the duration of the current attack.

        Returns:
            Attack duration in seconds.
        """
        if self._current_pattern is None:
            return 1.0

        pattern_id = self._current_pattern.get("id", "")
        params = self._current_pattern.get("params", {})

        if pattern_id == "bull_rush":
            # Duration based on arena width / speed.
            speed = params.get("speed", 200)
            return (self._arena_right - self._arena_left) / max(speed, 1)
        elif pattern_id == "headbutt":
            return 0.4
        elif pattern_id == "ground_stomp":
            return 0.8
        elif pattern_id == "rock_hurl":
            return 1.0
        elif pattern_id == "frenzy_rush":
            bounces = params.get("bounces", 3)
            speed = params.get("speed", 280)
            return bounces * (self._arena_right - self._arena_left) / max(speed, 1)
        elif pattern_id == "core_pulse":
            return 0.5
        return 1.0

    def _on_phase_transition(self, old_phase: int, new_phase: int) -> None:
        """Handle phase transition effects.

        Args:
            old_phase: Previous phase.
            new_phase: New phase.
        """
        # Stop any movement.
        self._moving = False
        self._move_speed = 0.0
        # Clear projectiles.
        self.projectiles.clear()
        self.shadow_markers.clear()

    # ── Bull Rush ──────────────────────────────────────────────────

    def _start_bull_rush(self, params: dict) -> None:
        """Begin a Bull Rush charge across the arena.

        Args:
            params: Pattern params (speed, stun_on_wall_hit, destroys_pillars).
        """
        speed = params.get("speed", 200)
        self._move_speed = speed
        self._moving = True
        self._rush_bounces_remaining = 0

        # Charge toward the player.
        if self._player_rect is not None:
            if self._player_rect.centerx < self.rect.centerx:
                self._move_direction = -1.0
            else:
                self._move_direction = 1.0
        else:
            self._move_direction = -1.0 if self.facing_right else 1.0

        self.facing_right = self._move_direction > 0

    def _start_frenzy_rush(self, params: dict) -> None:
        """Begin a Frenzy Rush (bouncing off walls).

        Args:
            params: Pattern params (speed, bounces).
        """
        speed = params.get("speed", 280)
        self._rush_bounces_remaining = params.get("bounces", 3)
        self._move_speed = speed
        self._moving = True

        # Charge toward the player.
        if self._player_rect is not None:
            if self._player_rect.centerx < self.rect.centerx:
                self._move_direction = -1.0
            else:
                self._move_direction = 1.0
        else:
            self._move_direction = -1.0

        self.facing_right = self._move_direction > 0

    def _on_hit_wall(self, wall_side: int) -> None:
        """Handle the boss hitting an arena wall during a rush.

        Args:
            wall_side: -1 for left wall, 1 for right wall.
        """
        if self._state != BossState.ATTACKING:
            self._moving = False
            return

        pattern_id = ""
        if self._current_pattern:
            pattern_id = self._current_pattern.get("id", "")

        if pattern_id == "frenzy_rush":
            if self._rush_bounces_remaining > 0:
                self._rush_bounces_remaining -= 1
                self._move_direction = -self._move_direction
                self.facing_right = self._move_direction > 0
                self._event_bus.publish(
                    "screen_shake", intensity=4.0, duration=0.15
                )
            else:
                # Frenzy ended -- enter punish.
                self._moving = False
                self._state_timer = 0.0  # Force transition to punish.
        elif pattern_id == "bull_rush":
            # Hit wall -> stunned (punish window).
            self._moving = False
            self._event_bus.publish(
                "screen_shake", intensity=6.0, duration=0.3
            )
            self._state_timer = 0.0  # Force transition to punish.
        else:
            self._moving = False

    def _check_pillar_collision(self) -> None:
        """Check if the boss collides with a pillar during a rush."""
        for pillar in self.pillars:
            if not pillar.active:
                continue
            if self.rect.colliderect(pillar.rect):
                pillar.active = False
                self._event_bus.publish(
                    "screen_shake", intensity=5.0, duration=0.25
                )
                # Bull Rush: hitting a pillar also stuns the boss.
                pattern_id = ""
                if self._current_pattern:
                    pattern_id = self._current_pattern.get("id", "")
                if pattern_id == "bull_rush":
                    self._moving = False
                    self._state_timer = 0.0  # Force to punish.
                # Frenzy rush keeps going through pillars.

    # ── Headbutt ───────────────────────────────────────────────────

    def _start_headbutt(self, params: dict) -> None:
        """Begin a short-range headbutt attack.

        Args:
            params: Pattern params (range).
        """
        # Face the player.
        if self._player_rect is not None:
            if self._player_rect.centerx < self.rect.centerx:
                self.facing_right = False
            else:
                self.facing_right = True

        # Create a melee hitbox in front of the boss.
        attack_range = params.get("range", 2.0) * TILE_SIZE
        damage = self._current_pattern.get("damage", 1.0) if self._current_pattern else 1.0

        if self.facing_right:
            hx = self.rect.right
        else:
            hx = self.rect.left - int(attack_range)

        proj = BossProjectile(
            x=hx,
            y=self.rect.y,
            width=int(attack_range),
            height=self.rect.height,
            vx=0,
            vy=0,
            damage=damage,
            lifetime=0.3,
            proj_type="shockwave",
        )
        self.projectiles.append(proj)

    # ── Ground Stomp ───────────────────────────────────────────────

    def _start_ground_stomp(self, params: dict) -> None:
        """Begin a Ground Stomp sending shockwaves along the ground.

        Args:
            params: Pattern params (shockwave_range, direct_damage).
        """
        shockwave_range = params.get("shockwave_range", 6) * TILE_SIZE
        damage = self._current_pattern.get("damage", 1.0) if self._current_pattern else 1.0

        # Screen shake.
        self._event_bus.publish("screen_shake", intensity=5.0, duration=0.3)

        # Spawn shockwaves going left and right along the ground.
        ground_y = self.rect.bottom - 8
        speed = 180.0

        # Right shockwave.
        self.projectiles.append(BossProjectile(
            x=self.rect.right,
            y=ground_y,
            width=16,
            height=8,
            vx=speed,
            vy=0,
            damage=damage,
            lifetime=shockwave_range / speed,
            proj_type="shockwave",
        ))

        # Left shockwave.
        self.projectiles.append(BossProjectile(
            x=self.rect.left - 16,
            y=ground_y,
            width=16,
            height=8,
            vx=-speed,
            vy=0,
            damage=damage,
            lifetime=shockwave_range / speed,
            proj_type="shockwave",
        ))

    # ── Rock Hurl ──────────────────────────────────────────────────

    def _start_rock_hurl(self, params: dict) -> None:
        """Hurl rocks at predicted player positions.

        Args:
            params: Pattern params (rock_count).
        """
        rock_count = params.get("rock_count", 3)
        damage = self._current_pattern.get("damage", 1.0) if self._current_pattern else 1.0

        if self._player_rect is None:
            return

        # Predict landing positions around the player.
        player_cx = self._player_rect.centerx
        spread = 32  # Pixels between landing points.

        for i in range(rock_count):
            offset = (i - rock_count // 2) * spread
            land_x = player_cx + offset

            # Shadow marker at landing position.
            self.shadow_markers.append(ShadowMarker(
                x=land_x,
                y=self._ground_y,
                duration=0.8,
            ))

            # Rock projectile (arcs from boss to landing position).
            start_x = float(self.rect.centerx)
            start_y = float(self.rect.top)
            dx = land_x - start_x
            travel_time = 0.7
            vx = dx / travel_time
            # Arc: goes up then comes down.
            vy = -200.0  # Initial upward velocity.

            self.projectiles.append(BossProjectile(
                x=start_x,
                y=start_y,
                width=8,
                height=8,
                vx=vx,
                vy=vy,
                damage=damage,
                lifetime=travel_time + 0.1,
                proj_type="rock",
            ))

    # ── Core Pulse ─────────────────────────────────────────────────

    def _start_core_pulse(self, params: dict) -> None:
        """Release a circular shockwave from the exposed core.

        Must be airborne to dodge.

        Args:
            params: Pattern params (radius).
        """
        radius_tiles = params.get("radius", 8)
        damage = self._current_pattern.get("damage", 1.0) if self._current_pattern else 1.0

        self._event_bus.publish("screen_shake", intensity=4.0, duration=0.3)

        # Create expanding pulse projectiles in 4 cardinal directions.
        pulse_speed = 150.0
        radius_px = radius_tiles * TILE_SIZE
        lifetime = radius_px / pulse_speed

        cx = float(self.rect.centerx)
        cy = float(self.rect.centery)

        # Create ground-level shockwave (player must jump to dodge).
        # This is a wide horizontal wave at ground level.
        for direction in [-1.0, 1.0]:
            self.projectiles.append(BossProjectile(
                x=cx,
                y=self.rect.bottom - 16,
                width=24,
                height=16,
                vx=direction * pulse_speed,
                vy=0,
                damage=damage,
                lifetime=lifetime,
                proj_type="pulse",
            ))

    # ── Rendering (extends base) ───────────────────────────────────

    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[int, int],
    ) -> None:
        """Draw the boss, pillars, projectiles, and markers.

        Args:
            surface: Target surface.
            camera_offset: Camera offset.
        """
        # Draw pillars.
        for pillar in self.pillars:
            pillar.render(surface, camera_offset)

        # Draw shadow markers.
        for marker in self.shadow_markers:
            marker.render(surface, camera_offset)

        # Draw boss projectiles.
        for proj in self.projectiles:
            proj.render(surface, camera_offset)

        # Draw the boss itself.
        super().render(surface, camera_offset)

    # ── Collision helpers for BossScene ─────────────────────────────

    def get_attack_rects(self) -> list[tuple[pygame.Rect, float]]:
        """Get active attack hitboxes and their damage values.

        Used by the boss scene for player-vs-boss-attack collision.

        Returns:
            List of (rect, damage) tuples.
        """
        result: list[tuple[pygame.Rect, float]] = []

        # Boss body collision during rush attacks.
        if self._moving and self._state == BossState.ATTACKING:
            damage = 1.5
            if self._current_pattern:
                damage = self._current_pattern.get("damage", 1.5)
            result.append((self.rect.copy(), damage))

        # Boss projectiles.
        for proj in self.projectiles:
            if proj.active:
                result.append((proj.rect.copy(), proj.damage))

        return result

    def blocks_rush(self, other_rect: pygame.Rect) -> bool:
        """Check if a rect (player behind pillar) blocks the rush.

        Args:
            other_rect: Rect to check.

        Returns:
            True if a pillar is between the boss and the rect.
        """
        for pillar in self.pillars:
            if not pillar.active:
                continue
            # Pillar is between boss and target.
            if (
                min(self.rect.centerx, other_rect.centerx)
                < pillar.rect.centerx
                < max(self.rect.centerx, other_rect.centerx)
            ):
                return True
        return False
