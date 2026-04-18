"""Combat system: damage resolution, hit detection, invincibility frames.

The CombatSystem is a decoupled system that the GameplayScene calls
each frame with references to the player, enemies, projectiles, and
melee hitboxes.  It resolves all combat interactions:

- Player <-> Enemy contact damage
- Projectile -> Enemy damage
- Melee hitbox -> Enemy damage
- Enemy attack -> Player damage

Damage and invincibility are communicated via EventBus events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from sa_fona.config.settings import PLAYER_BLINK_INTERVAL, PLAYER_INVINCIBILITY_DURATION
from sa_fona.core.event_bus import EventBus
from sa_fona.entities.enemy import Enemy
from sa_fona.entities.pickup import Pickup

if TYPE_CHECKING:
    from sa_fona.entities.player import Player
    from sa_fona.entities.projectile import Projectile
    from sa_fona.systems.sling_system import MeleeHitbox


class CombatSystem:
    """Manages damage dealing, hit detection, and invincibility frames.

    All damage interactions are resolved through AABB overlap checks.
    The system publishes events for visual/audio feedback and tracks
    invincibility timers.

    Args:
        event_bus: Shared event bus for publishing combat events.
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

        # Player invincibility state.
        self._player_invincible_timer: float = 0.0
        self._player_blink_timer: float = 0.0
        self._player_visible: bool = True

        # Player health tracking (mirrors HUD, used for death detection).
        self._player_hearts: float = 3.0
        self._player_max_hearts: int = 3
        self._player_dead: bool = False
        self._god_mode: bool = False

        # Subscribe to heart events to track health.
        self._event_bus.subscribe("heart_collected", self._on_heart_collected)

    # ── Public API ─────────────────────────────────────────────────

    def set_player_health(self, current: float, max_hearts: int) -> None:
        """Initialize or reset the player's health tracking.

        Args:
            current: Current heart count.
            max_hearts: Maximum heart count.
        """
        self._player_hearts = current
        self._player_max_hearts = max_hearts
        self._player_dead = False
        self._player_invincible_timer = 0.0

    @property
    def player_hearts(self) -> float:
        """Current player heart count tracked by combat system."""
        return self._player_hearts

    @property
    def player_dead(self) -> bool:
        """Whether the player is dead (hearts <= 0)."""
        return self._player_dead

    @property
    def player_invincible(self) -> bool:
        """Whether the player is currently invincible."""
        return self._player_invincible_timer > 0

    @property
    def player_visible(self) -> bool:
        """Whether the player should be visible (for blink rendering)."""
        if self._player_invincible_timer <= 0:
            return True
        return self._player_visible

    def update(
        self,
        player: Player,
        enemies: list[Enemy],
        projectiles: list[Projectile],
        melee_hitboxes: list[MeleeHitbox],
        dt: float,
    ) -> list[Pickup]:
        """Resolve all combat interactions for one frame.

        Args:
            player: The player entity.
            enemies: Active enemy entities.
            projectiles: Active projectile entities.
            melee_hitboxes: Active melee hitbox rects from the sling system.
            dt: Delta time in seconds.

        Returns:
            A list of Pickup entities dropped by killed enemies.
        """
        if self._player_dead:
            return []

        dropped_pickups: list[Pickup] = []

        # Tick player invincibility.
        self._tick_invincibility(dt)

        # 1. Projectile -> Enemy
        for proj in projectiles:
            if not proj.active:
                continue
            for enemy in enemies:
                if not enemy.is_alive:
                    continue
                if proj.rect.colliderect(enemy.rect):
                    drops = self._handle_projectile_hit(proj, enemy, player)
                    dropped_pickups.extend(drops)
                    break  # Projectile destroyed, stop checking.

        # 2. Melee hitbox -> Enemy
        for hitbox in melee_hitboxes:
            for enemy in enemies:
                if not enemy.is_alive:
                    continue
                if hitbox.rect.colliderect(enemy.rect):
                    drops = self._handle_melee_hit(hitbox, enemy, player)
                    dropped_pickups.extend(drops)

        # 3. Enemy contact -> Player (if not invincible)
        if not self.player_invincible:
            for enemy in enemies:
                if not enemy.is_alive:
                    continue
                if player.rect.colliderect(enemy.rect):
                    self._handle_enemy_contact(enemy)
                    break  # Only take damage once per frame.

        # 4. Enemy attack -> Player (if enemy is attacking and not invincible)
        if not self.player_invincible:
            for enemy in enemies:
                if not enemy.is_alive or not enemy.is_attacking:
                    continue
                # Attack hitbox: slightly larger than the enemy rect.
                attack_rect = enemy.rect.inflate(8, 4)
                if player.rect.colliderect(attack_rect):
                    self._handle_enemy_attack(enemy)
                    break  # Only take damage once per frame.

        return dropped_pickups

    def deal_damage_to_player(self, amount: float) -> None:
        """Apply damage to the player and enter invincibility.

        Public API for external systems (e.g. BossScene) that need to
        deal damage to the player outside the normal enemy pipeline.

        Args:
            amount: Damage in hearts.
        """
        self._deal_damage_to_player(amount)

    def tick(self, dt: float) -> None:
        """Tick timers (invincibility, blink) without resolving combat.

        Args:
            dt: Delta time in seconds.
        """
        self._tick_invincibility(dt)

    def cleanup(self) -> None:
        """Unsubscribe from EventBus events."""
        self._event_bus.unsubscribe("heart_collected", self._on_heart_collected)

    # ── Private helpers ────────────────────────────────────────────

    def _tick_invincibility(self, dt: float) -> None:
        """Update the player's invincibility timer and blink state.

        Args:
            dt: Delta time in seconds.
        """
        if self._player_invincible_timer > 0:
            self._player_invincible_timer -= dt
            self._player_blink_timer -= dt
            if self._player_blink_timer <= 0:
                self._player_visible = not self._player_visible
                self._player_blink_timer = PLAYER_BLINK_INTERVAL
            if self._player_invincible_timer <= 0:
                self._player_invincible_timer = 0.0
                self._player_visible = True

    def _handle_projectile_hit(
        self, proj: Projectile, enemy: Enemy, player: Player
    ) -> list[Pickup]:
        """Resolve a projectile hitting an enemy.

        Args:
            proj: The projectile that hit.
            enemy: The enemy that was hit.
            player: The player entity (for aggro callback).

        Returns:
            Pickup drops if the enemy was killed.
        """
        # Check if the enemy blocks the hit.
        blocked = enemy.behavior.try_block()

        proj.on_hit_entity(enemy)  # Destroy the projectile.

        if blocked:
            self._event_bus.publish(
                "attack_blocked", enemy_type=enemy.enemy_type
            )
            enemy.behavior.on_damaged(
                float(player.rect.centerx), float(player.rect.centery)
            )
            return []

        applied = enemy.take_damage(proj.damage)
        if applied:
            enemy.behavior.on_damaged(
                float(player.rect.centerx), float(player.rect.centery)
            )
            self._event_bus.publish(
                "damage_dealt",
                target_type="enemy",
                enemy_type=enemy.enemy_type,
                amount=proj.damage,
            )
        return self._check_enemy_death(enemy)

    def _handle_melee_hit(
        self, hitbox: MeleeHitbox, enemy: Enemy, player: Player
    ) -> list[Pickup]:
        """Resolve a melee hitbox hitting an enemy.

        Args:
            hitbox: The melee hitbox.
            enemy: The enemy that was hit.
            player: The player entity (for aggro callback).

        Returns:
            Pickup drops if the enemy was killed.
        """
        # Check block.
        blocked = enemy.behavior.try_block()

        if blocked:
            self._event_bus.publish(
                "attack_blocked", enemy_type=enemy.enemy_type
            )
            enemy.behavior.on_damaged(
                float(player.rect.centerx), float(player.rect.centery)
            )
            return []

        applied = enemy.take_damage(hitbox.damage)
        if applied:
            enemy.behavior.on_damaged(
                float(player.rect.centerx), float(player.rect.centery)
            )
            self._event_bus.publish(
                "damage_dealt",
                target_type="enemy",
                enemy_type=enemy.enemy_type,
                amount=hitbox.damage,
            )
        return self._check_enemy_death(enemy)

    def _check_enemy_death(self, enemy: Enemy) -> list[Pickup]:
        """Check if an enemy is dead and handle drops.

        Args:
            enemy: The enemy to check.

        Returns:
            Pickup entities if the enemy died.
        """
        if not enemy.is_alive:
            self._event_bus.publish(
                "enemy_killed", enemy_type=enemy.enemy_type
            )
            return enemy.get_drops()
        return []

    def _handle_enemy_contact(self, enemy: Enemy) -> None:
        """Handle player touching an enemy (contact damage).

        Args:
            enemy: The enemy the player touched.
        """
        self._deal_damage_to_player(enemy.contact_damage)

    def _handle_enemy_attack(self, enemy: Enemy) -> None:
        """Handle an enemy's attack hitting the player.

        Args:
            enemy: The attacking enemy.
        """
        # Attacks deal the enemy's contact_damage (could be different
        # in future; for now, same value).
        self._deal_damage_to_player(enemy.contact_damage)

    def _deal_damage_to_player(self, amount: float) -> None:
        """Apply damage to the player and enter invincibility.

        Args:
            amount: Damage in hearts.
        """
        if self._god_mode:
            return
        self._player_hearts -= amount
        self._player_invincible_timer = PLAYER_INVINCIBILITY_DURATION
        self._player_blink_timer = PLAYER_BLINK_INTERVAL
        self._player_visible = True

        self._event_bus.publish("damage_taken", amount=amount)

        if self._player_hearts <= 0:
            self._player_hearts = 0
            self._player_dead = True
            self._event_bus.publish("player_died")

    # ── Event handlers ────────────────────────────────────────────

    def _on_heart_collected(self, amount: float = 1.0, **kwargs: Any) -> None:
        """Track heart pickups for accurate health tracking.

        Args:
            amount: Hearts restored.
        """
        self._player_hearts = min(
            self._player_hearts + amount,
            float(self._player_max_hearts),
        )
