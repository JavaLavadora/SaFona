# Deliverable 9: Boss System & Es Bou de Pedra -- Handoff Report

**Author**: N'Andreu (Engine Programmer)
**Date**: 2026-04-18
**Branch**: `feature/d9-boss-system`
**Issue**: #32

---

## Summary

Implemented the boss entity framework and the first boss fight (Es Bou de Pedra) with 3 phases, 6 distinct attack patterns, tell/punish windows, destructible arena pillars, and a boss health bar HUD.

## Files Created

| File | Purpose |
|------|---------|
| `sa_fona/entities/boss_entity.py` | BossEntity base class: phase management, pattern sequencing, tell/punish timers, invincibility, weak point multipliers |
| `sa_fona/entities/bosses/__init__.py` | Package init |
| `sa_fona/entities/bosses/bou_de_pedra.py` | Es Bou de Pedra: all 6 attack implementations, destructible pillars, boss projectiles, shadow markers |
| `sa_fona/scenes/boss_scene.py` | BossScene: arena generation, boss-vs-player combat, intro/defeat sequences, health bar integration |
| `sa_fona/ui/boss_health_bar.py` | Boss health bar: phase markers, smooth damage animation, phase transition flash |
| `sa_fona/data/bosses/boss_bou_de_pedra.json` | Boss data: HP, attack timings, damage values, arena layout, phase definitions |
| `tests/test_boss_entity.py` | 71 tests covering all boss systems |
| `docs/reports/n-andreu-d9-boss-system.md` | This report |

## Architecture Decisions

1. **BossEntity extends Entity, NOT Enemy** -- Bosses have fundamentally different behavior (phase system, invulnerability logic, tell/punish cycles). Sharing Enemy's behavior component pattern would be more coupling than benefit.

2. **Data-driven boss configuration** -- All timings, damage values, HP thresholds, arena layout, and pattern weights are in `boss_bou_de_pedra.json`. Tuning the fight requires zero code changes.

3. **BossScene is standalone, not extending GameplayScene** -- While it reuses the same systems (PhysicsSystem, CombatSystem, SlingSystem, Camera, HUD), boss arenas have different entity management (no enemies, no pickups, no triggers). Composition was cleaner than inheritance.

4. **Boss vulnerability model** -- The boss is ONLY vulnerable during punish windows (or when the Phase 3 core is exposed). This enforces the GDD's design rule that all damage opportunities are earned.

5. **Procedural arena generation** -- The BossScene can generate a simple arena tilemap from the boss JSON data without needing a level file. A level_path can also be passed for hand-crafted arenas later.

6. **Weak point multipliers** -- Phase 3 exposed core grants 2x damage on charged shots and 3x on Tier 3 shots (melee gets no bonus). This rewards players who mastered the charge mechanic.

## Design Rules Verified

- All attacks have >= 0.5s tell time (verified in tests)
- All attacks have >= 1.5s punish window (verified in tests)
- Boss is invulnerable during phase transitions
- Phase transitions trigger screen shake events
- 4 destructible pillars in the arena
- Boss can skip phases when massive damage is dealt (e.g., phase 1 directly to phase 3)
- Pattern selection avoids repeating the same attack twice in a row

## Attack Pattern Summary

| Phase | Attack | Tell | Punish | Notes |
|-------|--------|------|--------|-------|
| 1 | Bull Rush | 1.0s | 2.5s | Charges across arena, stuns on wall/pillar hit |
| 1 | Headbutt | 0.5s | 1.5s | Short-range melee arc |
| 2 | Bull Rush (fast) | 0.8s | 2.5s | 250 px/s (up from 200) |
| 2 | Ground Stomp | 1.2s | 2.0s | Bidirectional ground shockwaves, jump to dodge |
| 2 | Rock Hurl | 0.8s | 1.5s | 3 arcing rocks with shadow markers |
| 3 | Frenzy Rush | 0.6s | 2.5s | Bounces off walls 3 times |
| 3 | Core Pulse | 1.0s | 2.0s | Ground-level expanding pulse, must be airborne |

## EventBus Events

| Event | Publisher | Data |
|-------|-----------|------|
| `boss_phase_change` | BossEntity | boss_id, old_phase, new_phase |
| `boss_defeated` | BossEntity | boss_id, post_defeat (mask_granted, dialogue, cutscene) |
| `boss_attack_tell` | BossEntity | boss_id, pattern_id |
| `boss_stunned` | BossEntity | boss_id, duration |
| `screen_shake` | BossEntity/BossScene | intensity, duration |
| `damage_dealt` | BossEntity | target_type="boss", boss_id, amount |

## Test Results

- **71 new tests** covering: initialization, state transitions, phase transitions, vulnerability logic, damage multipliers, attack implementations, pillar destruction, projectile behavior, health bar, rendering, JSON loading, full attack cycles
- **482 total tests pass** (all existing + new)
- BossScene integration verified: 300 frames rendered without errors

## Open Questions for Review

1. **Boss spawn position vs pillar overlap**: The boss spawns at (20, 9) in tile coords, which is near pillar 3 at (20, 10). The pillar extends upward 3 tiles from (y-2). In the current setup, the boss can collide with the pillar immediately during a rush. Should the boss spawn position or pillar positions be adjusted?

2. **Rock Hurl arc physics**: Currently uses a simple linear velocity (constant vx, initial vy of -200). A proper parabolic arc with gravity would be more realistic. Worth the complexity?

3. **Contact damage during non-attack states**: The BossScene applies contact damage when the player touches the boss during idle/tell states. Should the boss only deal contact damage during rush attacks?

4. **Intro duration**: Currently 2.0s (1.0s on retry). The GDD mentions a "brief, skippable" intro cutscene. The full cutscene with dialogue would be handled by the CutsceneScene in D10.

## Dependencies for D10

- `boss_defeated` event carries `post_defeat.mask_granted = "stone_slam"` for the mask system
- `post_defeat.dialogue_id` and `post_defeat.cutscene` are ready for D10's cutscene/dialogue integration
- The BossScene's defeat sequence (white flash + "VICTORY!") is a placeholder; D10 will replace it with the dimoni cutscene
