# Handoff Report: Software Architecture Document

> **Author**: En Miquel (Software Architect)
> **Date**: 2026-04-16
> **Task**: Translate GDD v3.0 into modular Pygame software architecture

---

## What Was Produced

| File | Description |
|---|---|
| `docs/software_architecture.md` | Full software architecture document: project structure, 22 system interfaces with public APIs, 11 JSON data format schemas, dependency diagram, 9 extension points, 4 appendices (state machine, mask acquisition flow, death rollback flow, level replay flow) |

---

## Key Architectural Decisions

### Decision 1: EventBus for Inter-System Communication

**Choice**: A publish/subscribe event bus (`core/event_bus.py`) is the primary mechanism for cross-system communication.

**Rationale**: The GDD requires many systems to react to the same game events (e.g., killing an enemy triggers: stone drops in Economy, SFX in AudioManager, recharge acceleration in SpecialAmmo, HUD refresh). Without an event bus, each system would need direct references to every other system it needs to notify, creating a tightly coupled web. The event bus lets systems publish events without knowing who listens, and subscribe to events without knowing who publishes.

**Trade-off considered**: Direct method calls between systems would be simpler but create coupling. A full Entity-Component-System (ECS) would be more flexible but is overkill for a Pygame project of this scope. The event bus is the right middle ground: decoupled enough to avoid circular dependencies, simple enough that any developer can follow the flow.

### Decision 2: Single economy.json as the Economy Source of Truth

**Choice**: Every economy value (prices, drops, costs, effects, thresholds, multipliers) lives in a single `data/economy.json` file. The EconomySystem loads it at startup and provides typed accessors.

**Rationale**: This is a hard requirement from the GDD (Section 4.4 and Section 7.4). The project owner must be able to adjust balance during playtesting by editing one file. No economy value is hardcoded. The file includes a version field for forward compatibility.

**Trade-off considered**: Splitting economy data across multiple files (one per system) was considered, but rejected because it would make balance tuning harder -- the owner would need to hunt across files to adjust related values. A single file with clear sections is easier to navigate.

### Decision 3: Separate SlingSystem and SpecialAmmoSystem

**Choice**: The sling mechanics (tap/hold/charge/release) are in `systems/sling_system.py`. Special ammo (types, inventory, hybrid recharge) is in `systems/special_ammo.py`.

**Rationale**: The sling is always available and operates on every frame during gameplay. Special ammo is optional, has its own recharge loop, and interacts with the economy (purchasing packs). Separating them keeps each module focused and testable. The SlingSystem queries SpecialAmmoSystem only when spawning a projectile (to check if special ammo is equipped and available).

### Decision 4: Scene Stack (Push/Pop) for Overlays

**Choice**: The SceneManager uses a stack. Overlay scenes (pause, dialogue, shop) are pushed on top without destroying the gameplay scene below.

**Rationale**: The GDD requires dialogue, pause, and shop to overlay gameplay without losing game state. A stack naturally models this: push dialogue, pop back to gameplay. The alternative (recreating gameplay state after returning from a menu) would be fragile and slow.

### Decision 5: EnemyFactory with Behavior Components

**Choice**: Enemies are created by a factory that reads JSON definitions and attaches behavior components (`patrol`, `chase`, `shield`, `swoop`, etc.) rather than using deep class hierarchies.

**Rationale**: The GDD defines many enemy types across 6 worlds. Most share behaviors (patrol, chase) with different parameters. A factory + component approach means a new enemy type is usually just a new JSON entry. Only genuinely new behaviors require new code. This directly supports the extension point requirement.

### Decision 6: Per-Level Completion Tracking in Save

**Choice**: The save file tracks individual level completion (`level_completion` dictionary with `completed` and `secrets_found` per level).

**Rationale**: The GDD requires per-level replay unlock (Section 4.8). Each completed level must appear independently in Level Select. Secret-found flags per level drive the completion badges. This granular tracking also supports the retroactive secret system (Appendix C in the GDD) where players revisit levels with later masks.

### Decision 7: Snapshot/Rollback for Death Penalty

**Choice**: On level entry, the SaveSystem captures a snapshot of the player's economy state (stones, hearts, consumables, ammo). On death, this snapshot is restored.

**Rationale**: The GDD specifies that death returns the player to their pre-level state, with collected stones lost and used consumables refunded. A snapshot/rollback pattern is the cleanest way to implement this without tracking every individual transaction during a level.

### Decision 8: Mask Quick-Swap as a Mode Toggle in MaskSystem

**Choice**: Quick-swap is implemented as a boolean flag (`quick_swap_enabled`) in MaskSystem. When disabled, `cycle_mask()` is a no-op. When enabled (W5.5 start), it processes cycling input with a 0.3s cooldown.

**Rationale**: The GDD requires quick-swap to be unavailable before W5.5 and available in all levels via Level Select after unlock. A simple boolean in MaskSystem, persisted in the save file, handles both cases. The alternative (separate MaskSystem modes or subclasses) adds complexity for no benefit.

### Decision 9: 384x216 as Default Resolution

**Choice**: 384x216 is the default base resolution (configurable in `config/settings.py`).

**Rationale**: 384x216 provides 24x13.5 tiles visible on screen (vs. 20x11.25 for 320x180). The extra width is important for boss arenas (the GDD specifies bosses up to 96x96 pixels in arenas 25+ tiles wide). Both resolutions are exact 16:9 and divide cleanly by the 16px tile grid. The choice is a single constant change.

### Decision 10: Boss Definitions in Separate JSON Files

**Choice**: Each boss has its own JSON file under `data/bosses/` with full phase, pattern, and post-defeat data.

**Rationale**: Boss definitions are complex (3 phases, multiple patterns each with tell times, damage, punish windows, parameters). Putting them in their own files keeps them readable and allows level designers to iterate on boss balance independently. The `post_defeat` section drives the mask acquisition flow end-to-end.

---

## Open Questions (Filed as GitHub Issues)

The following design questions need team input. Each has been filed as a GitHub Issue.

### 1. Design Question: Level File Format -- Custom JSON vs. Tiled TMX

The GDD mentions both Tiled .tmx and custom JSON as level format options (Section 11.4). The architecture uses custom JSON because it gives us full control over the schema and avoids a Tiled dependency. However, if En Tomeu (Level Designer) prefers using Tiled for map editing, we should support .tmx import. This would require a converter or a dual-format LevelLoader.

**Recommendation**: Start with custom JSON. Add a Tiled-to-JSON converter script if the level designer requests it. Do not add runtime TMX parsing.

### 2. Design Question: Hot-Reload Scope During Development

The architecture supports `reload_config()` for economy.json and audio_config.json. Should we extend hot-reload to ALL data files (level JSON, enemy definitions, masks, dialogue) during development? This would require file watchers and careful state management.

**Recommendation**: Hot-reload economy.json and audio_config.json only. For other data, rely on restarting the level (fast enough during development). Avoid the complexity of full hot-reload.

### 3. Design Question: Consumable Usage From Pause Menu vs. Dedicated System

The GDD says the pause menu has an "Items" option (Section 10.4). Should consumables be usable ONLY from the pause menu, or also from a quick-use keybind during gameplay? The architecture supports both but the GDD does not specify.

**Recommendation**: Pause menu only. This prevents consumable usage from becoming a twitch mechanic and keeps the game's flow clean. If playtesting shows this is too cumbersome, a quick-use keybind can be added later.

### 4. Design Question: Multiple Save Slots

The GDD specifies a single save slot (Section 11.7) with "expandable later." The architecture uses a single save file path. Adding multiple slots later would require: a slot selection UI, parameterized save paths, and slot management (copy/delete). Should the save system be built with multiple slots in mind from the start?

**Recommendation**: Build for single slot. The SaveSystem already takes a `save_path` parameter, making it trivial to add slot selection later by passing different paths. Over-engineering now wastes time.

---

## Assumptions

1. **Python 3.10+**: The architecture uses dataclasses with `field(default_factory=...)`, type hints with `X | None`, and `list[str]` syntax. Python 3.10 is the minimum.

2. **No networking**: The game is single-player, local-only. No multiplayer or online features are considered.

3. **Single-threaded**: All game logic runs in Pygame's main loop on a single thread. Audio playback uses Pygame's mixer (which handles its own threading internally). No explicit multithreading in game code.

4. **Tile size is always 16x16**: The architecture assumes a uniform tile grid. Variable tile sizes are not supported.

5. **One active game session**: The game does not support background save management or multiple simultaneous sessions. When the game is running, it owns the save file exclusively.

6. **Placeholder assets are colored rectangles**: During development, the SpriteRenderer generates simple colored rectangles when asset files are missing. This is sufficient for gameplay testing and allows the team to work before Na Margalida produces real art.

7. **Boss behaviors require code**: While boss tuning parameters (damage, tell times, punish windows) are data-driven via JSON, the actual boss behavior logic (movement patterns, attack choreography, phase transitions) requires Python code. This is inherent to the complexity of boss encounters. Each boss has a dedicated behavior implementation that reads parameters from its JSON definition.

8. **Vertical slice scope**: The architecture covers the full game (all 6 worlds, 23 levels, 6 bosses, 5 masks), but Phase 1 implementation is World 1 complete + World 2 stub. The architecture is designed so that Phase 1 and subsequent phases use the exact same systems -- nothing is "prototype-only."

---

## Quality Gate Checklist

- [x] Every GDD system has a corresponding module with a defined API
- [x] All data formats have JSON schemas (11 data format schemas defined)
- [x] No circular dependencies (verified in dependency diagram + rules)
- [x] Level data is user-modifiable without code changes
- [x] Extension points documented for worlds, enemies, masks, items, audio, dialogue, levels, economy tuning
- [x] A developer can read this document and know exactly where to put new code
- [x] Economy values in data/economy.json (single source of truth, hot-reloadable)
- [x] Mask post-boss acquisition flow fully specified (Appendix B)
- [x] Level replay system with per-level unlock (Appendix D)
- [x] Quick-swap mechanic handled in MaskSystem with W5.5 unlock gate
- [x] Death rollback preserves pre-level state (Appendix C)
