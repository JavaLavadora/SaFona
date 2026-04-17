# N'Andreu -- D3: Player Entity & Movement -- Handoff Report

**Date**: 2026-04-17
**Agent**: N'Andreu (Engine Programmer)
**Deliverable**: D3 -- Player Entity & Movement
**Issue**: #21
**Branch**: `feature/d3-player-movement`

---

## Summary

Implemented Ramon as a playable entity with the full core moveset (walk, jump, wall jump, wall slide) using placeholder graphics. Established the Entity base class that all future entities will extend. Created the GameplayScene that replaces DemoTilemapScene as the default scene.

## What Was Built

### New Files
- `sa_fona/entities/__init__.py` -- Package init
- `sa_fona/entities/entity.py` -- Abstract Entity base class with position, velocity, rect, sprite, update/render
- `sa_fona/entities/player.py` -- Player entity with FSM: idle, running, jumping, falling, wall_sliding, wall_jumping
- `sa_fona/scenes/gameplay.py` -- GameplayScene that loads a level, spawns the player, runs physics + camera

### Modified Files
- `sa_fona/config/settings.py` -- Added player movement constants (speed, jump force, wall slide speed, wall jump force, coyote time, jump buffer, state colors)
- `sa_fona/core/game.py` -- Changed default scene from DemoTilemapScene to GameplayScene
- `sa_fona/data/levels/test/test_level.json` -- Added boundary walls (columns 0 and 59) and wall-jump pillars (columns 26 and 33) for movement testing
- `tests/test_level_loader.py` -- Updated spawn coordinate expectations to match new test level

### New Tests
- `tests/test_entity.py` -- 5 tests: Entity init, defaults, render, properties
- `tests/test_player.py` -- 15 tests: State transitions (idle, running, jumping, falling, wall sliding), wall jump detection (left/right wall), variable jump height (full vs short), wall slide speed cap, facing direction, placeholder rendering
- `tests/test_gameplay_scene.py` -- 8 tests: Scene init, player spawning, input handling, rendering, screen shake

### Test Results
- **146 tests passing** (28 new, 118 existing -- all green)
- All previous functionality preserved

## Architecture Decisions

1. **State machine is enum-based** (`PlayerState` enum) rather than class-per-state. This is simpler for the current 6 states and avoids over-engineering. If states grow complex (20+ with distinct enter/exit logic), refactor to a State pattern.

2. **Player owns its own physics integration** -- calls `PhysicsSystem.update_rect()` directly. This keeps the physics step tightly coupled to the player's input processing (important for variable jump and wall slide).

3. **Coyote time + jump buffer** included for responsiveness. These are small grace windows (60ms coyote, 80ms jump buffer) that make platforming feel fair. Values in `config/settings.py`.

4. **Wall jump has input lockout** (120ms) -- prevents the player from immediately wall-sliding back onto the same wall after jumping off it. This makes wall jumps feel intentional.

5. **GameplayScene exposes player/camera/physics as properties** -- needed for future systems (HUD, combat) to access these without tight coupling.

## Movement Parameters (config/settings.py)

| Parameter | Value | Notes |
|---|---|---|
| PLAYER_MOVE_SPEED | 120 px/s | Horizontal movement |
| PLAYER_JUMP_FORCE | -280 px/s | Upward impulse |
| PLAYER_VARIABLE_JUMP_CUTOFF | 0.5 | Multiply vy on early release |
| PLAYER_WALL_SLIDE_SPEED | 40 px/s | Max fall speed on wall |
| PLAYER_WALL_JUMP_FORCE_X | 160 px/s | Horizontal push off wall |
| PLAYER_WALL_JUMP_FORCE_Y | -260 px/s | Upward impulse on wall jump |
| PLAYER_WALL_JUMP_LOCKOUT | 0.12s | Input lockout after wall jump |
| PLAYER_COYOTE_TIME | 0.06s | Grace after leaving ground |
| PLAYER_JUMP_BUFFER | 0.08s | Jump press memory |
| PLAYER_GRAVITY | 800 px/s^2 | Same as PhysicsSystem default |

All values are tunable without code changes.

## Open Questions / Future Work

1. **DemoTilemapScene still exists** but is no longer the default. It can be removed or kept as a standalone test scene.
2. **Animation system stub**: The `Animation` class from D2 exists and works; Player currently uses static colored surfaces per state rather than multi-frame animations. When Na Margalida provides sprite sheets, swapping in real animations is straightforward.
3. **Wall jump feel tuning**: The lockout, forces, and coyote times may need adjustment after playtesting. All values are in `config/settings.py`.
4. **Hazard tiles**: The test level has hazard tiles (ID 40) but the player does not yet take damage from them. This is D6 scope (combat system).

## Verification

- All 146 tests pass: `SDL_VIDEODRIVER=dummy conda run -n safona python -m pytest tests/ -v`
- Game launches: `DISPLAY=:99 conda run -n safona python -m sa_fona.main`
- Player can be controlled with arrow keys / WASD + Space for jump
- Port 6080 for VNC (after display setup from CLAUDE.md)
