# D7: Dialogue System & Companion -- Handoff Report

**Author**: N'Andreu (Engine Programmer)
**Date**: 2026-04-17
**Issue**: #25
**Branch**: `feature/d7-dialogue-companion`

---

## What Was Built

### 1. Trigger System (`sa_fona/level/trigger.py`)
- `Trigger` class: rectangular zones with type (dialogue, level_end, save_point), once/repeatable firing, and arbitrary properties
- `TriggerSystem` class: manages all triggers, checks player overlap each frame, publishes events via EventBus
- `Trigger.from_dict()` factory creates triggers from level JSON data with tile-to-pixel coordinate conversion
- Trigger events: `trigger_dialogue`, `trigger_level_end`, `trigger_save_point`
- Unknown trigger types are skipped gracefully (forward-compatible with boss_gate, cutscene, etc.)

### 2. Dialogue Box UI (`sa_fona/ui/dialogue_box.py`)
- Bottom-screen text box with semi-transparent background, border, speaker name, and portrait
- Portrait: colored square (green for Bep, blue for Ramon, grey for narrator) with speaker initial
- Letter-by-letter text reveal at configurable speed (default 30 chars/s)
- Word-wrapped text rendering that fits within the box
- `advance()`: if text is mid-reveal, finish it; if fully revealed, move to next line; if last line, complete dialogue
- `skip()`: ends the dialogue immediately (only if `skippable` flag is True)
- Auto-advance support: lines with `auto_advance_ms` advance automatically after the specified delay
- EventBus integration: publishes `dialogue_started` and `dialogue_ended`

### 3. Dialogue Scene Overlay (`sa_fona/scenes/dialogue.py`)
- `is_overlay = True`: SceneManager renders gameplay underneath with dimming
- Loads dialogue data from all `data/dialogue/*.json` files, merged into one lookup dict
- Interact key (Enter) advances text; Pause key (Escape) skips if allowed
- `on_complete` callback support for scene stack management
- Pre-loadable dialogue data for testing (avoids filesystem dependency)

### 4. Companion Entity (`sa_fona/entities/companion.py`)
- Bep rendered as 16x16 green rectangle with "B" label
- Follow AI: stays behind player at ~32px offset
  - Normal speed (100 px/s) when within moderate range
  - Catch-up speed (180 px/s) when >80px away
  - Teleport when >300px away (e.g. after level reset)
  - Stops moving when very close to target (<4px)
- Vertical bob animation for visual life
- Font rendering wrapped in try/except for headless test environments
- No gameplay interaction: purely visual

### 5. Dialogue Data
- `data/dialogue/world1_dialogue.json`: 4 dialogue sequences (test level intro, movement hint, wall jump hint, Bep intro)
- `data/dialogue/bep_hints.json`: 4 hint sequences (sling, wall jump, save point, level end)

### 6. GameplayScene Integration
- TriggerSystem loaded from level JSON triggers on init and reset
- Companion spawns at `companion_spawn` coordinates from level JSON
- Dialogue trigger callback defers push to end of update (avoids mid-frame stack mutation)
- Level-end and save-point triggers publish events for future deliverables
- Companion rendered between projectiles and player (correct z-order)
- Debug screen shake on interact removed (Enter key now used for dialogue)

### 7. Game Class Update
- `scene_manager` reference passed to GameplayScene so it can push DialogueScene overlays

### 8. Test Level Update
- Added 3 triggers to `test_level.json`:
  - Dialogue trigger at (5,10) with `w1_test_level_intro` (fires once)
  - Save point trigger at (30,12) (repeatable)
  - Level end trigger at (57,11) (fires once)

---

## Test Summary

| Category | New Tests | Total |
|----------|-----------|-------|
| Trigger system | 18 tests | 18 |
| DialogueBox | 25 tests | 25 |
| DialogueScene | 6 tests | 6 |
| Companion | 9 tests | 9 |
| **Subtotal new** | **58** | |
| Previous tests | | 213 |
| Existing gameplay tests | | 12 (all pass) |
| **Grand total** | | **273 passing** |

---

## Design Decisions

1. **Deferred dialogue push**: Trigger callbacks set `_pending_dialogue_id` which is processed at the end of `update()`. This avoids modifying the scene stack during mid-frame event processing.

2. **Dialogue data merging**: `DialogueScene._load_all_dialogue()` reads all JSON files in `data/dialogue/` and merges them. This means dialogue can be split across files by topic without code changes.

3. **Trigger coordinate convention**: Trigger rects in JSON use tile coordinates (matching entity spawns); `Trigger.from_dict()` converts to pixels.

4. **Interact key stays as Enter**: E and K are already bound to mask_cycle_right and mask_power respectively. Enter (return) is the interact key per the existing controls_default.json.

5. **Companion follows behind player**: Bep tracks to a position 32px left of the player's position. The follow distance is configurable via constants.

---

## Open Questions / Future Work

- **Dialogue scene pop timing**: The `on_complete` callback pops the dialogue scene. If the scene has already been popped by another mechanism, this could cause issues. Currently guarded by a None check on scene_manager.
- **Trigger re-entry**: Once-triggers deactivate after first fire. For repeatable triggers (save_point), they fire every frame while the player overlaps. A debounce mechanism (fire once per entry) may be needed for D8/D10.
- **Level-end and save-point**: Currently publish events but nothing listens. D10 (Save System) will wire these up.
- **Bep physics**: Bep currently floats/follows without collision. For D8 levels, this is fine since Bep is purely visual.

---

## Files Changed

### New Files
- `sa_fona/level/trigger.py` -- Trigger and TriggerSystem
- `sa_fona/ui/dialogue_box.py` -- DialogueBox UI component
- `sa_fona/scenes/dialogue.py` -- DialogueScene overlay
- `sa_fona/entities/companion.py` -- Companion entity (Bep)
- `sa_fona/data/dialogue/world1_dialogue.json` -- W1 dialogue data
- `sa_fona/data/dialogue/bep_hints.json` -- Bep hint dialogues
- `tests/test_trigger.py` -- 18 trigger tests
- `tests/test_dialogue.py` -- 31 dialogue tests
- `tests/test_companion.py` -- 9 companion tests

### Modified Files
- `sa_fona/scenes/gameplay.py` -- Trigger, companion, and dialogue integration
- `sa_fona/core/game.py` -- Pass scene_manager to GameplayScene
- `sa_fona/data/levels/test/test_level.json` -- Added trigger zones
