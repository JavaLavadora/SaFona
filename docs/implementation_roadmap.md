# Sa Fona -- Implementation Roadmap

**Last updated**: 2026-04-18
**Status**: Approved — In Progress
**Maintained by**: Na Francina (Project Manager)

---

## Overview

This roadmap covers **Phase 1 -- the Vertical Slice**, as decided in [Issue #8](https://github.com/Tonigit/SaFona/issues/8). The goal is to validate the core gameplay feel before committing to full content production.

**Phase 1 delivers:**
- World 1 (Sa Talaia) complete: 4 levels + Es Bou de Pedra boss fight
- World 2 stub: 1 level (Sa Via Nova) to validate Stone Slam usage in a Roman-themed context
- All core engine systems needed to support the above
- Placeholder art throughout (geometric shapes, hot-swappable)

**Phase 1 answers these questions:**
- Does the movement feel good? (walk, jump, wall jump)
- Is the sling combat satisfying? (tap + charge tiers)
- Does earning a mask at the end of a world create forward momentum?
- Does the difficulty curve from W1-L1 (tutorial) to W1-Boss feel right?
- Can the engine handle the target scope at 60 FPS?

**Critical design rule for Phase 1:** Masks are obtained at the END of each world (post-boss). W1 levels have NO masks. Stone Slam is earned after beating Es Bou de Pedra. The W2 stub level uses Stone Slam.

Development does NOT begin until this roadmap is approved by the project owner.

---

## Phase 1 Dependency Diagram

```
D1 (Core Engine Bootstrap)
 |
 +---> D2 (Tilemap, Physics & Camera)
 |      |
 |      +---> D3 (Player Entity & Movement)
 |             |
 |             +---> D4 (Sling Combat & Projectiles)
 |             |      |
 |             |      +---> D6 (Enemies & Combat Integration)
 |             |      |      |
 |             |      |      +---> D8 (W1 Levels: L1-L4) ----+
 |             |      |      |                                |
 |             |      |      +---> D9 (Boss System &          |
 |             |      |             Es Bou de Pedra) -------->+
 |             |      |                                       |
 |             +---> D5 (HUD, Pickups & Economy)              |
 |             |      |                                       |
 |             |      +---> D8                                |
 |             |      +---> D10                               |
 |             |                                              |
 |             +---> D7 (Dialogue & Companion)                |
 |                    |                                       |
 |                    +---> D8                                |
 |                                                            v
 |                                              D10 (Mask System, Shop,
 |                                                   Post-Boss Flow &
 |                                                   W2 Stub)
 |
 +---> D5, D7 (parallel with D2-D4 where possible)
```

**Critical path**: D1 -> D2 -> D3 -> D4 -> D6 -> D9 -> D10 (7 deliverables in sequence)

**Parallel opportunities**:
- D5 (HUD, Pickups & Economy) can be built in parallel with D4 (Sling) once D3 is done
- D7 (Dialogue & Companion) can be built in parallel with D4-D6 once D3 is done
- D8 (W1 Levels) can begin once D6 is done, in parallel with D9 starting

---

## Deliverables

### Completed

**Deliverable 1: Core Engine Bootstrap** -- PR #18, Issue #17
- Merged 2026-04-17, user signed off
- 70 tests, all passing
- Game loop, PixelScaler, InputHandler, EventBus, SceneManager, SpriteRenderer, BaseScene, TestScene
- `config/controls.py` removed per review (bindings in InputHandler + controls_default.json)

**Deliverable 2: Tilemap, Physics & Camera** -- PR #20, Issue #19
- Merged 2026-04-17, user signed off
- 118 tests, all passing
- TileMap (3-layer rendering, collision types), PhysicsSystem (AABB, gravity, one-way platforms), Camera (smooth follow, bounds clamping, screen shake), LevelLoader, demo tilemap scene
- `rendering/animation.py` extracted from `sprite_renderer.py` per architecture review

**Deliverable 3: Player Entity & Movement** -- PR #22, Issue #21
- Merged 2026-04-18, user signed off
- 159 tests, all passing
- Entity base class, Player FSM (idle, running, jumping, falling, wall_sliding, wall_jumping), GameplayScene
- Nintendo-style wall jump (press into wall + jump), same-wall climb prevention (height tracking), variable jump height
- Player decoupled from PhysicsSystem per architecture review (update_intent/post_physics split)
- R key reset for testing convenience, 400ms wall jump lockout tuned with user

**Deliverable 4: Sling Combat & Projectiles** -- PR #24, Issue #23
- Merged 2026-04-18, user signed off
- 213 tests, all passing
- SlingSystem (tap melee + 3-tier charge ranged), Projectile entity, ChargeIndicator UI
- economy.json with data-driven sling config, SlingSystem decoupled from Player
- Attack keys: J/Z

**Deliverable 5: HUD, Pickups & Economy** -- PR #27, Issue #26
- Merged 2026-04-18, user signed off
- 347 tests (with D7), all passing
- EconomySystem (stone tracking, snapshot/restore), HUD (hearts + stone count), Pickup entities (heart/stone), Breakable entities (pots/crates)
- economy.json extended with drops, prices, pickup values. Single source of truth fix per architecture review.

**Deliverable 7: Dialogue System & Companion** -- PR #28, Issue #25
- Merged 2026-04-18, user signed off
- 347 tests (with D5), all passing
- DialogueBox (letter-by-letter reveal), DialogueScene (overlay), TriggerSystem (dialogue/level_end/save_point), Companion Bep (follow AI)
- Dialogue data in JSON, interact key E/K, sample dialogue in test level

**Deliverable 6: Enemies & Combat Integration** -- PR #30, Issue #29
- Merged 2026-04-18, user signed off
- 411 tests, all passing
- Enemy base entity, EnemyFactory (JSON-driven), W1 enemies (possessed_sheep, rival_warrior, stone_guardian)
- PatrolBehavior and ChaseBehavior with aggro, edge detection, ledge retreat, return-to-origin
- CombatSystem (projectile/melee/contact damage, invincibility frames, block mechanic)
- Sub-pixel movement accumulator, blocked-shot aggro trigger
- GameOverScene, pickup drops on death

**Deliverable 8: World 1 Levels (L1-L4)** -- PR #33, Issue #31
- Merged 2026-04-18, user sign-off pending
- 485 tests, all passing
- 4 levels: Es Primer Pas (tutorial), Sa Cova des Foner (cave), Es Talayot Sagrat (vertical), Sa Porta des Bou (gauntlet)
- Level progression chaining, Bep companion integration, 10 dialogue sequences
- `--level` CLI argument for testing specific levels
- Varied terrain design (hills, ledges, shafts, caves, pillars)

**Deliverable 9: Boss System & Es Bou de Pedra** -- PR #34, Issue #32
- Merged 2026-04-18, user sign-off pending
- 493 tests, all passing
- BossEntity base class with phase management, attack pattern sequencing, tell/punish state machine
- Es Bou de Pedra: 3 phases, 6 attacks (Bull Rush, Headbutt, Ground Stomp, Rock Hurl, Frenzy Rush, Core Pulse)
- BossScene with procedural arena, destructible pillars, intro/defeat sequences
- Boss health bar with phase markers and smooth damage trail
- Boss registry/factory pattern, data-driven from JSON

### Upcoming

---

### Deliverable 2: Tilemap, Physics & Camera

**Purpose**: Build the tile-based level geometry, AABB physics with gravity, and camera follow system so that a character can exist in a scrollable tile world with solid ground.

**Depends on**: Deliverable 1

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] TileMap loads tile data from JSON, manages background/midground/foreground layers
- [ ] TileMap renders layers with camera offset using placeholder colored tiles
- [ ] Collision types defined: solid, one-way, breakable_slam, hazard (per architecture spec)
- [ ] PhysicsSystem applies gravity and resolves AABB collisions against the tilemap
- [ ] One-way platforms work (pass through from below, land on top)
- [ ] Camera follows a target rect with smooth interpolation
- [ ] Camera clamps to level bounds (never shows outside the map)
- [ ] Camera screen shake works (driven by event bus `screen_shake` events)
- [ ] LevelLoader loads a level JSON file and produces a LevelData container (tilemap + entity spawn list + trigger list)
- [ ] A test level JSON file exists (`data/levels/test/test_level.json`) with the documented format
- [ ] A demo scene shows a scrolling tilemap with a controllable rectangle (no player entity yet -- raw rect movement)
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works (scene manager, input, event bus)
- [ ] Tests exist for: PhysicsSystem (gravity, collision resolution, one-way), Camera, TileMap, LevelLoader

**Estimated complexity**: Large

**Architecture references**: `level/tilemap.py`, `level/level_loader.py`, `systems/physics.py`, `core/camera.py`, data format Section 4.1

---

### Deliverable 3: Player Entity & Movement

**Purpose**: Create Ramon as a playable entity with the full core moveset (walk, jump, wall jump) using placeholder graphics, establishing the entity base class that all future entities will extend.

**Depends on**: Deliverable 2

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] Entity base class exists with position, velocity, rect, sprite reference, update/render methods
- [ ] Player entity (Ramon) extends Entity with a state machine (idle, running, jumping, falling, wall_sliding, wall_jumping)
- [ ] Left/right movement with configurable speed
- [ ] Single jump with configurable force, variable jump height (hold jump for higher, release for lower)
- [ ] Wall jump: automatic when pressing jump while against a wall and airborne
- [ ] Wall slide: Ramon slides down walls slowly when pressing into them while airborne
- [ ] Player integrates with PhysicsSystem for gravity and collision
- [ ] Player responds to InputState actions (move_left, move_right, jump_pressed, jump_held, jump_released)
- [ ] Placeholder rendering: Ramon is a colored rectangle (24x32 pixels) with different colors per state (idle=blue, running=green, jumping=yellow, wall_sliding=cyan)
- [ ] Animation system stub exists (Animation class with frame durations, but uses placeholder colored surfaces)
- [ ] A GameplayScene exists that loads a test level, spawns the player, and runs physics + camera
- [ ] The movement feels responsive and satisfying at 60 FPS
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works
- [ ] Tests exist for: Player state transitions, wall jump detection, variable jump height

**Estimated complexity**: Large

**Architecture references**: `entities/entity.py`, `entities/player.py`, `scenes/gameplay.py`, `rendering/animation.py`

**Tuning note**: Movement parameters (speed, jump force, gravity, wall slide speed, wall jump force) should be defined in `config/settings.py` as constants, easily adjustable for feel tuning.

---

### Deliverable 4: Sling Combat & Projectiles

**Purpose**: Implement Ramon's sling weapon with tap-attack (melee) and hold-to-charge (ranged projectile with 3 tiers), plus the projectile entity system.

**Depends on**: Deliverable 3

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] SlingSystem detects tap vs. hold from InputState (attack_pressed, attack_held, attack_released)
- [ ] Tap attack creates a short-lived melee hitbox in front of Ramon (whip-crack feel)
- [ ] Hold attack tracks charge time across 3 tiers with thresholds from `economy.json`
- [ ] Charge tier visual feedback: a ChargeIndicator UI element near Ramon changes color per tier (Tier 1 = faint glow, Tier 2 = bright, Tier 3 = flash)
- [ ] On release, a Projectile entity spawns with damage and range based on charge tier
- [ ] Projectile entity moves in a direction, checks collision with tilemap (destroyed on hit) and entities
- [ ] Projectile base class supports future special ammo types (extensible, not built yet)
- [ ] `data/economy.json` exists with sling charge thresholds and damage values (per architecture spec)
- [ ] Sling combat works in the test level (player can tap-attack and charge-shoot)
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works (movement, physics, camera)
- [ ] Tests exist for: SlingSystem (tap detection, charge tiers, timing), Projectile (movement, collision)

**Estimated complexity**: Medium

**Architecture references**: `systems/sling_system.py`, `entities/projectile.py`, `ui/charge_indicator.py`, `data/economy.json` (sling section)

---

### Deliverable 5: HUD, Pickups & Economy

**Purpose**: Implement the heads-up display (hearts, stone count), the pickup system (heart pickups, stone pickups), and the economy system so the player has visible health, can collect resources, and the game tracks currency.

**Depends on**: Deliverable 3 (needs player entity and gameplay scene)

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] HUD renders in the gameplay scene: hearts (top-left, half-heart granularity, starting 3 hearts), stone count (top-right)
- [ ] HUD updates via EventBus subscriptions (heart_collected, stone_collected, damage_taken)
- [ ] EconomySystem loads all values from `data/economy.json` (prices, drops, costs)
- [ ] EconomySystem tracks stone count, supports add_stones/spend_stones
- [ ] EconomySystem provides snapshot/restore for death rollback
- [ ] Pickup entity exists: heart pickups restore health, stone pickups add currency
- [ ] Pickups spawn from level JSON entity definitions
- [ ] Pickups have placeholder rendering (heart = red diamond, stone = grey circle)
- [ ] Player contact with a pickup triggers collection via EventBus
- [ ] Breakable objects concept exists: certain tiles (pots, crates) can be hit with the sling tap and drop pickups based on economy.json drop tables
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works
- [ ] Tests exist for: EconomySystem (add/spend/snapshot/restore), HUD (data update), Pickup collection

**Estimated complexity**: Medium

**Architecture references**: `ui/hud.py`, `entities/pickup.py`, `systems/economy.py`, `data/economy.json`

**Note**: This deliverable can be built in parallel with D4 (Sling Combat) once D3 is complete, since they have no mutual dependency. However, pickup drops from breakable objects require the sling tap from D4, so full integration happens when both are done.

---

### Deliverable 6: Enemies & Combat Integration

**Purpose**: Implement the enemy system (base enemy, enemy factory, W1 enemy types) and the combat system that resolves damage between player, enemies, and projectiles.

**Depends on**: Deliverable 4 (sling combat), Deliverable 5 (economy for drop tables, HUD for damage display)

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] Enemy base class extends Entity with health, contact damage, behavior reference, and drop table
- [ ] EnemyFactory creates enemies from JSON definitions (`data/enemies/world1_enemies.json`)
- [ ] W1 enemy types implemented with behavior components:
  - Possessed sheep: patrol behavior, charge attack with tell (0.8s), 2 HP
  - Rival tribal warrior: chase behavior, block mechanic, 3 HP
  - Stone guardian: patrol behavior, heavy attack with tell (1.0s), 6 HP
- [ ] Enemy behavior components: patrol (walk back and forth within range) and chase (follow player within range)
- [ ] CombatSystem resolves player-vs-enemy contact damage, projectile-vs-enemy damage, and enemy-attack-vs-player damage
- [ ] Invincibility frames after taking damage (player blinks, brief damage immunity)
- [ ] Enemies drop stones on death (amount from economy.json via EnemyFactory)
- [ ] Enemies can drop heart pickups on death (chance from economy.json)
- [ ] Player death triggers when hearts reach 0 (publishes player_died event)
- [ ] GameOverScene exists (placeholder: colored screen with "Press any key to restart")
- [ ] Enemy placeholder rendering: different colored rectangles per type (sheep=white, warrior=brown, guardian=dark grey)
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works (movement, sling, pickups, HUD)
- [ ] Tests exist for: CombatSystem (damage dealing, invincibility frames), EnemyFactory, enemy behaviors (patrol range, chase activation)

**Estimated complexity**: Large

**Architecture references**: `entities/enemy.py`, `entities/enemy_behaviors.py`, `systems/combat.py`, `data/enemies/world1_enemies.json`, `scenes/game_over.py`

---

### Deliverable 7: Dialogue System & Companion

**Purpose**: Implement the dialogue box UI, the dialogue scene overlay, Bep's companion entity, and the trigger system so that Bep can deliver tutorial hints and story dialogue can play during levels.

**Depends on**: Deliverable 3 (needs player entity and gameplay scene)

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] DialogueBox renders at the bottom of the screen: text box with speaker name and letter-by-letter text reveal
- [ ] Portrait placeholder (colored square with speaker initial)
- [ ] Pressing interact advances to next line or finishes revealing current line
- [ ] Dialogue is skippable (per dialogue definition)
- [ ] DialogueScene is an overlay scene (pushes onto scene stack on top of gameplay, gameplay is visible but dimmed behind)
- [ ] Dialogue data loads from JSON files (`data/dialogue/world1_dialogue.json`, `data/dialogue/bep_hints.json`)
- [ ] Trigger system: rectangular trigger zones in levels that fire events when the player enters them
- [ ] Trigger types implemented: dialogue trigger (starts a dialogue sequence), level_end trigger (completes the level)
- [ ] Companion entity (Bep): follows Ramon with simple AI (stays near, catches up when far), placeholder rendering (16x16 green rectangle)
- [ ] Bep does NOT have gameplay interaction -- purely visual + dialogue trigger
- [ ] Save point trigger type exists (marks where Llorencc shop appears later -- for now just marks level progress)
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works
- [ ] Tests exist for: DialogueBox (advance, skip, letter reveal timing), Trigger (player enters zone -> event fires)

**Estimated complexity**: Medium

**Architecture references**: `ui/dialogue_box.py`, `scenes/dialogue.py`, `entities/companion.py`, `level/trigger.py`, `data/dialogue/*.json`

**Note**: This deliverable can be built in parallel with D4, D5, and D6 once D3 is complete.

---

### Deliverable 8: World 1 Levels (L1-L4)

**Purpose**: Design and implement the four World 1 levels with proper enemy placement, platforming challenges, collectibles, dialogue triggers, and difficulty progression following the GDD specifications.

**Depends on**: Deliverable 6 (enemies & combat), Deliverable 7 (dialogue & triggers), Deliverable 5 (pickups & economy)

**Assigned to**: En Tomeu (Level Designer), with support from N'Andreu for any engine gaps

**Acceptance criteria**:
- [ ] Level 1-1 "Es Primer Pas": tutorial level, horizontal, difficulty 1/10, teaches movement + jump + wall jump hint. No enemies first half, 2-3 possessed sheep second half. 15-20 stones, 1 heart pickup. Bep dialogue triggers teach controls.
- [ ] Level 1-2 "Sa Cova des Foner": cave section, difficulty 2/10, teaches sling tap + charge. 4-5 sheep, 2 warriors. Distant switch teaches charged shot. 1 secret (hidden alcove).
- [ ] Level 1-3 "Es Talayot Sagrat": vertical layout, difficulty 3/10, mandatory wall jumps, stone guardian first encounter. 1 secret + 1 retroactive secret placeholder (cracked floor for Stone Slam). Proto-shop save point.
- [ ] Level 1-4 "Sa Porta des Bou": mixed layout, difficulty 4/10, pre-boss gauntlet combining all movement + combat skills. Enemy combinations. Boss gate at end.
- [ ] All levels use the documented JSON level format
- [ ] All levels have correct enemy types and counts per GDD specifications
- [ ] All levels have dialogue triggers with Bep hint text per GDD teaching beats
- [ ] All levels have save points at the end
- [ ] Difficulty progression feels appropriate (1 -> 2 -> 3 -> 4)
- [ ] Tileset uses placeholder colored tiles with distinct collision types visible
- [ ] Parallax background layers configured (placeholder colored gradients)
- [ ] `data/dialogue/world1_dialogue.json` and `data/dialogue/bep_hints.json` populated with W1 dialogue
- [ ] The game launches and all four levels are playable in sequence without errors
- [ ] Previous functionality still works

**Estimated complexity**: Large

**Architecture references**: GDD Section 5.3 (W1 level details), data format Section 4.1 (level JSON), `data/levels/world1/`

---

### Deliverable 9: Boss System & Es Bou de Pedra

**Purpose**: Implement the boss entity framework and the first boss fight (Es Bou de Pedra) with 3 phases, attack patterns, tells, punish windows, and the boss health bar HUD element.

**Depends on**: Deliverable 6 (combat system, enemy base), Deliverable 4 (sling for dealing damage), Deliverable 2 (camera shake for boss effects)

**Assigned to**: N'Andreu (Engine Programmer)

**Acceptance criteria**:
- [ ] BossEntity base class extends Entity with: phase management (HP thresholds), pattern sequencing, tell timers, punish windows, and a health pool
- [ ] Boss health bar renders at the top of the screen with phase markers
- [ ] BossScene extends GameplayScene with boss-specific logic (arena, phase transitions, intro cutscene trigger)
- [ ] Boss data loads from `data/bosses/boss_bou_de_pedra.json` (per architecture spec)
- [ ] Es Bou de Pedra implemented with 3 phases:
  - Phase 1 (100%-66%): Bull Rush (charge + wall stun, 2.5s punish), Headbutt (short range, 1.5s punish)
  - Phase 2 (66%-33%): Faster Bull Rush, Ground Stomp (shockwave, jump to dodge), Rock Hurl (3 projectiles with shadow markers)
  - Phase 3 (33%-0%): Frenzy Rush (bounce off walls), Core Pulse (circular shockwave, airborne to dodge), exposed core weak point (2x charge damage, 3x Tier 3)
- [ ] All attacks have tell times matching GDD specs (minimum 0.5s tell rule)
- [ ] All attacks have punish windows matching GDD specs (minimum 1.5s punish rule)
- [ ] Phase transitions have screen shake and visual feedback
- [ ] Destructible pillars in the arena (4 pillars, Bull Rush shatters them)
- [ ] Boss defeat triggers `boss_defeated` event
- [ ] Boss intro cutscene plays before the fight (brief, skippable on retry)
- [ ] Boss placeholder rendering: large rectangle (48x48+) with color changes per phase
- [ ] The boss fight is playable, fair, and learnable
- [ ] The game launches and runs without errors
- [ ] Previous functionality still works
- [ ] Tests exist for: BossEntity (phase transitions, HP thresholds), attack pattern timing

**Estimated complexity**: Large

**Architecture references**: GDD Section 6.2 (Es Bou de Pedra), `entities/boss_entity.py`, `scenes/boss.py`, `data/bosses/boss_bou_de_pedra.json`, `ui/boss_health_bar.py`

---

### Deliverable 10: Mask System, Shop, Post-Boss Flow & W2 Stub

**Purpose**: Implement the mask system (Stone Slam only for Phase 1), Llorencc's shop (basic), the post-boss reward flow, the save system, and the W2 stub level to validate the "earn mask -> use mask in next world" loop.

**Depends on**: Deliverable 9 (boss defeat triggers mask acquisition), Deliverable 8 (W1 levels complete), Deliverable 5 (economy for shop purchases)

**Assigned to**: N'Andreu (Engine Programmer) + En Tomeu (Level Designer, W2 stub)

**Acceptance criteria**:
- [ ] MaskSystem manages mask inventory, equipping, and cooldowns. Loads from `data/masks.json`.
- [ ] Stone Slam power implemented: ground pound shockwave (3-tile range), breaks breakable_slam tiles, stuns grounded enemies, 2s cooldown
- [ ] Mask power activated with dedicated button (mask_power_pressed in InputState)
- [ ] HUD shows mask icon (top-right) with cooldown radial fill. Shows empty/no-mask state during W1.
- [ ] Post-boss cutscene flow: boss defeated -> dimoni dialogue -> mask granted to Llorencc -> time portal transition
- [ ] CutsceneScene handles scripted sequences (boss intros, mask grants, portal)
- [ ] SaveSystem implements JSON save/load with the documented format
- [ ] Save triggers: end of each level (automatic), post-boss mask acquisition
- [ ] Death rollback: restart level with pre-level state (stones, hearts restored to level entry)
- [ ] Consumable refund on death (consumables used during failed attempt are restored)
- [ ] ShopScene (Llorencc's shop): basic UI with Items tab (ensaimada, heart upgrade 1). Masks tab shows Stone Slam for equipping.
- [ ] Shop accessible from save points (after L1-2 as proto-shop per GDD, full shop from W2)
- [ ] NPC entity for Llorencc (placeholder: tall rectangle with "L" label)
- [ ] MainMenuScene: title screen with Start/Continue options
- [ ] Level transition flow: level end trigger -> save -> load next level (or shop -> next level)
- [ ] W2 stub level "Sa Via Nova" (Level 2-1): Roman-themed, teaches Stone Slam usage, cracked floors, 3 legionaries (shield + patrol behavior), 2 war dogs (chase behavior, fast). Llorencc introduction dialogue.
- [ ] W2 enemies defined in `data/enemies/world2_enemies.json`: legionary (shield behavior) and war dog (chase, fast)
- [ ] Complete playthrough possible: Main Menu -> W1-L1 through W1-L4 -> Boss -> Stone Slam earned -> W2-L1 with Stone Slam
- [ ] The game launches and the full Phase 1 vertical slice is playable end-to-end
- [ ] Previous functionality still works
- [ ] Tests exist for: MaskSystem (unlock, equip, cooldown), SaveSystem (save/load/rollback), Stone Slam (shockwave range, tile breaking)

**Estimated complexity**: Extra Large

**Architecture references**: `systems/mask_system.py`, `systems/save_system.py`, `scenes/shop.py`, `scenes/cutscene.py`, `scenes/main_menu.py`, `ui/shop_ui.py`, `entities/npc.py`, `data/masks.json`, GDD Section 5.4 Level 2-1

---

## Phase 2+ (Deferred)

After Phase 1 sign-off, the following will be planned:
- W2 complete (remaining 3 levels + Metellus boss)
- W3 through W5.5 (incremental world production)
- Double Jump, Fire Dash, Smoke Vanish, Tourist Rage mask powers
- Special ammo system
- Consumable system (full)
- Level Select & replay
- Settings menu & control remapping
- Audio integration (music + SFX)
- Quick-swap mechanic (W5.5)

These are NOT planned in detail yet. Each world will be scoped after the previous one is signed off.

---

## Auditor Notes

### Audit Process

The deliverable plan was reviewed by N'Aina (Auditor) following her standard workflow: dependency graph construction, mental simulation of each deliverable, integration risk analysis, and efficiency check.

**Round 1 Findings and Responses:**

| # | Finding | Type | Recommendation | Decision | Reasoning |
|---|---------|------|---------------|----------|-----------|
| 1 | Event bus is a silent dependency for nearly every system | Critical | Include EventBus in D1 alongside game loop | **Accepted** | EventBus is zero-dependency and blocks everything. Bundling with D1 avoids a tiny standalone deliverable. |
| 2 | SpriteRenderer/Animation system is implicit | Critical | Include placeholder rendering foundation in D1 | **Accepted** | Every deliverable needs to render something. The sprite renderer stub (generating colored rectangles) must exist from D1. |
| 3 | InputHandler too small as standalone | Optimization | Merge with game loop in D1 | **Accepted** | InputHandler is tightly coupled to the game loop. Merged into D1. |
| 4 | Tilemap and Physics have no value without each other | Optimization | Merge TileMap + Physics + Camera into one deliverable (D2) | **Accepted** | These three form one coherent unit: the level world. Splitting them would produce deliverables that cannot be demonstrated independently. |
| 5 | Entity base class placement | Optimization | Move Entity base to D3 (Player) rather than a standalone deliverable | **Accepted** | The entity base is best defined when writing the first real entity (Player). Designing it in isolation risks premature abstraction. |
| 6 | LevelLoader should be in D2 not D8 | Critical | LevelLoader must exist before any level can be loaded. Place in D2. | **Accepted** | Correct -- LevelLoader and the level JSON format must be defined in D2 so that D3+ can use level files for testing. |
| 7 | D10 is very large (mask + shop + save + cutscene + W2 stub + main menu) | Optimization | Consider splitting into D10a (save + main menu + level flow) and D10b (mask + shop + W2) | **Rejected** | These systems are tightly coupled in the end-to-end flow. Splitting would create a deliverable (D10a) that cannot demonstrate the full loop. The payoff of Phase 1 is the complete experience from menu to W2 stub. Keeping them together ensures the integration is tested as a unit. Complexity is high but the developer understands the full picture. |
| 8 | W2 enemy types (legionary with shield, war dog) need a new behavior: shield | Optimization | Ensure shield behavior is part of D10 scope, not D6 | **Accepted** | D6 only builds patrol and chase behaviors for W1. The shield behavior for legionaries is needed for D10's W2 stub and is scoped there. |

**Round 2 Findings and Responses:**

| # | Finding | Type | Recommendation | Decision | Reasoning |
|---|---------|------|---------------|----------|-----------|
| 1 | Parallel work opportunity: D5 and D7 can both start once D3 is done | Approved | Already noted in the plan | **Acknowledged** | This is documented in the dependency diagram. D5 (HUD/Pickups/Economy) and D7 (Dialogue/Companion) have no mutual dependency and both only require D3. |
| 2 | Integration risk at D8-D9: boss fight is where physics, combat, sling, camera shake, HUD, enemies all converge | Optimization | Consider a lightweight D8.5 integration checkpoint | **Rejected** | D9 (Boss) already serves as the integration checkpoint. The boss fight inherently tests all systems working together. Adding a separate integration deliverable is overhead that produces no new user-visible value. If integration issues surface in D9, they will be fixed in D9's PR review cycle. |
| 3 | Audio system not in Phase 1 | Observation | Confirm this is intentional | **Confirmed intentional** | AudioManager with placeholder silence is sufficient for Phase 1. The architecture already handles graceful fallback for missing audio files. Real audio is Phase 2+ scope. The event bus slots for audio events exist but no sounds play -- this is by design. |
| 4 | Economy.json should be created in D4 (when sling needs it) and extended in D5 (when economy system needs it) | Optimization | Define economy.json structure incrementally | **Accepted** | D4 creates economy.json with the sling section. D5 extends it with drops, prices, and consumable data. D10 extends it further for shop inventory. This avoids defining a massive JSON upfront that might need restructuring. |
| 5 | Mask system only needs Stone Slam for Phase 1 -- avoid over-engineering | Approved | Build MaskSystem with the full interface but only Stone Slam implementation | **Acknowledged** | The MaskSystem class will have the full API (unlock, equip, cooldown, cycle) but only Stone Slam is implemented. Other masks are JSON definitions that produce "not implemented" behavior. This is the right balance between future-proofing and YAGNI. |

### Auditor Summary

N'Aina approved the plan after Round 2 with no remaining critical findings. The plan front-loads foundations correctly, produces runnable builds at every step, and minimizes rework. The main risk is D10's size, which the PM accepted with documented reasoning.

---

## Agent Assignment Summary

| Deliverable | Primary Agent | Support |
|---|---|---|
| D1: Core Engine Bootstrap | N'Andreu | -- |
| D2: Tilemap, Physics & Camera | N'Andreu | -- |
| D3: Player Entity & Movement | N'Andreu | -- |
| D4: Sling Combat & Projectiles | N'Andreu | -- |
| D5: HUD, Pickups & Economy | N'Andreu | -- |
| D6: Enemies & Combat Integration | N'Andreu | -- |
| D7: Dialogue System & Companion | N'Andreu | -- |
| D8: World 1 Levels (L1-L4) | En Tomeu | N'Andreu (engine gaps) |
| D9: Boss System & Es Bou de Pedra | N'Andreu | -- |
| D10: Mask System, Shop, Post-Boss Flow & W2 Stub | N'Andreu | En Tomeu (W2 stub level) |

---

## Change Log

- 2026-04-17: Initial roadmap created by Na Francina. Audited by N'Aina (2 rounds). Awaiting user approval.
