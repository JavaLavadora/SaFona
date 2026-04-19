# D10 Task Breakdown: Mask System, Shop, Post-Boss Flow & W2 Stub

**Date**: 2026-04-18
**Author**: Na Francina (Project Manager)
**Deliverable**: D10 — Mask System, Shop, Post-Boss Flow & W2 Stub
**Estimated complexity**: Extra Large
**Assigned to**: N'Andreu (Engine Programmer) + En Tomeu (Level Designer)

---

## 1. Task Breakdown

D10 is split into 5 sub-tasks. Each builds on the previous and can be independently tested.

### Sub-task 10A: Save System & Main Menu
**Assigned to**: N'Andreu
**Depends on**: D1-D9 (all merged)

Implement the SaveSystem and MainMenuScene so the game has a proper entry point and persistent state.

**Scope**:
- `systems/save_system.py` — JSON save/load, single save slot (`saves/save_slot_1.json`)
- `snapshot_level_entry()` and `rollback_to_snapshot()` for death rollback
- Save triggers: publish `level_completed` event already exists — SaveSystem subscribes to it and writes to disk
- Death rollback: on `player_died`, restore stone count, hearts, consumables to level-entry state
- Consumable refund on death (consumables used during failed attempt are restored)
- `scenes/main_menu.py` — Title screen with Start (new game) and Continue (load save) options
- Level transition flow: `level_end` trigger -> save -> load next level
- `data/save_format.json` not needed as a file — the format is defined in the architecture (Section 4.6)

**Acceptance criteria**:
- [ ] `SaveSystem` saves game state to JSON on `level_completed` events
- [ ] `SaveSystem` loads game state from JSON; returns `None` if no save exists
- [ ] `snapshot_level_entry()` captures stones, hearts, consumable inventory at level start
- [ ] `rollback_to_snapshot()` restores pre-level state on death (stones, hearts, consumables)
- [ ] Consumables used during a failed attempt are refunded on death
- [ ] `MainMenuScene` renders title screen with Start / Continue options
- [ ] Continue is disabled (grayed out) when no save file exists
- [ ] Start begins at W1-L1; Continue loads from save file
- [ ] Level transition: completing a level saves and loads the next level
- [ ] Tests exist for: save/load round-trip, death rollback, consumable refund, `exists()` check

---

### Sub-task 10B: Mask System & Stone Slam Power
**Assigned to**: N'Andreu
**Depends on**: 10A (save system persists mask state)

Implement the MaskSystem and the Stone Slam power as the first (and only Phase 1) mask.

**Scope**:
- `systems/mask_system.py` — Mask inventory, equip/unequip, cooldown timer, power activation
- `data/masks.json` — Stone Slam definition (per architecture Section 4.4)
- Stone Slam power: ground pound shockwave (3-tile range), breaks `breakable_slam` tiles, stuns grounded enemies, 2s cooldown
- Player integration: `mask_power_pressed` in InputState triggers the active mask power
- HUD update: mask icon (top-right) with cooldown radial fill; empty/no-mask state during W1
- Camera shake on Stone Slam activation
- `breakable_slam` tile type added to the tilemap/physics system
- SaveSystem integration: masks are persisted in save data

**Acceptance criteria**:
- [ ] `MaskSystem` loads mask definitions from `data/masks.json`
- [ ] `unlock_mask(mask_id)` adds mask to inventory; `equip_mask(mask_id)` sets the active mask
- [ ] `activate_power()` triggers Stone Slam effect when equipped and off cooldown
- [ ] Stone Slam shockwave has 3-tile range, damages and stuns grounded enemies (1.5s stun)
- [ ] Stone Slam breaks tiles tagged `breakable_slam`
- [ ] 2-second cooldown enforced; mask_power_pressed ignored during cooldown
- [ ] HUD shows mask icon with cooldown radial fill; shows empty state when no mask equipped
- [ ] Camera shake fires on Stone Slam activation
- [ ] Mask state (unlocked, equipped) is included in save data
- [ ] Tests exist for: unlock, equip, cooldown timing, shockwave range, tile breaking

---

### Sub-task 10C: Post-Boss Cutscene Flow & Mask Acquisition
**Assigned to**: N'Andreu
**Depends on**: 10B (mask system to receive `mask_acquired` event)

Implement the CutsceneScene and the post-boss reward flow that connects the boss defeat to the mask grant.

**Scope**:
- `scenes/cutscene.py` — Scripted sequence scene: plays dialogue, visual effects, and transitions
- Post-boss flow: `boss_defeated` event -> dimoni dialogue -> `mask_acquired` event -> time portal transition
- The cutscene reads the boss definition's `post_defeat` block (already in `boss_bou_de_pedra.json`)
- `mask_acquired` event publishes to MaskSystem (unlock) and SaveSystem (persist immediately)
- Save on mask acquisition: mask is saved before portal transition (player can quit during portal without losing mask)
- Portal transition: visual effect (screen fade/wipe) leading to next world's first level
- `ui/transition.py` — Screen fade and wipe effects (used by cutscene and level transitions)
- Boss intro cutscene support: brief, skippable on retry (current boss scene has intro text — extend or replace with CutsceneScene push)

**Acceptance criteria**:
- [ ] `CutsceneScene` handles scripted sequences driven by cutscene definition data
- [ ] Post-boss flow: boss defeat -> dimoni dialogue -> mask granted -> portal transition
- [ ] `mask_acquired` event fires at the grant moment (not before, not after)
- [ ] MaskSystem unlocks Stone Slam on `mask_acquired`; does NOT auto-equip
- [ ] SaveSystem writes save immediately on `mask_acquired` (mask persists even if player quits)
- [ ] Portal transition uses screen fade/wipe effect
- [ ] Transition loads W2-L1 after the portal animation
- [ ] Flow is skippable on retry (if boss re-fought after death)
- [ ] Tests exist for: cutscene sequence progression, `mask_acquired` event integration

---

### Sub-task 10D: Shop System & Llorencc NPC
**Assigned to**: N'Andreu
**Depends on**: 10B (mask system for equipping), 10A (save system for persisting purchases)

Implement the ShopScene, shop UI, and the Llorencc NPC entity.

**Scope**:
- `scenes/shop.py` — Shop scene (overlay or replacement), two tabs: Items and Masks
- `ui/shop_ui.py` — Tab navigation, item listing, price display, purchase confirmation, feedback
- Items tab: ensaimada (heal, 10 stones), heart upgrade 1 (40 stones). Prices from `economy.json`.
- Masks tab: shows unlocked masks (Stone Slam after W1 boss). Equip button. No purchase — masks are free to equip.
- `entities/npc.py` — Generic NPC entity. Llorencc: tall rectangle placeholder with "L" label.
- `data/shop/shop_inventory.json` — Shop inventory with unlock-world thresholds
- `data/dialogue/llorencc_shop.json` — Llorencc greeting/interaction dialogue
- Shop accessible from save points: after L1-2 as proto-shop (limited to ensaimada), full shop from W2
- Proto-shop: a simplified version at save points in W1 (after L1-2). Only sells ensaimada.
- Economy integration: `shop_purchase` event deducts stones via EconomySystem
- Save integration: purchases are persisted

**Acceptance criteria**:
- [ ] `ShopScene` renders with Items tab and Masks tab
- [ ] Items tab lists available items based on current world (ensaimada from W1, heart_upgrade_1 from W1)
- [ ] Purchase deducts stones; insufficient stones shows feedback (price turns red or message)
- [ ] Masks tab shows unlocked masks; equip button sets active mask via MaskSystem
- [ ] `NPC` entity renders Llorencc as placeholder (tall rectangle, "L" label)
- [ ] Llorencc NPC at save points triggers shop on interaction
- [ ] Proto-shop after L1-2: limited inventory (ensaimada only)
- [ ] `shop_purchase` event published on purchase; EconomySystem deducts stones
- [ ] Purchases persist in save data
- [ ] Tests exist for: shop purchase flow, insufficient funds rejection, mask equip from shop

---

### Sub-task 10E: W2 Stub Level "Sa Via Nova" (Level 2-1)
**Assigned to**: En Tomeu (Level Designer), with N'Andreu support for new enemy types
**Depends on**: 10B (Stone Slam for level design), 10C (post-boss flow transitions to W2), 10D (shop for Llorencc intro)

Build the W2-L1 stub level that validates the "earn mask -> use mask" loop.

**Scope**:
- `data/levels/world2/level_2_1.json` — Level layout with Roman theme
- Roman-themed tiles: stone road, columns, atrium multi-level platforms. Use existing tilemap system with new tile IDs.
- Cracked floors (`breakable_slam` tiles) that require Stone Slam to break
- `data/enemies/world2_enemies.json` — Legionary (shield + patrol) and War Dog (chase, fast)
- Legionary: shield behavior — blocks frontal sling attacks, vulnerable to Stone Slam shockwave and attacks from above/behind
- War dog: chase behavior with fast movement speed, low to ground
- 3 legionaries and 2 war dogs placed in the level per GDD
- 25-30 sling stones, 1 heart pickup, 1 secret (beneath cracked atrium floor, 10 bonus stones)
- Llorencc introduction dialogue at level start (world arrival cutscene + shop tutorial)
- `data/dialogue/world2_dialogue.json` — W2 dialogue lines (Llorencc intro, Bep hints for cracked floors and legionaries)
- Save point with Llorencc shop at level end
- `data/levels/world2/` — New parallax background config for Roman theme (placeholder colors)

**Acceptance criteria**:
- [ ] Level 2-1 loads and is playable after the post-boss portal transition
- [ ] Roman-themed tileset (placeholder rectangles with distinct palette: warm grey stone, red accents)
- [ ] Cracked floors break when Stone Slam is used on them
- [ ] 3 legionaries with shield behavior: block frontal attacks, vulnerable to Stone Slam and rear attacks
- [ ] 2 war dogs with chase behavior: fast, low to ground
- [ ] Llorencc NPC appears at level start with introduction dialogue and shop tutorial
- [ ] Stone Slam is the key mechanic: breaks floors, scatters shields
- [ ] 1 secret area beneath cracked atrium floor (10 bonus stones)
- [ ] Save point with Llorencc shop at level end
- [ ] W2 enemy definitions in `data/enemies/world2_enemies.json`
- [ ] W2 dialogue in `data/dialogue/world2_dialogue.json`
- [ ] Tests exist for: legionary shield behavior, war dog chase behavior

---

## 2. Dependency Order

```
10A: Save System & Main Menu
 |
 v
10B: Mask System & Stone Slam ──────────┐
 |                                       |
 v                                       v
10C: Post-Boss Cutscene Flow         10D: Shop System & Llorencc NPC
 |                                       |
 └──────────────┬────────────────────────┘
                |
                v
             10E: W2 Stub Level "Sa Via Nova"
```

**Sequential dependencies**:
- 10A must come first (save system is needed by everything downstream)
- 10B depends on 10A (mask state needs to be saved)
- 10C depends on 10B (mask_acquired event needs MaskSystem)
- 10D depends on 10B (masks tab needs MaskSystem) and 10A (purchases need SaveSystem)
- 10E depends on 10B, 10C, and 10D (needs Stone Slam, post-boss flow, and shop)

**Parallel opportunity**:
- **10C and 10D can be built in parallel** after 10B is complete. They share no code dependencies — 10C is the cutscene/transition pipeline, 10D is the shop UI pipeline. Both depend on 10B but not on each other.

---

## 3. Implementation Order

| Order | Sub-task | Assignee | Est. Size | Notes |
|-------|----------|----------|-----------|-------|
| 1 | **10A**: Save System & Main Menu | N'Andreu | Medium | Foundation for persistence. Unblocks everything. |
| 2 | **10B**: Mask System & Stone Slam | N'Andreu | Medium-Large | Core gameplay addition. The new verb. |
| 3a | **10C**: Post-Boss Cutscene Flow | N'Andreu | Medium | Can start once 10B merges. |
| 3b | **10D**: Shop System & Llorencc | N'Andreu | Medium | Can start once 10B merges. Parallel with 10C if using worktrees. |
| 4 | **10E**: W2 Stub Level | En Tomeu + N'Andreu | Medium | N'Andreu adds shield/chase enemy behaviors; En Tomeu builds the level. |

**Recommended approach**: Implement 10A and 10B as two PRs on the same branch or consecutive branches. Then use worktree isolation to build 10C and 10D in parallel. Finally, 10E integrates everything.

---

## 4. Risk Assessment

### High Risk
1. **Post-boss-to-W2 flow integration** (10C + 10E): The transition from boss defeat -> cutscene -> mask grant -> portal -> W2-L1 load -> Llorencc intro is the longest chain of scene transitions in the game so far. Each handoff (BossScene -> CutsceneScene -> GameplayScene with new level) must preserve game state correctly. **Mitigation**: Test the full chain manually after 10C and again after 10E. Write an integration test that simulates the event sequence.

2. **Stone Slam physics interaction** (10B): The shockwave needs to interact with the physics system (break tiles, apply stun to entities within range). This is the first time a player action modifies the tilemap at runtime. **Mitigation**: Start with a simple implementation — mark tiles as destroyed and update collision data. Keep the shockwave as a circular range check, not a physics body.

### Medium Risk
3. **Save system rollback correctness** (10A): The death rollback must restore the exact pre-level state including consumables. If any system holds state that isn't captured in the snapshot, the rollback will be incomplete. **Mitigation**: The architecture specifies exactly what to snapshot (stones, hearts, consumables, special ammo). Enumerate each and write a test that uses a consumable, dies, and verifies restoration.

4. **Shop UI complexity** (10D): Two-tab UI with item listings, prices, purchase flow, and mask equipping is the most complex UI built so far. The game only has the HUD and dialogue box currently. **Mitigation**: Keep the shop UI minimal — text-based list with cursor navigation. No fancy graphics. Placeholder "box with text" aesthetic consistent with development style.

### Low Risk
5. **New enemy behaviors** (10E): Shield and chase behaviors are variants of existing patrol/chase patterns in `enemy_behaviors.py`. Shield adds a frontal damage check; chase increases speed. **Mitigation**: Build on the existing behavior component system.

---

## 5. Open Questions

### Q1: Proto-Shop Implementation — Separate Scene or Simplified Shop?
The GDD mentions a "proto-shop" (mysterious stone pedestal) opening after L1-2 that sells basic ensaimadas. Should this be:
- **(A)** The same ShopScene with a filtered inventory (only ensaimada, no masks tab), or
- **(B)** A simpler interaction (interact with pedestal -> buy ensaimada dialog) without the full shop UI?

Option A is less code (one shop, filtered by world). Option B is more thematic but requires a second purchase flow. **Recommendation**: Option A — same ShopScene, inventory filtered by `unlock_world` threshold in `shop_inventory.json`.

### Q2: CutsceneScene Data Format — Hardcoded or Data-Driven?
The architecture defines `scenes/cutscene.py` but doesn't specify the cutscene data format in detail. For D10, the only cutscenes needed are:
- Post-boss dimoni dialogue + mask grant
- Portal transition to W2
- Llorencc introduction in W2-L1

Should these be:
- **(A)** Data-driven (JSON cutscene definitions, similar to dialogue), or
- **(B)** Code-driven sequences for D10, with a data format designed later when more cutscenes exist?

Option B is faster for D10 but creates tech debt. Option A is more work upfront but aligns with the data-driven philosophy. **Recommendation**: Option A — define a simple JSON cutscene format now. The post-boss flow and Llorencc intro are good test cases for the format.

### Q3: Level Transition After Portal — Direct Load or Main Menu Checkpoint?
After the post-boss portal cutscene, should the game:
- **(A)** Load W2-L1 directly (seamless progression), or
- **(B)** Return to a world-transition screen / main menu before loading W2-L1?

The GDD implies seamless (portal -> next world). But the architecture mentions MainMenuScene. For Phase 1, the end-to-end playthrough needs to feel continuous. **Recommendation**: Option A — direct load into W2-L1 after portal. The main menu is for game start/resume only.

---

## 6. End-to-End Verification Checklist

After all 5 sub-tasks are merged, verify the complete Phase 1 vertical slice:

- [ ] Game launches to MainMenuScene with Start / Continue
- [ ] Start -> W1-L1 loads; player can play through all W1 levels
- [ ] Save triggers at end of each level; progress persists across restart
- [ ] Death restores pre-level state (stones, hearts, consumables)
- [ ] Proto-shop accessible after L1-2 (ensaimada purchase works)
- [ ] W1-L4 leads to boss arena; boss fight is playable
- [ ] Boss defeat triggers cutscene: dimoni dialogue -> Stone Slam mask granted
- [ ] Mask acquisition saved immediately; safe to quit
- [ ] Portal transitions to W2-L1
- [ ] Llorencc introduction dialogue plays; shop tutorial
- [ ] Stone Slam is equippable at Llorencc's shop
- [ ] Stone Slam works: breaks cracked floors, stuns enemies, 3-tile range, 2s cooldown
- [ ] HUD shows mask icon with cooldown radial
- [ ] Legionaries block frontal attacks; Stone Slam scatters shields
- [ ] War dogs chase the player at high speed
- [ ] Secret area accessible via Stone Slam on cracked atrium floor
- [ ] Save point with shop at W2-L1 end
- [ ] Continue from main menu loads the correct position
- [ ] The game runs at 60 FPS throughout

---

*This report is a working document. Sub-task branches and PRs will be tracked on the corresponding GitHub issue.*
