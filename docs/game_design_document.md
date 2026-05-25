# SA FONA — Game Design Document

> **Working title**: Sa Fona
> **Version**: 3.0 (Production — Mask Acquisition Restructure)
> **Genre**: 2D Retro Side-Scrolling Platformer with Combat
> **Engine**: Pygame (Python)
> **Refined by**: En Biel (Game Director)
> **Based on**: GDD v2.0

---

## 1. GAME OVERVIEW

### 1.1 Concept Summary

Sa Fona is a 2D retro platformer set across the Balearic Islands through different historical eras. The player controls Balchar, a grumpy talayotic slinger who gets cursed into time-traveling with his annoying (but lovable) myotragus companion Bep. Each world represents a different period of Mallorcan history or folklore, blending real events and local legends with lighthearted parody. The game features a dimoni mask power-up system inspired by Mallorcan village demons, satisfying sling-based combat with tap-and-charge mechanics, and a reluctant-hero story in the spirit of Shrek.

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

- **Shrek** -- Reluctant hero, buddy dynamic between Balchar and Bep, parody tone
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
| **World 1 — Sa Talaia** | Complete: 4 levels + Es Bou de Pedra boss fight. Full tutorial flow, sling combat (tap + charge), wall jump, pure movement-based gameplay (no masks during levels). Stone Slam earned post-boss. Shop introduction, Bep dialogue system. |
| **World 2 — Mallorca Romana (stub)** | 1 basic level to validate Stone Slam usage in a Roman-themed context. No boss, no full progression — just enough to prove the second world's feel works with the newly acquired mask. |

Phase 1 answers the critical design questions: Does the movement feel good? Is the sling combat satisfying? Does earning a mask at the end of a world create satisfying forward momentum? Does the difficulty curve from W1-L1 (tutorial) to W1-Boss feel right? Can the engine handle the target scope at 60 FPS?

**Phase 2+ — Incremental World Production**

After Phase 1 sign-off, remaining worlds (W2 complete, W3–W5, W5.5) are built incrementally. Each world is scoped, built, and playtested before the next begins. The full GDD content below serves as the design target, but production commitments beyond Phase 1 are deferred until the vertical slice proves the concept.

---

## 2. STORY & NARRATIVE

### 2.1 Premise & Inciting Incident

Balchar, a foner from the talayotic period (~1000 BC Mallorca), is napping against a talayot. His myotragus, Bep, wanders off and eats the sacred herbs growing on a dimoni's altar -- the dimoni's prized garden. The dimoni arrives furious, curses Bep, and storms off. Balchar wakes up, sees Bep chewing with a guilty face: "...What did you eat now?"

The curse has two effects: Bep gains the ability to speak (and won't shut up), and Bep becomes a living time-travel trigger -- after moments of great energy (boss defeats), the curse activates, Bep glows, sneezes, and rips open a time portal.

The player does not know any of this during World 1. It plays as a straight talayotic adventure. The time-travel premise is only revealed after beating the first boss.

### 2.2 Full Story Arc

**World 1 -- Sa Talaia (Talayotic ~1000 BC)**
Balchar and Bep navigate their own era. Something feels off -- possessed sheep, unnatural energy, a creeping wrongness. They defeat Es Bou de Pedra. The dimoni de Sant Joan appears, impressed and grudgingly grateful. It grants its mask -- the Stone Slam -- to Llorenç (who will be met in the next world, but narratively the mask is entrusted for safekeeping). Then Bep starts glowing. He sneezes. A time portal rips open. The dimoni from the intro appears, laughing: "You thought we were done? That sheep ate my herbs. Every dimoni on this island wants a piece of him now. Good luck." Balchar and Bep are sucked in.

Balchar: "...I just wanted a nap."

**World 2 -- Mallorca Romana (Roman Conquest, 123 BC)**
Balchar is confused by roads and tall architecture. Romans mistake him for a barbarian rebel. He meets Llorenc, a fellow talayotic warrior from Menorca who has been researching dimoni activity and tracked the time disturbance. Llorenc is fascinated by the curse; Balchar is annoyed. They become reluctant allies. Balchar now has Stone Slam from World 1's dimoni -- and it proves devastatingly effective against Roman shield formations. After defeating Quintus Metellus, the local dimoni de Manacor appears, impressed by Balchar's tenacity against the organized invaders. It grants the Double Jump mask to Llorenc for safekeeping. This establishes the shop mechanic.

**World 3 -- El Comte Mal (Feudal Mallorca, legend-based)**
Dark feudal Mallorca. The Comte Mal, a powerful vampire nobleman, has captured and imprisoned a dimoni to siphon its supernatural power. An old witch, La Bruixa, maintains the binding ritual for the Comte -- she is a pawn, used by him, not an enemy in her own right. Strange fires burn across the Comte's lands. Balchar uses Stone Slam and the newly acquired Double Jump to navigate the gothic towers and claustrophobic corridors. After freeing the dimoni by defeating the Comte, the grateful dimoni grants its Fire Dash mask to Llorenc. This cements the narrative rule: dimonis don't trust Balchar (he's cursed, chaotic, everything explodes around him), so all masks go to Llorenc.

**World 4 -- Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)**
Ottoman pirate raids on the Mallorcan coast. Coastal watchtowers, burning villages, moonlit beaches. Locals beg Balchar to help defend. He sighs deeply: "First Romans, then a vampire, now pirates. Is there a single century where people leave this island alone?" Fire Dash proves invaluable for burning through wooden pirate barricades and dashing across gaps between ships. After defeating Dragut, the local dimoni de Pollenca emerges from the shadows and grants the Smoke Vanish mask.

**World 5 -- S'Invasio (Modern Day)**
Balchar arrives in the present. His ancestral land has been turned into hotel chains. "...I think I preferred the pirates." A satirical world full of tourists, real estate agents, influencers, and party buses. Smoke Vanish lets Balchar phase through tourist crowds and dodge influencer camera flashes. He defeats El Magnat, a real estate tycoon, on a luxury hotel rooftop. But the Magnat pulls out a phone: "You think Mallorca was my endgame? I own IBIZA." A helicopter arrives. He escapes. The overwhelmed dimoni de Sa Pobla grants Tourist Rage.

**World 5.5 -- Eivissa (Modern Ibiza)**
Bep's curse activates one last time -- but instead of a time jump, it's a geographic jump. They're sneezed to Ibiza. The Magnat has built a mega-resort empire powered by enslaved fameliars (little demons from Santa Eularia folklore). Shorter but harder world. Balchar uses all his collected powers -- including the newly acquired Tourist Rage for crowd control -- to bring it down. Final confrontation with El Magnat empowered by familiar energy.

### 2.3 Narrative Tone & Voice

The game is a lighthearted parody. Real historical events and genuine Mallorcan folklore are the foundation, but everything is viewed through the lens of a protagonist who finds it all deeply inconvenient. The humor comes from the contrast: the world is dramatic and high-stakes, Balchar is not.

- Dialogue is short and punchy
- Historical commentary is always filtered through character perspective
- Serious themes (colonization, piracy, gentrification) are addressed through satire, never preachy
- Every NPC interaction should be either funny, informative, or both

### 2.4 Ending & Post-Credits

El Magnat phase 2 is defeated. His empire crumbles. The curse breaks -- all dimoni debts are settled through the journey. Bep stops glowing. Balchar looks at Bep. Looks at Llorenc. Looks at the player.

"...I'm taking a nap."

Credits roll over pixel art: Balchar and Bep walking along a Mediterranean coast toward Mallorca. Llorenc waves goodbye from Ibiza with Bruna.

**Post-credits**: Bep is grazing peacefully near a talayot. He spots a strange plant. He eats it. His eyes widen. Screen cuts to black. A single bleat. Silence.

---

## 3. CHARACTERS

### 3.1 Balchar -- Protagonist

- **What he is**: A foner -- a talayotic warrior and slinger from ~1000 BC Mallorca
- **Personality**: Grumpy, laconic, reluctant. Just wants to be left alone. Dry Mallorcan humor. Never asked to be a hero. Complains about everything but quietly does the right thing when it matters (without admitting it).
- **Visual direction**: Stocky build, simple tunic, leather sling always in hand. Bronze-age aesthetic. Perpetually unimpressed expression.
- **Dialogue style**: Short sentences. Deadpan. "No." "Fine." "This is your fault, Bep." Never more than two lines at a time.

### 3.2 Bep -- Companion

- **What he is**: A myotragus balearicus (extinct Balearic bovid, sheep-like). Balchar's companion animal.
- **Personality**: Cheerful, oblivious, unconditionally loyal. Loves Balchar despite constant rejection. Talks too much after being cursed. Comic relief. Occasionally says something accidentally wise.
- **Gameplay role**:
  - Hints mechanics through dialogue ("Balchar! I bet if you hold that button longer the rock goes further!" / "That wall looks jumpable!")
  - Triggers time-travel portals after each boss (involuntary curse activation: glows -> sneezes -> portal opens)
  - Visual companion on screen with idle animations (chews on things, falls asleep, gets startled by enemies)
  - Does NOT have a gameplay button or direct mechanical interaction -- purely narrative and cosmetic presence
- **Visual direction**: Small, round, sheep-like with stubby horns. Expressive eyes. Faint glowing aura after the curse.
- **Dialogue style**: Enthusiastic, rambling. "Balchar! Did you see that? You were amazing! ...Balchar? Balchar, are you ignoring me? That's okay, I still think you're great."

### 3.3 Llorenc -- Shop/Lore NPC

- **What he is**: A talayotic warrior from Menorca. Researcher, collector, nerd.
- **Personality**: Enthusiastic about artifacts and dimoni lore. Friendly rivalry with Balchar based on the classic Mallorca-vs-Menorca banter. Genuine friends despite the jabs.
- **Gameplay role**:
  - Appears between worlds and at level-end save points
  - Runs the **Mask Shop**: player swaps dimoni powers here
  - Sells **consumables** (health recovery, temporary buffs)
  - Sells **max heart upgrades** (permanent, increasingly expensive)
  - Provides optional lore about each era and dimoni
- **Why he holds the masks**: Established through plot (Worlds 1-3). Dimonis don't trust Balchar -- he's cursed, chaotic, destruction follows him. They entrust their masks to Llorenc, the calm, respectful researcher. Balchar has to visit Llorenc to equip powers. This is both narrative and a gameplay gate.
- **Companion**: Bruna, a Menorcan cow. Calm, stoic. Looks at Bep with quiet disdain. Bep is terrified of her.
- **Visual direction**: Similar build to Balchar but slightly taller. Carries a satchel full of artifacts. Always has a scroll or mask in hand. Bruna stands behind him at the shop.
- **Dialogue style**: Wordy, excited. "Fascinating! This mask channels the fire dimoni of the Comte Mal's domain. In Menorca we have similar legends but -- you don't care, do you." Balchar: "No."

### 3.4 Dimonis -- Per-World NPCs

**[REVISED v3.0]** Each world features a dimoni that appears **after the boss is defeated** as a post-boss reward moment. The dimoni is impressed (or grudgingly grateful) that Balchar dealt with the local threat, and grants its mask power to Llorenc. The dimoni may appear briefly earlier in the world for **narrative foreshadowing** (a glimpse, a voice, environmental signs of its presence), but the mask is **never given until the boss is beaten**.

| World | Dimoni | Personality | Foreshadowing | Mask Granted Post-Boss |
|-------|--------|-------------|---------------|----------------------|
| 1 -- Sa Talaia | Es Dimoni de Sant Joan | The original offended dimoni. Furious, vindictive, dramatic. | Appears in the intro curse scene. His energy corrupts the landscape. | Stone Slam (post-Es Bou de Pedra) |
| 2 -- Mallorca Romana | Es Dimoni de Manacor | Intense, impatient, fed up with Roman order. | Strange energy disruptions in Roman structures. Bep senses something familiar. | Double Jump (post-Metellus) |
| 3 -- El Comte Mal | Captured dimoni (unnamed, from the Comte's lands) | Imprisoned, weakened. Grateful when freed but doesn't trust Balchar. | Strange fires, flickering torches, La Bruixa's rituals hint at the imprisoned dimoni. | Fire Dash (post-Comte Mal) |
| 4 -- Els Pirates | Es Dimoni de Pollenca | Sneaky, nocturnal, whisper-voiced. Fits the stealth theme. Hates the noise pirates make. | Moonlit shadows move strangely. Whispers in the wind near coastal ruins. | Smoke Vanish (post-Dragut) |
| 5 -- S'Invasio | Es Dimoni de Sa Pobla | The most iconic Mallorcan dimoni. Overwhelmed by modernity. Confused by phones. | Modern construction has disturbed ancient sites. Strange energy in the hotel foundations. | Tourist Rage (post-El Magnat P1) |

### 3.5 Bosses

| World | Boss | Description |
|-------|------|-------------|
| 1 | **Es Bou de Pedra** | A massive stone bull animated by dimoni energy from a talayotic sanctuary -- rooted in the bronze-age bull worship evidenced by Balearic bull figurines. The first real test. After defeating it, the time-travel reveal happens and Stone Slam is earned. |
| 2 | **Quintus Caecilius Metellus** | The actual Roman general who conquered the Balearics. Fights from a chariot. Arrogant, tactical. After defeat, Double Jump is earned. |
| 3 | **El Comte Mal** | A vampire nobleman from Mallorcan legend. Has been siphoning a captured dimoni's power with the help of La Bruixa, an old witch he manipulates. Powerful, aristocratic, cruel. After defeat, Fire Dash is earned. La Bruixa is part of the story (cutscenes, plot) but NOT part of the gameplay fight. |
| 4 | **Dragut** | Famous Ottoman corsair. Ship-to-shore battle. Boisterous, confident, respects strength. After defeat, Smoke Vanish is earned. |
| 5 | **El Magnat (Phase 1)** | A real estate tycoon in a golden suit. Fought on his luxury hotel rooftop. Uses money and lawyers. Flees to Ibiza when defeated. After his escape, Tourist Rage is earned. |
| 5.5 | **El Magnat (Phase 2)** | Empowered by absorbed familiar energy. Bigger, golden, floating. Multi-phase fight testing all mechanics. No new mask — the final victory. |

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
- Wall jump: automatic -- when the player is against a wall and presses jump, Balchar kicks off it. No special input required, triggered by context.

**Sling Combat (the fona)**

The sling has two modes on a single button:

- **Tap attack**: Balchar swings the loaded sling as a melee weapon -- short range hit, like a whip crack. Quick, no cost. This is the primary combat tool for close encounters.
- **Hold attack**: Balchar loads a stone and begins charging. The longer the button is held, the more powerful the shot (visual/audio feedback as charge builds). Released when the player lets go. Fires a ranged projectile. **Unlimited basic ammo** -- the charge time is the balancing cost. Useful for hitting distant targets, specific boss weak points, and triggering ranged switches/mechanisms.

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

**[REVISED v3.0 — Post-Boss Mask Acquisition]**

Masks are earned at the **end of each world**, after defeating the boss, as a post-boss reward from the local dimoni. The mask fills a single **power-up slot** activated with a dedicated button. Only one mask can be active at a time. Masks are swapped at Llorenc's shop.

**Core Design Rule**: Each mask is earned in World N and becomes available **from World N+1 onward**. The levels within World N are designed around the masks the player already has from previous worlds. This creates a "look forward" reward structure — beating a boss earns the player a new tool that they're excited to use in the next world.

**Cross-World Synergy Principle**: Each mask is designed to be **especially relevant and synergistic** for the world that follows the one where it's earned. Stone Slam (earned W1) is particularly effective in W2's Roman setting. Double Jump (earned W2) is critical for W3's gothic vertical spaces. And so on.

**[NEW] Mask Cooldown System**: Each mask power has a cooldown after use. This prevents spamming and creates rhythm in combat/traversal. Cooldowns are displayed visually as a radial fill on the mask icon in the HUD.

| Earned After | Mask | Power | Cooldown | Traversal Use | Combat Use |
|--------------|------|-------|----------|---------------|------------|
| W1 Boss (Es Bou de Pedra) | Mask of Sant Joan | **Stone Slam** | 2s | Breaks floor tiles to reveal areas below. Creates stone platforms in certain lava/water sections (platform rises from rubble). | Ground pound shockwave damages all grounded enemies in range (~3 tiles). Stuns heavy enemies briefly. |
| W2 Boss (Metellus) | Mask of Manacor | **Double Jump** | 0.5s (resets on landing) | Second midair jump. Reach higher platforms, cross wider gaps. Essential for vertical level design. | Aerial repositioning. Jump over shield formations to hit from above. Dodge boss attacks with vertical escape. |
| W3 Boss (Comte Mal) | Mask of Fire | **Fire Dash** | 3s | Horizontal dash covers ~5 tiles. Burns through wooden barricades. Crosses gaps too wide for double jump. | Invulnerable during dash frames (~0.3s). Damages all enemies in the dash path. Breaks through enemy shields. |
| W4 Boss (Dragut) | Mask of Pollenca | **Smoke Vanish** | 4s | Phase through thin walls to find hidden routes. Brief invisibility (~1.5s). | Dodge through enemy attacks untouched. Phase through projectiles. Reposition behind shielded enemies. |
| W5 Boss (Magnat P1) | Mask of Sa Pobla | **Tourist Rage** | 5s | AoE push clears destructible environmental obstacles. Activates certain crowd-triggered switches (need multiple hits simultaneously). | Pushes all nearby enemies back ~4 tiles and stuns for 2s. Essential crowd control for swarm encounters. |

**Mask Availability Per World**:

| World | Available Masks | Earned After Boss |
|-------|----------------|-------------------|
| W1 -- Sa Talaia | **None** (pure movement + sling combat) | Stone Slam |
| W2 -- Mallorca Romana | **Stone Slam** | Double Jump |
| W3 -- El Comte Mal | **Stone Slam + Double Jump** | Fire Dash |
| W4 -- Els Pirates | **Stone Slam + Double Jump + Fire Dash** | Smoke Vanish |
| W5 -- S'Invasio | **Stone Slam + Double Jump + Fire Dash + Smoke Vanish** | Tourist Rage |
| W5.5 -- Eivissa | **All 5 masks + quick-swap** | None (final world) |

**Design principle**: Each power changes both combat AND traversal. Powers aren't just for fighting -- they open up navigation options. This encourages replaying earlier worlds with later masks to find secrets (optional, not required).

**Design rule — Mask Availability** *(per [Issue #3](https://github.com/Tonigit/SaFona/issues/3), revised v3.0)*: No level may require a mask the player has not yet obtained to be completed. Masks are acquired **after defeating the boss of their respective world** and are only available from the following world onward. There are no temporary power pickups, preview pickups, or any other way to use a mask power before it is permanently unlocked. Areas in levels that respond to a future mask (e.g., breakable floors in W1 that respond to Stone Slam from post-W1) are strictly **optional replay secrets** accessible via Level Select. They must never gate required progression.

**[NEW] Mask Quick-Swap Mechanic** *(per [Issue #5](https://github.com/Tonigit/SaFona/issues/5))*:

At the start of World 5.5 (Eivissa), Balchar unlocks the ability to **cycle through all collected masks in real time** using shoulder buttons (L1/R1 on gamepad, Q/E on keyboard). This replaces the need to visit Llorenç's shop to swap masks during W5.5.

- **Unlock trigger**: Automatic at the start of W5.5-1. Narrative justification: the curse reaching its peak in Eivissa destabilizes all mask bindings, letting Balchar channel them freely without Llorenç as intermediary.
- **Cycling**: L1 cycles left (previous mask), R1 cycles right (next mask) through the collected mask list. The cycle wraps around.
- **Cooldown**: 0.3-second cooldown between swaps to prevent accidental cycling. During cooldown, swap input is ignored (no queuing).
- **HUD feedback**: The mask icon in the top-right HUD updates in real time when cycling. A brief swap animation (icon slides out/in) confirms the change.
- **No pause**: Swapping happens in real time — the game does not pause or slow down. This is intentional: mid-combat mask swaps are the core skill test of W5.5.
- **Level Select replay**: Once unlocked, quick-swap is available in **all levels accessed via Level Select**, including earlier worlds. This is the key replay motivator — revisiting W1-W5 levels for retroactive secrets (Appendix C) becomes fluid and fun instead of requiring shop visits between attempts.
- **Llorenç's shop**: Still exists for buying consumables, upgrades, and special ammo. The Masks tab in the shop remains functional but is no longer the only way to swap masks once quick-swap is unlocked.

### 4.3 Health & Damage

- **Hearts system** (Zelda-style)
- Balchar starts with **3 hearts** (6 half-hearts)
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

**[REVISED v3.0 — Post-Boss Acquisition Model]**

This matrix maps how masks earned in previous worlds serve traversal, combat, and boss testing in each world. Masks are earned at the END of a world and become available from the NEXT world onward. Each mask is designed to be especially synergistic with the world that follows.

| World | Available Masks | Key Synergy (Newest Mask vs. This World) | Traversal Use | Combat Use | Boss Test | Retroactive Secrets |
|-------|----------------|------------------------------------------|---------------|------------|-----------|-------------------|
| W1 -- Sa Talaia | **None** | N/A — Pure movement + sling. The game's tutorial world teaches core mechanics without mask complexity. | Jump, wall jump only | Sling tap + charge only | Es Bou de Pedra: tests jump, wall jump, sling mastery, pattern recognition | N/A (first world) |
| W2 -- Mallorca Romana | **Stone Slam** (from W1) | Stone Slam vs. Roman architecture: break Roman shield formations from above, shatter stone columns to create stepping platforms, smash through reinforced Roman fortifications, cave in aqueduct sections to reveal shortcuts | Break floors to find hidden paths beneath Roman roads, shatter stone columns to create platforms across gaps, collapse weak aqueduct sections | Ground pound shockwave scatters shield formations, stuns legionaries through their shields from above, shatters armored war dogs' helmets | Metellus: Stone Slam scatters legionary reinforcements in phase 3, breaks chariot wheel supports, shatters arena columns for tactical advantage | W1: high cliff ledges, sealed caves, breakable floors now accessible |
| W3 -- El Comte Mal | **Stone Slam + Double Jump** (from W1-W2) | Double Jump vs. Gothic architecture: navigate vertical gothic towers, escape ceiling traps by jumping to safety, reach high platforms in claustrophobic manor rooms, clear wide chasms in the Comte's crumbling estate | Double Jump up church towers, escape collapsing ceiling traps, reach chandelier platforms, clear wide gaps between tower sections | Aerial repositioning over undead swarms, escape bat dive-bombs, jump over cursed villager charge attacks | Comte Mal: Double Jump to chandelier platforms to dodge bat storms, escape teleport strikes vertically, reach elevated safe zones during fire pillar eruptions | W1-W2: vertical secrets, high ledges in Roman atriums |
| W4 -- Els Pirates | **Stone Slam + Double Jump + Fire Dash** (from W1-W3) | Fire Dash vs. Pirate setting: burn through wooden ship barricades, dash across water gaps between boats, break through wooden pirate fortifications, ignite powder kegs for chain explosions, clear burning debris paths | Dash across water gaps between ships, burn through wooden barricades on docks and ships, cross burning village sections safely (invulnerability frames) | Dash through pirate melee rushers dealing damage, break through musket sniper barricades, ignite powder monkey bombs prematurely | Dragut: Fire Dash through cannon barrage debris to reach rowboats faster, dash across ship gaps during boarding, dash through Dragut's twin-scimitar combos for counterattack positioning | W1-W3: wooden barricades, wide gaps unreachable without dash |
| W5 -- S'Invasio | **Stone Slam + Double Jump + Fire Dash + Smoke Vanish** (from W1-W4) | Smoke Vanish vs. Modern crowds: phase through tourist crowds undetected, dodge influencer camera flash cones, sneak past party bus routes, infiltrate "Staff Only" areas, bypass real estate agent contract-chase sequences | Phase through tourist walls, vanish past influencer sight cones, infiltrate restricted modern areas (staff doors, VIP sections) | Vanish through camera flash stuns, phase through real estate agent grabs, reposition behind shielded enemies, dodge party bus impacts | Magnat P1: Vanish through lawyer swarms to reach Magnat, phase through golden beam attacks, dodge Contract Wall creation | W1-W4: thin walls throughout all prior worlds, shimmering surfaces |
| W5.5 -- Eivissa | **All 5 masks + quick-swap** | Tourist Rage (from W5) vs. Familiar swarms: crowd control against bottle imp swarms, push back VIP familiars, clear neon familiar trail buildup, activate crowd-pressure switches in ancient ruins | Tourist Rage clears destructible obstacles, activates multi-hit switches. All masks needed for comprehensive traversal. | Rage for bottle imp crowd control, combined with mask-swapping for VIP and neon fameliars. | Magnat P2 phase 3: specific attacks require specific masks in sequence — full toolkit mastery test | All remaining secrets accessible with quick-swap |

**Cross-World Synergy Design Rationale**:

The post-boss mask acquisition creates a powerful "earned reward" loop. Each boss fight is a climax that proves the player's mastery of their current toolkit, and the mask reward immediately makes the player excited for the next world. The synergies are designed so the new mask feels like the *answer* to the next world's challenges:

- **Stone Slam → W2 (Romans)**: Romans rely on rigid formations and stone architecture. Stone Slam breaks both — it shatters shields from above and collapses their engineered structures. Thematically, the ancient talayotic power disrupts Roman order.
- **Double Jump → W3 (Gothic)**: The Comte's domain is vertical — towers, manors, ceilings that close in. Double Jump gives Balchar the vertical freedom to survive claustrophobic gothic spaces. It also provides escape routes from the Comte's teleportation ambushes.
- **Fire Dash → W4 (Pirates)**: Pirate ships are wooden. Pirate fortifications are wooden. The gaps between ships and shore demand horizontal speed. Fire Dash burns through all of it and provides the horizontal mobility that naval combat environments demand.
- **Smoke Vanish → W5 (Modern)**: Modern Mallorca is about crowds, surveillance (influencer cameras), and restricted access (VIP areas, "Staff Only"). Smoke Vanish provides the stealth toolkit to navigate a world where the "enemies" are overwhelming numbers and detection systems.
- **Tourist Rage → W5.5 (Ibiza)**: The familiar swarms in Ibiza are the densest enemy encounters in the game. Tourist Rage's AoE crowd control is the direct answer to being overwhelmed by bottle imps and neon fameliars in every room.

### 5.1 Learning Curve Map

**[REVISED v3.0]** What the player knows at each world's start, what new mask they have access to (earned in the previous world), and how the world teaches them to apply it.

#### World 1 -- Sa Talaia (Tutorial World)
- **Entering knowledge**: Nothing. This is the start.
- **Available masks**: None. W1 is pure movement + sling combat.
- **New skills taught**: Move, jump, wall jump, sling tap, sling charge (3 tiers)
- **Teaching structure**:
  - Level 1-1: Move and jump only. Simple gaps, no enemies for first section. Bep teaches controls through dialogue.
  - Level 1-2: Sling tap introduced (first enemies: possessed sheep). Hold-to-charge taught via a distant switch.
  - Level 1-3: Wall jump introduced via vertical cave. Complex platforming using jump + wall jump chains.
  - Level 1-4: All mechanics combined in pre-boss gauntlet. Stone guardians test everything.
  - Boss: Tests jump, wall jump, sling charge, and pattern recognition. **Post-boss: Stone Slam earned.**
- **Difficulty arc**: 1 -> 2 -> 3 -> 4 -> 5 (boss)
- **Relief valves**: Generous heart pickups. Proto-shop opens after level 1-2.
- **Design note**: The absence of masks in W1 is a feature, not a limitation. It forces the player to fully internalize the core moveset before any powers are layered on. This makes the Stone Slam reward feel *earned* and meaningful.

#### World 2 -- Mallorca Romana
- **Entering knowledge**: Full moveset (no masks yet in W1, so the core is solid)
- **Available masks**: Stone Slam (earned post-W1 boss)
- **New skill to master**: Stone Slam applied to Roman architecture and formations
- **Teaching structure**:
  - Level 2-1: Roman road and settlement. Stone Slam is the player's first mask — teach it here. Cracked Roman floors hide treasure. Shield legionaries block frontal attacks — Stone Slam's shockwave scatters them. Bep: "That mask is doing something! Try it on that cracked floor!"
  - Level 2-2: Aqueduct run. Vertical platforming chains with wall jumps. Stone Slam opens paths through cracked aqueduct sections. Tax collectors add economic pressure.
  - Level 2-3: Roman camp. Shield formations demand Stone Slam mastery — shockwave is the most efficient way through packed legionaries. Wave arena tests crowd management.
  - Level 2-4: Amphitheater approach. All enemy types mixed. Stone Slam + sling charge combinations for maximum efficiency.
  - Boss: Chariot requires wall jump to dodge, sling mastery for damage. Stone Slam scatters legionary reinforcements in phase 3. **Post-boss: Double Jump earned.**
- **Difficulty arc**: 3 -> 4 -> 5 -> 6 -> 6 (boss)
- **Relief valves**: Shop fully stocked with consumables. Ensaimadas cheap. Llorenc fully introduced.

#### World 3 -- El Comte Mal
- **Entering knowledge**: Full moveset + Stone Slam
- **Available masks**: Stone Slam + Double Jump (earned post-W2 boss)
- **New skill to master**: Double Jump applied to gothic vertical spaces
- **Teaching structure**:
  - Level 3-1: Dark corridors and eerie forest. Double Jump introduced in this context — a tall tree canopy section requires it. Gothic atmosphere with strange fires foreshadowing the imprisoned dimoni.
  - Level 3-2: Abandoned village with church tower. Vertical church tower climb demands Double Jump mastery. Catacomb exploration uses Stone Slam for breakable floors. La Bruixa cutscene foreshadows the imprisoned dimoni.
  - Level 3-3: Comte's outer estate. Claustrophobic interiors with trap-heavy corridors. Double Jump is critical for escaping ceiling traps and reaching chandelier platforms. Tight corridors demand precision.
  - Level 3-4: Inner tower. Dark vertical ascent. Double Jump + wall jump chains for the tightest platforming yet. Bat gauntlets while climbing. Audio cues critical.
  - Boss: Tests timing, pattern recognition, charged sling accuracy. Double Jump to chandelier platforms to dodge attacks. **Post-boss: Fire Dash earned.**
- **Difficulty arc**: 5 -> 5 -> 6 -> 7 -> 7 (boss)
- **Relief valves**: Herbes Liqueur and Oli d'Oliva now available. Dark atmosphere is tense but enemy density is lower.

#### World 4 -- Els Pirates
- **Entering knowledge**: Full moveset + Stone Slam + Double Jump
- **Available masks**: Stone Slam + Double Jump + Fire Dash (earned post-W3 boss)
- **New skill to master**: Fire Dash applied to pirate/coastal environments
- **Teaching structure**:
  - Level 4-1: Coastal watchtower. Fire Dash taught here — a wooden barricade blocks the path, burning debris litters the coast. Dash through both. A water gap between the shore and a docked ship is the first "dash across water" moment. Bep: "That fire power! Try it on that wooden wall!"
  - Level 4-2: Burning village. Fire Dash through burning debris (invulnerability frames), across rooftop gaps between buildings, through pirate wooden fortifications. Sniper gauntlets test dash timing.
  - Level 4-3: Pirate cove. Ship interiors with wooden barricades. Fire Dash essential for clearing paths. Powder monkey bomb zones encourage dash-and-retreat tactics.
  - Level 4-4: Boarding Dragut's flagship. Dash across water gaps between rowboats. Burn through ship hull barricades. Combined combat/platforming gauntlet.
  - Boss: Shore-to-ship transition. Fire Dash across water gaps during boarding. Dash through cannon debris. **Post-boss: Smoke Vanish earned.**
- **Difficulty arc**: 5 -> 6 -> 7 -> 7 -> 8 (boss)
- **Relief valves**: Frozen Rock ammo slows tough enemies. Aigua de Font for panic moments.

#### World 5 -- S'Invasio
- **Entering knowledge**: All prior moveset + 3 masks
- **Available masks**: Stone Slam + Double Jump + Fire Dash + Smoke Vanish (earned post-W4 boss)
- **New skill to master**: Smoke Vanish applied to modern crowd/stealth challenges
- **Teaching structure**:
  - Level 5-1: Magaluf strip. Smoke Vanish taught here — thick tourist crowds block the path, phasing through them is the "aha!" moment. Influencer camera flashes create detection cones — vanishing through them is immediately intuitive. Bep: "We can go right through them?! That's sneaky, Balchar!"
  - Level 5-2: Palma airport. "Staff Only" doors (thin walls) accessible via Smoke Vanish. Conveyor belt platforming. Dense enemy groups where vanish repositioning is key.
  - Level 5-3: Beach resort. Influencer stun mechanics demand Smoke Vanish to dodge flash cones. Party bus hazards. Indoor sections with no escape room force creative vanish usage.
  - Level 5-4: Hotel construction site. Vertical scaffolding climb. All 4 masks useful in combination — Stone Slam through floors, Double Jump up scaffolding, Fire Dash through barricades, Smoke Vanish past security cameras.
  - Boss: Vanish through lawyer swarms, phase through golden beam attacks. **Post-boss: Tourist Rage earned.**
- **Difficulty arc**: 6 -> 7 -> 7 -> 8 -> 8 (boss)
- **Relief valves**: Smoke Vanish itself IS the relief valve for crowd pressure (phase through instead of fighting). Full shop inventory.

#### World 5.5 -- Eivissa (Endgame)
- **Entering knowledge**: ALL masks
- **Available masks**: All 5 masks + quick-swap unlocked at start
- **New skill to master**: Tourist Rage for crowd control + real-time mask swapping
- **Teaching structure**:
  - Level 5.5-1: Nightclub ruins. Tourist Rage taught first — bottle imp swarm at the entrance. Then rapid mask-test sections: slam a floor, double jump a shaft, dash a gap, vanish a wall, rage a swarm. Each section teaches quick-swap rhythm.
  - Level 5.5-2: Mega-resort interior. Longer mixed sections requiring mid-combat mask swaps. Neon fameliars and VIP fameliars test different approaches. Tourist Rage essential for familiar density.
  - Level 5.5-3: Rooftop ascent to Magnat's penthouse. Hardest platforming in the game. All mask powers needed. Tourist Rage clears familiar clusters that block the climb.
  - Boss: Multi-phase endgame test of everything learned. Phase 3 cycles through attacks requiring specific masks.
- **Difficulty arc**: 8 -> 9 -> 9 -> 10 (boss)
- **Relief valves**: Full shop available before each level. Sobrassada Pot and Aigua de Font recommended. Economy should have ample reserves for thorough players.

### 5.2 Common World Template

**[REVISED v3.0]** Worlds 2-5 follow a repeating structure so the game feels familiar but fresh:

1. **Arrival**: Bep's portal drops Balchar and Bep into the new era. Cutscene: Balchar reacts to the setting, Bep is excited.
2. **Dimoni foreshadowing** *(optional, narrative only)*: Early in the world, environmental hints suggest a dimoni's presence — strange energy, atmospheric disturbances, Bep sensing something. The dimoni may appear briefly (a shadow, a voice) but does NOT grant any mask. This builds anticipation for the post-boss reward.
3. **Levels**: 4 platforming/combat levels with increasing difficulty. Levels 1-2 teach the player how the **newest available mask** (earned from the previous world's boss) applies to this world's theme. Levels 3-4 demand mastery of combining all available masks. Each level ends at a save point where Llorenc may appear.
4. **Boss**: Final level is the boss encounter. Preceded by a boss intro cutscene. Boss tests the player's full available toolkit (all masks from previous worlds).
5. **Post-boss dimoni reward**: After the boss is defeated, the local dimoni appears (or is freed). Brief dialogue — impressed, grateful, or grudging. Grants its mask to Llorenç. This is the emotional climax of the world: victory + new power.
6. **Transition**: Bep's curse activates. Time portal. Next world — where the newly earned mask awaits.

**World 1 breaks this template** (no prior masks, no dimoni encounter until post-boss, the time-travel reveal is the twist).
**World 5.5 breaks this template** (geographic jump, no new mask earned, 3 levels + boss, endgame).

---

### 5.3 World 1 -- Sa Talaia (Talayotic Period, ~1000 BC)

- **Setting**: Rocky Mediterranean landscape. Talayots, taulas, navetas. Blue sky, dry stone, olive trees, coastal cliffs. Bronze-age Mallorca.
- **Color palette**: Warm earth tones -- ochre, stone grey, olive green, Mediterranean blue.
- **Enemies**: Possessed sheep, rival tribal warriors, stone guardians.
- **Available masks**: **None.** World 1 is the pure tutorial — movement, jumping, wall jumping, and sling combat only. No mask powers complicate the learning curve.
- **Mask earned post-boss**: Stone Slam (Mask of Sant Joan) — the dimoni de Sant Joan appears after Es Bou de Pedra is defeated, grants the mask to Llorenç (who the player will meet at the start of W2).

#### Level 1-1: "Es Primer Pas" (The First Step)
- **Layout**: Horizontal. Open Mediterranean landscape with gentle slopes, low cliffs, and olive trees. A coastal path leading to a stone village.
- **Difficulty**: 1/10
- **Enemy composition**: None in the first half. 2-3 possessed sheep in the second half (the gentlest enemy -- slow, telegraphed charge).
- **Platforming challenges**: Simple gaps (2-3 tile wide). Low walls requiring jump. One slightly taller cliff introducing wall jump context (optional path, main path goes around).
- **Collectibles**: 15-20 sling stones in breakable pots and tall grass. 1 heart pickup near the end. 0 secrets (pure tutorial).
- **Teaching beats**:
  - Bep teaches movement: "Balchar! Move! The sheep are acting strange!"
  - First gap: Bep says "Jump, Balchar! You've done it a thousand times!"
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
- **Layout**: Vertical. A massive talayot interior. Climb upward through stone chambers.
- **Difficulty**: 3/10
- **Enemy composition**: 3 possessed sheep, 2 tribal warriors, 1 stone guardian (first encounter -- slow but hits hard, teaches dodging heavy enemies).
- **Platforming challenges**: Vertical shaft requiring wall jumps (mandatory -- the level forces it). Narrow passages that test jump precision. A section with alternating platforms and enemy pressure from below.
- **Collectibles**: 25-30 sling stones. 2 heart pickups. 1 secret: a side chamber behind breakable rocks (10 bonus stones). **Retroactive secret**: A cracked floor visible but not breakable with any current ability — requires Stone Slam (post-W1 boss) on replay.
- **Teaching beats**:
  - Vertical shaft: Bep says "We need to go UP! Try jumping off the walls!"
  - Wall jump section is narrow enough that it's hard to fail -- forgiving geometry.
  - Stone guardian encounter: "That one's big! Watch out for its swing!"
  - Cracked floor tease: Bep says "The ground here looks crumbly... but nothing happens when we jump on it." This plants the seed for returning with Stone Slam later.
- **End**: Save point. Proto-shop opens (a mysterious stone pedestal offering basic ensaimadas).

#### Level 1-4: "Sa Porta des Bou" (The Gate of the Bull)
- **Layout**: Mixed horizontal and vertical. An outdoor approach to the boss arena through a ruined sanctuary. Combines all prior terrain types.
- **Difficulty**: 4/10
- **Enemy composition**: 3 possessed sheep, 3 tribal warriors, 2 stone guardians. Enemies are placed in combinations for the first time (warrior + sheep, guardian + sheep).
- **Platforming challenges**: A gauntlet section: wall jump up a cliff, cross a wide gap, navigate a narrow cave with enemies. Tests all acquired movement skills.
- **Collectibles**: 30-35 sling stones (generous before the boss). 2 heart pickups. 1 secret: a hidden cave behind a destructible wall with 15 bonus stones and a free ensaimada.
- **Teaching beats**:
  - Pre-boss area: Bep says "Something feels wrong here... the ground is shaking."
  - The combined enemy encounters teach the player to prioritize targets.
  - A wide open area before the boss door serves as a "calm before the storm."
- **End**: Boss gate. Dramatic visual change -- stone pillars, bull iconography.

#### Boss: Es Bou de Pedra
*(Full details in Section 6)*

- **Story beat (post-boss)**: The reveal. Es Bou de Pedra crumbles. The dimoni de Sant Joan appears — dramatic, vindictive, but grudgingly impressed. "You destroyed my guardian, you fool. Take this, before something worse finds you." Grants the Stone Slam mask to Llorenç (who arrives via the time portal's pull — this is a compressed narrative beat). Then Bep glows, sneezes, portal opens. Balchar and Bep are pulled into the portal. The game's real premise begins. **Stone Slam is now permanently available from World 2 onward.**

---

### 5.4 World 2 -- Mallorca Romana (Roman Conquest, 123 BC)

- **Setting**: Roman roads cutting through Mallorcan landscape. Amphitheaters, legionary camps, early Palma (Palmaria). Aqueducts, columns, ordered architecture.
- **Color palette**: Stone white, imperial red, laurel green, marble grey.
- **Enemies**: Roman legionaries (shield formations), war dogs, tax collectors.
- **Available masks**: **Stone Slam** (earned post-W1 boss). Especially relevant here — Roman shield formations crumble under the shockwave, stone architecture breaks open to reveal shortcuts.
- **Mask earned post-boss**: Double Jump (Mask of Manacor). Given by Es Dimoni de Manacor after Metellus is defeated.
- **Llorenc introduction**: Appears at the start of this world. Has been tracking the time disturbance. Excited to meet Balchar. Balchar is not excited. Shop mechanic fully introduced here with personality and lore. Llorenc now holds the Stone Slam mask — Balchar equips it at the shop.

#### Level 2-1: "Sa Via Nova" (The New Road)
- **Layout**: Horizontal with a tall vertical section midway. Roman road leading to a newly built settlement. The vertical section is a Roman atrium with multi-level platforms.
- **Difficulty**: 3/10
- **Enemy composition**: 3 legionaries (first encounter -- shield blocks frontal attacks), 2 war dogs. Legionaries placed to teach "Stone Slam breaks their formation" and "attack from above or behind."
- **Platforming challenges**: First section uses single jump + wall jump through Roman structures. A cracked Roman floor at the atrium entrance — Stone Slam reveals a shortcut below. High ledges in the atrium hint at future vertical potential (not reachable yet — tease for Double Jump later).
- **Collectibles**: 25-30 sling stones. 1 heart pickup. 1 secret: beneath a cracked atrium floor accessible only with Stone Slam (10 bonus stones — teaches that the mask opens new exploration).
- **Teaching beats**:
  - World arrival cutscene: Balchar: "Who paved over my goat path?"
  - Llorenc introduction and shop tutorial. Llorenc gives Balchar the Stone Slam mask.
  - First cracked floor: Bep says "Remember that crumbly floor feeling? This mask might help!"
  - First legionary: Bep says "His shield blocks everything! That ground-pound might scatter them!"
  - Stone Slam shockwave vs. shield formation: the key "aha!" moment for the mask's combat utility in this world.
- **End**: Save point with Llorenc shop.

#### Level 2-2: "S'Aqeducte" (The Aqueduct)
- **Layout**: Primarily vertical. A massive Roman aqueduct stretching across a valley. Player climbs the aqueduct structure, runs along the top, and navigates water channels.
- **Difficulty**: 4/10
- **Enemy composition**: 4 legionaries (some on narrow aqueduct platforms -- tight spaces make shield problem harder), 3 war dogs (running along the top of the aqueduct), 1 tax collector.
- **Platforming challenges**: Vertical climbing up the aqueduct's arches (wall jump chains). Moving water platforms along the channel on top. A section where the aqueduct crumbles and the player must jump between falling segments. A cracked aqueduct floor — Stone Slam reveals a hidden chamber below with treasure.
- **Collectibles**: 30-35 sling stones (many in water channel). 2 heart pickups. 1 secret: inside the aqueduct's base, accessible by Stone Slam through a cracked floor (20 bonus stones — reinforces the mask's exploration utility).
- **Teaching beats**:
  - The crumbling aqueduct section teaches urgency -- platforms disappear after a few seconds.
  - Tax collector: first encounter. Bep: "He stole your rocks! Chase him!" (teaches that these enemies are a priority target or an avoidance challenge).
  - Stone Slam through aqueduct floor: "There's a whole room down there!"
- **End**: Save point with Llorenc shop.

#### Level 2-3: "Es Campament Roma" (The Roman Camp)
- **Layout**: Horizontal. A sprawling Roman military camp with tents, barricades, and training grounds. More combat-focused than platforming.
- **Difficulty**: 5/10
- **Enemy composition**: 5 legionaries (including 2 in shield formation -- side by side, requiring Stone Slam shockwave to scatter or careful flanking), 4 war dogs (in packs for the first time), 2 tax collectors.
- **Platforming challenges**: Barricade walls requiring wall jump. A training ground arena where enemies spawn in waves (first wave encounter). Tent rooftops as platforms. Stone column that can be shattered with Stone Slam to create a stepping platform across a wide gap.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: behind a tent row, a hidden path with 15 stones and an ensaimada.
- **Teaching beats**:
  - Shield formation: "They're standing together! That ground-pound scatters them, Balchar!"
  - Wave arena: teaches crowd management -- Stone Slam shockwave is the key tool for groups.
  - War dog packs: teach prioritizing fast enemies (dogs are low to ground, Stone Slam less effective — forces sling usage).
  - Stone column destruction: teaches that Stone Slam creates traversal options, not just combat advantages.
- **End**: Save point with Llorenc shop.

#### Level 2-4: "S'Amfiteatre" (The Amphitheater)
- **Layout**: Mixed. An approach road leading to a grand amphitheater. The level is a gauntlet -- continuous forward momentum with escalating challenges.
- **Difficulty**: 6/10
- **Enemy composition**: 4 legionaries, 3 war dogs, 2 tax collectors, 1 stone guardian (returning from W1 -- appears in Roman armor, slightly faster). All enemy types mixed in combinations.
- **Platforming challenges**: Multi-tiered amphitheater seating to climb (wall jumps). A collapsing stairway. A section requiring precise jump timing over a pit with legionaries at the landing (must fight immediately after landing). Stone Slam through the amphitheater floor reveals a hidden underground chamber.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: under the amphitheater floor, accessible by Stone Slam (25 stones, a sobrassada pot).
- **Teaching beats**:
  - Enemy combinations ramp up: "They're everywhere! Use everything you've learned!"
  - Pre-boss corridor: calm, atmospheric. Roman banners, torches. Builds tension.
  - Optional Llorenc dialogue: "The general Metellus conquered these islands in 123 BC. Brilliant tactician. You'll be fine." Balchar: "Inspiring."
- **End**: Boss gate. Amphitheater center stage.

#### Boss: Quintus Caecilius Metellus
*(Full details in Section 6)*

- **Story beat (post-boss)**: Metellus falls. The dimoni de Manacor emerges from the shadows of the amphitheater — intense, impatient. "Finally. These organized fools have been stifling my territory for too long. Take this before the next era's problems find you." Grants Double Jump mask to Llorenç. Bep glows. Portal opens. **Double Jump is now permanently available from World 3 onward.**
- **Llorenc**: "Technically it's a road, and it's quite well-eng--" Balchar: "I didn't ask."

---

### 5.5 World 3 -- El Comte Mal (Feudal Mallorca, Legend-Based)

- **Setting**: Dark feudal Mallorca. The Comte Mal's cursed estates, oppressed villages, gothic manor, eerie forests. Torchlit stone corridors, strange fires burning in the hills.
- **Color palette**: Dark -- charcoal, blood red, sickly green, candlelight orange. Highest contrast of any world.
- **Enemies**: Undead servants, vampire bats, cursed villagers.
- **Available masks**: **Stone Slam + Double Jump** (from W1-W2). Double Jump is especially relevant here — gothic towers demand vertical navigation, ceiling traps require aerial escape, chandelier platforms need a second jump to reach.
- **Mask earned post-boss**: Fire Dash (Mask of Fire). The imprisoned dimoni is freed when the Comte Mal is defeated and grants its mask. The dimoni's power is foreshadowed throughout W3 via strange fires, leaking energy, and La Bruixa's binding rituals.
- **La Bruixa**: Appears in cutscenes. She is a pawn -- manipulated by the Comte -- not an enemy. NOT a gameplay encounter.

#### Level 3-1: "Es Bosc Maleït" (The Cursed Forest)
- **Layout**: Horizontal with narrow paths. An eerie forest with gnarled trees, hanging moss, and strange green firelight. Paths wind through dense foliage.
- **Difficulty**: 5/10
- **Enemy composition**: 4 undead servants (slow, persistent -- teach patience), 3 vampire bats (first encounter -- swoop from above, teach looking up). Placed to create atmosphere: undead emerge from the ground, bats drop from trees.
- **Platforming challenges**: Narrow branch platforms. Moving log bridges over dark pits. A tall tree canopy section with platforms at different heights — Double Jump is needed to reach the upper path (which has better rewards). A wall jump + Double Jump chain to reach a high branch with a heart pickup.
- **Collectibles**: 25-30 sling stones. 2 heart pickups. 1 secret: behind a cluster of trees, a hidden glade with 15 stones (accessible from any world revisit).
- **Teaching beats**:
  - World arrival cutscene: Dark, ominous. Balchar: "...This is worse." Bep: "I like the trees!" (a bat swoops past) "I don't like the trees!"
  - Undead servants: Bep says "They keep getting back up!" (they take 2 hits to kill -- teaches persistence in combat).
  - Vampire bats: swoop with a visible shadow on the ground beforehand -- teaches looking for visual cues.
  - Tree canopy: "We can jump AGAIN in the air now! This is amazing!" — teaches Double Jump application in gothic vertical environment.
  - Strange fires in the background foreshadow the imprisoned dimoni's leaking power.
- **End**: Save point with Llorenc shop. Llorenc: "The legends say the Comte Mal sold his soul. In Menorca we have better taste in—" Balchar: "Llorenc."

#### Level 3-2: "Es Poble Perdut" (The Lost Village)
- **Layout**: Mixed horizontal and vertical. An abandoned village with collapsed buildings, a church tower, and underground catacombs.
- **Difficulty**: 5/10
- **Enemy composition**: 3 undead servants, 4 vampire bats, 2 cursed villagers (first encounter -- erratic, unpredictable movement patterns, teaches reactive combat).
- **Platforming challenges**: Church tower climb (vertical — Double Jump + wall jump chain required, the first real vertical challenge demanding the new mask). Catacomb section with collapsing floor tiles. Rooftop platforming across the village (one-way platforms on thatched roofs). Stone Slam on catacomb floors reveals hidden chambers.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: in the catacombs, a hidden chamber accessible by Stone Slam (20 stones, an oli d'oliva).
- **Teaching beats**:
  - Church tower climb: the definitive Double Jump teaching moment. The tower is tall, narrow, and requires precise Double Jump + wall jump combos. Bep: "Keep going up! I think I can see something at the top!"
  - Cursed villagers: erratic movement contrasts the predictable undead. Bep: "That one moves funny... careful, Balchar!"
  - Collapsing floors: visual cue (dust particles from cracks). Teaches observation.
  - La Bruixa cutscene: spotted from a distance performing a ritual. Sets up the imprisoned dimoni story.
- **End**: Save point with Llorenc shop.

#### Level 3-3: "Sa Finca del Comte" (The Comte's Estate)
- **Layout**: Claustrophobic interiors. The Comte's outer estate -- stables, servant quarters, trap-laden corridors. Tight spaces, low ceilings, many hazards.
- **Difficulty**: 6/10
- **Enemy composition**: 4 undead servants, 3 vampire bats, 3 cursed villagers. Enemies appear in tighter spaces, making combat more dangerous.
- **Platforming challenges**: Spike pit corridors (timing-based). Collapsing floor chains (step on one, the next starts crumbling). A chandelier-swinging section over a great hall — Double Jump to reach chandelier platforms, then jump between them. A gauntlet corridor where the player must use Stone Slam to break through crumbling walls while bats swoop from above. A ceiling trap section where the ceiling descends — Double Jump provides the vertical clearance to escape.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: behind a wooden barricade near the level start (requires Fire Dash from W3 boss — retroactive replay secret only).
- **Teaching beats**:
  - Tight corridors: teach careful movement. Rushing gets you hit by traps.
  - Chandelier section: Double Jump mastery. The chandeliers are just out of single-jump reach — must Double Jump to each one.
  - Ceiling trap: "The ceiling's coming down! Jump higher, Balchar!" Double Jump is the escape.
  - Multiple trap types layer together: spikes + bats = precision under pressure.
  - Strange fire in the estate's hearths burns unnaturally. Bep: "That flame felt alive! Like it wanted to help us!" Foreshadows the dimoni.
- **End**: Save point with Llorenc shop.

#### Level 3-4: "Sa Torre Fosca" (The Dark Tower)
- **Layout**: Vertical. The Comte's inner tower. Dark, oppressive. Ascending toward the great hall (boss arena). Most trap-dense level so far.
- **Difficulty**: 7/10
- **Enemy composition**: 3 undead servants, 5 vampire bats (positioned along vertical ascent), 3 cursed villagers. Heavy bat presence makes climbing treacherous.
- **Platforming challenges**: Spiral ascent with crumbling platforms. Bat gauntlets while wall jumping. A section with extinguishing/relighting torches (dark sections where you can only see Balchar's outline). A challenging vertical gap requiring precise Double Jump + wall jump chain (the tightest platforming in W3, demanding mastery of the skill). A wide pit that hints at a future horizontal traversal power (unreachable now — tease for Fire Dash).
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: a side room behind a thin wall (visible but requires Smoke Vanish from W4 to access -- retroactive replay secret).
- **Teaching beats**:
  - Dark sections: audio cues become important (enemy footsteps, bat screeches). Teaches listening.
  - The dimoni's power leaks more visibly as the player ascends: Bep: "The fire's getting stronger! Something's trapped up there!" Foreshadows the boss encounter.
  - Pre-boss atmosphere: the tower grows darker, the music changes, strange fire flickers from above.
  - Wide pit tease: "That gap is huge! There must be another way..." (Hints at future Fire Dash ability.)
- **End**: Boss gate. The great hall doors.

#### Boss: El Comte Mal
*(Full details in Section 6)*

- **Story beat (post-boss)**: After defeat, the imprisoned dimoni is freed. Its chains shatter, fire erupts joyfully. The dimoni — weakened but grateful — hands its mask to Llorenc. "Keep it away from the sheep." **Fire Dash now permanently available from World 4 onward.** All wooden barricades and wide gaps in W1-W3 can be cleared on revisit.

---

### 5.6 World 4 -- Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)

- **Setting**: Coastal Mallorca under siege. Watchtowers, burning fishing villages, pirate ships anchored offshore, hidden coves, moonlit beaches.
- **Color palette**: Midnight blue, sand gold, fire orange, dark wood brown. Moonlit and atmospheric.
- **Enemies**: Scimitar pirates, musket snipers, powder monkeys.
- **Available masks**: **Stone Slam + Double Jump + Fire Dash** (from W1-W3). Fire Dash is especially relevant here — wooden pirate ships and barricades burn, water gaps between boats demand horizontal dashing, and the coastal environment rewards speed and aggression.
- **Mask earned post-boss**: Smoke Vanish (Mask de Pollenca). Given by Es Dimoni de Pollenca after Dragut is defeated.

#### Level 4-1: "Sa Torre de Guaita" (The Watchtower)
- **Layout**: Mixed. A coastal watchtower and the surrounding cliffs. Starts on the moonlit beach, climbs the watchtower, overlooks pirate ships below.
- **Difficulty**: 5/10
- **Enemy composition**: 3 scimitar pirates (first encounter -- melee rushers, aggressive, fast), 2 musket snipers (first encounter -- stationary, ranged, positioned on tower levels). Relatively light enemy density to let the player absorb the new setting.
- **Platforming challenges**: Beach-to-tower climb using cliff faces and tower windows. A wooden barricade blocks the tower stairway — Fire Dash burns right through it (first teaching moment for the new mask in this world's context). A water gap between the shore and a docked ship — dash across. Narrow watchtower interior with sniper sightlines (cover-based platforming).
- **Collectibles**: 25-30 sling stones. 1 heart pickup. 1 secret: inside a sealed room behind a wooden door that Fire Dash burns through (15 bonus stones — reinforces the mask's utility in this world).
- **Teaching beats**:
  - World arrival: "First Romans, then a vampire, now pirates. Is there a single century where people leave this island alone?" Bep: "I think they like it here! I like it here too!" Balchar: "You like everything."
  - Wooden barricade: Bep says "That's a wooden wall! Remember that fire power?" Player uses Fire Dash to burn through — instant satisfaction.
  - Water gap: "We can't swim... but can we dash across?!" First water-gap Fire Dash. The invulnerability frames carry Balchar over the water.
  - Sniper sightline: snipers positioned on ledges. Fire Dash can close distance rapidly, or player can use cover.
  - Dimoni de Pollenca foreshadowing: moonlit shadows move strangely near the watchtower base. A whisper in the wind.
- **End**: Save point with Llorenc shop.

#### Level 4-2: "Es Poble Cremat" (The Burning Village)
- **Layout**: Horizontal. A coastal fishing village under pirate attack. Burning buildings, fleeing NPCs, chaos. Dynamic level with fire hazards.
- **Difficulty**: 6/10
- **Enemy composition**: 5 scimitar pirates, 3 musket snipers (on rooftops), 2 powder monkeys (first encounter -- throw timed bombs that explode after 2 seconds, area denial).
- **Platforming challenges**: Rooftop running across burning buildings (some roofs collapse). Fire Dash through burning debris sections (invulnerability frames make Balchar immune to fire during the dash). Sniper gauntlets along streets — Fire Dash to close distance or use cover. A dock section with swinging ropes between boats. Wooden pirate fortifications blocking paths — Fire Dash burns through all of them.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: inside a collapsed house, accessible by Stone Slam through the floor then Fire Dash through debris (combination of W1 + W3 powers). 20 stones inside.
- **Teaching beats**:
  - Powder monkeys: Bep says "That little one threw something! Run! RUN!" Teaches bomb avoidance timing.
  - Fire Dash through burning debris: "We can dash RIGHT THROUGH the fire?!" The invulnerability frames during dash make fire hazards traversable.
  - Burning building rooftops: visual urgency (fire rising) teaches speed. Collapse timing is generous enough on first attempts.
  - Wooden fortification destruction: Fire Dash is the primary path-clearing tool in this world.
- **End**: Save point with Llorenc shop.

#### Level 4-3: "Sa Cala des Corsaris" (The Corsair's Cove)
- **Layout**: Mixed horizontal and vertical. A hidden pirate cove with ship interiors, cave networks, and an underwater grotto (no swimming -- stone platforms over water).
- **Difficulty**: 7/10
- **Enemy composition**: 4 scimitar pirates, 3 musket snipers (in ship rigging), 4 powder monkeys (increased presence -- bomb zones become more frequent). First combined encounters: pirates advance while powder monkeys lob bombs from behind.
- **Platforming challenges**: Ship interior navigation (tight corridors, swinging lanterns as hazards — Fire Dash through wooden internal walls). Cave system with one-way platforms over water. Water gaps between cave sections and ships require Fire Dash. A vertical climb up a cliff face with snipers shooting from adjacent ship masts — Double Jump for vertical escape, Fire Dash for horizontal repositioning.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: behind a thin wall inside the cave (visible shimmer — requires Smoke Vanish from W4 boss, retroactive secret). Contains 20 stones and a frozen rock pack.
- **Teaching beats**:
  - Combined enemy tactics: "They're working together!" Pirates push forward while bombs deny retreat. Fire Dash through the pirate line to escape the bomb zone.
  - Ship interiors: wooden walls everywhere. Fire Dash turns the confined spaces into advantages — dash through walls to flank enemies.
  - Cave grotto: atmospheric calm before the storm. Beautiful parallax backgrounds contrast the violence above.
- **End**: Save point with Llorenc shop.

#### Level 4-4: "S'Abordatge" (The Boarding)
- **Layout**: Horizontal. A direct assault on Dragut's flagship from shore. Beach, rowboats as platforms, ship hull, deck.
- **Difficulty**: 7/10
- **Enemy composition**: 5 scimitar pirates, 4 musket snipers, 3 powder monkeys. Heaviest enemy density yet. Pirates attack in pairs.
- **Platforming challenges**: Rowboat hopping (small moving platforms on waves — Fire Dash across larger water gaps between boats). Ship hull climbing (vertical, with pirates kicking down barrels as hazards — Double Jump for vertical repositioning). Deck approach with combined sniper fire and melee rushers — Fire Dash through the melee line, then sling the snipers.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the ship's hold, accessible by Stone Slam through the deck (25 stones, an ensaimada).
- **Teaching beats**:
  - Rowboat section: teaches precision platforming on small, moving surfaces. Fire Dash bridges the wider gaps.
  - Ship hull climbing: combines vertical platforming with enemy hazards -- everything the player has learned.
  - Deck approach: the gauntlet before the boss. Intense, fast-paced, but with clear forward momentum.
- **End**: Boss gate. Dragut's captain's cabin at the ship's stern.

#### Boss: Dragut
*(Full details in Section 6)*

- **Story beat (post-boss)**: Dragut falls. The dimoni de Pollença emerges from the moonlit shadows — sneaky, whisper-voiced. "Finally quiet. Those pirates were insufferable. Take this — perhaps it will teach you to be subtle." Grants Smoke Vanish mask to Llorenç. Portal opens. **Smoke Vanish is now permanently available from World 5 onward.** Dragut: "You fight well for a man from the rocks." Balchar: "Everyone on this island fights well. That's why you keep losing."

---

### 5.7 World 5 -- S'Invasio (Modern Day)

- **Setting**: Modern Mallorca. Magaluf strip, Palma airport, overcrowded beaches, "Se Vende" signs on every traditional house, luxury yachts, concrete hotels built over historic sites.
- **Color palette**: Oversaturated -- neon pink, tourist-brochure blue, concrete grey, gold (money). Garish and loud, contrasting all previous worlds.
- **Enemies**: Aggressive tourists, real estate agents, influencers, party buses (environmental hazard).
- **Available masks**: **Stone Slam + Double Jump + Fire Dash + Smoke Vanish** (from W1-W4). Smoke Vanish is especially relevant here — phase through tourist crowds, dodge influencer camera flashes, sneak into restricted areas, bypass overwhelming modern obstacles.
- **Mask earned post-boss**: Tourist Rage (Mask of Sa Pobla). Given by Es Dimoni de Sa Pobla after El Magnat Phase 1 is defeated.

#### Level 5-1: "Sa Platja de s'Infern" (Hell's Beach)
- **Layout**: Horizontal. The Magaluf beachfront strip. Wide, open spaces packed with enemies. The widest level design in the game to accommodate crowds.
- **Difficulty**: 6/10
- **Enemy composition**: 8-10 tourists (swarms -- first encounter with large groups), 2 influencers (first encounter -- camera flash stun in a cone in front of them), 1 party bus pass (environmental).
- **Platforming challenges**: Minimal platforming. This is a crowd-navigation level. Beach umbrella hopping. Hotel pool as a pit hazard. Party bus crosses the screen periodically (telegraphed by engine sound and screen edge indicator). Tourist crowds form walls — Smoke Vanish phases right through them.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: inside a beach shack, accessible by Stone Slam through the floor (15 stones).
- **Teaching beats**:
  - Arrival cutscene: Balchar sees modern Mallorca. "...I think I preferred the pirates." Bep: "What's a hotel?" Balchar: "Where they charge you to sleep." Bep: "You can sleep anywhere!" Balchar: "...I know, Bep."
  - Tourist crowd wall: Bep says "There's too many of them! Maybe we can sneak through?" Player uses Smoke Vanish to phase through the crowd — instant relief, no combat needed.
  - Influencer: camera flash creates a visible cone. Smoke Vanish phases through the stun effect entirely. "We went invisible! Their magic box can't see us!"
  - Dimoni de Sa Pobla foreshadowing: hotel foundations disturb ancient sites. Strange energy pulses from underground.
  - Party bus: Bep screams before it appears. "WHAT IS THAT THING?!"
- **End**: Save point with Llorenc shop. Llorenc: "Fascinating. In Menorca, tourism is more... dignified." Balchar: "Is it." Llorenc: "...No."

#### Level 5-2: "S'Aeroport" (The Airport)
- **Layout**: Horizontal with conveyor sections. Palma airport interior. Conveyor belts as moving platforms, luggage carousels as hazards, boarding gates as checkpoints.
- **Difficulty**: 7/10
- **Enemy composition**: 6 tourists, 3 real estate agents (first encounter -- chase relentlessly with contracts, faster than tourists, take 3 hits), 2 influencers.
- **Platforming challenges**: Conveyor belt platforming (belts move in different directions, requiring adjustment). Luggage carousel section (rotating platforms with suitcases as obstacles). Escalator sections (moving platforms that speed up/slow down). "Staff Only" doors — thin walls that Smoke Vanish phases through, providing shortcuts and secrets.
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: behind a "Staff Only" door (thin wall, Smoke Vanish). 20 stones inside.
- **Teaching beats**:
  - Real estate agents: aggressive pursuers. Bep: "He wants you to sign something! DON'T SIGN ANYTHING!" Smoke Vanish phases through their grab attempts.
  - Conveyor mechanics: some belts help, some hinder. Teaches reading the environment.
  - "Staff Only" doors: Smoke Vanish utility for bypassing modern access control. Feels like a superpower in a mundane setting.
  - Airport PA system announcements serve as ambient comedy: "Flight to Menorca delayed. Llorenc, your cow is blocking the terminal."
- **End**: Save point with Llorenc shop.

#### Level 5-3: "Es Resort" (The Resort)
- **Layout**: Mixed horizontal and vertical. A massive beach resort complex. Pool areas, hotel lobbies, rooftop bars. Combines indoor and outdoor sections.
- **Difficulty**: 7/10
- **Enemy composition**: 6 tourists, 3 real estate agents, 3 influencers (camera flash becomes more dangerous in indoor areas with no escape room), 2 party bus passes (outdoor sections).
- **Platforming challenges**: Pool-hopping (fall in = damage, like pit hazards). Hotel balcony climbing (vertical sections — Double Jump essential). Rooftop bar with breakable furniture and neon signs as platforms. Indoor influencer encounters in tight spaces where Smoke Vanish is the primary escape tool.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the hotel basement, accessible by Stone Slam from the lobby floor (25 stones, a sobrassada pot).
- **Teaching beats**:
  - Indoor influencer encounters: tight spaces make the camera flash harder to avoid. Smoke Vanish essential — phase through the flash and get behind the influencer.
  - Balcony climbing: tests Double Jump + wall jump in a modern architecture context.
  - Rooftop bar: chaotic combat arena with all 4 masks usable. Tables break, neon signs fall. Environmental destruction as comedy.
- **End**: Save point with Llorenc shop.

#### Level 5-4: "Sa Grua" (The Crane)
- **Layout**: Vertical. Climbing a hotel under construction via scaffolding, cranes, and unfinished floors. The approach to El Magnat's penthouse.
- **Difficulty**: 8/10
- **Enemy composition**: 5 tourists, 4 real estate agents, 2 influencers, 1 party bus (drives across an unfinished floor). High density, mixed types.
- **Platforming challenges**: Scaffolding platforming (narrow, some sections collapse). Crane arm as a moving platform (swings slowly, player must time jumps). Unfinished floors with gaps (Double Jump + Fire Dash). Wind gusts on upper floors push Balchar sideways (new environmental hazard). This is the "all masks" showcase — Stone Slam through floors, Double Jump up scaffolding, Fire Dash through barricades, Smoke Vanish past security cameras.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: inside the crane cabin (requires Fire Dash through a metal barricade). 25 stones and an aigua de font.
- **Teaching beats**:
  - Construction site: everything is unstable. The level reinforces careful platforming.
  - Crane section: dramatic set piece. Wind + moving platform + enemies = peak difficulty before boss.
  - All 4 masks useful: this level is the first to truly demand fluid mask switching at the shop (or strategic mask choice before entering).
  - Top of the crane: panoramic view of Palma. Quiet moment. Bep: "It's beautiful up here." Balchar: "...It was better before."
- **End**: Boss gate. Penthouse elevator.

#### Boss: El Magnat (Phase 1)
*(Full details in Section 6)*

- **Story beat (post-boss)**: El Magnat escapes to Ibiza. The dimoni de Sa Pobla stumbles out of a disrupted hotel foundation — overwhelmed, confused, furious. "I can't take this anymore. TAKE THIS AND MAKE THEM STOP." Grants Tourist Rage mask to Llorenç. Bep's curse activates for the geographic jump. **Tourist Rage is now permanently available from World 5.5 onward.**

---

### 5.8 World 5.5 -- Eivissa (Modern Ibiza, Endgame)

- **Setting**: A nightmarish fusion of the Magnat's mega-resort empire on Ibiza. Ancient Phoenician ruins repurposed as nightclub foundations. Neon lights strung across historic walls. Es Vedra looms in the background. The whole island is the Magnat's domain.
- **Color palette**: Electric -- neon purple, toxic green, black, gold. The most visually aggressive world.
- **Enemies**: Fameliars (bottle imps, neon fameliars, VIP fameliars).
- **Available masks**: **All 5 masks + quick-swap.** Tourist Rage (earned post-W5 boss) is especially relevant here — the familiar swarms are the densest enemy encounters in the game, and Tourist Rage's AoE crowd control is the direct answer.
- **No new mask earned**: This is the final world. The player must use all previously collected masks strategically. Mask swapping is the meta-skill.
- **[NEW] Quick-swap unlock**: At the start of W5.5-1, the mask quick-swap mechanic activates automatically (see Section 4.2). Narrative beat: as Balchar arrives in Eivissa, all his collected masks flare simultaneously. Bep: "Something's different... they're all awake!" The curse reaching its peak destabilizes the mask bindings — Balchar can now channel any mask freely without Llorenç as intermediary. From this point, shoulder buttons (L1/R1) or Q/E cycle through masks in real time. This is the mechanical payoff for collecting all five masks.
- **Length**: 3 levels + boss (shorter but significantly harder).

#### Level 5.5-1: "Sa Discoteca Antiga" (The Ancient Disco)
- **Layout**: Mixed. Phoenician ruins converted into a nightclub. Alternating sections that each test a different mask power in sequence.
- **Difficulty**: 8/10
- **Enemy composition**: 3 bottle imps (swarm section), 2 neon fameliars (light trail section), 2 VIP fameliars (first encounter -- shields block attacks from the front, must reposition). Mixed encounters at the end.
- **Platforming challenges**: Tourist Rage is taught first — a bottle imp swarm ambush at the entrance. Then each section tests a different mask:
  - Section A: Bottle imp swarm (Tourist Rage to clear — the "aha!" moment for the newest mask)
  - Section B: Breakable floor (Stone Slam) over a lower path
  - Section C: Tall shaft (Double Jump + wall jump) to upper level
  - Section D: Wide neon-lit gap (Fire Dash across)
  - Section E: VIP familiars blocking a thin wall (Smoke Vanish through)
  - Final section: Combination requiring 2+ mask swaps in sequence
- **Collectibles**: 30-35 sling stones. 2 heart pickups. 1 secret: requires Stone Slam + Smoke Vanish in sequence (30 stones).
- **Teaching beats**:
  - Bottle imp swarm at entrance: "There's too many of them!" Player activates Tourist Rage — massive AoE clear. This is the first use of the newest mask and the most satisfying crowd-control moment in the game.
  - This level is a "mask exam" -- it tests each power individually, then in combination. It also serves as the tutorial for the quick-swap mechanic — each section naturally prompts the player to cycle to the right mask.
  - Bep (at level start, after quick-swap unlock): "They're all responding to you now! Try switching — the shoulder buttons!" (Or Q/E prompt on keyboard.)
  - VIP fameliars: "That big one has a shield! Like those Roman soldiers, but... shinier."
  - The final combination section is the real teaching beat: players must learn to use quick-swap fluidly mid-action.
- **End**: Save point with Llorenc shop. Llorenc: "I've catalogued all the masks. They're all remarkable. Balchar, we've come so far—" Balchar: "Shop. Now."

#### Level 5.5-2: "Es Mega-Resort" (The Mega-Resort)
- **Layout**: Horizontal with large rooms. The Magnat's mega-resort interior. Massive lobbies, VIP lounges, back-stage corridors. The longest level in the game.
- **Difficulty**: 9/10
- **Enemy composition**: 5 bottle imps, 4 neon fameliars, 3 VIP fameliars. Mixed encounters throughout -- no "safe" enemy type. Neon fameliars leave trails that restrict movement; VIP fameliars funnel the player into bad positions. Tourist Rage essential for managing bottle imp density.
- **Platforming challenges**: Neon light trail navigation (trails persist for 5 seconds, blocking paths -- must time movement). VIP fameliars on narrow platforms (can't be attacked from the front, must vanish behind or slam from above). Combination challenges requiring mid-combat mask swaps. Tourist Rage clears imp swarms that block platforming paths.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: in the VIP lounge, behind a triple-locked door (Stone Slam a floor, Fire Dash through a barricade, then Smoke Vanish through a thin wall). 40 stones and a sobrassada pot.
- **Teaching beats**:
  - Neon fameliars: their trails create dynamic platforming. The floor changes moment to moment.
  - VIP + bottle imp combos: the VIP blocks while imps swarm. Tourist Rage clears the imps, then reposition with Smoke Vanish to get behind the VIP.
  - Mid-combat mask swaps: the game's hardest non-boss challenge. Multiple tools needed for a single encounter.
- **End**: Save point with Llorenc shop (final shop before the last boss).

#### Level 5.5-3: "Es Penyasegat d'Es Vedra" (The Cliff of Es Vedra)
- **Layout**: Vertical. The ascent to the Magnat's penthouse overlooking Es Vedra. A cliff-face climb with the resort built into the rock. The hardest pure platforming in the game.
- **Difficulty**: 9/10
- **Enemy composition**: 4 bottle imps, 3 neon fameliars, 3 VIP fameliars. Enemies placed at platforming cruxes (the worst possible moments). Tourist Rage essential for clearing familiar clusters that block the climbing path.
- **Platforming challenges**: Cliff-face wall jumping with wind gusts. Neon trail avoidance during vertical climbs. Crumbling platforms over a long fall. A section requiring Fire Dash between two wall-jump surfaces (dash horizontally mid-climb). The final approach is a gauntlet of all hazard types. Tourist Rage clears swarm ambushes on narrow ledges.
- **Collectibles**: 35-40 sling stones. 2 heart pickups. 1 secret: near the summit, a hidden cave entrance behind a Smoke Vanish wall (30 stones, an aigua de font, an ensaimada -- stocking up for the boss).
- **Teaching beats**:
  - This level is pure execution. Minimal Bep commentary -- even he's nervous.
  - The cliff face with Es Vedra in the background is the game's most dramatic visual set piece.
  - Final approach before the boss: Bep quietly says "We can do this, Balchar." Balchar says nothing. (The only time Balchar's silence is played for sincerity rather than comedy.)
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
- **[REVISED v3.0]** Bosses test the player's **currently available masks** (earned from previous worlds), not the mask earned in the current world. The boss fight is the culmination of the player's toolkit up to that point. The mask earned AFTER the boss is a reward, not a test.
- Boss arenas are unique environments, not reused level geometry
- Every boss has a brief **intro cutscene** with personality-establishing dialogue
- Health is visible (boss health bar at top of screen)
- Half-heart minimum damage means bosses can have chip-damage moves and heavy-hit moves
- **[NEW] Boss Health Pools**: Expressed as "hits to kill" with the basic sling tap (1x damage). Charged shots and mask powers deal proportionally more. This makes balance transparent.

### 6.2 Es Bou de Pedra (World 1 Boss)

**Available masks during fight**: **None.** This is a pure skill test of movement, jumping, wall jumping, and sling combat. The absence of masks makes the victory feel earned, and the Stone Slam reward afterward is a powerful "level up" moment.

**Arena**: Open stone courtyard surrounded by taulas (T-shaped stone monuments). 4 stone pillars in the arena that can be shattered. Mediterranean sky above.

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
- **Phase transition**: At 33% HP, the bull's stone body cracks, revealing a glowing dimoni-energy core in its chest. It staggers, roars in pain.

**Phase 3: "The Core" (33%-0% HP)**
- The bull's attacks become erratic and desperate.
- **Pattern A -- Frenzy Rush**: Charges back and forth rapidly (0.6s tell per charge), bouncing off walls 2-3 times. Player must wall jump to stay above. Punish window: 2.5s of panting after the frenzy ends.
  - Damage: 1.5 hearts
- **Pattern B -- Core Pulse**: The exposed core pulses with energy (tell: 1.0s, core brightens + high-pitched whine), releasing a circular shockwave. Must be airborne to dodge. Punish window: 2.0s after pulse.
  - Damage: 1 heart
- **Weak point**: The glowing core takes 2x damage from charged sling shots. Tier 3 (full charge) shots deal 3x. This makes the final phase faster for players who have mastered the charge mechanic. The core is only exposed from the front.
- **Death**: The bull freezes, cracks spread from the core outward, and it crumbles into a pile of stones. The dimoni energy wisps away.

**What skilled players can do differently**: Time Tier 3 shots during short punish windows for faster kills. Stay close and aggressive rather than waiting for charges. Master the wall jump to stay above during Frenzy Rush.

**Post-boss reward**: Stone Slam mask granted by the dimoni de Sant Joan.

---

### 6.3 Quintus Caecilius Metellus (World 2 Boss)

**Available masks during fight**: **Stone Slam.** The boss fight tests the player's ability to use Stone Slam in combat alongside the core moveset.

**Arena**: Roman amphitheater. Sand floor, tiered stone seating on both sides (wall-jumpable). 4 columns at the arena's edges. A chariot track runs through the center.

**Health Pool**: ~35 tap-hits.

**Phase 1: "The Chariot" (100%-60% HP)**
- **Pattern A -- Chariot Charge**: Metellus drives his chariot from one side of the arena to the other (tell: 1.0s, whip crack + horse neigh + chariot visible at screen edge). Crosses the entire arena horizontally. Wall jump up the seating tiers to avoid. Punish window: 2.0s while the chariot turns at the far side.
  - Damage: 2 hearts (heavy, but long tell)
- **Pattern B -- Pilum Volley**: Metellus stands in the chariot and throws 3 javelins in a spread pattern (tell: 0.8s, arm raised + glint on spear tip). Gaps between javelins are jumpable. Punish window: 1.5s while he reaches for more spears.
  - Damage: 1 heart per javelin
- **Pattern C -- Shield Bash Drive-by**: Chariot passes close; Metellus swings a shield outward (tell: 0.5s, shield glow). Short range but catches players who dodge the chariot too late.
  - Damage: 1 heart
- **Stone Slam Interaction**: If the player uses Stone Slam while the chariot passes nearby, the shockwave can damage the chariot wheels, accelerating the Phase 1 transition. Reward for creative mask usage.
- **Phase transition**: At 60% HP, a wheel breaks on the chariot. Metellus crashes, rolls to his feet, draws his gladius. "On foot, then. I conquered the Balearics on foot anyway."

**Phase 2: "The General" (60%-30% HP)**
- Metellus fights on foot. Faster than expected for a general in armor.
- **Pattern A -- Gladius Combo**: 3-hit sword combo (tell: 0.5s, sword raised). Each swing covers ~2 tiles forward. Punish window: 2.0s after the third swing (sword stuck briefly).
  - Damage: 1 heart per hit
- **Pattern B -- Shield Wall**: Raises shield and advances slowly (tell: obvious, he crouches behind shield). Blocks all frontal attacks. Must jump over him and attack from behind, or use Stone Slam — the shockwave penetrates the shield. While shielded, he can still bash (0.5s tell, shield glows).
  - Damage: 0.5 hearts (shield bash)
- **Pattern C -- Tactical Retreat**: Jumps backward to a column, kicks rubble forward (tell: 0.8s, foot plants on column). 3 pieces of rubble in a spread. Jump through gaps. He uses this to create distance.
  - Damage: 1 heart per rubble
- **Stone Slam Mastery Test**: Metellus's Shield Wall is the core test. Stone Slam bypasses the shield — the shockwave damages him through his guard. This rewards players who have mastered the W2 mechanic. Without Stone Slam, the player must jump over him (harder but possible).
- **Phase transition**: At 30% HP, Metellus blows a horn. "Legionaries! To me!" He backs to the arena center.

**Phase 3: "The Legion" (30%-0% HP)**
- 2 legionaries spawn on each side of the arena (4 total, respawn in pairs every 15 seconds if killed). Metellus fights simultaneously.
- **Metellus continues Phase 2 patterns** but with legionaries adding pressure.
- **Legionary behavior**: Same as normal legionaries -- shield front, attackable from above or behind. They slowly advance toward Balchar.
- **Stone Slam crowd control**: Stone Slam shockwave scatters ALL legionaries in range, stunning them for 2 seconds. This is the primary crowd management tool — slam, then rush Metellus during the stun window. This is the definitive Stone Slam combat test.
- **Punish windows**: Metellus's recovery windows remain the same, but the player must clear/stun legionaries first.
- **Death**: Metellus drops to one knee. "You fight like the old slingers of legend. Perhaps these islands weren't so easy to conquer." Collapses.

**What skilled players can do differently**: Stay aggressive in Phase 1, landing hits between chariot passes. Use Stone Slam on the chariot wheel for faster transition. In Phase 3, chain Stone Slams to keep legionaries permanently stunned while focusing Metellus.

**Post-boss reward**: Double Jump mask granted by the dimoni de Manacor.

---

### 6.4 El Comte Mal (World 3 Boss)

**Available masks during fight**: **Stone Slam + Double Jump.** The boss fight tests the player's mastery of Double Jump (the newest mask) for vertical positioning and evasion, alongside Stone Slam for combat.

**Arena**: The Comte's great hall. Long, tall room with chandeliers, stone pillars, and the chained dimoni visible in the background. Dimoni-fire braziers at the edges of the room flare when the Comte drains power. The room has 3 elevated platforms (chandeliers that can be stood on — Double Jump required to reach them).

**Health Pool**: ~40 tap-hits.

**Phase 1: "The Aristocrat" (100%-60% HP)**
- **Pattern A -- Teleport Strike**: The Comte vanishes in a cloud of bats (tell: 0.8s, bats swirl around him + a shadow appears at his destination 0.5s before he materializes). Appears next to Balchar and slashes with clawed hands. Punish window: 2.0s after the slash as he adjusts his cape dramatically.
  - Damage: 1 heart
- **Pattern B -- Bat Swarm**: Raises a hand (tell: 0.8s, hand glows red) and sends 5 bats in a wave pattern across the room. Bats move in a sine wave vertically. Jump through gaps between them — Double Jump provides extra height to dodge the upper wave. Punish window: 1.5s while his hand is extended.
  - Damage: 0.5 hearts per bat
- **Pattern C -- Blood Drain**: If Balchar is within melee range for too long, the Comte reaches out (tell: 0.5s, eyes flash red) to grab. If successful, drains 1.5 hearts and heals himself for 5% HP. Mash buttons to break free faster. Teaches staying mobile.
  - Damage: 1.5 hearts (grab), but breakable
- **Double Jump utility**: Double Jump to the chandelier platforms provides a safe zone from Teleport Strike (the Comte only teleports to ground level in Phase 1). Punish from above with charged sling shots.
- **Phase transition**: At 60% HP, the Comte hisses in frustration. "Enough." He turns toward the chained dimoni and begins draining its power. The room darkens, fire braziers flare.

**Phase 2: "The Drain" (60%-30% HP)**
- The Comte is visually powered up: red aura, eyes glowing, moves faster.
- **Pattern A -- Teleport Strike** is faster (0.5s tell, less shadow warning). Now can teleport to chandelier level — chandeliers are no longer automatically safe. Must Double Jump OFF chandeliers to dodge.
- **Pattern B -- Fire Pillar Eruption**: The dimoni's leaking energy erupts as fire pillars from the braziers (tell: 1.0s, braziers brighten + ground glows at eruption points). 3 pillars rise from the floor in sequence. Double Jump to the chandelier platforms to escape — the pillars only affect ground level.
  - Damage: 1.5 hearts
- **Pattern C -- Shadow Dash**: The Comte dashes across the room leaving a damaging shadow trail (tell: 0.8s, he crouches + trail preview on the ground). Trail persists for 3 seconds. Double Jump to the chandelier platforms to escape. Stone Slam can disrupt the trail if used at the right moment (it shatters the shadow energy on the ground).
  - Damage: 1 heart (trail contact)
- **Double Jump Mastery Test**: The chandelier platforms become essential. Double Jump is needed to reach them, escape them, and reposition between them. The vertical game is the key to survival.
- **[NEW] Fire Dash Foreshadowing**: The fire pillars ARE the dimoni's power leaking. After this fight, the freed dimoni grants Fire Dash. Observant players will recognize the connection.
- **Phase transition**: At 30% HP, the dimoni's prison cracks loudly. The Comte stumbles, weakened by the dimoni pulling back its power. "No! The power is MINE!"

**Phase 3: "The Desperate Count" (30%-0% HP)**
- The Comte is visibly weakened -- flickering, unstable. But desperation makes him dangerous.
- **Pattern A -- Frenzy Teleport**: Teleports 3 times rapidly, slashing each time (tell: 0.5s per teleport, but shadow markers help). Each slash covers a wider area. Punish window: 3.0s after the frenzy (gasping, hunched). Double Jump between chandeliers to evade the frenzy chain.
  - Damage: 1 heart per slash
- **Pattern B -- Bat Storm**: Fills the room with bats (tell: 1.0s, screech + screen darkens). Bats swirl in a pattern with safe spots near the chandelier platforms. Double Jump to reach safe zones. Lasts 5 seconds. Punish window: 2.0s after storm clears.
  - Damage: 0.5 hearts per bat hit
- **Weak point**: The Comte takes 1.5x damage from charged sling shots while weakened in Phase 3. Tier 3 charged shots from the chandeliers (above him, clear line of sight) deal devastating damage.
- **Death**: The Comte's form destabilizes. "This... is not over..." He dissolves into bats that scatter and vanish. The dimoni's chains shatter.

**What skilled players can do differently**: Aggressive melee during Phase 1 punish windows (no need to charge shots). In Phase 2, use chandelier platforms to stay above fire pillars and snipe during recovery. Phase 3 can be ended in 2-3 punish windows with full-charge shots from the chandeliers.

**Post-boss reward**: Fire Dash mask granted by the freed dimoni.

---

### 6.5 Dragut (World 4 Boss)

**Available masks during fight**: **Stone Slam + Double Jump + Fire Dash.** The boss fight tests the player's mastery of Fire Dash (the newest mask) for horizontal mobility and aggressive combat, alongside previous masks.

**Arena**: Three-part arena. Phase 1 on the moonlit beach (flat, wide). Phase 2 boarding the ship (vertical climb). Phase 3 on the ship deck (medium, flat with mast obstacles).

**Health Pool**: ~40 tap-hits (split: Phase 1 lasts until boarding, Phase 2 is crew-clearing with no boss HP drain, Phase 3 is the real health bar).

**Phase 1: "The Bombardment" (Beach)**
- **No direct combat with Dragut** -- he's on the ship commanding cannons.
- **Pattern A -- Cannon Volley**: 3 cannons fire in sequence (tell: 1.0s per cannon, visible cannon flash + whistling sound). Impact zones marked by shadow circles on the beach. Dodge by running/jumping between impacts.
  - Damage: 1.5 hearts per cannonball
- **Pattern B -- Grapeshot Sweep**: A wide cannon fires a horizontal spread of small projectiles (tell: 0.8s, distinct cannon sound). Jump or Double Jump over the spread. Lower grapeshot can be ducked under (crouch at wall edge).
  - Damage: 1 heart
- **Pattern C -- Fire Barrel**: A burning barrel is launched in a high arc (tell: 1.0s, barrel visible in the air, shadow grows on ground). Explodes on impact in a wide radius. Run clear. Fire Dash THROUGH the explosion for stylish invulnerability-frame dodge.
  - Damage: 1.5 hearts (explosion)
- **Fire Dash utility**: Dash across the beach to reach the rowboats faster. Dash through cannon impact zones during their detonation (invulnerability frames). This phase rewards aggressive use of Fire Dash to minimize time on the exposed beach.
- **Objective**: Survive the bombardment while reaching the rowboats at the water's edge. 3-4 volleys, then a rowboat section (Fire Dash across water gaps between small boats to reach the ship).
- **Phase transition**: Balchar reaches the ship's hull. Dragut: "Coming aboard? Bold. I like bold. Kill him."

**Phase 2: "The Boarding" (Ship Hull + Deck)**
- **Gauntlet section**, not a boss HP phase. Fight through 6 pirate crew members on the deck (scimitar pirates + 2 powder monkeys).
- The ship rocks gently, causing all characters to slide slightly left/right periodically (environmental mechanic -- adds unpredictability).
- **Fire Dash** is extremely useful here: dash through the crew cluster to reach safer positions, burn through a wooden barricade the pirates set up on deck, dash past powder monkey bombs.
- **Stone Slam** can scatter grouped pirates on the deck.
- **End of Phase 2**: All crew defeated or bypassed. Dragut draws twin scimitars. "Just you and me, then. Good."

**Phase 3: "The Duel" (Ship Deck)**
- **The real boss fight**. Dragut is fast, aggressive, and relentless.
- **Pattern A -- Twin Slash Combo**: 4 rapid horizontal slashes (tell: 0.3s per slash -- fast! -- but he takes a wide stance 0.8s before starting the full combo). Covers ~3 tiles forward per slash. Punish window: 2.5s after the fourth slash (arms wide, panting). Fire Dash through the combo path to end up behind Dragut for immediate counterattack.
  - Damage: 1 heart per slash
- **Pattern B -- Scimitar Throw**: Throws one scimitar like a boomerang (tell: 0.8s, arm winds back). Travels across the screen and returns. Double Jump over or Fire Dash through (invulnerability frames). While one scimitar is thrown, his melee combos are only 2 slashes instead of 4. Punish window: 1.5s while catching the return.
  - Damage: 1.5 hearts
- **Pattern C -- Deck Slam**: Stabs both scimitars into the deck (tell: 1.0s, jumps into the air), sending a shockwave along the wood. Jump or Double Jump to avoid. The slam also knocks loose rigging ropes that swing across the deck for 3 seconds (secondary hazard). Punish window: 2.0s while pulling scimitars free. Stone Slam during his recovery creates extra stagger.
  - Damage: 1.5 hearts (slam), 0.5 hearts (rope)
- **Fire Dash Mastery Test**: Dragut's 4-slash combo is specifically designed so that Fire Dash allows dashing through the entire combo if timed at the start — you end up behind him with invulnerability frames. Without Fire Dash, the player must retreat or wall-jump the mast to escape. Both work, but Fire Dash is cleaner and more aggressive.
- **Ship rock**: The deck still rocks gently. At ~15% HP, the rocking intensifies (the ship is breaking apart from the battle).
- **Death**: Dragut drops to one knee, scimitars clattering. "You fight well for a man from the rocks." Balchar: "Everyone on this island fights well. That's why you keep losing." Dragut laughs, then collapses.

**What skilled players can do differently**: Parry the scimitar throw with a timed sling tap (returns it for 3x damage -- hidden mechanic, not required). Fire Dash through every combo for aggressive counterattacks. Stay in melee range and chain Fire Dash repositioning.

**Post-boss reward**: Smoke Vanish mask granted by the dimoni de Pollenca.

---

### 6.6 El Magnat Phase 1 (World 5 Boss)

**Available masks during fight**: **Stone Slam + Double Jump + Fire Dash + Smoke Vanish.** The boss fight tests the player's mastery of Smoke Vanish (the newest mask) for evasion and repositioning, alongside the full existing toolkit.

**Arena**: Rooftop of an illegally-built luxury hotel overlooking Palma Bay. Helipad at one end, penthouse pool at the other (pit hazard). Golden furniture as destructible obstacles. Neon "SE VENDE" sign flickering in the background.

**Health Pool**: ~35 tap-hits.

**Phase 1: "The Mogul" (100%-60% HP)**
- **Pattern A -- Money Toss**: Throws bundles of euro bills that create shockwaves on impact (tell: 0.8s, reaches into golden suit jacket, bills glow). 2-3 bundles in a spread. Jump the shockwaves (they travel along the ground ~4 tiles each way). Punish window: 1.5s while he adjusts his cufflinks.
  - Damage: 1 heart (shockwave), 0.5 hearts (direct bundle hit)
- **Pattern B -- Lawyer Summon**: Pulls out a golden phone (tell: 1.0s, phone ring sound), summons 2 lawyer minions. Lawyers are weak (2 hits) but chase aggressively with briefcases. They respawn after 10 seconds if not killed. Stone Slam shockwave scatters them.
  - Damage: 0.5 hearts (briefcase swing)
- **Pattern C -- Gold Card Throw**: Flicks a golden credit card like a shuriken (tell: 0.5s, hand flick). Fast, low projectile. Duck, jump, or Smoke Vanish through.
  - Damage: 1 heart
- **Smoke Vanish utility**: Vanish through lawyer swarms to reach the Magnat directly. Phase through gold card projectiles. Reposition behind the Magnat during his cufflink-adjusting punish window.
- **Phase transition**: At 60% HP, the Magnat snaps his fingers. "You're trespassing on private property." Construction walls rise around the arena edges, shrinking the playable area by ~25%.

**Phase 2: "The Developer" (60%-30% HP)**
- The arena is smaller. The Magnat adds construction-themed attacks.
- **Pattern A -- Contract Wall**: Slams the ground with a rolled-up contract (tell: 1.0s, contract unrolls visually + ground glows). A wall of legal paperwork rises from the ground, blocking the arena further. Must break through with attacks (5 hits) or Fire Dash through. Creates strategic lane management.
  - No direct damage, but restricts movement
- **Pattern B -- Money Toss** continues, more bundles (4 at once), harder to dodge in the smaller space.
- **Pattern C -- Phone Call Reinforcements**: Now summons 3 lawyers at once. Stone Slam scatters them; Smoke Vanish phases through them to reach Magnat.
- **Pattern D -- Wrecking Ball**: A construction crane swings a wrecking ball across the arena (tell: 1.2s, crane creaks + shadow on ground). Horizontal sweep. Double Jump over or Smoke Vanish through. The wrecking ball destroys Contract Walls in its path (environmental help).
  - Damage: 2 hearts
- **Smoke Vanish Mastery Test**: The smaller arena makes crowd management critical. Smoke Vanish through lawyer clusters and Contract Walls (phase through) is the most efficient strategy. Without Vanish, the player must destroy walls and fight through lawyers the hard way.
- **Phase transition**: At 30% HP, the Magnat stumbles backward. "You don't understand! This isn't just Mallorca!" He pulls out his phone again.

**Phase 3: "The Escape" (30%-0% HP)**
- The Magnat becomes frantic. Attacks are faster and more desperate.
- **Pattern A -- Money Rain**: Throws money into the air. Bills rain down across the arena (tell: 1.0s, money flies up + shadow rain on ground). Random impact points, but density is manageable. Punish window: 2.0s (he's out of money momentarily, patting his jacket). Smoke Vanish provides brief invulnerability through the rain.
  - Damage: 0.5 hearts per bill
- **Pattern B -- Golden Phone Laser**: Points his phone and fires a beam across the arena (tell: 1.0s, phone charges with golden light). Sweeps left to right. Jump, Double Jump, or Smoke Vanish through.
  - Damage: 1.5 hearts
- **Pattern C -- Lawyer Wave**: Summons 4 lawyers in a line. Stone Slam scatter or fight through.
- **At 0% HP**: The Magnat raises his hands. "You think Mallorca was my endgame? I own IBIZA." A helicopter appears. He grabs a ladder and escapes. The arena crumbles. Cutscene transition.
- **[NEW] This is NOT a real defeat** -- the player doesn't get the satisfaction of a proper kill. This is intentional -- it fuels the desire to chase him to Ibiza. The "escape boss" is a narrative tool.

**What skilled players can do differently**: Smoke Vanish through Contract Walls instantly (no need to break them). Ignore lawyers entirely by phasing through them. Fire Dash through Contract Walls for aggressive destruction. Chain Smoke Vanish repositioning behind the Magnat during every punish window.

**Post-boss reward**: Tourist Rage mask granted by the dimoni de Sa Pobla.

---

### 6.7 El Magnat Phase 2 (World 5.5 Boss)

**Available masks during fight**: **All 5 masks + quick-swap.** This is the ultimate test of the player's full toolkit and real-time mask switching.

**Arena**: The pinnacle of the Magnat's mega-resort, overlooking the Ibiza coastline. Es Vedra visible in the moonlit background. The platform is circular, surrounded by neon lights. Familiar energy crackles across the surface.

**Health Pool**: ~50 tap-hits (the longest fight in the game).

**Phase 1: "The Tycoon Empowered" (100%-60% HP)**
- The Magnat floats above the arena, powered by familiar energy. Golden aura, eyes glowing, physically larger.
- **Pattern A -- Money Meteor**: Hurls golden energy balls downward (tell: 0.8s, hand raises + shadow on ground). 3 meteors in sequence. Each creates a shockwave on impact. Jump the shockwave, Double Jump the meteor.
  - Damage: 1.5 hearts (meteor), 1 heart (shockwave)
- **Pattern B -- Familiar Summon**: Opens a portal (tell: 1.0s, portal crackles). 4 bottle imps pour out. Tourist Rage clears them instantly — and they drop heart pickups (1 guaranteed per wave), providing sustain for the long fight.
  - Damage: 0.5 hearts per imp contact
- **Pattern C -- Golden Beam**: Fires a horizontal beam across the arena (tell: 1.0s, eyes flash gold). Sweeps in an arc. Double Jump to avoid, or Smoke Vanish through.
  - Damage: 1.5 hearts
- **How to damage him**: He's floating -- melee doesn't reach. Must use charged sling shots (Tier 2+) or lure him to a lower hover during punish windows (after Familiar Summon, he descends briefly for 2.5s to observe the fight -- punish window).
- **Phase transition**: At 60% HP, the arena cracks. "You can't stop progress!" He channels more familiar energy. The outer ring of the arena crumbles away, reducing the platform size by ~30%.

**Phase 2: "The Arena Crumbles" (60%-30% HP)**
- Smaller arena. The Magnat alternates between floating and ground slams.
- **Pattern A -- Ground Slam**: Descends rapidly (tell: 1.0s, floats higher first + shadow expands). Slams the ground, cracking it further. Shockwave in all directions. Jump to avoid. Punish window: 3.0s while he pulls himself out of the crater (this is the main damage window -- get close and melee).
  - Damage: 2 hearts (slam), 1 heart (shockwave)
- **Pattern B -- Neon Familiar Trail**: Summons 2 neon fameliars that race across the arena, leaving damaging light trails (tell: 0.8s, portals open at arena edges). Trails persist for 5 seconds. Limits movement. Fire Dash through trails (invulnerability frames).
  - Damage: 1 heart (trail contact)
- **Pattern C -- VIP Shield**: Summons a VIP familiar as a bodyguard (tell: 0.8s, golden portal). The VIP has a shield and blocks Balchar's attacks until dispatched (3 hits from behind, or Stone Slam stuns it, or Smoke Vanish to get behind).
- **Pattern D -- Money Meteor** continues with 4 meteors now.
- **Stone Slam utility**: After the Ground Slam, if the player uses Stone Slam on the cracked ground, rubble rises and hits the Magnat for bonus damage. Reward for reading the environment.
- **Phase transition**: At 30% HP, the Magnat screams. Familiar energy surges. The arena shrinks to its final size (~60% of original). "EVERYONE HAS A PRICE!"

**Phase 3: "The Final Mask Test" (30%-0% HP)**
- This phase is the game's ultimate test. The Magnat uses attacks that each require a SPECIFIC mask to counter optimally. The attacks cycle in a fixed sequence, teaching the player the pattern before demanding it. Quick-swap fluency is essential.
- **Cycle** (repeats until death):
  1. **Familiar Floor Slam**: Entire ground pulses with energy (tell: 1.0s, ground glows gold). **Stone Slam the ground** to disrupt the pulse and create a safe stone platform. Without Stone Slam, the player takes unavoidable chip damage (0.5 hearts).
  2. **Aerial Barrage**: Magnat flies high and rains 6 projectiles (tell: 0.8s, arms spread). **Double Jump** to reach the stone platform created by Stone Slam (or just dodge on the ground -- harder).
  3. **Golden Barrier**: Magnat surrounds himself with a golden energy wall while charging a beam (tell: 1.2s, barrier appears). **Fire Dash through** the barrier to interrupt the charge and deal damage. Without Fire Dash, the beam fires and must be jumped (1.5 hearts).
  4. **Familiar Wave**: 6 bottle imps + 2 VIP fameliars swarm the arena (tell: 0.8s, portals everywhere). **Tourist Rage** to clear the bottle imps, then deal with VIPs individually. Without Rage, the swarm overwhelms.
  5. **Scythe Sweep**: Magnat swoops across the arena with arms extended (tell: 0.8s, he banks into a glide). **Smoke Vanish** to phase through. Without Vanish, extremely tight jump timing required.
  6. **Punish Window**: After the full cycle, Magnat lands, exhausted, for 4.0 seconds. All-out attack. This is the main damage window for the entire phase.
- Each cycle takes ~30 seconds. The fight requires 3-4 full cycles to kill.
- **On defeat**: The Magnat staggers. "Everyone... has a price..." Balchar: "I don't even know what money is." The familiar energy explodes outward. The Magnat collapses. His empire literally crumbles -- the resort disintegrates around them. The fameliars are freed, cheering as they scatter.

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

- **Balchar**: 24x32 pixels (or similar, proportional to a stocky warrior)
- **Bep**: 16x16 pixels (small, round, always near Balchar)
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
- **[NEW] Charge indicator**: When holding the sling attack, a small charge meter appears near Balchar (not in the HUD -- world-space) showing Tier 1/2/3 progression
- **[NEW] No-mask indicator**: In World 1 (before any mask is earned), the mask icon slot shows an empty/greyed-out placeholder. This primes the player to expect a mask will eventually fill that slot.
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
damage_taken       -- Balchar hit
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
- **[NEW] No-mask state**: During World 1 (before Stone Slam is earned), the mask icon area shows a greyed-out placeholder mask silhouette. This trains the player to associate that HUD space with mask powers before they have one.
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
- Bruna visible in the background. Bep hides behind Balchar if Bruna is on screen.
- **[NEW] Insufficient funds feedback**: If the player tries to buy something they can't afford, the item shakes and Llorenc has a quip: "That one's expensive. Try breaking more pots."

### 10.4 Pause Menu

- Pause available at any time during gameplay
- Options: Resume, Items (use consumables), Controls, Quit to Menu
- No mid-level saving from pause -- pause is just a pause

### 10.5 World Transition Screens

- After boss defeat + dimoni mask reward + Bep's portal: a brief animated cutscene of the mask being granted, then the portal opening and the characters being pulled in
- Loading screen: pixel art vignette of the next era with the world name and date
- Arrival: brief cutscene of Balchar and Bep arriving, reacting to the new setting

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
- **[NEW] Post-boss mask grant state**: After a boss defeat, the game enters a brief CUTSCENE state for the dimoni mask grant before transitioning to the portal/world transition. This is a distinct state to ensure the mask is permanently added to the player's save data at a controlled moment.

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
- **[REVISED v3.0] Post-boss mask save**: Mask acquisition is saved as part of the post-boss sequence. The mask is permanently added to the save data after the dimoni grants it, before the portal transition. If the player quits during the portal cutscene, the mask is still saved.
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
- Mask power has a single dedicated button. The current mask determines the effect. **In World 1, the Mask Power button is inactive** (no mask equipped yet). No error feedback needed — the button simply does nothing until Stone Slam is earned after the W1 boss.
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

B = Boss encounter. The curve is designed to be smooth with no jarring spikes. Each world starts slightly below the previous world's midpoint, providing a brief ramp-up period with the newly available mask before difficulty escalates.

## APPENDIX C: Retroactive Secret Map

**[NEW]** Secrets that become accessible when revisiting earlier worlds with later mask powers.

| Secret Location | World | Requires | Reward |
|----------------|-------|----------|--------|
| Cracked floor in talayot (1-3) | W1 | Stone Slam (post-W1 boss) | 15 stones |
| High cliff ledge (1-1 area) | W1 | Double Jump (post-W2 boss) | 15 stones |
| Sealed cave (1-3 area) | W1 | Fire Dash (post-W3 boss) | 25 stones + ensaimada |
| Shimmering wall (1-4 area) | W1 | Smoke Vanish (post-W4 boss) | 20 stones |
| High ledge in atrium (2-1) | W2 | Double Jump (post-W2 boss) | 10 stones |
| Narrow passage (2-1 area) | W2 | Fire Dash (post-W3 boss) | 20 stones |
| Thin wall in aqueduct (2-2) | W2 | Smoke Vanish (post-W4 boss) | 25 stones + ammo pack |
| Crowd switch (2-3 area) | W2 | Tourist Rage (post-W5 boss) | 30 stones |
| Wooden barricade (3-3) | W3 | Fire Dash (post-W3 boss)* | 20 stones |
| Side room in tower (3-4) | W3 | Smoke Vanish (post-W4 boss) | 20 stones |
| Heavy door (3-2 area) | W3 | Tourist Rage (post-W5 boss) | 25 stones |
| Thin wall in cave (4-3) | W4 | Smoke Vanish (post-W4 boss)* | 20 stones + frozen rock pack |
| Collapsed building (4-2) | W4 | Stone Slam + Fire Dash combo | 20 stones |
| Deep cave (4-3 area) | W4 | Tourist Rage (post-W5 boss) | 30 stones + oli d'oliva |

*W3 wooden barricade and W4 thin wall can be accessed on first visit if the player has the relevant mask equipped (they are earned before those levels in the post-boss sequence of the immediately preceding world). These are the rare non-retroactive secrets — they reward having the right mask selected.

Retroactive secrets are purely optional. They provide economic bonuses for completionists but are never required for progression.

**[NEW] Quick-swap synergy**: Once the mask quick-swap mechanic is unlocked at W5.5 (see Section 4.2), replaying earlier levels for retroactive secrets becomes significantly more enjoyable. Players can cycle masks on the fly during Level Select replays, making multi-mask secrets (e.g., the W5.5-2 triple-locked door requiring Stone Slam + Fire Dash + Smoke Vanish) feel like fluid puzzle-solving rather than trial-and-error with pre-selected masks. This is the primary replay motivator for post-endgame content.

## APPENDIX D: Mask Acquisition Timeline

**[NEW v3.0]** Complete timeline of mask acquisition showing the "earn then use" flow.

```
W1 Levels (no masks) -> W1 Boss -> EARN STONE SLAM
    |
W2 Levels (Stone Slam) -> W2 Boss -> EARN DOUBLE JUMP
    |
W3 Levels (Stone Slam + Double Jump) -> W3 Boss -> EARN FIRE DASH
    |
W4 Levels (Stone Slam + Double Jump + Fire Dash) -> W4 Boss -> EARN SMOKE VANISH
    |
W5 Levels (All above + Smoke Vanish) -> W5 Boss -> EARN TOURIST RAGE
    |
W5.5 Levels (All 5 masks + quick-swap) -> W5.5 Boss -> GAME COMPLETE
```

Each arrow represents the post-boss dimoni encounter where the mask is granted. The mask immediately enters the player's inventory and is available at Llorenç's shop from the next world's first save point onward.
