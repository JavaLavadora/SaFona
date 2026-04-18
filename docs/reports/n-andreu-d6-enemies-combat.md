# D6: Enemies & Combat Integration -- Handoff Report

**Author**: N'Andreu (Engine Programmer)
**Date**: 2026-04-17
**Issue**: #29
**Branch**: `feature/d6-enemies-combat`

---

## Summary

Implemented the enemy system, combat resolution, and game over flow for Deliverable 6. The game now has three World 1 enemy types with distinct behaviors, a decoupled combat system, invincibility frames with player blink, enemy drops, player death detection, and a placeholder game over screen.

---

## What Was Built

### New Files

| File | Purpose |
|------|---------|
| `sa_fona/entities/enemy.py` | Enemy base class + EnemyFactory (JSON-driven creation) |
| `sa_fona/entities/enemy_behaviors.py` | Behavior components: PatrolBehavior, ChaseBehavior |
| `sa_fona/systems/combat.py` | CombatSystem: damage resolution, invincibility frames, death |
| `sa_fona/scenes/game_over.py` | GameOverScene: placeholder death screen with restart |
| `sa_fona/data/enemies/world1_enemies.json` | W1 enemy definitions (sheep, warrior, guardian) |
| `tests/test_combat.py` | 13 tests for CombatSystem |
| `tests/test_enemy_factory.py` | 10 tests for EnemyFactory and Enemy entity |
| `tests/test_enemy_behaviors.py` | 16 tests for patrol, chase, and factory |

### Modified Files

| File | Changes |
|------|---------|
| `sa_fona/scenes/gameplay.py` | Integrated enemies, CombatSystem, game over, player blink |
| `sa_fona/data/economy.json` | Added per-enemy-type drop tables |
| `sa_fona/data/levels/test/test_level.json` | Added 4 enemy spawns (2 sheep, 1 warrior, 1 guardian) |
| `sa_fona/config/settings.py` | Added combat constants (invincibility duration, blink interval) |

---

## Architecture Decisions

1. **CombatSystem is fully decoupled**: GameplayScene passes entity lists each frame. CombatSystem has no direct references to the scene, physics, or sling systems.

2. **Enemy behaviors are strategy components**: PatrolBehavior and ChaseBehavior implement an abstract EnemyBehavior interface. The EnemyFactory attaches the correct behavior based on the JSON definition. New behaviors (e.g., shield for D10 W2) can be added by registering in `_BEHAVIOR_REGISTRY`.

3. **EnemyFactory reads JSON**: All enemy stats, hitbox sizes, behavior params, and drop tables come from `data/enemies/world1_enemies.json`. No enemy values are hardcoded.

4. **Invincibility frames**: Player gets 1.0s of invincibility after taking damage. During this time, the player blinks (visibility toggles every 0.08s). CombatSystem tracks the timer and exposes `player_visible` for GameplayScene's render method.

5. **Game over is deferred**: Player death publishes a `player_died` event. GameplayScene defers the scene push to the end of the update frame to avoid stack corruption. GameOverScene has a 0.5s input delay to prevent accidental skip.

6. **Enemy drops**: Enemies generate stone pickups and chance-based heart pickups from their drop table on death. The pickups are spawned into the scene's pickup list and collected normally.

7. **Block mechanic**: The rival warrior's ChaseBehavior has a `try_block()` method called by CombatSystem when the warrior is about to take projectile/melee damage. Block chance is data-driven (0.3 = 30%).

---

## W1 Enemy Types

| Type | HP | Contact Dmg | Behavior | Special |
|------|----|-------------|----------|---------|
| Possessed Sheep | 2 | 0.5 | Patrol + charge | 0.8s tell, 80px/s charge |
| Rival Warrior | 3 | 1.0 | Chase | 30% block chance, 0.5s block |
| Stone Guardian | 6 | 1.5 | Patrol + heavy attack | 1.0s tell, slow (20px/s) |

Placeholder rendering: sheep=white, warrior=brown, guardian=dark grey. Each enemy shows a letter label and has visual overlays for tell (red flash) and block (blue tint).

---

## Test Coverage

39 new tests added (386 total, all passing):
- **test_combat.py** (13): Projectile damage, melee damage, enemy contact, invincibility frames, blink visibility, player death, heart tracking
- **test_enemy_factory.py** (10): JSON loading, enemy creation, entity def parsing, death/drops, default world1 loading
- **test_enemy_behaviors.py** (16): Patrol movement, boundary reversal, attack tell/charge, chase follow/idle/attack, block mechanic, factory function

---

## Test Level Enemy Placement

The test level now has 4 enemies for playtesting:
- 2 possessed sheep at x=10, x=20 (early, easy encounters)
- 1 rival warrior at x=35 (mid-level, chases player)
- 1 stone guardian at x=50 (late, tanky with slow heavy attacks)

---

## Open Questions / Future Work

1. **Enemy gravity/platforms**: Enemies currently use simple horizontal movement only (no physics/gravity). For D8 levels with varied terrain, enemies may need basic gravity to avoid floating. This is scoped for D8 support work.

2. **Enemy-to-enemy collision**: Currently enemies can overlap each other. Not a problem for the test level but may need attention in D8 with denser enemy placement.

3. **Attack damage differentiation**: Currently enemy attacks deal the same as contact damage. The architecture supports separate attack damage values if the GDD needs them later.

---

## Verification

- All 386 tests pass: `SDL_VIDEODRIVER=dummy conda run -n safona python -m pytest tests/ -v`
- Game launches and runs: `DISPLAY=:99 conda run -n safona python -m sa_fona.main`
- VNC viewing: Forward port 6080, open `http://localhost:6080/vnc.html`
- Enemies are visible and fightable in the test level
- Player takes damage from enemy contact (hearts update in HUD)
- Player blinks during invincibility frames
- Killed enemies drop stone pickups
- When hearts reach 0, GameOverScene appears
- Press any key to restart from level beginning
