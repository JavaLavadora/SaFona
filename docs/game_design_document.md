# SA FONA — Game Design Document

> **Working title**: Sa Fona
> **Version**: 2.0 (Production)
> **Genre**: 2D Retro Side-Scrolling Platformer with Combat
> **Engine**: Pygame (Python)
> **Refined by**: En Biel (Game Director)
> **Based on**: Draft v1.0

---

## 1. GAME OVERVIEW

### 1.1 Concept Summary

Sa Fona is a 2D retro platformer set across the Balearic Islands through different historical eras. The player controls Ramon, a grumpy talayotic slinger who gets cursed into time-traveling with his annoying (but lovable) myotragus companion Bep. Each world represents a different period of Mallorcan history or folklore, blending real events and local legends with lighthearted parody. The game features a dimoni mask power-up system inspired by Mallorcan village demons, satisfying sling-based combat with tap-and-charge mechanics, and a reluctant-hero story in the spirit of Shrek.

### 1.2 Genre & Platform

- 2D side-scrolling platformer with combat
- PC (keyboard + gamepad support)

### 1.3 Engine & Technical Constraints

- Pygame (Python)
- Target resolution: 320x180 or 384x216 (scaled up, pixel-perfect)
- 60 FPS target
- No external game engine dependencies

### 1.4 Art Style & Tone

- 16-bit pixel art aesthetic (SNES era)
- Limited color palettes per world to give each era a distinct visual identity
- Lighthearted parody tone: serious historical and cultural themes are presented through the dry, deadpan perspective of a protagonist who wants absolutely nothing to do with any of it
- Cultural references to Mallorcan folklore, history, and modern-day reality, played for comedy but rooted in real tradition

### 1.5 References & Inspirations

- **Shrek** -- Reluctant hero, buddy dynamic between Ramon and Bep, parody tone
- **Crash Bandicoot** -- Mask power-up system (Aku Aku -> dimoni masks)
- **Castlevania** -- Sling-as-whip melee feel, gothic atmosphere (World 3)
- **Asterix** -- Historical comedy, small hero vs. empires
- **Shovel Knight** -- Retro platformer structure, world progression, shop NPCs

---

## 1.6 Development Scope & Phasing

> **Decision**: Vertical slice approach adopted per [Issue #8](https://github.com/Tonigit/SaFona/issues/8), confirmed by the project owner.

The full GDD describes the complete vision (6 worlds, all bosses, all mask powers). However, production follows a **vertical slice strategy** to validate the core gameplay feel before committing to full content production.

**Phase 1 — Vertical Slice (Proof of Concept)**

| Deliverable | Scope |
|---|---|
| **World 1 — Sa Talaia** | Complete: 4 levels + Es Bou de Pedra boss fight. Full tutorial flow, sling combat (tap + charge), wall jump, Stone Slam mask, shop introduction, Bep dialogue system. |
| **World 2 — Mallorca Romana (stub)** | 1 basic level to validate the double jump mechanic and Roman-themed tileset/enemies. No boss, no full progression — just enough to prove the second world's feel works. |

Phase 1 answers the critical design questions: Does the movement feel good? Is the sling combat satisfying? Does the mask system add meaningful depth? Does the difficulty curve from W1-L1 (tutorial) to W1-Boss feel right? Can the engine handle the target scope at 60 FPS?

**Phase 2+ — Incremental World Production**

After Phase 1 sign-off, remaining worlds (W2 complete, W3–W5, W5.5) are built incrementally. Each world is scoped, built, and playtested before the next begins. The full GDD content below serves as the design target, but production commitments beyond Phase 1 are deferred until the vertical slice proves the concept.

---

## 2. STORY & NARRATIVE

### 2.1 Premise & Inciting Incident

Ramon, a foner from the talayotic period (~1000 BC Mallorca), is napping against a talayot. His myotragus, Bep, wanders off and eats the sacred herbs growing on a dimoni's altar -- the dimoni's prized garden. The dimoni arrives furious, curses Bep, and storms off. Ramon wakes up, sees Bep chewing with a guilty face: "...What did you eat now?"

The curse has two effects: Bep gains the ability to speak (and won't shut up), and Bep becomes a living time-travel trigger -- after moments of great energy (boss defeats), the curse activates, Bep glows, sneezes, and rips open a time portal.

The player does not know any of this during World 1. It plays as a straight talayotic adventure. The time-travel premise is only revealed after beating the first boss.

### 2.2 Full Story Arc

**World 1 -- Sa Talaia (Talayotic ~1000 BC)**
Ramon and Bep navigate their own era. Something feels off -- possessed sheep, unnatural energy, a creeping wrongness. They defeat Es Bou de Pedra. Then Bep starts glowing. He sneezes. A time portal rips open. The dimoni from the intro appears, laughing: "You thought we were done? That sheep ate my herbs. Every dimoni on this island wants a piece of him now. Good luck." Ramon and Bep are sucked in.

Ramon: "...I just wanted a nap."

**World 2 -- Mallorca Romana (Roman Conquest, 123 BC)**
Ramon is confused by roads and tall architecture. Romans mistake him for a barbarian rebel. He meets Llorenc, a fellow talayotic warrior from Menorca who has been researching dimoni activity and tracked the time disturbance. Llorenc is fascinated by the curse; Ramon is annoyed. They become reluctant allies. The local dimoni lends its mask power but hands it to Llorenc for safekeeping -- Ramon is too chaotic. This establishes the shop mechanic.

**World 3 -- El Comte Mal (Feudal Mallorca, legend-based)**
Dark feudal Mallorca. The Comte Mal, a powerful vampire nobleman, has captured and imprisoned a dimoni to siphon its supernatural power. An old witch, La Bruixa, maintains the binding ritual for the Comte -- she is a pawn, used by him, not an enemy in her own right. Strange fires burn across the Comte's lands. Ramon frees the dimoni by defeating the Comte. The freed dimoni, like the others, refuses to stay with Ramon and entrusts its mask to Llorenc. This cements the narrative rule: dimonis don't trust Ramon (he's cursed, chaotic, everything explodes around him), so all masks go to Llorenc.

**World 4 -- Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)**
Ottoman pirate raids on the Mallorcan coast. Coastal watchtowers, burning villages, moonlit beaches. Locals beg Ramon to help defend. He sighs deeply: "First Romans, then a vampire, now pirates. Is there a single century where people leave this island alone?"

**World 5 -- S'Invasio (Modern Day)**
Ramon arrives in the present. His ancestral land has been turned into hotel chains. "...I think I preferred the pirates." A satirical world full of tourists, real estate agents, influencers, and party buses. He defeats El Magnat, a real estate tycoon, on a luxury hotel rooftop. But the Magnat pulls out a phone: "You think Mallorca was my endgame? I own IBIZA." A helicopter arrives. He escapes.

**World 5.5 -- Eivissa (Modern Ibiza)**
Bep's curse activates one last time -- but instead of a time jump, it's a geographic jump. They're sneezed to Ibiza. The Magnat has built a mega-resort empire powered by enslaved fameliars (little demons from Santa Eularia folklore). Shorter but harder world. Ramon uses all his collected powers to bring it down. Final confrontation with El Magnat empowered by familiar energy.

### 2.3 Narrative Tone & Voice

The game is a lighthearted parody. Real historical events and genuine Mallorcan folklore are the foundation, but everything is viewed through the lens of a protagonist who finds it all deeply inconvenient. The humor comes from the contrast: the world is dramatic and high-stakes, Ramon is not.

- Dialogue is short and punchy
- Historical commentary is always filtered through character perspective
- Serious themes (colonization, piracy, gentrification) are addressed through satire, never preachy
- Every NPC interaction should be either funny, informative, or both

### 2.4 Ending & Post-Credits

El Magnat phase 2 is defeated. His empire crumbles. The curse breaks -- all dimoni debts are settled through the journey. Bep stops glowing. Ramon looks at Bep. Looks at Llorenc. Looks at the player.

"...I'm taking a nap."

Credits roll over pixel art: Ramon and Bep walking along a Mediterranean coast toward Mallorca. Llorenc waves goodbye from Ibiza with Bruna.

**Post-credits**: Bep is grazing peacefully near a talayot. He spots a strange plant. He eats it. His eyes widen. Screen cuts to black. A single bleat. Silence.

---

## 3. CHARACTERS

### 3.1 Ramon -- Protagonist

- **What he is**: A foner -- a talayotic warrior and slinger from ~1000 BC Mallorca
- **Personality**: Grumpy, laconic, reluctant. Just wants to be left alone. Dry Mallorcan humor. Never asked to be a hero. Complains about everything but quietly does the right thing when it matters (without admitting it).
- **Visual direction**: Stocky build, simple tunic, leather sling always in hand. Bronze-age aesthetic. Perpetually unimpressed expression.
- **Dialogue style**: Short sentences. Deadpan. "No." "Fine." "This is your fault, Bep." Never more than two lines at a time.

### 3.2 Bep -- Companion

- **What he is**: A myotragus balearicus (extinct Balearic bovid, sheep-like). Ramon's companion animal.
- **Personality**: Cheerful, oblivious, unconditionally loyal. Loves Ramon despite constant rejection. Talks too much after being cursed. Comic relief. Occasionally says something accidentally wise.
- **Gameplay role**:
  - Hints mechanics through dialogue ("Ramon! I bet if you hold that button longer the rock goes further!" / "That wall looks jumpable!")
  - Triggers time-travel portals after each boss (involuntary curse activation: glows -> sneezes -> portal opens)
  - Visual companion on screen with idle animations (chews on things, falls asleep, gets startled by enemies)
  - Does NOT have a gameplay button or direct mechanical interaction -- purely narrative and cosmetic presence
- **Visual direction**: Small, round, sheep-like with stubby horns. Expressive eyes. Faint glowing aura after the curse.
- **Dialogue style**: Enthusiastic, rambling. "Ramon! Did you see that? You were amazing! ...Ramon? Ramon, are you ignoring me? That's okay, I still think you're great."

### 3.3 Llorenc -- Shop/Lore NPC

- **What he is**: A talayotic warrior from Menorca. Researcher, collector, nerd.
- **Personality**: Enthusiastic about artifacts and dimoni lore. Friendly rivalry with Ramon based on the classic Mallorca-vs-Menorca banter. Genuine friends despite the jabs.
- **Gameplay role**:
  - Appears between worlds and at level-end save points
  - Runs the **Mask Shop**: player swaps dimoni powers here
  - Sells **consumables** (health recovery, temporary buffs)
  - Sells **max heart upgrades** (permanent, increasingly expensive)
  - Provides optional lore about each era and dimoni
- **Why he holds the masks**: Established through plot (Worlds 2-3). Dimonis don't trust Ramon -- he's cursed, chaotic, destruction follows him. They entrust their masks to Llorenc, the calm, respectful researcher. Ramon has to visit Llorenc to equip powers. This is both narrative and a gameplay gate.
- **Companion**: Bruna, a Menorcan cow. Calm, stoic. Looks at Bep with quiet disdain. Bep is terrified of her.
- **Visual direction**: Similar build to Ramon but slightly taller. Carries a satchel full of artifacts. Always has a scroll or mask in hand. Bruna stands behind him at the shop.
- **Dialogue style**: Wordy, excited. "Fascinating! This mask channels the fire dimoni of the Comte Mal's domain. In Menorca we have similar legends but -- you don't care, do you." Ramon: "No."

### 3.4 Dimonis -- Per-World NPCs

Each world (after World 1) features a dimoni that Ramon encounters early in the world. The dimoni is annoyed by Bep's curse attracting attention but grudgingly lends Ramon a power (in mask form) to deal with the local threat faster -- so Ramon leaves sooner. The mask is given to Llorenc.

| World | Dimoni | Personality |
|-------|--------|-------------|
| 1 -- Sa Talaia | Es Dimoni de Sant Joan | The original offended dimoni. Furious, vindictive, dramatic. Appears at the end of World 1 to explain the curse. |
| 2 -- Mallorca Romana | Es Dimoni de Manacor | Intense, impatient, fed up with Roman order. Lends power so Ramon can "deal with these organized invaders." |
| 3 -- El Comte Mal | Captured dimoni (unnamed, from the Comte's lands) | Imprisoned, weakened. Grateful when freed but doesn't trust Ramon. Hands mask to Llorenc immediately. |
| 4 -- Els Pirates | Es Dimoni de Pollenca | Sneaky, nocturnal, whisper-voiced. Fits the stealth theme. Hates the noise pirates make. Historically fitting: Dragut attacked Pollenca in 1550. |
| 5 -- S'Invasio | Es Dimoni de Sa Pobla | The most iconic Mallorcan dimoni. Overwhelmed by modernity. Confused by phones. Gives power out of sheer frustration. |

### 3.5 Bosses

| World | Boss | Description |
|-------|------|-------------|
| 1 | **Es Bou de Pedra** | A massive stone bull animated by dimoni energy from a talayotic sanctuary -- rooted in the bronze-age bull worship evidenced by Balearic bull figurines. The first real test. After defeating it, the time-travel reveal happens. |
| 2 | **Quintus Caecilius Metellus** | The actual Roman general who conquered the Balearics. Fights from a chariot. Arrogant, tactical. |
| 3 | **El Comte Mal** | A vampire nobleman from Mallorcan legend. Has been siphoning a captured dimoni's power with the help of La Bruixa, an old witch he manipulates. Powerful, aristocratic, cruel. La Bruixa is part of the story (cutscenes, plot) but NOT part of the gameplay fight. |
| 4 | **Dragut** | Famous Ottoman corsair. Ship-to-shore battle. Boisterous, confident, respects strength. |
| 5 | **El Magnat (Phase 1)** | A real estate tycoon in a golden suit. Fought on his luxury hotel rooftop. Uses money and lawyers. Flees to Ibiza when defeated. |
| 5.5 | **El Magnat (Phase 2)** | Empowered by absorbed familiar energy. Bigger, golden, floating. Multi-phase fight testing all mechanics. |

### 3.6 Enemy Types

**World 1 -- Sa Talaia**
- Possessed sheep (glowing eyes, aggressive, corrupted by dimoni energy)
- Rival tribal warriors
- Stone guardians (slow, heavy hitters)

**World 2 -- Mallorca Romana**
- Roman legionaries (shield formation -- must hit from above or behind)
- War dogs (fast, low to ground)
- Tax collectors (weak but steal your sling stones on contact)

**World 3 -- El Comte Mal**
- Undead servants (slow, persistent)
- Vampire bats (airborne, swoop patterns)
- Cursed villagers (erratic movement)

**World 4 -- Els Pirates**
- Pirates with scimitars (melee rushers)
- Musket snipers (ranged, positioned on ships/towers)
- Powder monkeys (throw bombs, timed explosions)

**World 5 -- S'Invasio**
- Aggressive tourists (throw beer cans)
- Real estate agents (chase you with contracts)
- Influencers (camera flash stuns you)
- Party buses (environmental hazard)

**World 5.5 -- Eivissa**
- Fameliars -- enslaved little demons from the folklore of Santa Eularia, Ibiza. Visually small, imp-like, reminiscent of Dobby from Harry Potter. Artificially created and bound to El Magnat's service. Three variants:
  - **Bottle imps**: Small, fast, swarm in groups
  - **Neon fameliars**: Leave damaging light trails behind them
  - **VIP fameliars**: Larger, have shields (bouncer energy)

---

## 4. GAMEPLAY MECHANICS

### 4.1 Core Moveset

**Movement**
- Left/right movement
- Single jump (baseline)
- Wall jump: automatic -- when the player is against a wall and presses jump, Ramon kicks off it. No special input required, triggered by context.

**Sling Combat (the fona)**

The sling has two modes on a single button:

- **Tap attack**: Ramon swings the loaded sling as a melee weapon -- short range hit, like a whip crack. Quick, no cost. This is the primary combat tool for close encounters.
- **Hold attack**: Ramon loads a stone and begins charging. The longer the button is held, the more powerful the shot (visual/audio feedback as charge builds). Released when the player lets go. Fires a ranged projectile. **Unlimited basic ammo** -- the charge time is the balancing cost. Useful for hitting distant targets, specific boss weak points, and triggering ranged switches/mechanisms.

**[NEW] Charge Levels**: The hold attack has 3 charge tiers for clear player feedback:
- **Tier 1** (0.3-0.8s hold): Quick shot. 1x damage, medium range. Sling glows faintly.
- **Tier 2** (0.8-1.5s hold): Power shot. 2x damage, long range. Sling glows brightly, audio pitch rises.
- **Tier 3** (1.5s+ hold): Full charge. 3x damage, full screen range. Sling flashes, distinct audio cue. Required for certain boss weak points and distant switches.

**Special ammo (power-up rocks)**
- Unlockable rock types with special effects (e.g., explosive rocks, piercing rocks)
- These are **limited by a recharge mechanic** -- not unlimited like basic shots
- **Hybrid recharge system (decided)**: Special ammo recharges on a **passive timer** (base recharge time ~15-20 seconds per ammo unit; exact tuning left to implementation). Each **enemy kill instantly reduces the remaining recharge time by 30%**, applied multiplicatively on the current remaining time. Example: 10s remaining -> kill -> 7s remaining -> kill -> 4.9s remaining.
- This rewards aggressive combat engagement (kills accelerate recharge) while still allowing passive recharge during exploration and platforming sections, so the player is never stuck without ammo for long.
- Multiple kills stack multiplicatively -- chaining kills in quick succession dramatically speeds up recharge, reinforcing the game's action rhythm.
- Bought or found, managed as a resource

**[NEW] Special Ammo Types**:

| Ammo Type | Effect | Unlock World | Shop Price |
|-----------|--------|-------------|------------|
| Explosive Rock | AoE damage on impact, breaks walls | World 2 | 30 stones per 3-pack |
| Piercing Rock | Passes through shields/enemies, hits 3 targets | World 3 | 40 stones per 3-pack |
| Frozen Rock | Freezes enemy for 3 seconds on hit | World 4 | 50 stones per 3-pack |

### 4.2 Dimoni Mask System

Each world (after World 1) grants a new dimoni mask. The mask fills a single **power-up slot** activated with a dedicated button. Only one mask can be active at a time. Masks are swapped at Llorenc's shop.

**[NEW] Mask Cooldown System**: Each mask power has a cooldown after use. This prevents spamming and creates rhythm in combat/traversal. Cooldowns are displayed visually as a radial fill on the mask icon in the HUD.

| World | Mask | Power | Cooldown | Traversal Use | Combat Use |
|-------|------|-------|----------|---------------|------------|
| 1 -- Sa Talaia | Mask of Sant Joan | **Stone Slam** | 2s | Breaks floor tiles to reveal areas below. Creates stone platforms in certain lava/water sections (platform rises from rubble). | Ground pound shockwave damages all grounded enemies in range (~3 tiles). Stuns heavy enemies briefly. |
| 2 -- Mallorca Romana | Mask of Manacor | **Double Jump** | 0.5s (resets on landing) | Second midair jump. Reach higher platforms, cross wider gaps. Essential for vertical level design. | Aerial repositioning. Jump over shield formations to hit legionaries from above. Dodge boss attacks with vertical escape. |
| 3 -- El Comte Mal | Mask of Fire | **Fire Dash** | 3s | Horizontal dash covers ~5 tiles. Burns through wooden barricades. Crosses gaps too wide for double jump. | Invulnerable during dash frames (~0.3s). Damages all enemies in the dash path. Breaks through enemy shields. |
| 4 -- Els Pirates | Mask of Pollenca | **Smoke Vanish** | 4s | Phase through thin walls to find hidden routes. Brief invisibility (~1.5s). | Dodge through enemy attacks untouched. Phase through projectiles. Reposition behind shielded enemies. |
| 5 -- S'Invasio | Mask of Sa Pobla | **Tourist Rage** | 5s | AoE push clears destructible environmental obstacles. Activates certain crowd-triggered switches (need multiple hits simultaneously). | Pushes all nearby enemies back ~4 tiles and stuns for 2s. Essential crowd control for swarm encounters. |

**Design principle**: Each power changes both combat AND traversal. Powers aren't just for fighting -- they open up navigation options. This encourages replaying earlier worlds with later masks to find secrets (optional, not required for completion).

**Design rule — Mask Availability** *(per [Issue #3](https://github.com/Tonigit/SaFona/issues/3))*: No level may require a mask the player has not yet obtained to be completed. Masks are only acquired by defeating the dimoni boss of their respective world — there are no temporary power pickups, preview pickups, or any other way to use a mask power before it is permanently unlocked. Areas in earlier levels that respond to a future mask (e.g., wooden barricades in W1 that require Fire Dash from W3) are strictly **optional replay secrets** accessible via Level Select. They must never gate required progression.

**[NEW] Mask Quick-Swap Mechanic** *(per [Issue #5](https://github.com/Tonigit/SaFona/issues/5))*:

At the start of World 5.5 (Eivissa), Ramon unlocks the ability to **cycle through all collected masks in real time** using shoulder buttons (L1/R1 on gamepad, Q/E on keyboard). This replaces the need to visit Llorenç's shop to swap masks during W5.5.

- **Unlock trigger**: Automatic at the start of W5.5-1. Narrative justification: the curse reaching its peak in Eivissa destabilizes all mask bindings, letting Ramon channel them freely without Llorenç as intermediary.
- **Cycling**: L1 cycles left (previous mask), R1 cycles right (next mask) through the collected mask list. The cycle wraps around.
- **Cooldown**: 0.3-second cooldown between swaps to prevent accidental cycling. During cooldown, swap input is ignored (no queuing).
- **HUD feedback**: The mask icon in the top-right HUD updates in real time when cycling. A brief swap animation (icon slides out/in) confirms the change.
- **No pause**: Swapping happens in real time — the game does not pause or slow down. This is intentional: mid-combat mask swaps are the core skill test of W5.5.
- **Level Select replay**: Once unlocked, quick-swap is available in **all levels accessed via Level Select**, including earlier worlds. This is the key replay motivator — revisiting W1-W5 levels for retroactive secrets (Appendix C) becomes fluid and fun instead of requiring shop visits between attempts.
- **Llorenç's shop**: Still exists for buying consumables, upgrades, and special ammo. The Masks tab in the shop remains functional but is no longer the only way to swap masks once quick-swap is unlocked.

### 4.3 Health & Damage

- **Hearts system** (Zelda-style)
- Ramon starts with **3 hearts** (6 half-hearts)
- **Minimum damage**: Half a heart
- **Maximum damage**: 2 hearts (boss heavy attacks only)
- Additional max hearts can be purchased at Llorenc's shop (permanent upgrade, increasingly expensive)
- **[NEW] Max heart cap**: 8 hearts (5 purchasable upgrades)
- Hearts are restored by pickups found in levels and by consumables from the shop

**[NEW] Damage Reference Table** (relative values -- exact tuning during implementation):

| Source | Damage | Notes |
|--------|--------|-------|
| Weak enemy contact (sheep, bats, bottle imps) | 0.5 hearts | Chip damage |
| Standard enemy attack (warriors, legionaries, pirates) | 1 heart | Core threat |
| Heavy enemy attack (stone guardians, VIP fameliars) | 1.5 hearts | Punishing |
| Environmental hazard (spikes, fire, bombs) | 1 heart | Consistent |
| Boss normal attack | 1 heart | Learnable |
| Boss heavy attack (telegraphed) | 1.5-2 hearts | High-risk, high-tell |
| Tax collector contact | 0 hearts | Steals 5-15 stones instead |

### 4.4 Economy -- Sling Stones

- **Sling stones (pedres de fona)** are the currency
- Found throughout levels: in breakable objects, dropped by enemies, hidden in secrets
- Spent at Llorenc's shop on consumables, max heart upgrades, and special ammo types
- Tax collectors (World 2 enemy) steal stones on contact -- a risk/annoyance mechanic

**[ARCHITECTURE REQUIREMENT]** All economy values -- prices, drop rates, upgrade costs, enemy drop tables, consumable effects, and shop inventory -- MUST be stored in a single configuration file (e.g. `data/economy.json`). This file is the **single source of truth** for economy tuning. No economy values may be hardcoded in game logic. During playtesting, the project owner can edit this file directly to adjust balance without touching code. This is a requirement for En Miquel's architecture design.

### 4.5 Consumables & Llorenc's Shop

Consumables are **accessibility tools** -- they help less skilled players get past sections they're stuck on without lowering the baseline difficulty for experienced players.

**Consumable types** (values are defaults; loaded from `data/economy.json`):

| Item | Effect | Price | Available From |
|------|--------|-------|---------------|
| Ensaimada | Restores 2 hearts | 10 stones | World 1 |
| Sobrassada Pot | Restores all hearts | 25 stones | World 2 |
| Herbes Liqueur | +50% damage for 60 seconds | 30 stones | World 3 |
| Oli d'Oliva | -50% damage taken for 60 seconds | 30 stones | World 3 |
| Aigua de Font | 5 seconds invincibility | 40 stones | World 4 |
| Explosive Rock Pack (x3) | Special ammo | 30 stones | World 2 |
| Piercing Rock Pack (x3) | Special ammo | 40 stones | World 3 |
| Frozen Rock Pack (x3) | Special ammo | 50 stones | World 4 |

**Permanent purchases -- Heart Upgrades** (values are defaults; loaded from `data/economy.json`):

| Upgrade | Cost | Total Max Hearts After |
|---------|------|----------------------|
| Heart Upgrade 1 | 40 stones | 4 |
| Heart Upgrade 2 | 75 stones | 5 |
| Heart Upgrade 3 | 120 stones | 6 |
| Heart Upgrade 4 | 175 stones | 7 |
| Heart Upgrade 5 | 240 stones | 8 |

Total cost for all heart upgrades: 650 stones (~72% of explorer income). A thorough explorer can afford all upgrades AND have ~250 stones left for consumables throughout the game.

**Shop availability**: Llorenc appears between every world and at the save point after each level. His shop inventory expands as the game progresses (new items unlock per the table above).

**[NEW] Post-W5.5 shop role**: Once the quick-swap mechanic is unlocked (see Section 4.2), Llorenç's shop is no longer required for mask swapping. The shop remains essential for consumables, heart upgrades, and special ammo purchases. The Masks tab still functions for players who prefer browsing mask descriptions and lore, but the quick-swap shoulder buttons are the primary swap method from W5.5 onward.

### 4.6 Difficulty & Accessibility

- Linear difficulty progression across worlds
- No difficulty selector -- the baseline is the intended experience
- Consumables serve as the difficulty relief valve: players who are stuck can buy temporary boosts to push through
- The economy is tuned so that a player who explores thoroughly has plenty of stones to buy help when needed
- World 5.5 (Eivissa) is explicitly harder as the endgame challenge

### 4.7 Save System

- **Save after each level** (automatic)
- **No mid-level saves** -- dying in a level means restarting that level
- Save data includes: current world/level, collected masks, heart count, stone count, shop purchases, **per-level completion status**, and **per-level secret-found flags**
- Death returns the player to the start of the current level with their pre-level state

### 4.8 Level Select & Replay

> **Decision**: Per-level instant replay unlock, per [Issue #6](https://github.com/Tonigit/SaFona/issues/6).

- **Each completed level is immediately unlocked for replay.** The moment a player beats a level, it becomes available in the Level Select screen.
- The **Level Select** screen is accessible from the main menu (and optionally from save points). It lists every level the player has beaten, organized by world.
- **Per-level granularity**: replay is unlocked individually per level, not per world. Beating W1-L2 does not unlock W1-L3 for replay — only W1-L2.
- **Completion indicators**: Each level entry on the Level Select screen shows its completion state (e.g., beaten / secret found / secret not found). This encourages revisiting earlier levels.
- **Revisiting with later powers**: Players are explicitly encouraged to replay earlier levels after acquiring new mask powers in later worlds, since some secrets are only reachable with abilities gained later (see Section 5.0 Mechanic Synergy Matrix).
- **[NEW] Quick-swap in replay**: Once the mask quick-swap mechanic is unlocked at W5.5 (see Section 4.2), it is available in all Level Select replays. This makes revisiting earlier worlds for retroactive secrets (Appendix C) significantly more fluid — players can cycle masks on the fly instead of pre-selecting a single mask at the shop before each attempt.
- Replaying a level does **not** affect main progression — the player's current story position is preserved. Stones collected during a replay are kept.

**[NEW] Death Penalty Specifics**:
- On death, the player restarts the level with the stone count and heart max they had when they ENTERED the level
- Stones collected during the failed attempt are lost
- Consumables used during the failed attempt are refunded
- This prevents a death spiral where the player gets poorer each attempt

---

## 5. WORLD DESIGN

### 5.0 Mechanic Synergy Matrix

This matrix maps how each mask power serves traversal, combat, boss testing, and retroactive secrets across all worlds. It is the backbone of the game's learning curve.

| World | New Mechanic | Traversal Use | Combat Use | Teaching Moment | Boss Test | Retroactive Secrets |
|-------|-------------|---------------|------------|-----------------|-----------|-------------------|
| W1 -- Sa Talaia | Stone Slam | Break floor tiles, reveal caves below | Shockwave damages grounded enemies | Level 1-3: breakable floors with visible cracks and reward beneath. Bep says "That floor looks crumbly!" | Es Bou de Pedra phase 2: must slam to create cover from debris arcs, or slam stunned bull for bonus damage | N/A (first world) |
| W2 -- Mallorca Romana | Double Jump | Reach high Roman structures, cross wide aqueduct gaps | Jump over shield formations to hit from above | Level 2-1: low ceiling forces single jump, then opens to tall atrium requiring double jump. Bep: "We can jump TWICE now?!" | Metellus phase 1: double jump through pilum gaps; phase 3: jump over reinforcement clusters | W1 secrets: high ledges in cliff areas now reachable |
| W3 -- El Comte Mal | Fire Dash | Burn through wooden barricades, cross wide pits | Invulnerable dash through enemy clusters, break shields | Fire Dash is granted AFTER the Comte Mal boss. W3 levels use atmosphere (strange fires, the imprisoned dimoni's leaking energy) to foreshadow the power narratively, but NO level requires it. | Comte Mal phase 2: dash through fire pillar barriers to reach him; phase 3: dash to close distance during teleports | W1-2 secrets: wooden barricades and wide gaps in earlier worlds |
| W4 -- Els Pirates | Smoke Vanish | Phase through thin walls to hidden routes | Dodge through attacks/projectiles, reposition behind shields | Level 4-1: visible treasure behind thin wall, Bep: "I can see through that wall..." Level 4-2: sniper gauntlet where vanish avoids musket shots | Dragut phase 3: vanish through his twin-scimitar combos to survive and counterattack | W1-3 secrets: thin walls marked with faint shimmer in all prior worlds |
| W5 -- S'Invasio | Tourist Rage | AoE clears destructible obstacles, activates crowd switches | Pushes and stuns all nearby enemies, essential crowd control | Level 5-1: swarmed by tourist groups with no room to fight individually. Bep: "There's too many of them!" Rage taught as survival | Magnat P1 phase 1: rage clears lawyer waves; phase 3: rage needed to push back corner trap | W1-4 secrets: crowd-triggered pressure plates requiring AoE activation |
| W5.5 -- Eivissa | None (all masks) | Sections require swapping: slam floors, double jump heights, dash gaps, vanish walls, rage crowds | Must match mask to enemy type and encounter design | Level 5.5-1: rapid-fire sections each gated by a different mask power, teaching mask-swap rhythm | Magnat P2 phase 3: specific attacks require specific masks in sequence | All remaining secrets accessible |

**Gaps identified and resolved**:
- The draft had Fire Dash acquired AFTER the Comte Mal boss, meaning World 3 levels could not use it for traversal. **Resolution** *(revised per [Issue #3](https://github.com/Tonigit/SaFona/issues/3))*: W3 levels are designed to be completable WITHOUT Fire Dash. The world's challenge comes from gothic atmosphere, trap-heavy design, and enemy gauntlets using the player's existing moveset (Stone Slam + Double Jump). Fire Dash is granted after the boss and retroactively opens secrets in W1-W3. No temporary power pickups exist.
- World 4's Smoke Vanish had no obvious teaching beat. **Resolution**: Level 4-1 has a visible treasure room behind a thin wall that Bep comments on, and a stealth-tutorial section where vanishing past a sniper is clearly easier than fighting.

### 5.1 Learning Curve Map

**What the player knows at each world's start, what they learn, and how difficulty flows.**

#### World 1 -- Sa Talaia (Tutorial World)
- **Entering knowledge**: Nothing. This is the start.
- **New skills**: Move, jump, wall jump, sling tap, sling charge (3 tiers), Stone Slam
- **Teaching structure**:
  - Level 1-1: Move and jump only. Simple gaps, no enemies for first section. Bep teaches controls through dialogue.
  - Level 1-2: Sling tap introduced (first enemies: possessed sheep). Hold-to-charge taught via a distant switch.
  - Level 1-3: Wall jump introduced via vertical cave. Stone Slam found as artifact; breakable floor immediately below.
  - Level 1-4: All mechanics combined in pre-boss gauntlet. Stone guardians test everything.
  - Boss: Tests jump, wall jump, sling charge, and pattern recognition.
- **Difficulty arc**: 1 -> 2 -> 3 -> 4 -> 5 (boss)
- **Relief valves**: Generous heart pickups. Llorenc shop opens after level 1-2.

#### World 2 -- Mallorca Romana
- **Entering knowledge**: Full moveset + Stone Slam
- **New skill**: Double Jump
- **Teaching structure**:
  - Level 2-1: Tall Roman atrium. First section passable with single jump + wall jump; second section requires double jump (given early in level via dimoni encounter).
  - Level 2-2: Aqueduct run. Vertical platforming chains. Double jump essential.
  - Level 2-3: Roman camp. Shield legionaries force double jump over formations. Tax collectors add economic pressure.
  - Level 2-4: Amphitheater approach. Combat gauntlet mixing all enemy types.
  - Boss: Chariot requires double jump to dodge pilum, wall jump to avoid charges, crowd management in phase 3.
- **Difficulty arc**: 3 -> 4 -> 5 -> 6 -> 6 (boss)
- **Relief valves**: Shop fully stocked with consumables. Ensaimadas cheap.

#### World 3 -- El Comte Mal
- **Entering knowledge**: Full moveset + Stone Slam + Double Jump
- **New skill**: Fire Dash
- **Teaching structure**:
  - Level 3-1: Dark corridors. Strange fires in the background foreshadow the imprisoned dimoni. Gothic atmosphere. First undead and bat encounters.
  - Level 3-2: Abandoned village. Vertical church tower climb, catacomb exploration. La Bruixa cutscene foreshadows the imprisoned dimoni.
  - Level 3-3: Comte's outer estate. Trap-heavy (spike pits, collapsing floors, chandelier-swinging). Tight corridors demand precision with existing moveset.
  - Level 3-4: Inner tower. Vertical ascent with dark sections and bat gauntlets. Audio cues become critical. Peak difficulty before boss.
  - Boss: Tests timing, pattern recognition, charged sling accuracy. Fire Dash granted after victory; retrofits all barricades/gaps in earlier worlds.
- **Difficulty arc**: 5 -> 5 -> 6 -> 7 -> 7 (boss)
- **Relief valves**: Herbes Liqueur and Oli d'Oliva now available. Dark atmosphere is tense but enemy density is lower.

#### World 4 -- Els Pirates
- **Entering knowledge**: Full moveset + Stone Slam + Double Jump + Fire Dash
- **New skill**: Smoke Vanish
- **Teaching structure**:
  - Level 4-1: Coastal watchtower. Treasure visible behind thin wall (Bep comments). Smoke Vanish given via dimoni encounter.
  - Level 4-2: Burning village. Sniper gauntlet where vanish through sight lines is clearly easier. Moonlit stealth sections.
  - Level 4-3: Pirate cove. Ship interiors with tight corridors. Powder monkeys make pure combat costly (vanish past bomb zones).
  - Level 4-4: Approach to Dragut's flagship. Mixed combat/stealth.
  - Boss: Shore-to-ship transition. Vanish essential for Dragut's fast combos in phase 3.
- **Difficulty arc**: 5 -> 6 -> 7 -> 7 -> 8 (boss)
- **Relief valves**: Frozen Rock ammo slows tough enemies. Aigua de Font for panic moments.

#### World 5 -- S'Invasio
- **Entering knowledge**: All prior masks
- **New skill**: Tourist Rage
- **Teaching structure**:
  - Level 5-1: Magaluf strip. Immediate swarm of tourists. Tourist Rage given early; using it is an "aha!" moment of crowd control.
  - Level 5-2: Palma airport. Conveyor belts as moving platforms, luggage hazards. Dense enemy groups.
  - Level 5-3: Beach resort. Influencer stun mechanics force rage to clear space. Party bus hazards.
  - Level 5-4: Hotel approach. Vertical climb up construction scaffolding. All enemy types in combinations.
  - Boss: Crowd management (lawyer waves) + arena manipulation. Rage essential for phase 1 and 3.
- **Difficulty arc**: 6 -> 7 -> 7 -> 8 -> 8 (boss)
- **Relief valves**: Tourist Rage itself IS the relief valve for crowd pressure. Full shop inventory.

#### World 5.5 -- Eivissa (Endgame)
- **Entering knowledge**: ALL masks
- **New skill**: None. Mask swapping is the meta-skill.
- **Teaching structure**:
  - Level 5.5-1: Nightclub ruins. Rapid mask-test sections: slam a floor, double jump a shaft, dash a gap, vanish a wall, rage a swarm. Each section is short but teaches the swap rhythm.
  - Level 5.5-2: Mega-resort interior. Longer mixed sections requiring mid-combat mask swaps. Neon fameliars and VIP fameliars test different approaches.
  - Level 5.5-3: Rooftop ascent to Magnat's penthouse. Hardest platforming in the game. All mask powers needed.
  - Boss: Multi-phase endgame test of everything learned.
- **Difficulty arc**: 8 -> 9 -> 9 -> 10 (boss)
- **Relief valves**: Full shop available before each level. Sobrassada Pot and Aigua de Font recommended. Economy should have ample reserves for thorough players.

### 5.2 Common World Template

Worlds 2-5 follow a repeating structure so the game feels familiar but fresh:

1. **Arrival**: Bep's portal drops Ramon and Bep into the new era. Cutscene: Ramon reacts to the setting, Bep is excited.
2. **Dimoni encounter**: Early in the world (level 1 or 2), the local dimoni appears. Brief dialogue. Grants mask power to Llorenc.
3. **Levels**: 4 platforming/combat levels with increasing difficulty. Each level ends at a save point where Llorenc may appear.
4. **Boss**: Final level is the boss encounter. Preceded by a boss intro cutscene.
5. **Transition**: After the boss, Bep's curse activates. Time portal. Next world.

**World 1 breaks this template** (no prior knowledge of time travel, the reveal is the twist).
**World 5.5 breaks this template** (geographic jump, no new mask, 3 levels + boss, endgame).

---

### 5.3 World 1 -- Sa Talaia (Talayotic Period, ~1000 BC)

- **Setting**: Rocky Mediterranean landscape. Talayots, taulas, navetas. Blue sky, dry stone, olive trees, coastal cliffs. Bronze-age Mallorca.
- **Color palette**: Warm earth tones -- ochre, stone grey, olive green, Mediterranean blue.
- **Enemies**: Possessed sheep, rival tribal warriors, stone guardians.
- **Dimoni power acquired**: Stone Slam (Mask of Sant Joan) -- acquired differently here. Since the time-travel mechanic isn't revealed yet, the mask is found as an ancient artifact in a talayot rather than given by a dimoni. After the World 1 reveal, the player retroactively understands it was dimoni-related.

#### Level 1-1: "Es Primer Pas" (The First Step)
- **Layout**: Horizontal. Open Mediterranean landscape with gentle slopes, low cliffs, and olive trees. A coastal path leading to a stone village.
- **Difficulty**: 1/10
- **Enemy composition**: None in the first half. 2-3 possessed sheep in the second half (the gentlest enemy -- slow, telegraphed charge).
- **Platforming challenges**: Simple gaps (2-3 tile wide). Low walls requiring jump. One slightly taller cliff introducing wall jump context (optional path, main path goes around).
- **Collectibles**: 15-20 sling stones in breakable pots and tall grass. 1 heart pickup near the end. 0 secrets (pure tutorial).
- **Teaching beats**:
  - Bep teaches movement: "Ramon! Move! The sheep are acting strange!"
  - First gap: Bep says "Jump, Ramon! You've done it a thousand times!"
  - First wall: "That wall looks climbable... if you jump at it!"
  - First sheep: Bep panics, prompting player to try attacking.
- **End**: Save point. Llorenc NOT present yet (he appears in World 2).

#### Level 1-2: "Sa Cova des Foner" (The Slinger's Cave)
- **Layout**: Horizontal with a cave interior section. Starts outdoors, enters a limestone cave system, exits to a cliff overlook.
- **Difficulty**: 2/10
- **Enemy composition**: 4-5 possessed sheep, 2 rival tribal warriors (first encounter -- they block and require sling charge or tap timing).
- **Platforming challenges**: Cave has narrow ledges. One section with a gap too wide to walk across (forces jump). A high ledge that hints at wall jump (reachable but not required).
- **Collectibles**: 20-25 sling stones. 1 heart pickup in the cave. 1 secret: a hidden alcove behind breakable rocks (3 bonus stones) -- teaches that the environment is destructible.
- **Teaching beats**:
  - Cave entrance: Bep says "It's dark in there! I'll stay close."
  - First warrior: "He's blocking! Try hitting him harder... or from the side!"
  - Distant switch on a ledge visible but out of melee range: "Maybe if you hold the sling longer..."
  - Switch tutorial: Player holds attack to charge, hits the distant switch, a platform extends. This teaches charged shots.
- **End**: Save point. Llorenc NOT present yet.

#### Level 1-3: "Es Talayot Sagrat" (The Sacred Talayot)
- **Layout**: Vertical. A massive talayot interior. Climb upward through stone chambers. The Stone Slam mask artifact is found midway up.
- **Difficulty**: 3/10
- **Enemy composition**: 3 possessed sheep, 2 tribal warriors, 1 stone guardian (first encounter -- slow but hits hard, teaches dodging heavy enemies).
- **Platforming challenges**: Vertical shaft requiring wall jumps (mandatory -- the level forces it). After Stone Slam acquisition, a breakable floor directly below the player with visible cracks and a reward below (teaches the power immediately).
- **Collectibles**: 25-30 sling stones. 2 heart pickups. 1 secret: a side chamber accessible by Stone Slam (10 bonus stones).
- **Teaching beats**:
  - Vertical shaft: Bep says "We need to go UP! Try jumping off the walls!"
  - Wall jump section is narrow enough that it's hard to fail -- forgiving geometry.
  - Stone Slam artifact: Bep says "Ooh, that mask looks powerful! Put it on!"
  - Immediately after: cracked floor below with visible sparkle. "The ground here looks crumbly..."
  - Stone guardian encounter: "That one's big! Watch out for its swing!"
- **End**: Save point. Llorenc NOT present yet. Shop opens after this level (accessible from the save point, but without Llorenc's personality -- just a "mysterious stone pedestal" that functions as the proto-shop, offering basic ensaimadas).

#### Level 1-4: "Sa Porta des Bou" (The Gate of the Bull)
- **Layout**: Mixed horizontal and vertical. An outdoor approach to the boss arena through a ruined sanctuary. Combines all prior terrain types.
- **Difficulty**: 4/10
- **Enemy composition**: 3 possessed sheep, 3 tribal warriors, 2 stone guardians. Enemies are placed in combinations for the first time (warrior + sheep, guardian + sheep).
- **Platforming challenges**: A gauntlet section: wall jump up a cliff, cross a wide gap, slam through a breakable floor to a lower path, then navigate a narrow cave with enemies. Tests all acquired skills.
- **Collectibles**: 30-35 sling stones (generous before the boss). 2 heart pickups. 1 secret: a hidden cave behind a destructible wall with 15 bonus stones and a free ensaimada.
- **Teaching beats**:
  - Pre-boss area: Bep says "Something feels wrong here... the ground is shaking."
  - The combined enemy encounters teach the player to prioritize targets.
  - A wide open area before the boss door serves as a "calm before the storm."
- **End**: Boss gate. Dramatic visual change -- stone pillars, bull iconography.

#### Boss: Es Bou de Pedra
*(Full details in Section 6)*

- **Story beat (post-boss)**: The reveal. Es Bou de Pedra crumbles. Bep glows, sneezes, portal opens. The dimoni de Sant Joan appears and explains the curse. Ramon and Bep are pulled into the portal. The game's real premise begins.

---

### 5.4 World 2 -- Mallorca Romana (Roman Conquest, 123 BC)

- **Setting**: Roman roads cutting through Mallorcan landscape. Amphitheaters, legionary camps, early Palma (Palmaria). Aqueducts, columns, ordered architecture.
- **Color palette**: Stone white, imperial red, laurel green, marble grey.
- **Enemies**: Roman legionaries (shield formations), war dogs, tax collectors.
- **Dimoni power acquired**: Double Jump (Mask of Manacor). Given by Es Dimoni de Manacor early in level 2-1.
- **Llorenc introduction**: Appears at the start of this world. Has been tracking the time disturbance. Excited to meet Ramon. Ramon is not excited. Shop mechanic fully introduced here with personality and lore.

#### Level 2-1: "Sa Via Nova" (The New Road)
- **Layout**: Horizontal with a tall vertical section midway. Roman road leading to a newly built settlement. The vertical section is a Roman atrium with multi-level platforms.
- **Difficulty**: 3/10
- **Enemy composition**: 3 legionaries (first encounter -- shield blocks frontal attacks), 2 war dogs. Legionaries placed to teach "attack from above or behind." War dogs placed in open areas where their speed is manageable.
- **Platforming challenges**: First section uses single jump + wall jump through Roman structures. Midway: dimoni encounter grants Double Jump. Immediately after: a tall atrium with high platforms only reachable with double jump.
- **Collectibles**: 25-30 sling stones. 1 heart pickup. 1 secret: high ledge in the atrium with 10 bonus stones (teaches that double jump opens new vertical exploration).
- **Teaching beats**:
  - World arrival cutscene: Ramon: "Who paved over my goat path?"
  - Llorenc introduction and shop tutorial.
  - Dimoni de Manacor encounter: "Take this and get rid of these organized fools." Hands mask to Llorenc.
  - Double jump teaching: a tall column with a visible reward on top. Single jump + wall jump gets you partway; double jump gets the rest.
  - First legionary: Bep says "His shield blocks everything! Can you get above him?"
- **End**: Save point with Llorenc shop.

#### Level 2-2: "S'Aqeducte" (The Aqueduct)
- **Layout**: Primarily vertical. A massive Roman aqueduct stretching across a valley. Player climbs the aqueduct structure, runs along the top, and navigates water channels.
- **Difficulty**: 4/10
- **Enemy composition**: 4 legionaries (some on narrow aqueduct platforms -- tight spaces make shield problem harder), 3 war dogs (running along the top of the aqueduct), 1 tax collector.
- **Platforming challenges**: Vertical climbing up the aqueduct's arches (double jump + wall jump chains). Moving water platforms along the channel on top. A section where the aqueduct crumbles and the player must double jump between falling segments.
- **Collectibles**: 30-35 sling stones (many in water channel). 2 heart pickups. 1 secret: inside the aqueduct's base, accessible by Stone Slam through a cracked floor (20 bonus stones -- first W1 retroactive test).
- **Teaching beats**:
  - The crumbling aqueduct section teaches urgency -- platforms disappear after a few seconds.
  - Tax collector: first encounter. Bep: "He stole your rocks! Chase him!" (teaches that these enemies are a priority target or an avoidance challenge).
  - Water platform timing teaches patience between jumps.
- **End**: Save point with Llorenc shop.

#### Level 2-3: "Es Campament Roma" (The Roman Camp)
- **Layout**: Horizontal. A sprawling Roman military camp with tents, barricades, and training grounds. More combat-focused than platforming.
- **Difficulty**: 5/10
- **Enemy composition**: 5 legionaries (including 2 in shield formation -- side by side, requiring double jump over them or Stone Slam to stun), 4 war dogs (in packs for the first time), 2 tax collectors.
- **Platforming challenges**: Barricade walls requiring double jump. A training ground arena where enemies spawn in waves (first wave encounter). Tent rooftops as platforms.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: behind a tent row, a hidden path with 15 stones and an ensaimada.
- **Teaching beats**:
  - Shield formation: "They're standing together! Jump over them, Ramon!"
  - Wave arena: teaches crowd management -- fight multiple enemies with positioning and sling usage.
  - War dog packs: teach prioritizing fast enemies.
- **End**: Save point with Llorenc shop.

#### Level 2-4: "S'Amfiteatre" (The Amphitheater)
- **Layout**: Mixed. An approach road leading to a grand amphitheater. The level is a gauntlet -- continuous forward momentum with escalating challenges.
- **Difficulty**: 6/10
- **Enemy composition**: 4 legionaries, 3 war dogs, 2 tax collectors, 1 stone guardian (returning from W1 -- appears in Roman armor, slightly faster). All enemy types mixed in combinations.
- **Platforming challenges**: Multi-tiered amphitheater seating to climb. A collapsing stairway. A section requiring double jump over a pit with legionaries at the landing (must fight immediately after landing).
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: under the amphitheater floor, accessible by Stone Slam (25 stones, a sobrassada pot).
- **Teaching beats**:
  - Enemy combinations ramp up: "They're everywhere! Use everything you've learned!"
  - Pre-boss corridor: calm, atmospheric. Roman banners, torches. Builds tension.
  - Optional Llorenc dialogue: "The general Metellus conquered these islands in 123 BC. Brilliant tactician. You'll be fine." Ramon: "Inspiring."
- **End**: Boss gate. Amphitheater center stage.

#### Boss: Quintus Caecilius Metellus
*(Full details in Section 6)*

- **Story beat**: Llorenc: "Technically it's a road, and it's quite well-eng--" Ramon: "I didn't ask."

---

### 5.5 World 3 -- El Comte Mal (Feudal Mallorca, Legend-Based)

- **Setting**: Dark feudal Mallorca. The Comte Mal's cursed estates, oppressed villages, gothic manor, eerie forests. Torchlit stone corridors, strange fires burning in the hills.
- **Color palette**: Dark -- charcoal, blood red, sickly green, candlelight orange. Highest contrast of any world.
- **Enemies**: Undead servants, vampire bats, cursed villagers.
- **Dimoni power acquired**: Fire Dash (Mask of Fire). The permanent mask is granted AFTER the boss, when the imprisoned dimoni is freed. W3 levels are completed using the player's existing moveset (Stone Slam + Double Jump). The dimoni's imprisoned power is foreshadowed through atmosphere (strange fires, flickering torches, La Bruixa's rituals) but is never available as a gameplay mechanic until the boss is defeated.
- **La Bruixa**: Appears in cutscenes. She is a pawn -- manipulated by the Comte -- not an enemy. NOT a gameplay encounter.

#### Level 3-1: "Es Bosc Maleït" (The Cursed Forest)
- **Layout**: Horizontal with narrow paths. An eerie forest with gnarled trees, hanging moss, and strange green firelight. Paths wind through dense foliage.
- **Difficulty**: 5/10
- **Enemy composition**: 4 undead servants (slow, persistent -- teach patience), 3 vampire bats (first encounter -- swoop from above, teach looking up). Placed to create atmosphere: undead emerge from the ground, bats drop from trees.
- **Platforming challenges**: Narrow branch platforms. Moving log bridges over dark pits. A section requiring wall jump up a cliff face with bats swooping to knock the player off (tight timing).
- **Collectibles**: 25-30 sling stones. 2 heart pickups. 1 secret: behind a cluster of trees, a hidden glade with 15 stones (accessible from any world revisit).
- **Teaching beats**:
  - World arrival cutscene: Dark, ominous. Ramon: "...This is worse." Bep: "I like the trees!" (a bat swoops past) "I don't like the trees!"
  - Undead servants: Bep says "They keep getting back up!" (they take 2 hits to kill -- teaches persistence in combat).
  - Vampire bats: swoop with a visible shadow on the ground beforehand -- teaches looking for visual cues.
  - Strange fires in the background foreshadow the dimoni's imprisoned power.
- **End**: Save point with Llorenc shop. Llorenc: "The legends say the Comte Mal sold his soul. In Menorca we have better taste in—" Ramon: "Llorenc."

#### Level 3-2: "Es Poble Perdut" (The Lost Village)
- **Layout**: Mixed horizontal and vertical. An abandoned village with collapsed buildings, a church tower, and underground catacombs.
- **Difficulty**: 5/10
- **Enemy composition**: 3 undead servants, 4 vampire bats, 2 cursed villagers (first encounter -- erratic, unpredictable movement patterns, teaches reactive combat).
- **Platforming challenges**: Church tower climb (vertical, double jump + wall jump). Catacomb section with collapsing floor tiles. Rooftop platforming across the village (one-way platforms on thatched roofs).
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: in the catacombs, a hidden chamber accessible by Stone Slam (20 stones, an oli d'oliva).
- **Teaching beats**:
  - Cursed villagers: erratic movement contrasts the predictable undead. Bep: "That one moves funny... careful, Ramon!"
  - Collapsing floors: visual cue (dust particles from cracks). Teaches observation.
  - La Bruixa cutscene: spotted from a distance performing a ritual. Sets up the imprisoned dimoni story.
- **End**: Save point with Llorenc shop.

#### Level 3-3: "Sa Finca del Comte" (The Comte's Estate)
- **Layout**: Claustrophobic interiors. The Comte's outer estate -- stables, servant quarters, trap-laden corridors. Tight spaces, low ceilings, many hazards.
- **Difficulty**: 6/10
- **Enemy composition**: 4 undead servants, 3 vampire bats, 3 cursed villagers. Enemies appear in tighter spaces, making combat more dangerous.
- **Platforming challenges**: Spike pit corridors (timing-based). Collapsing floor chains (step on one, the next starts crumbling). A chandelier-swinging section over a great hall. A gauntlet corridor where the player must use Stone Slam to break through crumbling walls while bats swoop from above.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: behind a wooden barricade near the level start (requires Fire Dash from W3 boss — retroactive replay secret only).
- **Teaching beats**:
  - Tight corridors: teach careful movement. Rushing gets you hit by traps.
  - Multiple trap types layer together: spikes + bats = precision under pressure.
  - Strange fire in the estate's hearths burns unnaturally. Bep: "That flame felt alive! Like it wanted to help us!" Foreshadows the dimoni.
- **End**: Save point with Llorenc shop.

#### Level 3-4: "Sa Torre Fosca" (The Dark Tower)
- **Layout**: Vertical. The Comte's inner tower. Dark, oppressive. Ascending toward the great hall (boss arena). Most trap-dense level so far.
- **Difficulty**: 7/10
- **Enemy composition**: 3 undead servants, 5 vampire bats (positioned along vertical ascent), 3 cursed villagers. Heavy bat presence makes climbing treacherous.
- **Platforming challenges**: Spiral ascent with crumbling platforms. Bat gauntlets while wall jumping. A section with extinguishing/relighting torches (dark sections where you can only see Ramon's outline). A challenging vertical gap requiring precise double jump + wall jump chain (the tightest platforming in W3, demanding mastery of existing skills).
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: a side room behind a thin wall (visible but requires Smoke Vanish from W4 to access -- retroactive replay secret).
- **Teaching beats**:
  - Dark sections: audio cues become important (enemy footsteps, bat screeches). Teaches listening.
  - The dimoni's power leaks more visibly as the player ascends: Bep: "The fire's getting stronger! Something's trapped up there!" Foreshadows the boss encounter.
  - Pre-boss atmosphere: the tower grows darker, the music changes, strange fire flickers from above.
- **End**: Boss gate. The great hall doors.

#### Boss: El Comte Mal
*(Full details in Section 6)*

- **Story beat**: After defeat, the dimoni is freed. It hands its mask to Llorenc. "Keep it away from the sheep." Fire Dash now permanent. All wooden barricades and wide gaps in W1-W3 can be cleared on revisit.

---

### 5.6 World 4 -- Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)

- **Setting**: Coastal Mallorca under siege. Watchtowers, burning fishing villages, pirate ships anchored offshore, hidden coves, moonlit beaches.
- **Color palette**: Midnight blue, sand gold, fire orange, dark wood brown. Moonlit and atmospheric.
- **Enemies**: Scimitar pirates, musket snipers, powder monkeys.
- **Dimoni power acquired**: Smoke Vanish (Mask de Pollenca). Given by Es Dimoni de Pollenca early in level 4-1.

#### Level 4-1: "Sa Torre de Guaita" (The Watchtower)
- **Layout**: Mixed. A coastal watchtower and the surrounding cliffs. Starts on the moonlit beach, climbs the watchtower, overlooks pirate ships below.
- **Difficulty**: 5/10
- **Enemy composition**: 3 scimitar pirates (first encounter -- melee rushers, aggressive, fast), 2 musket snipers (first encounter -- stationary, ranged, positioned on tower levels). Relatively light enemy density to let the player absorb the new setting.
- **Platforming challenges**: Beach-to-tower climb using cliff faces and tower windows. Narrow watchtower interior with sniper sightlines (cover-based platforming). Tower top with sweeping views.
- **Collectibles**: 25-30 sling stones. 1 heart pickup. 1 secret: a treasure room behind a thin wall (visible from the beach, accessible with Smoke Vanish given early in this level). 15 bonus stones inside.
- **Teaching beats**:
  - World arrival: "First Romans, then a vampire, now pirates. Is there a single century where people leave this island alone?" Bep: "I think they like it here! I like it here too!" Ramon: "You like everything."
  - Dimoni de Pollenca encounter (early): sneaky, whisper-voiced. "Take this and be quiet about it." Gives Smoke Vanish to Llorenc.
  - Thin wall secret: Bep says "I can see something shimmering through that wall..." Player uses Smoke Vanish for the first time to phase through.
  - Sniper sightline: a corridor lit by moonlight where the sniper's laser-like gaze is visible. Vanishing makes the player invisible and avoids the shot.
- **End**: Save point with Llorenc shop.

#### Level 4-2: "Es Poble Cremat" (The Burning Village)
- **Layout**: Horizontal. A coastal fishing village under pirate attack. Burning buildings, fleeing NPCs, chaos. Dynamic level with fire hazards.
- **Difficulty**: 6/10
- **Enemy composition**: 5 scimitar pirates, 3 musket snipers (on rooftops), 2 powder monkeys (first encounter -- throw timed bombs that explode after 2 seconds, area denial).
- **Platforming challenges**: Rooftop running across burning buildings (some roofs collapse). Sniper gauntlets along streets (use Smoke Vanish or cover). A dock section with swinging ropes between boats.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: inside a collapsed house, accessible by dropping through a hole and using Fire Dash through debris (retroactive W3 power test). 20 stones inside.
- **Teaching beats**:
  - Powder monkeys: Bep says "That little one threw something! Run! RUN!" Teaches bomb avoidance timing.
  - Sniper gauntlet: clear sightlines. Smoke Vanish is the obvious tool, but skilled players can dash through or time their runs.
  - Burning building rooftops: visual urgency (fire rising) teaches speed. Collapse timing is generous enough on first attempts.
- **End**: Save point with Llorenc shop.

#### Level 4-3: "Sa Cala des Corsaris" (The Corsair's Cove)
- **Layout**: Mixed horizontal and vertical. A hidden pirate cove with ship interiors, cave networks, and an underwater grotto (no swimming -- stone platforms over water).
- **Difficulty**: 7/10
- **Enemy composition**: 4 scimitar pirates, 3 musket snipers (in ship rigging), 4 powder monkeys (increased presence -- bomb zones become more frequent). First combined encounters: pirates advance while powder monkeys lob bombs from behind.
- **Platforming challenges**: Ship interior navigation (tight corridors, swinging lanterns as hazards). Cave system with one-way platforms over water. A vertical climb up a cliff face with snipers shooting from adjacent ship masts.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: behind a thin wall inside the cave (Smoke Vanish). Contains 20 stones and a frozen rock pack.
- **Teaching beats**:
  - Combined enemy tactics: "They're working together!" Pirates push forward while bombs deny retreat.
  - Ship interiors: tight spaces change the combat dynamic. Vanish repositioning becomes essential.
  - Cave grotto: atmospheric calm before the storm. Beautiful parallax backgrounds contrast the violence above.
- **End**: Save point with Llorenc shop.

#### Level 4-4: "S'Abordatge" (The Boarding)
- **Layout**: Horizontal. A direct assault on Dragut's flagship from shore. Beach, rowboats as platforms, ship hull, deck.
- **Difficulty**: 7/10
- **Enemy composition**: 5 scimitar pirates, 4 musket snipers, 3 powder monkeys. Heaviest enemy density yet. Pirates attack in pairs.
- **Platforming challenges**: Rowboat hopping (small moving platforms on waves). Ship hull climbing (vertical, with pirates kicking down barrels as hazards). Deck approach with combined sniper fire and melee rushers.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the ship's hold, accessible by Stone Slam through the deck (25 stones, an ensaimada).
- **Teaching beats**:
  - Rowboat section: teaches precision platforming on small, moving surfaces.
  - Ship hull climbing: combines vertical platforming with enemy hazards -- everything the player has learned.
  - Deck approach: the gauntlet before the boss. Intense, fast-paced, but with clear forward momentum.
- **End**: Boss gate. Dragut's captain's cabin at the ship's stern.

#### Boss: Dragut
*(Full details in Section 6)*

- **Story beat**: After defeat, Dragut: "You fight well for a man from the rocks." Ramon: "Everyone on this island fights well. That's why you keep losing." Portal opens. Next world.

---

### 5.7 World 5 -- S'Invasio (Modern Day)

- **Setting**: Modern Mallorca. Magaluf strip, Palma airport, overcrowded beaches, "Se Vende" signs on every traditional house, luxury yachts, concrete hotels built over historic sites.
- **Color palette**: Oversaturated -- neon pink, tourist-brochure blue, concrete grey, gold (money). Garish and loud, contrasting all previous worlds.
- **Enemies**: Aggressive tourists, real estate agents, influencers, party buses (environmental hazard).
- **Dimoni power acquired**: Tourist Rage (Mask of Sa Pobla). Given by Es Dimoni de Sa Pobla at the start of level 5-1.

#### Level 5-1: "Sa Platja de s'Infern" (Hell's Beach)
- **Layout**: Horizontal. The Magaluf beachfront strip. Wide, open spaces packed with enemies. The widest level design in the game to accommodate crowds.
- **Difficulty**: 6/10
- **Enemy composition**: 8-10 tourists (swarms -- first encounter with large groups), 2 influencers (first encounter -- camera flash stun in a cone in front of them), 1 party bus pass (environmental).
- **Platforming challenges**: Minimal platforming. This is a crowd combat level. Beach umbrella hopping. Hotel pool as a pit hazard. Party bus crosses the screen periodically (telegraphed by engine sound and screen edge indicator).
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: inside a beach shack, accessible by Stone Slam through the floor (15 stones).
- **Teaching beats**:
  - Arrival cutscene: Ramon sees modern Mallorca. "...I think I preferred the pirates." Bep: "What's a hotel?" Ramon: "Where they charge you to sleep." Bep: "You can sleep anywhere!" Ramon: "...I know, Bep."
  - Dimoni de Sa Pobla encounter: overwhelmed, confused. "I can't take this anymore. TAKE THIS AND MAKE THEM STOP." Tourist Rage given.
  - First swarm: 6+ tourists surround Ramon. Bep: "There's too many of them!" Player uses Tourist Rage -- massive crowd clear. "Aha!" moment.
  - Influencer: flash stun teaches positioning (stay behind them or vanish through the flash).
  - Party bus: Bep screams before it appears. "WHAT IS THAT THING?!"
- **End**: Save point with Llorenc shop. Llorenc: "Fascinating. In Menorca, tourism is more... dignified." Ramon: "Is it." Llorenc: "...No."

#### Level 5-2: "S'Aeroport" (The Airport)
- **Layout**: Horizontal with conveyor sections. Palma airport interior. Conveyor belts as moving platforms, luggage carousels as hazards, boarding gates as checkpoints.
- **Difficulty**: 7/10
- **Enemy composition**: 6 tourists, 3 real estate agents (first encounter -- chase relentlessly with contracts, faster than tourists, take 3 hits), 2 influencers.
- **Platforming challenges**: Conveyor belt platforming (belts move in different directions, requiring adjustment). Luggage carousel section (rotating platforms with suitcases as obstacles). Escalator sections (moving platforms that speed up/slow down).
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: behind a "Staff Only" door (thin wall, Smoke Vanish). 20 stones inside.
- **Teaching beats**:
  - Real estate agents: aggressive pursuers. Bep: "He wants you to sign something! DON'T SIGN ANYTHING!"
  - Conveyor mechanics: some belts help, some hinder. Teaches reading the environment.
  - Airport PA system announcements serve as ambient comedy: "Flight to Menorca delayed. Llorenc, your cow is blocking the terminal."
- **End**: Save point with Llorenc shop.

#### Level 5-3: "Es Resort" (The Resort)
- **Layout**: Mixed horizontal and vertical. A massive beach resort complex. Pool areas, hotel lobbies, rooftop bars. Combines indoor and outdoor sections.
- **Difficulty**: 7/10
- **Enemy composition**: 6 tourists, 3 real estate agents, 3 influencers (camera flash becomes more dangerous in indoor areas with no escape room), 2 party bus passes (outdoor sections).
- **Platforming challenges**: Pool-hopping (fall in = damage, like pit hazards). Hotel balcony climbing (vertical sections). Rooftop bar with breakable furniture and neon signs as platforms.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the hotel basement, accessible by Stone Slam from the lobby floor (25 stones, a sobrassada pot).
- **Teaching beats**:
  - Indoor influencer encounters: tight spaces make the camera flash harder to avoid. Tourist Rage is essential.
  - Balcony climbing: tests double jump + wall jump in a modern architecture context.
  - Rooftop bar: chaotic combat arena. Tables break, neon signs fall. Environmental destruction as comedy.
- **End**: Save point with Llorenc shop.

#### Level 5-4: "Sa Grua" (The Crane)
- **Layout**: Vertical. Climbing a hotel under construction via scaffolding, cranes, and unfinished floors. The approach to El Magnat's penthouse.
- **Difficulty**: 8/10
- **Enemy composition**: 5 tourists, 4 real estate agents, 2 influencers, 1 party bus (drives across an unfinished floor). High density, mixed types.
- **Platforming challenges**: Scaffolding platforming (narrow, some sections collapse). Crane arm as a moving platform (swings slowly, player must time jumps). Unfinished floors with gaps (double jump + dash). Wind gusts on upper floors push Ramon sideways (new environmental hazard).
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: inside the crane cabin (requires Fire Dash through a metal barricade). 25 stones and an aigua de font.
- **Teaching beats**:
  - Construction site: everything is unstable. The level reinforces careful platforming.
  - Crane section: dramatic set piece. Wind + moving platform + enemies = peak difficulty before boss.
  - Top of the crane: panoramic view of Palma. Quiet moment. Bep: "It's beautiful up here." Ramon: "...It was better before."
- **End**: Boss gate. Penthouse elevator.

#### Boss: El Magnat (Phase 1)
*(Full details in Section 6)*

- **Story beat**: El Magnat escapes to Ibiza. Bep's curse activates for the geographic jump.

---

### 5.8 World 5.5 -- Eivissa (Modern Ibiza, Endgame)

- **Setting**: A nightmarish fusion of the Magnat's mega-resort empire on Ibiza. Ancient Phoenician ruins repurposed as nightclub foundations. Neon lights strung across historic walls. Es Vedra looms in the background. The whole island is the Magnat's domain.
- **Color palette**: Electric -- neon purple, toxic green, black, gold. The most visually aggressive world.
- **Enemies**: Fameliars (bottle imps, neon fameliars, VIP fameliars).
- **No new dimoni power**: The player must use all previously collected masks strategically. Mask swapping is the meta-skill.
- **[NEW] Quick-swap unlock**: At the start of W5.5-1, the mask quick-swap mechanic activates automatically (see Section 4.2). Narrative beat: as Ramon arrives in Eivissa, all his collected masks flare simultaneously. Bep: "Something's different... they're all awake!" The curse reaching its peak destabilizes the mask bindings — Ramon can now channel any mask freely without Llorenç as intermediary. From this point, shoulder buttons (L1/R1) or Q/E cycle through masks in real time. This is the mechanical payoff for collecting all five masks.
- **Length**: 3 levels + boss (shorter but significantly harder).

#### Level 5.5-1: "Sa Discoteca Antiga" (The Ancient Disco)
- **Layout**: Mixed. Phoenician ruins converted into a nightclub. Alternating sections that each test a different mask power in sequence: a floor to slam, a shaft to double jump, a gap to fire dash, a wall to vanish through, a swarm to rage.
- **Difficulty**: 8/10
- **Enemy composition**: 3 bottle imps (swarm section), 2 neon fameliars (light trail section), 2 VIP fameliars (first encounter -- shields block attacks from the front, must reposition). Mixed encounters at the end.
- **Platforming challenges**: Each section is a mini-challenge testing one mask:
  - Section A: Breakable floor (Stone Slam) over a lower path
  - Section B: Tall shaft (Double Jump + wall jump) to upper level
  - Section C: Wide neon-lit gap (Fire Dash across)
  - Section D: VIP familiars blocking a thin wall (Smoke Vanish through)
  - Section E: Bottle imp swarm (Tourist Rage to clear)
  - Final section: Combination requiring 2+ mask swaps in sequence
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: requires Stone Slam + Smoke Vanish in sequence (30 stones).
- **Teaching beats**:
  - This level is a "mask exam" -- it tests each power individually, then in combination. It also serves as the tutorial for the quick-swap mechanic — each section naturally prompts the player to cycle to the right mask.
  - Bep (at level start, after quick-swap unlock): "They're all responding to you now! Try switching — the shoulder buttons!" (Or Q/E prompt on keyboard.)
  - Bep: "We need everything we've got for this one."
  - VIP fameliars: "That big one has a shield! Like those Roman soldiers, but... shinier."
  - The final combination section is the real teaching beat: players must learn to use quick-swap fluidly mid-action (e.g., Stone Slam a floor, immediately cycle to Double Jump to clear the gap below).
- **End**: Save point with Llorenc shop. Llorenc: "I've catalogued all the masks. They're all remarkable. Ramon, we've come so far—" Ramon: "Shop. Now."

#### Level 5.5-2: "Es Mega-Resort" (The Mega-Resort)
- **Layout**: Horizontal with large rooms. The Magnat's mega-resort interior. Massive lobbies, VIP lounges, back-stage corridors. The longest level in the game.
- **Difficulty**: 9/10
- **Enemy composition**: 5 bottle imps, 4 neon fameliars, 3 VIP fameliars. Mixed encounters throughout -- no "safe" enemy type. Neon fameliars leave trails that restrict movement; VIP fameliars funnel the player into bad positions.
- **Platforming challenges**: Neon light trail navigation (trails persist for 5 seconds, blocking paths -- must time movement). VIP fameliars on narrow platforms (can't be attacked from the front, must vanish behind or slam from above). Combination challenges requiring mid-combat mask swaps.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the VIP lounge, behind a triple-locked door (Stone Slam a floor, Fire Dash through a barricade, then Smoke Vanish through a thin wall). 40 stones and a sobrassada pot.
- **Teaching beats**:
  - Neon fameliars: their trails create dynamic platforming. The floor changes moment to moment.
  - VIP + bottle imp combos: the VIP blocks while imps swarm. Must manage crowd AND reposition for the shield.
  - Mid-combat mask swaps: the game's hardest non-boss challenge. Multiple tools needed for a single encounter.
- **End**: Save point with Llorenc shop (final shop before the last boss).

#### Level 5.5-3: "Es Penyasegat d'Es Vedra" (The Cliff of Es Vedra)
- **Layout**: Vertical. The ascent to the Magnat's penthouse overlooking Es Vedra. A cliff-face climb with the resort built into the rock. The hardest pure platforming in the game.
- **Difficulty**: 9/10
- **Enemy composition**: 4 bottle imps, 3 neon fameliars, 3 VIP fameliars. Enemies placed at platforming cruxes (the worst possible moments).
- **Platforming challenges**: Cliff-face wall jumping with wind gusts. Neon trail avoidance during vertical climbs. Crumbling platforms over a long fall. A section requiring Fire Dash between two wall-jump surfaces (dash horizontally mid-climb). The final approach is a gauntlet of all hazard types.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: near the summit, a hidden cave entrance behind a Smoke Vanish wall (30 stones, an aigua de font, an ensaimada -- stocking up for the boss).
- **Teaching beats**:
  - This level is pure execution. Minimal Bep commentary -- even he's nervous.
  - The cliff face with Es Vedra in the background is the game's most dramatic visual set piece.
  - Final approach before the boss: Bep quietly says "We can do this, Ramon." Ramon says nothing. (The only time Ramon's silence is played for sincerity rather than comedy.)
- **End**: Boss gate. The Magnat's penthouse balcony.

#### Boss: El Magnat (Phase 2)
*(Full details in Section 6)*

- **Story beat**: El Magnat defeated. Empire crumbles. Curse breaks. "...I'm walking home." Credits.

---

## 6. BOSS DESIGN

### 6.1 Common Boss Design Principles

- Every boss has **3 phases** with escalating difficulty and changing patterns
- Each phase has clear **tells** before attacks (visual/audio cues) so the player can learn and react
- **[NEW] Tell Timing Rule**: Every boss attack has a minimum 0.5 second tell before the hitbox becomes active. Heavy attacks have 1.0+ second tells. This is non-negotiable -- if the player dies, they should always be able to say "I saw it coming and reacted too slowly," never "I couldn't see it."
- **[NEW] Punish Window Rule**: After every attack pattern, the boss has a recovery window of at least 1.5 seconds where the player can safely deal damage. Longer patterns have longer punish windows (up to 3 seconds).
- Bosses test the **mechanics introduced in their world** -- the current dimoni power should be useful (but not strictly required) during the fight
- Boss arenas are unique environments, not reused level geometry
- Every boss has a brief **intro cutscene** with personality-establishing dialogue
- Health is visible (boss health bar at top of screen)
- Half-heart minimum damage means bosses can have chip-damage moves and heavy-hit moves
- **[NEW] Boss Health Pools**: Expressed as "hits to kill" with the basic sling tap (1x damage). Charged shots and mask powers deal proportionally more. This makes balance transparent.

### 6.2 Es Bou de Pedra (World 1 Boss)

**Arena**: Open stone courtyard surrounded by taulas (T-shaped stone monuments). 4 stone pillars in the arena that can be shattered. The floor has 2 cracked sections (Stone Slam breakable). Mediterranean sky above.

**Health Pool**: ~30 tap-hits (or ~10 full-charge shots, or ~15 power shots).

**Phase 1: "The Charge" (100%-66% HP)**
- **Pattern A -- Bull Rush**: The bull paws the ground (tell: 1.0s, dust cloud + snorting sound), then charges horizontally across the arena. Hits a wall/pillar and is stunned for 2.5 seconds (punish window). If it hits a pillar, the pillar shatters (environmental change). Dodge by jumping or wall jumping off the arena edges.
  - Damage: 1.5 hearts on contact
- **Pattern B -- Headbutt**: If the player is close, the bull rears its head (tell: 0.5s, head glow) and bashes forward in a short arc. Quick attack, short punish window (1.5s of head shaking after).
  - Damage: 1 heart
- **Phase transition**: At 66% HP, the bull roars (screen shake), stamps both front hooves, and the arena changes.

**Phase 2: "The Stomp" (66%-33% HP)**
- **Pattern A -- Bull Rush** continues but faster (0.8s tell instead of 1.0s).
- **Pattern B -- Ground Stomp**: The bull rises on hind legs (tell: 1.2s, shadow grows beneath it) and slams down, sending stone shockwaves along the ground in both directions. Jump to avoid. Shockwaves travel ~6 tiles in each direction. Punish window: 2.0s while hooves are stuck.
  - Damage: 1 heart (shockwave), 1.5 hearts (direct stomp)
- **Pattern C -- Rock Hurl**: The bull scoops rubble with its horns (tell: 0.8s, horn glow) and flings it in a high arc. 3 rocks land at predicted positions (shadow markers on the ground). Punish window: 1.5s during the scoop animation (close range only).
  - Damage: 1 heart per rock
- **[NEW] Stone Slam Interaction**: If the player uses Stone Slam while the bull is mid-charge, the shockwave trips the bull, causing it to stumble and creating a 3.0 second punish window. Reward for reading the moment. Not required -- jumping still works.
- **Phase transition**: At 33% HP, the bull's stone body cracks, revealing a glowing dimoni-energy core in its chest. It staggers, roars in pain.

**Phase 3: "The Core" (33%-0% HP)**
- The bull's attacks become erratic and desperate.
- **Pattern A -- Frenzy Rush**: Charges back and forth rapidly (0.6s tell per charge), bouncing off walls 2-3 times. Player must wall jump to stay above. Punish window: 2.5s of panting after the frenzy ends.
  - Damage: 1.5 hearts
- **Pattern B -- Core Pulse**: The exposed core pulses with energy (tell: 1.0s, core brightens + high-pitched whine), releasing a circular shockwave. Must be airborne to dodge. Punish window: 2.0s after pulse.
  - Damage: 1 heart
- **Weak point**: The glowing core takes 2x damage from charged sling shots. Tier 3 (full charge) shots deal 3x. This makes the final phase faster for players who have mastered the charge mechanic. The core is only exposed from the front.
- **Death**: The bull freezes, cracks spread from the core outward, and it crumbles into a pile of stones. The dimoni energy wisps away.

**What skilled players can do differently**: Skip Stone Slam entirely (it's a bonus, not required). Time Tier 3 shots during short punish windows for faster kills. Stay close and aggressive rather than waiting for charges.

---

### 6.3 Quintus Caecilius Metellus (World 2 Boss)

**Arena**: Roman amphitheater. Sand floor, tiered stone seating on both sides (wall-jumpable). 4 columns at the arena's edges. A chariot track runs through the center.

**Health Pool**: ~35 tap-hits.

**Phase 1: "The Chariot" (100%-60% HP)**
- **Pattern A -- Chariot Charge**: Metellus drives his chariot from one side of the arena to the other (tell: 1.0s, whip crack + horse neigh + chariot visible at screen edge). Crosses the entire arena horizontally. Wall jump up the seating tiers to avoid, or double jump over if timed well. Punish window: 2.0s while the chariot turns at the far side.
  - Damage: 2 hearts (heavy, but long tell)
- **Pattern B -- Pilum Volley**: Metellus stands in the chariot and throws 3 javelins in a spread pattern (tell: 0.8s, arm raised + glint on spear tip). Gaps between javelins are jumpable with double jump. Punish window: 1.5s while he reaches for more spears.
  - Damage: 1 heart per javelin
- **Pattern C -- Shield Bash Drive-by**: Chariot passes close; Metellus swings a shield outward (tell: 0.5s, shield glow). Short range but catches players who dodge the chariot too late.
  - Damage: 1 heart
- **Double Jump Mastery Test**: The pilum gaps are specifically sized so that single jump can dodge one javelin but double jump is needed to dodge the spread. This is the core skill test.
- **Phase transition**: At 60% HP, a wheel breaks on the chariot. Metellus crashes, rolls to his feet, draws his gladius. "On foot, then. I conquered the Balearics on foot anyway."

**Phase 2: "The General" (60%-30% HP)**
- Metellus fights on foot. Faster than expected for a general in armor.
- **Pattern A -- Gladius Combo**: 3-hit sword combo (tell: 0.5s, sword raised). Each swing covers ~2 tiles forward. Punish window: 2.0s after the third swing (sword stuck briefly).
  - Damage: 1 heart per hit
- **Pattern B -- Shield Wall**: Raises shield and advances slowly (tell: obvious, he crouches behind shield). Blocks all frontal attacks. Must double jump over him and attack from behind. While shielded, he can still bash (0.5s tell, shield glows).
  - Damage: 0.5 hearts (shield bash)
- **Pattern C -- Tactical Retreat**: Jumps backward to a column, kicks rubble forward (tell: 0.8s, foot plants on column). 3 pieces of rubble in a spread. Double jump through gaps. He uses this to create distance.
  - Damage: 1 heart per rubble
- **Phase transition**: At 30% HP, Metellus blows a horn. "Legionaries! To me!" He backs to the arena center.

**Phase 3: "The Legion" (30%-0% HP)**
- 2 legionaries spawn on each side of the arena (4 total, respawn in pairs every 15 seconds if killed). Metellus fights simultaneously.
- **Metellus continues Phase 2 patterns** but with legionaries adding pressure.
- **Legionary behavior**: Same as normal legionaries -- shield front, attackable from above or behind. They slowly advance toward Ramon.
- **Crowd management test**: Must balance killing/avoiding legionaries while damaging Metellus. Double jump over legionary shields to reach Metellus. Tourist Rage (if replaying) clears the legionaries instantly.
- **Punish windows**: Metellus's recovery windows remain the same, but the player must create space from legionaries first.
- **Death**: Metellus drops to one knee. "You fight like the old slingers of legend. Perhaps these islands weren't so easy to conquer." Collapses.

**What skilled players can do differently**: Stay aggressive in Phase 1, landing hits between chariot passes. In Phase 3, ignore legionaries and focus Metellus down quickly. Stone Slam can stun legionaries to buy time.

---

### 6.4 El Comte Mal (World 3 Boss)

**Arena**: The Comte's great hall. Long, tall room with chandeliers, stone pillars, and the chained dimoni visible in the background. Dimoni-fire braziers at the edges of the room flare when the Comte drains power. The room has 3 elevated platforms (chandeliers that can be stood on).

**Health Pool**: ~40 tap-hits.

**Phase 1: "The Aristocrat" (100%-60% HP)**
- **Pattern A -- Teleport Strike**: The Comte vanishes in a cloud of bats (tell: 0.8s, bats swirl around him + a shadow appears at his destination 0.5s before he materializes). Appears next to Ramon and slashes with clawed hands. Punish window: 2.0s after the slash as he adjusts his cape dramatically.
  - Damage: 1 heart
- **Pattern B -- Bat Swarm**: Raises a hand (tell: 0.8s, hand glows red) and sends 5 bats in a wave pattern across the room. Bats move in a sine wave vertically. Jump through gaps between them. Punish window: 1.5s while his hand is extended.
  - Damage: 0.5 hearts per bat
- **Pattern C -- Blood Drain**: If Ramon is within melee range for too long, the Comte reaches out (tell: 0.5s, eyes flash red) to grab. If successful, drains 1.5 hearts and heals himself for 5% HP. Mash buttons to break free faster. Teaches staying mobile.
  - Damage: 1.5 hearts (grab), but breakable
- **Charged shot opportunity**: The Comte is briefly still during the cape-adjusting punish window -- perfect for Tier 2 or 3 charged shots.
- **Phase transition**: At 60% HP, the Comte hisses in frustration. "Enough." He turns toward the chained dimoni and begins draining its power. The room darkens, fire braziers flare.

**Phase 2: "The Drain" (60%-30% HP)**
- The Comte is visually powered up: red aura, eyes glowing, moves faster.
- **Pattern A -- Teleport Strike** is faster (0.5s tell, less shadow warning). Still punishable for 1.5s.
- **Pattern B -- Fire Pillar Eruption**: The dimoni's leaking energy erupts as fire pillars from the braziers (tell: 1.0s, braziers brighten + ground glows at eruption points). 3 pillars rise from the floor in sequence. Jump or use platforms to avoid.
  - Damage: 1.5 hearts
- **Pattern C -- Shadow Dash**: The Comte dashes across the room leaving a damaging shadow trail (tell: 0.8s, he crouches + trail preview on the ground). Trail persists for 3 seconds. Jump to the chandelier platforms to escape.
  - Damage: 1 heart (trail contact)
- **[NEW] Fire Dash Foreshadowing**: The fire pillars ARE the dimoni's power leaking. After this fight, the freed dimoni grants Fire Dash. Observant players will recognize the connection.
- **Phase transition**: At 30% HP, the dimoni's prison cracks loudly. The Comte stumbles, weakened by the dimoni pulling back its power. "No! The power is MINE!"

**Phase 3: "The Desperate Count" (30%-0% HP)**
- The Comte is visibly weakened -- flickering, unstable. But desperation makes him dangerous.
- **Pattern A -- Frenzy Teleport**: Teleports 3 times rapidly, slashing each time (tell: 0.5s per teleport, but shadow markers help). Each slash covers a wider area. Punish window: 3.0s after the frenzy (gasping, hunched).
  - Damage: 1 heart per slash
- **Pattern B -- Bat Storm**: Fills the room with bats (tell: 1.0s, screech + screen darkens). Bats swirl in a pattern with safe spots near the chandelier platforms. Lasts 5 seconds. Punish window: 2.0s after storm clears.
  - Damage: 0.5 hearts per bat hit
- **Weak point**: The Comte takes 1.5x damage from charged sling shots while weakened in Phase 3. Tier 3 charged shots to the Comte during his gasping recovery deal devastating damage.
- **Death**: The Comte's form destabilizes. "This... is not over..." He dissolves into bats that scatter and vanish. The dimoni's chains shatter.

**What skilled players can do differently**: Aggressive melee during Phase 1 punish windows (no need to charge shots). In Phase 2, use chandelier platforms to stay above fire pillars and snipe during recovery. Phase 3 can be ended in 2-3 punish windows with full-charge shots.

---

### 6.5 Dragut (World 4 Boss)

**Arena**: Three-part arena. Phase 1 on the moonlit beach (flat, wide). Phase 2 boarding the ship (vertical climb). Phase 3 on the ship deck (medium, flat with mast obstacles).

**Health Pool**: ~40 tap-hits (split: Phase 1 lasts until boarding, Phase 2 is crew-clearing with no boss HP drain, Phase 3 is the real health bar).

**Phase 1: "The Bombardment" (Beach)**
- **No direct combat with Dragut** -- he's on the ship commanding cannons.
- **Pattern A -- Cannon Volley**: 3 cannons fire in sequence (tell: 1.0s per cannon, visible cannon flash + whistling sound). Impact zones marked by shadow circles on the beach. Dodge by running/jumping between impacts.
  - Damage: 1.5 hearts per cannonball
- **Pattern B -- Grapeshot Sweep**: A wide cannon fires a horizontal spread of small projectiles (tell: 0.8s, distinct cannon sound). Jump or double jump over the spread. Lower grapeshot can be ducked under (crouch at wall edge).
  - Damage: 1 heart
- **Pattern C -- Fire Barrel**: A burning barrel is launched in a high arc (tell: 1.0s, barrel visible in the air, shadow grows on ground). Explodes on impact in a wide radius. Run clear.
  - Damage: 1.5 hearts (explosion)
- **Objective**: Survive the bombardment while reaching the rowboats at the water's edge. 3-4 volleys, then a rowboat section (platforming across small boats to reach the ship).
- **Phase transition**: Ramon reaches the ship's hull. Dragut: "Coming aboard? Bold. I like bold. Kill him."

**Phase 2: "The Boarding" (Ship Hull + Deck)**
- **Gauntlet section**, not a boss HP phase. Fight through 6 pirate crew members on the deck (scimitar pirates + 2 powder monkeys).
- The ship rocks gently, causing all characters to slide slightly left/right periodically (environmental mechanic -- adds unpredictability).
- **Smoke Vanish** is extremely useful here: vanish through the crowd to reach safer positions, dodge bombs, phase through a barricade the pirates set up on deck.
- **End of Phase 2**: All crew defeated or bypassed. Dragut draws twin scimitars. "Just you and me, then. Good."

**Phase 3: "The Duel" (Ship Deck)**
- **The real boss fight**. Dragut is fast, aggressive, and relentless.
- **Pattern A -- Twin Slash Combo**: 4 rapid horizontal slashes (tell: 0.3s per slash -- fast! -- but he takes a wide stance 0.8s before starting the full combo). Covers ~3 tiles forward per slash. Punish window: 2.5s after the fourth slash (arms wide, panting).
  - Damage: 1 heart per slash
- **Pattern B -- Scimitar Throw**: Throws one scimitar like a boomerang (tell: 0.8s, arm winds back). Travels across the screen and returns. Double jump over or Smoke Vanish through. While one scimitar is thrown, his melee combos are only 2 slashes instead of 4. Punish window: 1.5s while catching the return.
  - Damage: 1.5 hearts
- **Pattern C -- Deck Slam**: Stabs both scimitars into the deck (tell: 1.0s, jumps into the air), sending a shockwave along the wood. Jump to avoid. The slam also knocks loose rigging ropes that swing across the deck for 3 seconds (secondary hazard). Punish window: 2.0s while pulling scimitars free.
  - Damage: 1.5 hearts (slam), 0.5 hearts (rope)
- **Smoke Vanish Mastery Test**: Dragut's 4-slash combo is specifically designed so that Smoke Vanish allows phasing through the entire combo if timed at the start. Without vanish, the player must retreat or wall-jump the mast to escape. Both work, but vanish is cleaner.
- **Ship rock**: The deck still rocks gently. At ~15% HP, the rocking intensifies (the ship is breaking apart from the battle).
- **Death**: Dragut drops to one knee, scimitars clattering. "You fight well for a man from the rocks." Ramon: "Everyone on this island fights well. That's why you keep losing." Dragut laughs, then collapses.

**What skilled players can do differently**: Parry the scimitar throw with a timed sling tap (returns it for 3x damage -- hidden mechanic, not required). Stay in melee range and exploit the short recovery between Dragut's combo slashes rather than retreating.

---

### 6.6 El Magnat Phase 1 (World 5 Boss)

**Arena**: Rooftop of an illegally-built luxury hotel overlooking Palma Bay. Helipad at one end, penthouse pool at the other (pit hazard). Golden furniture as destructible obstacles. Neon "SE VENDE" sign flickering in the background.

**Health Pool**: ~35 tap-hits.

**Phase 1: "The Mogul" (100%-60% HP)**
- **Pattern A -- Money Toss**: Throws bundles of euro bills that create shockwaves on impact (tell: 0.8s, reaches into golden suit jacket, bills glow). 2-3 bundles in a spread. Jump the shockwaves (they travel along the ground ~4 tiles each way). Punish window: 1.5s while he adjusts his cufflinks.
  - Damage: 1 heart (shockwave), 0.5 hearts (direct bundle hit)
- **Pattern B -- Lawyer Summon**: Pulls out a golden phone (tell: 1.0s, phone ring sound), summons 2 lawyer minions. Lawyers are weak (2 hits) but chase aggressively with briefcases. They respawn after 10 seconds if not killed. Tourist Rage clears them instantly.
  - Damage: 0.5 hearts (briefcase swing)
- **Pattern C -- Gold Card Throw**: Flicks a golden credit card like a shuriken (tell: 0.5s, hand flick). Fast, low projectile. Duck or jump.
  - Damage: 1 heart
- **Tourist Rage test**: The lawyer summons specifically test crowd management. Rage -> clear lawyers -> punish Magnat during his phone animation.
- **Phase transition**: At 60% HP, the Magnat snaps his fingers. "You're trespassing on private property." Construction walls rise around the arena edges, shrinking the playable area by ~25%.

**Phase 2: "The Developer" (60%-30% HP)**
- The arena is smaller. The Magnat adds construction-themed attacks.
- **Pattern A -- Contract Wall**: Slams the ground with a rolled-up contract (tell: 1.0s, contract unrolls visually + ground glows). A wall of legal paperwork rises from the ground, blocking the arena further. Must break through with attacks (5 hits) or Fire Dash through. Creates strategic lane management.
  - No direct damage, but restricts movement
- **Pattern B -- Money Toss** continues, more bundles (4 at once), harder to dodge in the smaller space.
- **Pattern C -- Phone Call Reinforcements**: Now summons 3 lawyers at once. Tourist Rage is almost mandatory to manage them in the smaller arena.
- **Pattern D -- Wrecking Ball**: A construction crane swings a wrecking ball across the arena (tell: 1.2s, crane creaks + shadow on ground). Horizontal sweep. Double jump over or Smoke Vanish through. The wrecking ball destroys Contract Walls in its path (environmental help).
  - Damage: 2 hearts
- **Phase transition**: At 30% HP, the Magnat stumbles backward. "You don't understand! This isn't just Mallorca!" He pulls out his phone again.

**Phase 3: "The Escape" (30%-0% HP)**
- The Magnat becomes frantic. Attacks are faster and more desperate.
- **Pattern A -- Money Rain**: Throws money into the air. Bills rain down across the arena (tell: 1.0s, money flies up + shadow rain on ground). Random impact points, but density is manageable. Punish window: 2.0s (he's out of money momentarily, patting his jacket).
  - Damage: 0.5 hearts per bill
- **Pattern B -- Golden Phone Laser**: Points his phone and fires a beam across the arena (tell: 1.0s, phone charges with golden light). Sweeps left to right. Jump, double jump, or Smoke Vanish.
  - Damage: 1.5 hearts
- **Pattern C -- Lawyer Wave**: Summons 4 lawyers in a line. Tourist Rage or fight through.
- **At 0% HP**: The Magnat raises his hands. "You think Mallorca was my endgame? I own IBIZA." A helicopter appears. He grabs a ladder and escapes. The arena crumbles. Cutscene transition.
- **[NEW] This is NOT a real defeat** -- the player doesn't get the satisfaction of a proper kill. This is intentional -- it fuels the desire to chase him to Ibiza. The "escape boss" is a narrative tool.

**What skilled players can do differently**: Break Contract Walls immediately to keep the arena open. Ignore lawyers and focus Magnat down (requires dodging lawyers while attacking). Fire Dash through Contract Walls instantly.

---

### 6.7 El Magnat Phase 2 (World 5.5 Boss)

**Arena**: The pinnacle of the Magnat's mega-resort, overlooking the Ibiza coastline. Es Vedra visible in the moonlit background. The platform is circular, surrounded by neon lights. Familiar energy crackles across the surface.

**Health Pool**: ~50 tap-hits (the longest fight in the game).

**Phase 1: "The Tycoon Empowered" (100%-60% HP)**
- The Magnat floats above the arena, powered by familiar energy. Golden aura, eyes glowing, physically larger.
- **Pattern A -- Money Meteor**: Hurls golden energy balls downward (tell: 0.8s, hand raises + shadow on ground). 3 meteors in sequence. Each creates a shockwave on impact. Jump the shockwave, double jump the meteor.
  - Damage: 1.5 hearts (meteor), 1 heart (shockwave)
- **Pattern B -- Familiar Summon**: Opens a portal (tell: 1.0s, portal crackles). 4 bottle imps pour out. Tourist Rage clears them, but they also drop heart pickups (1 guaranteed per wave), providing sustain for the long fight.
  - Damage: 0.5 hearts per imp contact
- **Pattern C -- Golden Beam**: Fires a horizontal beam across the arena (tell: 1.0s, eyes flash gold). Sweeps in an arc. Double jump to avoid, or Smoke Vanish through.
  - Damage: 1.5 hearts
- **How to damage him**: He's floating -- melee doesn't reach. Must use charged sling shots (Tier 2+) or lure him to a lower hover during punish windows (after Familiar Summon, he descends briefly for 2.5s to observe the fight -- punish window).
- **Phase transition**: At 60% HP, the arena cracks. "You can't stop progress!" He channels more familiar energy. The outer ring of the arena crumbles away, reducing the platform size by ~30%.

**Phase 2: "The Arena Crumbles" (60%-30% HP)**
- Smaller arena. The Magnat alternates between floating and ground slams.
- **Pattern A -- Ground Slam**: Descends rapidly (tell: 1.0s, floats higher first + shadow expands). Slams the ground, cracking it further. Shockwave in all directions. Jump to avoid. Punish window: 3.0s while he pulls himself out of the crater (this is the main damage window -- get close and melee).
  - Damage: 2 hearts (slam), 1 heart (shockwave)
- **Pattern B -- Neon Familiar Trail**: Summons 2 neon fameliars that race across the arena, leaving damaging light trails (tell: 0.8s, portals open at arena edges). Trails persist for 5 seconds. Limits movement.
  - Damage: 1 heart (trail contact)
- **Pattern C -- VIP Shield**: Summons a VIP familiar as a bodyguard (tell: 0.8s, golden portal). The VIP has a shield and blocks Ramon's attacks until dispatched (3 hits from behind, or Stone Slam stuns it, or Smoke Vanish to get behind).
- **Pattern D -- Money Meteor** continues with 4 meteors now.
- **Stone Slam utility**: After the Ground Slam, if the player uses Stone Slam on the cracked ground, rubble rises and hits the Magnat for bonus damage. Reward for reading the environment.
- **Phase transition**: At 30% HP, the Magnat screams. Familiar energy surges. The arena shrinks to its final size (~60% of original). "EVERYONE HAS A PRICE!"

**Phase 3: "The Final Mask Test" (30%-0% HP)**
- This phase is the game's ultimate test. The Magnat uses attacks that each require a SPECIFIC mask to counter optimally. The attacks cycle in a fixed sequence, teaching the player the pattern before demanding it.
- **Cycle** (repeats until death):
  1. **Familiar Floor Slam**: Entire ground pulses with energy (tell: 1.0s, ground glows gold). **Stone Slam the ground** to disrupt the pulse and create a safe stone platform. Without Stone Slam, the player takes unavoidable chip damage (0.5 hearts).
  2. **Aerial Barrage**: Magnat flies high and rains 6 projectiles (tell: 0.8s, arms spread). **Double Jump** to reach the stone platform created by Stone Slam (or just dodge on the ground -- harder).
  3. **Golden Barrier**: Magnat surrounds himself with a golden energy wall while charging a beam (tell: 1.2s, barrier appears). **Fire Dash through** the barrier to interrupt the charge and deal damage. Without Fire Dash, the beam fires and must be jumped (1.5 hearts).
  4. **Familiar Wave**: 6 bottle imps + 2 VIP fameliars swarm the arena (tell: 0.8s, portals everywhere). **Tourist Rage** to clear the bottle imps, then deal with VIPs individually. Without Rage, the swarm overwhelms.
  5. **Scythe Sweep**: Magnat swoops across the arena with arms extended (tell: 0.8s, he banks into a glide). **Smoke Vanish** to phase through. Without Vanish, extremely tight jump timing required.
  6. **Punish Window**: After the full cycle, Magnat lands, exhausted, for 4.0 seconds. All-out attack. This is the main damage window for the entire phase.
- Each cycle takes ~30 seconds. The fight requires 3-4 full cycles to kill.
- **On defeat**: The Magnat staggers. "Everyone... has a price..." Ramon: "I don't even know what money is." The familiar energy explodes outward. The Magnat collapses. His empire literally crumbles -- the resort disintegrates around them. The fameliars are freed, cheering as they scatter.

**What skilled players can do differently**: Skip mask switches -- each attack CAN be dodged without the "right" mask, but it's significantly harder. Speedrunners will find that staying in Fire Dash and timing perfectly can bypass most of the cycle. Stone Slam during the Ground Slam creates extra damage in Phase 2 for a faster kill.

---

## 7. ECONOMY BALANCE

**[REVISED] Data-driven economy**: All economy values in this section (prices, costs, drop rates, income targets) are stored in `data/economy.json` -- the single source of truth for economy tuning. The project owner can edit this file directly during playtesting to adjust any value without touching game code. See Section 7.4 for the full architecture requirement.

### 7.1 Stone Income Per Level

**[NEW]** This section provides rough balance targets. Exact numbers are tuned during implementation (via `data/economy.json`), but the ratios should hold.

| Source | Stones per level (avg) | Notes |
|--------|----------------------|-------|
| Enemy drops | 8-12 | ~1 stone per enemy killed |
| Breakable objects | 10-15 | Pots, crates, grass tufts, furniture |
| Secrets | 10-25 | Rewards exploration; higher in later worlds |
| Heart/consumable trade-off | 0 | Hearts don't cost stones; they just occupy the same breakables |
| **Total per level (thorough explorer)** | **28-52** | Averages ~35 stones/level |
| **Total per level (rusher)** | **12-20** | Enemies only + obvious breakables |

### 7.2 Stone Income Per World

| World | Levels | Stones (explorer) | Stones (rusher) | Cumulative Explorer | Cumulative Rusher |
|-------|--------|-------------------|-----------------|--------------------|--------------------|
| W1 | 4 | 120-140 | 50-70 | 130 | 60 |
| W2 | 4 | 140-160 | 60-80 | 280 | 130 |
| W3 | 4 | 140-160 | 60-80 | 430 | 200 |
| W4 | 4 | 160-180 | 70-90 | 600 | 280 |
| W5 | 4 | 160-180 | 70-90 | 770 | 360 |
| W5.5 | 3 | 120-140 | 50-70 | 900 | 420 |
| **Total** | **23** | **~900** | **~420** | | |

### 7.3 Stone Spending Budget

| Purchase | Cost | When Available | Explorer Affordability | Rusher Affordability |
|----------|------|---------------|----------------------|---------------------|
| Ensaimada (2 hearts) | 10 | W1 | Trivial | Affordable |
| Heart Upgrade 1 | 40 | W1 | Affordable by end of W1 | Affordable by mid-W2 |
| Sobrassada Pot (full heal) | 25 | W2 | Trivial | Moderate |
| Heart Upgrade 2 | 75 | W2 | Affordable by end of W2 | Affordable by end of W3 |
| Herbes / Oli buffs | 30 | W3 | Trivial | Moderate |
| Heart Upgrade 3 | 120 | W3 | Affordable by end of W3 | Tight by end of W4 |
| Explosive/Piercing/Frozen packs | 30-50 | W2-W4 | Comfortable | Only basics |
| Heart Upgrade 4 | 175 | W4 | Affordable by end of W4 | Cannot afford easily |
| Aigua de Font (invincibility) | 40 | W4 | Affordable | Rare purchase |
| Heart Upgrade 5 | 240 | W5 | Affordable by end of W5 | Cannot afford |

**Balance intent**:
- An **explorer** who finds secrets and breaks everything can afford all 5 heart upgrades (650 stones) AND buy consumables regularly throughout the game. They should feel rewarded -- never broke, always able to stock up before a boss. The ~250 stones remaining after all upgrades provides a comfortable consumable budget.
- A **rusher** can afford 3 heart upgrades and occasional consumables. They feel the pinch around World 4, which is when the game's difficulty ramps up. This naturally encourages them to explore more OR rely on skill. They can complete the game without buying anything, but it's harder.
- No player should ever be locked out of progress by insufficient currency. The worst case (0 stones, no upgrades) just means the player is at base stats and must rely on pure skill.
- **All values in this table are loaded from `data/economy.json`** and can be adjusted during playtesting without code changes.

### 7.4 Heart Upgrade Cost Curve

**[REVISED]** The cost curve has been reduced so that a thorough explorer can afford all upgrades and still have stones left for consumables. The curve follows a roughly exponential pattern but stays within the explorer's budget:

```
Upgrade 1:   40 stones  (cumulative:   40)
Upgrade 2:   75 stones  (cumulative:  115)
Upgrade 3:  120 stones  (cumulative:  235)
Upgrade 4:  175 stones  (cumulative:  410)
Upgrade 5:  240 stones  (cumulative:  650)
```

This curve means:
- The first upgrade is a quick early reward (achievable in World 1)
- Mid-game upgrades require some exploration commitment
- The final upgrade is a long-term goal that rewards completionists
- Total cost (650) is ~72% of the explorer's total income (~900 stones), leaving ~250 stones for consumables, special ammo, and general shopping throughout the game
- A thorough explorer should feel **rewarded**, not forced into painful trade-offs

**Tuning note**: If playtesting reveals the economy is too generous or too tight, all these values live in `data/economy.json` and can be adjusted without code changes. The first levers to pull: heart upgrade costs (this curve) and secret stone counts per level.

**[ARCHITECTURE REQUIREMENT for En Miquel]**: The economy system must read ALL values from `data/economy.json` at runtime. This includes but is not limited to: heart upgrade costs, consumable prices, consumable effects (heal amounts, buff durations, buff multipliers), special ammo pack sizes and costs, enemy drop rates and amounts, breakable object stone yields, secret reward amounts, tax collector steal amounts, and shop unlock thresholds. The game must never hardcode any of these values. This enables rapid balance iteration during playtesting.

---

## 8. ART DIRECTION

### 8.1 Visual Style & Constraints

- 16-bit pixel art (SNES era reference)
- Pixel-perfect rendering at base resolution (320x180 or 384x216), scaled to display
- Limited color palette per world (8-16 dominant colors) for visual cohesion and retro authenticity
- No anti-aliasing, no sub-pixel rendering -- hard pixel edges

### 8.2 Sprite Size Guidelines

- **Ramon**: 24x32 pixels (or similar, proportional to a stocky warrior)
- **Bep**: 16x16 pixels (small, round, always near Ramon)
- **Standard enemies**: 16x24 to 24x32 pixels depending on type
- **Bosses**: 48x48 to 96x96+ pixels (large, imposing)
- **Tiles**: 16x16 pixel grid

### 8.3 Color Palettes per World

| World | Dominant Colors | Mood |
|-------|----------------|------|
| 1 -- Sa Talaia | Ochre, stone grey, olive green, Mediterranean blue | Warm, natural, open |
| 2 -- Mallorca Romana | Stone white, imperial red, laurel green, marble grey | Ordered, grand |
| 3 -- El Comte Mal | Charcoal, blood red, sickly green, candlelight orange | Dark, gothic, oppressive |
| 4 -- Els Pirates | Midnight blue, sand gold, fire orange, dark wood | Atmospheric, moonlit |
| 5 -- S'Invasio | Neon pink, brochure blue, concrete grey, gold | Garish, oversaturated |
| 5.5 -- Eivissa | Neon purple, toxic green, black, gold | Electric, aggressive |

### 8.4 Character Sprite Sheets

Each character needs a sprite sheet covering:
- Idle (with idle variations/breathing)
- Walk/run cycle
- Jump (ascending + descending)
- Wall slide
- Attack (sling tap -- quick swing)
- Attack (sling charge -- visible charge-up + release)
- Damage taken (hit stun)
- Death
- Mask-specific power animations (one per mask)
- Bep: idle variations (chewing, sleeping, startled, talking, glowing)

### 8.5 Tileset Guidelines

- One tileset per world (ground, walls, platforms, decorations, breakables)
- Each tileset must include: solid tiles, one-way platforms, breakable tiles (for Stone Slam), thin walls (for Smoke Vanish), wooden barricades (for Fire Dash)
- Background layers: parallax scrolling (2-3 layers per world)

### 8.6 UI/HUD Visual Design

- Hearts displayed top-left
- Current mask icon displayed top-right (with cooldown radial fill indicator)
- Sling stone count displayed below mask icon
- Special ammo indicator (if equipped) near stone count with recharge visual
- **[NEW] Charge indicator**: When holding the sling attack, a small charge meter appears near Ramon (not in the HUD -- world-space) showing Tier 1/2/3 progression
- Minimal UI -- retro clean, no clutter

---

## 9. AUDIO DIRECTION

### 9.1 Music System Architecture

Music is **mocked and stubbed** for initial development. The audio system must be built so that any music track can be trivially dropped in.

- All music playback goes through a central **AudioManager**
- Each music slot is a **named reference** pointing to a file path (or silence/placeholder)
- Replacing a track means changing a file path in a configuration file or dropping a file into the correct folder -- no code changes required
- Supported formats: .ogg, .mp3, .wav

### 9.2 Audio Slot Definitions

The following named slots must exist in the audio system:

```
menu_theme
world_1_theme
world_2_theme
world_3_theme
world_4_theme
world_5_theme
world_5_5_theme
boss_1_theme
boss_2_theme
boss_3_theme
boss_4_theme
boss_5_theme
boss_5_5_theme
shop_theme
cutscene_theme
victory_jingle
death_jingle
game_over_theme
credits_theme
```

Each slot defaults to silence (or a simple placeholder beep) until a real track is provided.

### 9.3 SFX List

Sound effects needed (also mocked/stubbed with simple placeholder sounds):

```
sling_tap          -- melee swing
sling_charge_1     -- charge tier 1 loop (low pitch)       [NEW]
sling_charge_2     -- charge tier 2 loop (medium pitch)    [NEW]
sling_charge_3     -- charge tier 3 loop (high pitch)      [NEW]
sling_release      -- stone fired
stone_hit          -- stone impacts enemy/surface
jump               -- basic jump
double_jump        -- second jump (slightly different sound)
wall_jump          -- kick off wall
land               -- landing on ground
damage_taken       -- Ramon hit
heart_pickup       -- health restored
stone_pickup       -- currency collected
mask_equip         -- swapping dimoni mask
mask_cooldown_ready -- mask power available again           [NEW]
power_stone_slam   -- ground pound
power_fire_dash    -- dash woosh + fire
power_smoke_vanish -- poof/smoke
power_tourist_rage -- scream/shockwave
bep_bleat          -- Bep's general sound
bep_sneeze         -- time portal trigger
portal_open        -- time portal opening
boss_intro         -- boss appears
boss_hit           -- boss takes damage
boss_phase_change  -- boss transitions between phases      [NEW]
boss_death         -- boss defeated
menu_select        -- UI navigation
menu_confirm       -- UI confirm
shop_buy           -- purchase confirmed                   [NEW]
shop_insufficient  -- not enough stones                    [NEW]
```

### 9.4 How to Replace Placeholder Audio

1. Place the audio file in the appropriate folder (`assets/audio/music/` or `assets/audio/sfx/`)
2. Update the audio configuration file (or name the file to match the slot name)
3. The AudioManager picks it up automatically on next load

No code changes needed. The system is hot-swappable during development.

---

## 10. UI & UX

### 10.1 HUD Layout

```
[Heart][Heart][Heart]                    [Mask Icon]
                                         [Stone: 042]
                                         [Ammo: 3/5]
```

- Top-left: Hearts (current and max, half-heart granularity)
- Top-right: Current dimoni mask icon with cooldown radial, sling stone count, special ammo count with recharge indicator
- **[NEW] Quick-swap HUD update**: When the quick-swap mechanic is active (W5.5+ or Level Select replay after unlock), the mask icon updates in real time as the player cycles with L1/R1 or Q/E. A brief slide animation (old icon slides out, new icon slides in, ~0.15s) confirms the swap. Small left/right arrows appear beside the mask icon to indicate quick-swap is available. During the 0.3s swap cooldown, the icon border briefly dims.
- Minimal, non-intrusive, retro-styled

### 10.2 Dialogue System

- **Text boxes** at the bottom of the screen (classic JRPG style)
- **Character portrait** on the left side of the text box (pixel art, expressive)
- Text appears letter-by-letter (skippable with button press)
- Bep's dialogue is frequent but always short (1-2 lines max)
- All dialogue is optional-feeling -- never blocks gameplay for long
- Boss intros are unskippable on first encounter, skippable on retry

### 10.3 Shop Interface

- Llorenc's shop is a dedicated screen (not in-level overlay)
- Two tabs: **Masks** (swap active dimoni power) and **Items** (buy consumables/upgrades). **[NEW]** Once quick-swap is unlocked (W5.5+), the Masks tab adds a note: "Quick-swap active — use L1/R1 to cycle masks anytime." The tab remains functional for browsing mask lore and descriptions.
- Each mask shows: icon, name, power description, button prompt
- Items show: name, effect, cost in sling stones
- Llorenc has optional dialogue for each mask/item (lore tidbits, one-liners)
- Bruna visible in the background. Bep hides behind Ramon if Bruna is on screen.
- **[NEW] Insufficient funds feedback**: If the player tries to buy something they can't afford, the item shakes and Llorenc has a quip: "That one's expensive. Try breaking more pots."

### 10.4 Pause Menu

- Pause available at any time during gameplay
- Options: Resume, Items (use consumables), Controls, Quit to Menu
- No mid-level saving from pause -- pause is just a pause

### 10.5 World Transition Screens

- After boss defeat + Bep's portal: a brief animated cutscene of the portal opening and the characters being pulled in
- Loading screen: pixel art vignette of the next era with the world name and date
- Arrival: brief cutscene of Ramon and Bep arriving, reacting to the new setting

---

## 11. TECHNICAL ARCHITECTURE

### 11.1 Pygame Structure Overview

- Main game loop: input -> update -> render at 60 FPS
- Scene/state-based architecture (menu, gameplay, dialogue, shop, cutscene, boss)
- All game logic separated from rendering

### 11.2 Game States & Scene Management

```
MAIN_MENU -> LEVEL_SELECT -> GAMEPLAY -> DIALOGUE
     |              |            |         |
  SETTINGS       CREDITS      PAUSE      SHOP
                                |
                            GAME_OVER
```

- **LEVEL_SELECT** replaces the earlier WORLD_SELECT concept. It shows all completed levels organized by world, with completion indicators (beaten, secret found/not found). Only levels the player has beaten are selectable. Accessible from the main menu at any time once at least one level has been completed.
- State machine with push/pop stack (e.g., GAMEPLAY -> push PAUSE -> pop back to GAMEPLAY)
- Transitions between states are handled by a central scene manager
- Entering a level from LEVEL_SELECT (replay) vs. entering from normal progression both lead to GAMEPLAY, but replay mode preserves the player's current story position

### 11.3 Sprite & Animation System

- Sprite sheets loaded and sliced into frames
- Animation defined as frame sequences with per-frame duration
- State-driven animation (idle, walk, jump, attack, etc.)
- Animation controller per entity, driven by game state

### 11.4 Tilemap & Level Format

- Tile-based levels using a standard format (Tiled .tmx or custom JSON)
- Layers: background, midground (collision), foreground (decoration), entities (spawn points)
- Collision layer defines solid, one-way, breakable, and phase-through tiles
- Levels are data files, not code -- editable externally

### 11.5 Collision System

- Axis-aligned bounding box (AABB) collision
- Separate collision layers for: terrain, enemies, projectiles, triggers
- Wall jump detection: check for wall collision while airborne + jump input
- Phase-through (Smoke Vanish): temporarily disable enemy/thin-wall collision

### 11.6 Audio Manager

- Centralized AudioManager class
- Named slots for music and SFX (see Section 9)
- Configuration-driven: a single file maps slot names to file paths
- Methods: play_music(slot), stop_music(), play_sfx(slot)
- Graceful fallback: if a file is missing, log a warning and play silence -- never crash
- Volume controls accessible from settings

### 11.7 Save System

- **Save trigger**: Automatic at the end of each level (after the level-complete screen)
- **No mid-level saves**
- **Save data**: Current world, current level, collected masks, current max hearts, sling stone count, purchased upgrades, special ammo state, **per-level completion flags** (beaten yes/no), **per-level secret-found flags**
- **Level replay data**: The save file tracks which individual levels have been completed. This drives the Level Select screen — only beaten levels appear as selectable. Secret-found flags are stored per level to display completion indicators.
- **Death behavior**: Restart current level with pre-level-start state (stones and hearts as they were when the level began). Consumables used during failed attempt are refunded.
- **Storage**: Local file (JSON or similar), single save slot (expandable later)

### 11.8 Performance Targets

- 60 FPS on modest hardware (the game is pixel art with simple physics -- performance should not be an issue)
- Pygame's sprite groups for efficient rendering
- No heavy computation per frame -- all physics is simple AABB
- Asset loading: per-world, loaded on world transition, not all at once

---

## 12. CONTROLS

### 12.1 Keyboard Layout

| Action | Key |
|--------|-----|
| Move Left | A / Left Arrow |
| Move Right | D / Right Arrow |
| Jump | Space |
| Sling Attack (tap/hold) | J / Z |
| Mask Power | K / X |
| Mask Cycle Left | Q *(quick-swap, W5.5+ only)* |
| Mask Cycle Right | E *(quick-swap, W5.5+ only)* |
| Special Ammo Toggle | L / C |
| Pause | Escape |
| Interact / Advance Dialogue | Enter |

### 12.2 Gamepad Layout

| Action | Button |
|--------|--------|
| Move | Left Stick / D-pad |
| Jump | A (Xbox) / X (PS) |
| Sling Attack (tap/hold) | X (Xbox) / Square (PS) |
| Mask Power | Y (Xbox) / Triangle (PS) |
| Mask Cycle Left | LB (Xbox) / L1 (PS) *(quick-swap, W5.5+ only)* |
| Mask Cycle Right | RB (Xbox) / R1 (PS) *(quick-swap, W5.5+ only)* |
| Special Ammo Toggle | B (Xbox) / Circle (PS) |
| Pause | Start |
| Interact / Advance Dialogue | A (Xbox) / X (PS) |

### 12.3 Design Notes

- Wall jump is automatic (jump while against wall). No extra input.
- Sling attack is a single button: tap for melee, hold for charge. The charge tier is shown by the in-world charge indicator.
- Mask power has a single dedicated button. The current mask determines the effect.
- **[NEW] Quick-swap controls**: Mask Cycle Left/Right (L1/R1 or Q/E) are inactive until the quick-swap mechanic unlocks at W5.5 start. Before that, pressing these buttons does nothing (no error feedback needed — the buttons simply aren't bound yet). After unlock, these become the primary mask-swap method. A 0.3-second cooldown between swaps prevents accidental rapid cycling. On keyboard, E is reassigned from Interact to Mask Cycle Right; Interact moves to Enter only.
- Controls should be remappable in the settings menu.

---

## APPENDIX A: Level Count Summary

| World | Levels | Boss | Total Encounters |
|-------|--------|------|-----------------|
| W1 -- Sa Talaia | 4 | 1 | 5 |
| W2 -- Mallorca Romana | 4 | 1 | 5 |
| W3 -- El Comte Mal | 4 | 1 | 5 |
| W4 -- Els Pirates | 4 | 1 | 5 |
| W5 -- S'Invasio | 4 | 1 | 5 |
| W5.5 -- Eivissa | 3 | 1 | 4 |
| **Total** | **23** | **6** | **29** |

## APPENDIX B: Difficulty Curve (All Levels)

```
Difficulty
10 |                                                          [5.5-B]
 9 |                                                    [5.5-2][5.5-3]
 8 |                                          [5-4][5-B][5.5-1]
 7 |                            [3-4][3-B][4-3][4-4][4-B][5-2][5-3]
 6 |                 [2-4][2-B][3-3]      [4-2]            [5-1]
 5 |           [2-2][2-3]      [3-1][3-2][4-1]
 4 |      [1-4][2-1]
 3 |  [1-3]
 2 | [1-2]
 1 |[1-1]
   +--------------------------------------------------------------
    W1-1  W1-4  W2-1  W2-4  W3-1  W3-4  W4-1  W4-4  W5-1  W5-4  5.5
```

B = Boss encounter. The curve is designed to be smooth with no jarring spikes. Each world starts slightly below the previous world's midpoint, providing a brief ramp-up period with the new mechanic before difficulty escalates.

## APPENDIX C: Retroactive Secret Map

**[NEW]** Secrets that become accessible when revisiting earlier worlds with later mask powers.

| Secret Location | World | Requires | Reward |
|----------------|-------|----------|--------|
| High cliff ledge (1-1 area) | W1 | Double Jump (W2) | 15 stones |
| Sealed cave (1-3 area) | W1 | Fire Dash (W3) | 25 stones + ensaimada |
| Shimmering wall (1-4 area) | W1 | Smoke Vanish (W4) | 20 stones |
| Narrow passage (2-1 area) | W2 | Fire Dash (W3) | 20 stones |
| Thin wall in aqueduct (2-2) | W2 | Smoke Vanish (W4) | 25 stones + ammo pack |
| Crowd switch (2-3 area) | W2 | Tourist Rage (W5) | 30 stones |
| Side room in tower (3-4) | W3 | Smoke Vanish (W4) | 20 stones |
| Heavy door (3-2 area) | W3 | Tourist Rage (W5) | 25 stones |
| Collapsed building (4-2) | W4 | Fire Dash (W3)* | 20 stones |
| Deep cave (4-3 area) | W4 | Tourist Rage (W5) | 30 stones + oli d'oliva |

*W4 collapsed building can be accessed on first visit if the player already has Fire Dash from W3. This is the one non-retroactive "secret" -- it rewards having the mask equipped at the right moment.

Retroactive secrets are purely optional. They provide economic bonuses for completionists but are never required for progression.

**[NEW] Quick-swap synergy**: Once the mask quick-swap mechanic is unlocked at W5.5 (see Section 4.2), replaying earlier levels for retroactive secrets becomes significantly more enjoyable. Players can cycle masks on the fly during Level Select replays, making multi-mask secrets (e.g., the W5.5-2 triple-locked door requiring Stone Slam + Fire Dash + Smoke Vanish) feel like fluid puzzle-solving rather than trial-and-error with pre-selected masks. This is the primary replay motivator for post-endgame content.
