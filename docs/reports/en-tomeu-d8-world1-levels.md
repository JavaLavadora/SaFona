# Deliverable 8: World 1 Levels (L1-L4) -- Handoff Report

**Author**: En Tomeu (Level Designer)
**Date**: 2026-04-18
**Issue**: #31
**Branch**: `feature/d8-world1-levels`

---

## Summary

Designed and implemented 4 World 1 levels following the GDD Section 5.3 specifications. Each level has distinct layout, enemy placement, dialogue triggers, collectibles, and difficulty progression (1/10 through 4/10).

---

## Levels Implemented

### Level 1-1: "Es Primer Pas" (The First Step)
- **Dimensions**: 80x15 tiles (horizontal)
- **Difficulty**: 1/10
- **Enemies**: 3 possessed sheep (second half only)
- **Collectibles**: 18 stones, 1 heart, 3 breakables
- **Teaching beats**: movement, jump, wall jump hint, first enemy encounter
- **Layout highlights**: gentle terrain with a small hill, 2-tile gap for first jump, tall wall with optional wall-jump path (bonus stones reward), one-way platforms for exploration

### Level 1-2: "Sa Cova des Foner" (The Slinger's Cave)
- **Dimensions**: 90x18 tiles (horizontal with cave interior)
- **Difficulty**: 2/10
- **Enemies**: 5 possessed sheep, 2 rival warriors
- **Collectibles**: 21 stones, 1 heart, 4 breakables
- **Teaching beats**: cave entrance atmosphere, warrior blocking hint, charged shot hint
- **Secret**: Hidden alcove in cave with bonus stones
- **Layout highlights**: outdoor-to-cave-to-cliff-overlook progression, narrow ledge section over a pit, distant breakable target for charged shot puzzle

### Level 1-3: "Es Talayot Sagrat" (The Sacred Talayot)
- **Dimensions**: 30x40 tiles (VERTICAL)
- **Difficulty**: 3/10
- **Enemies**: 3 possessed sheep, 2 rival warriors, 1 stone guardian
- **Collectibles**: 22 stones, 2 hearts, 3 breakables
- **Teaching beats**: mandatory wall jump, stone guardian warning, cracked floor tease
- **Secrets**: Side chamber with bonus stones, retroactive cracked floor (requires Stone Slam from post-W1 boss)
- **Layout highlights**: two vertical wall-jump shafts, stone guardian combat chamber, breakable_slam tiles in floor as visual tease, proto-shop save point at top

### Level 1-4: "Sa Porta des Bou" (The Gate of the Bull)
- **Dimensions**: 100x25 tiles (mixed horizontal + vertical)
- **Difficulty**: 4/10
- **Enemies**: 3 possessed sheep, 3 rival warriors, 2 stone guardians
- **Collectibles**: 29 stones, 3 hearts, 4 breakables
- **Teaching beats**: approach dialogue, calm-before-the-storm area, boss gate tremor
- **Secret**: Hidden cave behind wall with 15 bonus stones and a heart
- **Layout highlights**: outdoor approach with enemy combos, cliff wall-jump section, floating platform gap crossing, narrow cave with mixed enemies, dramatic boss gate with stone pillars and bull iconography

---

## Engine Changes

### Companion Integration (`sa_fona/scenes/gameplay.py`)
- Added Bep companion spawning from `companion_spawn` coordinates
- Companion follows Ramon and renders in the world
- Companion resets on level reload

### Level Progression (`sa_fona/scenes/gameplay.py`)
- Level-end triggers now support a `next_level` property
- `_load_next_level()` method creates a new GameplayScene with the next level and replaces the current one
- Gracefully handles missing level files (stays on current level)

### Game Entry Point (`sa_fona/core/game.py`, `sa_fona/main.py`)
- Game now defaults to W1-L1 if it exists, falls back to test level
- Added `--level` CLI argument for testing specific levels (e.g. `--level world1/level_1_3`)
- Game constructor accepts optional `level_path` parameter

### Dialogue Data (`sa_fona/data/dialogue/world1_dialogue.json`)
- Added 10 new dialogue sequences for W1 teaching beats:
  - `w1_l1_jump_hint`, `w1_l1_sheep_encounter`
  - `w1_l2_cave_entrance`, `w1_l2_warrior_hint`, `w1_l2_charge_hint`
  - `w1_l3_wall_jump_mandatory`, `w1_l3_guardian_warning`, `w1_l3_cracked_floor`
  - `w1_l4_approach`, `w1_l4_calm_before_storm`, `w1_l4_tremor`

---

## Level Transition Chain

```
W1-L1 --> W1-L2 --> W1-L3 --> W1-L4 --> boss_bou_de_pedra
```

Each level's `level_end` trigger has a `next_level` property. When the player enters the level-end zone, the gameplay scene replaces itself with the next level. The final level (L4) points to `boss_bou_de_pedra` which will be implemented in D9.

---

## Tests

74 new tests in `tests/test_world1_levels.py`:
- Level file existence (4 tests)
- Level loading through LevelLoader (20 tests)
- Per-level GDD compliance checks (L1-1: 9, L1-2: 5, L1-3: 7, L1-4: 5)
- Difficulty progression (2 tests)
- Tilemap integrity: dimensions, spawn bounds, spawn not in solid tile (12 tests)
- Level chain connectivity (1 test)
- Dialogue reference validity (4 tests)

**Total**: 485 tests pass (411 existing + 74 new), zero failures.

---

## Design Notes

- **Terrain variety**: Unlike the flat test level, these levels use varied terrain -- hills, narrow ledges, vertical shafts, cave ceilings, elevated platforms, and boss gate architecture.
- **Pacing**: Each level alternates between calm exploration and combat encounters. L4's "calm before the storm" area gives the player a breather and generous supplies before the boss gate.
- **Retroactive content**: L3's cracked floor (breakable_slam tiles) is visible but not interactable without Stone Slam, planting a seed for post-W1 replay.
- **Enemy combos in L4**: For the first time, enemies appear together (warrior + sheep, guardian + sheep). This tests the player's ability to prioritize targets.

---

## Open Questions

1. **Boss level file**: L4 points to `boss_bou_de_pedra` as next_level. D9 will need to create this level/scene. The `_load_next_level` method gracefully handles missing files (stays on current level).
2. **Secret discovery tracking**: The `secrets` field in level JSON exists but there is no runtime system to track which secrets the player has found. This should be part of D10 (save system).
3. **Proto-shop in L3**: The save point with `shop_available: true` fires the event but the shop UI does not exist yet (D10 scope).

---

## Files Changed

- `sa_fona/data/levels/world1/level_1_1.json` (NEW)
- `sa_fona/data/levels/world1/level_1_2.json` (NEW)
- `sa_fona/data/levels/world1/level_1_3.json` (NEW)
- `sa_fona/data/levels/world1/level_1_4.json` (NEW)
- `sa_fona/data/dialogue/world1_dialogue.json` (UPDATED - 10 new dialogue sequences)
- `sa_fona/scenes/gameplay.py` (UPDATED - companion, level progression)
- `sa_fona/core/game.py` (UPDATED - starting level resolution, level_path param)
- `sa_fona/main.py` (UPDATED - --level CLI argument)
- `tests/test_world1_levels.py` (NEW - 74 tests)
- `docs/reports/en-tomeu-d8-world1-levels.md` (NEW - this report)
