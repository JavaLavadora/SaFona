# SA FONA — Game Design Document

> **Working title**: Sa Fona
> **Version**: 1.0 (Draft)
> **Genre**: 2D Retro Side-Scrolling Platformer with Combat
> **Engine**: Pygame (Python)

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

- **Shrek** — Reluctant hero, buddy dynamic between Ramon and Bep, parody tone
- **Crash Bandicoot** — Mask power-up system (Aku Aku → dimoni masks)
- **Castlevania** — Sling-as-whip melee feel, gothic atmosphere (World 3)
- **Asterix** — Historical comedy, small hero vs. empires
- **Shovel Knight** — Retro platformer structure, world progression, shop NPCs

---

## 2. STORY & NARRATIVE

### 2.1 Premise & Inciting Incident

Ramon, a foner from the talayotic period (~1000 BC Mallorca), is napping against a talayot. His myotragus, Bep, wanders off and eats the sacred herbs growing on a dimoni's altar — the dimoni's prized garden. The dimoni arrives furious, curses Bep, and storms off. Ramon wakes up, sees Bep chewing with a guilty face: "...What did you eat now?"

The curse has two effects: Bep gains the ability to speak (and won't shut up), and Bep becomes a living time-travel trigger — after moments of great energy (boss defeats), the curse activates, Bep glows, sneezes, and rips open a time portal.

The player does not know any of this during World 1. It plays as a straight talayotic adventure. The time-travel premise is only revealed after beating the first boss.

### 2.2 Full Story Arc

**World 1 — Sa Talaia (Talayotic ~1000 BC)**
Ramon and Bep navigate their own era. Something feels off — possessed sheep, unnatural energy, a creeping wrongness. They defeat Es Bou de Pedra. Then Bep starts glowing. He sneezes. A time portal rips open. The dimoni from the intro appears, laughing: "You thought we were done? That sheep ate my herbs. Every dimoni on this island wants a piece of him now. Good luck." Ramon and Bep are sucked in.

Ramon: "...I just wanted a nap."

**World 2 — Mallorca Romana (Roman Conquest, 123 BC)**
Ramon is confused by roads and tall architecture. Romans mistake him for a barbarian rebel. He meets Llorenç, a fellow talayotic warrior from Menorca who has been researching dimoni activity and tracked the time disturbance. Llorenç is fascinated by the curse; Ramon is annoyed. They become reluctant allies. The local dimoni lends its mask power but hands it to Llorenç for safekeeping — Ramon is too chaotic. This establishes the shop mechanic.

**World 3 — El Comte Mal (Feudal Mallorca, legend-based)**
Dark feudal Mallorca. The Comte Mal, a powerful vampire nobleman, has captured and imprisoned a dimoni to siphon its supernatural power. An old witch, La Bruixa, maintains the binding ritual for the Comte — she is a pawn, used by him, not an enemy in her own right. Strange fires burn across the Comte's lands. Ramon frees the dimoni by defeating the Comte. The freed dimoni, like the others, refuses to stay with Ramon and entrusts its mask to Llorenç. This cements the narrative rule: dimonis don't trust Ramon (he's cursed, chaotic, everything explodes around him), so all masks go to Llorenç.

**World 4 — Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)**
Ottoman pirate raids on the Mallorcan coast. Coastal watchtowers, burning villages, moonlit beaches. Locals beg Ramon to help defend. He sighs deeply: "First Romans, then a vampire, now pirates. Is there a single century where people leave this island alone?"

**World 5 — S'Invasio (Modern Day)**
Ramon arrives in the present. His ancestral land has been turned into hotel chains. "...I think I preferred the pirates." A satirical world full of tourists, real estate agents, influencers, and party buses. He defeats El Magnat, a real estate tycoon, on a luxury hotel rooftop. But the Magnat pulls out a phone: "You think Mallorca was my endgame? I own IBIZA." A helicopter arrives. He escapes.

**World 5.5 — Eivissa (Modern Ibiza)**
Bep's curse activates one last time — but instead of a time jump, it's a geographic jump. They're sneezed to Ibiza. The Magnat has built a mega-resort empire powered by enslaved fameliars (little demons from Santa Eularia folklore). Shorter but harder world. Ramon uses all his collected powers to bring it down. Final confrontation with El Magnat empowered by familiar energy.

### 2.3 Narrative Tone & Voice

The game is a lighthearted parody. Real historical events and genuine Mallorcan folklore are the foundation, but everything is viewed through the lens of a protagonist who finds it all deeply inconvenient. The humor comes from the contrast: the world is dramatic and high-stakes, Ramon is not.

- Dialogue is short and punchy
- Historical commentary is always filtered through character perspective
- Serious themes (colonization, piracy, gentrification) are addressed through satire, never preachy
- Every NPC interaction should be either funny, informative, or both

### 2.4 Ending & Post-Credits

El Magnat phase 2 is defeated. His empire crumbles. The curse breaks — all dimoni debts are settled through the journey. Bep stops glowing. Ramon looks at Bep. Looks at Llorenç. Looks at the player.

"...I'm walking home."

Credits roll over pixel art: Ramon and Bep walking along a Mediterranean coast toward Mallorca. Llorenç waves goodbye from Ibiza with Bruna.

**Post-credits**: Bep is grazing peacefully near a talayot. He spots a strange plant. He eats it. His eyes widen. Screen cuts to black. A single bleat. Silence.

---

## 3. CHARACTERS

### 3.1 Ramon — Protagonist

- **What he is**: A foner — a talayotic warrior and slinger from ~1000 BC Mallorca
- **Personality**: Grumpy, laconic, reluctant. Just wants to be left alone. Dry Mallorcan humor. Never asked to be a hero. Complains about everything but quietly does the right thing when it matters (without admitting it).
- **Visual direction**: Stocky build, simple tunic, leather sling always in hand. Bronze-age aesthetic. Perpetually unimpressed expression.
- **Dialogue style**: Short sentences. Deadpan. "No." "Fine." "This is your fault, Bep." Never more than two lines at a time.

### 3.2 Bep — Companion

- **What he is**: A myotragus balearicus (extinct Balearic bovid, sheep-like). Ramon's companion animal.
- **Personality**: Cheerful, oblivious, unconditionally loyal. Loves Ramon despite constant rejection. Talks too much after being cursed. Comic relief. Occasionally says something accidentally wise.
- **Gameplay role**:
  - Hints mechanics through dialogue ("Ramon! I bet if you hold that button longer the rock goes further!" / "That wall looks jumpable!")
  - Triggers time-travel portals after each boss (involuntary curse activation: glows → sneezes → portal opens)
  - Visual companion on screen with idle animations (chews on things, falls asleep, gets startled by enemies)
  - Does NOT have a gameplay button or direct mechanical interaction — purely narrative and cosmetic presence
- **Visual direction**: Small, round, sheep-like with stubby horns. Expressive eyes. Faint glowing aura after the curse.
- **Dialogue style**: Enthusiastic, rambling. "Ramon! Did you see that? You were amazing! ...Ramon? Ramon, are you ignoring me? That's okay, I still think you're great."

### 3.3 Llorenç — Shop/Lore NPC

- **What he is**: A talayotic warrior from Menorca. Researcher, collector, nerd.
- **Personality**: Enthusiastic about artifacts and dimoni lore. Friendly rivalry with Ramon based on the classic Mallorca-vs-Menorca banter. Genuine friends despite the jabs.
- **Gameplay role**:
  - Appears between worlds and at level-end save points
  - Runs the **Mask Shop**: player swaps dimoni powers here
  - Sells **consumables** (health recovery, temporary buffs)
  - Sells **max heart upgrades** (permanent, increasingly expensive)
  - Provides optional lore about each era and dimoni
- **Why he holds the masks**: Established through plot (Worlds 2-3). Dimonis don't trust Ramon — he's cursed, chaotic, destruction follows him. They entrust their masks to Llorenç, the calm, respectful researcher. Ramon has to visit Llorenç to equip powers. This is both narrative and a gameplay gate.
- **Companion**: Bruna, a Menorcan cow. Calm, stoic. Looks at Bep with quiet disdain. Bep is terrified of her.
- **Visual direction**: Similar build to Ramon but slightly taller. Carries a satchel full of artifacts. Always has a scroll or mask in hand. Bruna stands behind him at the shop.
- **Dialogue style**: Wordy, excited. "Fascinating! This mask channels the fire dimoni of the Comte Mal's domain. In Menorca we have similar legends but — you don't care, do you." Ramon: "No."

### 3.4 Dimonis — Per-World NPCs

Each world (after World 1) features a dimoni that Ramon encounters early in the world. The dimoni is annoyed by Bep's curse attracting attention but grudgingly lends Ramon a power (in mask form) to deal with the local threat faster — so Ramon leaves sooner. The mask is given to Llorenç.

| World | Dimoni | Personality |
|-------|--------|-------------|
| 1 — Sa Talaia | Es Dimoni de Sant Joan | The original offended dimoni. Furious, vindictive, dramatic. Appears at the end of World 1 to explain the curse. |
| 2 — Mallorca Romana | Es Dimoni de Manacor | Intense, impatient, fed up with Roman order. Lends power so Ramon can "deal with these organized invaders." |
| 3 — El Comte Mal | Captured dimoni (unnamed, from the Comte's lands) | Imprisoned, weakened. Grateful when freed but doesn't trust Ramon. Hands mask to Llorenç immediately. |
| 4 — Els Pirates | Es Dimoni de Pollenca | Sneaky, nocturnal, whisper-voiced. Fits the stealth theme. Hates the noise pirates make. Historically fitting: Dragut attacked Pollenca in 1550. |
| 5 — S'Invasio | Es Dimoni de Sa Pobla | The most iconic Mallorcan dimoni. Overwhelmed by modernity. Confused by phones. Gives power out of sheer frustration. |

### 3.5 Bosses

| World | Boss | Description |
|-------|------|-------------|
| 1 | **Es Bou de Pedra** | A massive stone bull animated by dimoni energy from a talayotic sanctuary — rooted in the bronze-age bull worship evidenced by Balearic bull figurines. The first real test. After defeating it, the time-travel reveal happens. |
| 2 | **Quintus Caecilius Metellus** | The actual Roman general who conquered the Balearics. Fights from a chariot. Arrogant, tactical. |
| 3 | **El Comte Mal** | A vampire nobleman from Mallorcan legend. Has been siphoning a captured dimoni's power with the help of La Bruixa, an old witch he manipulates. Powerful, aristocratic, cruel. La Bruixa is part of the story (cutscenes, plot) but NOT part of the gameplay fight. |
| 4 | **Dragut** | Famous Ottoman corsair. Ship-to-shore battle. Boisterous, confident, respects strength. |
| 5 | **El Magnat (Phase 1)** | A real estate tycoon in a golden suit. Fought on his luxury hotel rooftop. Uses money and lawyers. Flees to Ibiza when defeated. |
| 5.5 | **El Magnat (Phase 2)** | Empowered by absorbed familiar energy. Bigger, golden, floating. Multi-phase fight testing all mechanics. |

### 3.6 Enemy Types

**World 1 — Sa Talaia**
- Possessed sheep (glowing eyes, aggressive, corrupted by dimoni energy)
- Rival tribal warriors
- Stone guardians (slow, heavy hitters)

**World 2 — Mallorca Romana**
- Roman legionaries (shield formation — must hit from above or behind)
- War dogs (fast, low to ground)
- Tax collectors (weak but steal your sling stones on contact)

**World 3 — El Comte Mal**
- Undead servants (slow, persistent)
- Vampire bats (airborne, swoop patterns)
- Cursed villagers (erratic movement)

**World 4 — Els Pirates**
- Pirates with scimitars (melee rushers)
- Musket snipers (ranged, positioned on ships/towers)
- Powder monkeys (throw bombs, timed explosions)

**World 5 — S'Invasio**
- Aggressive tourists (throw beer cans)
- Real estate agents (chase you with contracts)
- Influencers (camera flash stuns you)
- Party buses (environmental hazard)

**World 5.5 — Eivissa**
- Fameliars — enslaved little demons from the folklore of Santa Eularia, Ibiza. Visually small, imp-like, reminiscent of Dobby from Harry Potter. Artificially created and bound to El Magnat's service. Three variants:
  - **Bottle imps**: Small, fast, swarm in groups
  - **Neon fameliars**: Leave damaging light trails behind them
  - **VIP fameliars**: Larger, have shields (bouncer energy)

---

## 4. GAMEPLAY MECHANICS

### 4.1 Core Moveset

**Movement**
- Left/right movement
- Single jump (baseline)
- Wall jump: automatic — when the player is against a wall and presses jump, Ramon kicks off it. No special input required, triggered by context.

**Sling Combat (the fona)**

The sling has two modes on a single button:

- **Tap attack**: Ramon swings the loaded sling as a melee weapon — short range hit, like a whip crack. Quick, no cost. This is the primary combat tool for close encounters.
- **Hold attack**: Ramon loads a stone and begins charging. The longer the button is held, the more powerful the shot (visual/audio feedback as charge builds). Released when the player lets go. Fires a ranged projectile. **Unlimited basic ammo** — the charge time is the balancing cost. Useful for hitting distant targets, specific boss weak points, and triggering ranged switches/mechanisms.

**Special ammo (power-up rocks)**
- Unlockable rock types with special effects (e.g., explosive rocks, piercing rocks)
- These are **limited by a recharge mechanic** — not unlimited like basic shots
- Recharge can be time-based, kill-based, or tied to collecting specific pickups (to be determined during implementation)
- Bought or found, managed as a resource

### 4.2 Dimoni Mask System

Each world (after World 1) grants a new dimoni mask. The mask fills a single **power-up slot** activated with a dedicated button. Only one mask can be active at a time. Masks are swapped at Llorenç's shop.

| World | Mask | Power | Gameplay Effect |
|-------|------|-------|-----------------|
| 1 — Sa Talaia | Mask of Sant Joan | **Stone Slam** | Ground pound that sends a shockwave along the floor. Damages nearby enemies. Breaks certain floor tiles to reveal secrets below. |
| 2 — Mallorca Romana | Mask of Manacor | **Double Jump** | Grants a second jump in midair. Opens vertical platforming. Reach higher platforms, clear wider gaps. |
| 3 — El Comte Mal | Mask of Fire | **Fire Dash** | Horizontal dash that burns through enemies and wooden barricades. Brief invulnerability during dash frames. Covers distance quickly. |
| 4 — Els Pirates | Mask of Pollenca | **Smoke Vanish** | Brief invincibility and ability to phase through enemies and certain thin walls. Short duration. Evasion and secret-finding tool. |
| 5 — S'Invasio | Mask of Sa Pobla | **Tourist Rage** | Area-of-effect scream that pushes all nearby enemies back and stuns them briefly. Crowd control for the swarm-heavy modern world. |

**Design principle**: Each power changes both combat AND traversal. Powers aren't just for fighting — they open up navigation options. This encourages replaying earlier worlds with later masks to find secrets (optional, not required for completion).

### 4.3 Health & Damage

- **Hearts system** (Zelda-style)
- Ramon starts with **3 hearts**
- **Minimum damage**: Half a heart
- **Maximum damage**: Up to the design team per enemy/boss (calibrated by level design)
- Additional max hearts can be purchased at Llorenç's shop (permanent upgrade, increasingly expensive)
- Hearts are restored by pickups found in levels and by consumables from the shop

### 4.4 Economy — Sling Stones

- **Sling stones (pedres de fona)** are the currency
- Found throughout levels: in breakable objects, dropped by enemies, hidden in secrets
- Spent at Llorenç's shop on consumables, max heart upgrades, and special ammo types
- Tax collectors (World 2 enemy) steal stones on contact — a risk/annoyance mechanic

### 4.5 Consumables & Llorenç's Shop

Consumables are **accessibility tools** — they help less skilled players get past sections they're stuck on without lowering the baseline difficulty for experienced players.

**Consumable types** (examples, to be balanced during implementation):
- Heart refill (restores X hearts)
- Temporary damage boost
- Temporary defense boost
- Temporary invincibility (short duration)
- Special ammo packs (explosive rocks, etc.)

**Permanent purchases**:
- Max heart upgrades (increasingly expensive, capped at a maximum)

**Shop availability**: Llorenç appears between every world and at the save point after each level. His shop inventory may expand as the game progresses.

### 4.6 Difficulty & Accessibility

- Linear difficulty progression across worlds
- No difficulty selector — the baseline is the intended experience
- Consumables serve as the difficulty relief valve: players who are stuck can buy temporary boosts to push through
- The economy is tuned so that a player who explores thoroughly has plenty of stones to buy help when needed
- World 5.5 (Eivissa) is explicitly harder as the endgame challenge

### 4.7 Save System

- **Save after each level** (automatic)
- **No mid-level saves** — dying in a level means restarting that level
- Save data includes: current world/level, collected masks, heart count, stone count, shop purchases
- Death returns the player to the start of the current level with their pre-level state

---

## 5. WORLD DESIGN

### 5.1 Common World Template

Worlds 2-5 follow a repeating structure so the game feels familiar but fresh:

1. **Arrival**: Bep's portal drops Ramon and Bep into the new era. Cutscene: Ramon reacts to the setting, Bep is excited.
2. **Dimoni encounter**: Early in the world (level 1 or 2), the local dimoni appears. Brief dialogue. Grants mask power to Llorenç.
3. **Levels**: A series of platforming/combat levels with increasing difficulty. Each level ends at a save point where Llorenç may appear.
4. **Boss**: Final level is the boss encounter. Preceded by a boss intro cutscene.
5. **Transition**: After the boss, Bep's curse activates. Time portal. Next world.

**World 1 breaks this template** (no prior knowledge of time travel, the reveal is the twist).
**World 5.5 breaks this template** (geographic jump, no new mask, endgame).

### 5.2 World 1 — Sa Talaia (Talayotic Period, ~1000 BC)

- **Setting**: Rocky Mediterranean landscape. Talayots, taulas, navetas. Blue sky, dry stone, olive trees, coastal cliffs. Bronze-age Mallorca.
- **Color palette**: Warm earth tones — ochre, stone grey, olive green, Mediterranean blue.
- **Enemies**: Possessed sheep, rival tribal warriors, stone guardians.
- **Dimoni power acquired**: Stone Slam (Mask of Sant Joan) — but it is acquired differently here. Since the time-travel mechanic isn't revealed yet, the mask is found as an ancient artifact in a talayot rather than given by a dimoni. After the World 1 reveal, the player retroactively understands it was dimoni-related.
- **Level flow**: Horizontal design. Open landscapes, caves, stone structures. Teaches basic movement, sling combat (tap and charge), wall jumping. Bep's dialogue hints are the tutorial.
- **Boss — Es Bou de Pedra**: A massive stone bull animated by dimoni energy from a talayotic sanctuary. Rooted in Balearic bronze-age bull worship (evidenced by talayotic bull figurines). Arena: open stone courtyard surrounded by taulas. Phases:
  - Phase 1: Charges across the arena (dodge/wall jump), shatters stone pillars on impact
  - Phase 2: Stomps ground sending stone shockwaves (jump over), hurls rock debris in arcs
  - Phase 3: Crumbling, exposes a glowing dimoni-energy core — charged sling shots to finish
- **Story beat (post-boss)**: The reveal. Es Bou de Pedra crumbles. Bep glows, sneezes, portal opens. The dimoni de Sant Joan appears and explains the curse. Ramon and Bep are pulled into the portal. The game's real premise begins.

### 5.3 World 2 — Mallorca Romana (Roman Conquest, 123 BC)

- **Setting**: Roman roads cutting through Mallorcan landscape. Amphitheaters, legionary camps, early Palma (Palmaria). Aqueducts, columns, ordered architecture.
- **Color palette**: Stone white, imperial red, laurel green, marble grey.
- **Enemies**: Roman legionaries (shield formations), war dogs, tax collectors.
- **Dimoni power acquired**: Double Jump (Mask of Manacor). Given by Es Dimoni de Manacor, who is intense, impatient, and fed up with Roman order.
- **Llorenç introduction**: Appears early in this world. Has been tracking the time disturbance. Excited to meet Ramon. Ramon is not excited. Shop mechanic introduced here.
- **Level flow**: Vertical design — tall Roman structures, aqueducts to climb, multi-tiered arenas. The double jump is essential for navigation. Hidden paths reward exploration.
- **Boss — Quintus Caecilius Metellus**: Roman general, fights from a chariot. Arena: Roman amphitheater.
  - Phase 1: Chariot charges across the arena (wall jump to dodge), throws pilum volleys (double jump through gaps)
  - Phase 2: Chariot breaks, dismounts for melee combat with gladius and shield
  - Phase 3: Calls in reinforcement soldiers while fighting (crowd management + boss damage)
- **Story beat**: Ramon: "Who paved over my goat path?" Llorenç: "Technically it's a road, and it's quite well-eng—" Ramon: "I didn't ask."

### 5.4 World 3 — El Comte Mal (Feudal Mallorca, Legend-Based)

- **Setting**: Dark feudal Mallorca. The Comte Mal's cursed estates, oppressed villages, gothic manor, eerie forests. Torchlit stone corridors, strange fires burning in the hills.
- **Color palette**: Dark — charcoal, blood red, sickly green, candlelight orange. Highest contrast of any world.
- **Enemies**: Undead servants, vampire bats, cursed villagers.
- **Dimoni power acquired**: Fire Dash (Mask of Fire). The captured dimoni, once freed after the boss fight, grants this mask. The strange fires across the Comte's lands were the dimoni's power leaking through its prison.
- **La Bruixa**: An old woman who maintains the binding ritual that keeps the dimoni imprisoned for the Comte. She appears in cutscenes and story beats. She is a pawn — manipulated or coerced by the Comte — not an enemy. She is NOT a gameplay encounter. She may appear in the boss arena cutscene to provide context but does not participate in the fight.
- **Level flow**: Claustrophobic interiors mixed with eerie outdoor estates. Traps (spike pits, collapsing floors). Darker visual tone — some areas are dimly lit. The fire dash (acquired after the boss) retroactively opens secrets on replay.
- **Boss — El Comte Mal**: Vampire nobleman. Arena: the Comte's great hall, with the imprisoned dimoni visible in chains in the background.
  - Phase 1: Fast melee attacks, teleports around the room, summons bats
  - Phase 2: Drains energy from the chained dimoni to power up, arena hazards intensify (fire pillars from the leaking dimoni energy)
  - Phase 3: Weakened as the dimoni's prison cracks, desperate attacks, must be finished with charged sling shots
- **Story beat**: After defeat, the dimoni is freed. It looks at Ramon. Looks at Bep. Hands its mask to Llorenç. "Keep it away from the sheep." Llorenç: "Fascinating specimen." Ramon: "Can we leave?"

### 5.5 World 4 — Els Pirates (Ottoman/Barbary Raids, 1500s-1600s)

- **Setting**: Coastal Mallorca under siege. Watchtowers, burning fishing villages, pirate ships anchored offshore, hidden coves, moonlit beaches.
- **Color palette**: Midnight blue, sand gold, fire orange, dark wood brown. Moonlit and atmospheric.
- **Enemies**: Scimitar pirates, musket snipers (on ships and towers), powder monkeys (bomb throwers).
- **Dimoni power acquired**: Smoke Vanish (Mask de Pollenca). Given by Es Dimoni de Pollenca — historically fitting since Dragut attacked Pollenca in 1550. Sneaky, nocturnal, whisper-voiced. Hates the noise pirates make.
- **Level flow**: Stealth-flavored. Set around the Pollenca coast where Dragut historically attacked. Some sections reward avoiding enemies rather than fighting. Moonlit exteriors with limited visibility. Ship interiors. The smoke vanish power allows phasing through certain thin walls to find hidden routes.
- **Boss — Dragut**: Famous Ottoman corsair. Arena: starts on the shore, transitions to his ship.
  - Phase 1 (shore): Cannon volleys from the ship — dodge patterns on the beach
  - Phase 2 (boarding): Fight through crew on deck to reach Dragut
  - Phase 3 (duel): One-on-one on the ship deck, Dragut fights with twin scimitars, fast and aggressive. Smoke vanish useful to dodge his combos.
- **Story beat**: Locals beg Ramon to defend the coast. Ramon: "Is there a single century where people leave this island alone?" Bep: "I think they like it here! I like it here too!" Ramon: "You like everything."

### 5.6 World 5 — S'Invasio (Modern Day)

- **Setting**: Modern Mallorca. Magaluf strip, Palma airport, overcrowded beaches, "Se Vende" signs on every traditional house, luxury yachts, concrete hotels built over historic sites.
- **Color palette**: Oversaturated — neon pink, tourist-brochure blue, concrete grey, gold (money). Garish and loud, contrasting all previous worlds.
- **Enemies**: Aggressive tourists (throw beer cans), real estate agents (chase with contracts), influencers (camera flash stuns), party buses (environmental hazard, cross the screen periodically).
- **Dimoni power acquired**: Tourist Rage (Mask of Sa Pobla). Given by Es Dimoni de Sa Pobla — the most iconic Mallorcan dimoni, utterly overwhelmed by modernity and gives the mask out of sheer frustration with everything.
- **Level flow**: Crowd-based. Many weaker enemies on screen at once. Chaotic, noisy environments. The Tourist Rage AoE is essential for crowd control. Wider level design to accommodate groups.
- **Boss — El Magnat (Phase 1)**: Real estate tycoon in a golden suit. Arena: rooftop of an illegally-built luxury hotel overlooking Palma.
  - Phase 1: Throws money bundles that create shockwaves on impact, summons lawyer minions
  - Phase 2: Builds walls around the arena (break with attacks/powers), uses a golden phone to call in reinforcements
  - Phase 3: Cornered, desperate — "You think Mallorca was my endgame? I own IBIZA." Helicopter arrives. He escapes.
- **Story beat**: Ramon sees what's become of the island. "...I think I preferred the pirates." Bep: "What's a hotel?" Ramon: "Where they charge you to sleep." Bep: "You can sleep anywhere!" Ramon: "...I know, Bep."

### 5.7 World 5.5 — Eivissa (Modern Ibiza, Bonus World)

- **Setting**: A nightmarish fusion of the Magnat's mega-resort empire on Ibiza. Ancient Phoenician ruins repurposed as nightclub foundations. Neon lights strung across historic walls. Es Vedra looms in the background. The whole island is the Magnat's domain.
- **Color palette**: Electric — neon purple, toxic green, black, gold. The most visually aggressive world.
- **Enemies**: Fameliars — enslaved little demons from the folklore of Santa Eularia des Riu, Ibiza. Small, imp-like creatures (Dobby-like), artificially created and bound to the Magnat's service. Three variants:
  - **Bottle imps**: Small, fast, attack in swarms
  - **Neon fameliars**: Leave damaging neon light trails as they move
  - **VIP fameliars**: Larger, carry shields (bouncer energy), block paths
- **No new dimoni power**: The player must use all previously collected masks strategically. Llorenç's shop becomes critical — swapping masks for different sections is required.
- **Length**: 3-4 levels (shorter than a full world) but significantly harder. Endgame challenge.
- **Boss — El Magnat (Phase 2)**: Empowered by absorbed familiar energy. Arena: the top of his mega-resort, Ibiza skyline behind.
  - Phase 1: Money attacks + familiar summons (combine crowd control with boss damage)
  - Phase 2: Grows larger, golden aura, arena shrinks as edges crumble — familiar energy attacks in patterns
  - Phase 3: Full power. Multi-mechanic test — requires using the right mask at the right moment (stone slam to break his platform, double jump to reach him, fire dash through his barrier, smoke vanish through his attacks, tourist rage to clear familiar waves)
  - On defeat: "Everyone has a price!" Ramon: "I don't even know what money is."
- **Story beat**: The final confrontation. After the Magnat falls, his empire literally crumbles. The curse breaks. Bep stops glowing. Ramon can finally go home.

---

## 6. BOSS DESIGN

### 6.1 Common Boss Design Principles

- Every boss has **3 phases** with escalating difficulty and changing patterns
- Each phase has clear **tells** before attacks (visual/audio cues) so the player can learn and react
- Bosses test the **mechanics introduced in their world** — the current dimoni power should be useful (but not strictly required) during the fight
- Boss arenas are unique environments, not reused level geometry
- Every boss has a brief **intro cutscene** with personality-establishing dialogue
- Health is visible (boss health bar at top of screen)
- Half-heart minimum damage means bosses can have chip-damage moves and heavy-hit moves

### 6.2 Per-Boss Summary

| Boss | World | Mechanics Tested | Arena | Phases Summary |
|------|-------|-----------------|-------|---------------|
| Es Bou de Pedra | 1 | Basic movement, jump, sling (tap + charge) | Stone courtyard (taulas) | Charge dodging → stone shockwave jumping → core sniping |
| Quintus Metellus | 2 | Wall jump, double jump, crowd management | Roman amphitheater | Chariot dodging → melee duel → reinforcement waves |
| El Comte Mal | 3 | Sling timing, arena awareness | Gothic great hall | Teleport melee → powered-up hazards → desperate finish |
| Dragut | 4 | Smoke vanish, platforming, combat | Shore → ship deck | Cannon patterns → ship boarding → fast melee duel |
| El Magnat P1 | 5 | Tourist rage, crowd control | Hotel rooftop | Money shockwaves → arena manipulation → escape cutscene |
| El Magnat P2 | 5.5 | ALL masks, all mechanics | Mega-resort peak | Familiar waves → shrinking arena → multi-mask test |

---

## 7. ART DIRECTION

### 7.1 Visual Style & Constraints

- 16-bit pixel art (SNES era reference)
- Pixel-perfect rendering at base resolution (320x180 or 384x216), scaled to display
- Limited color palette per world (8-16 dominant colors) for visual cohesion and retro authenticity
- No anti-aliasing, no sub-pixel rendering — hard pixel edges

### 7.2 Sprite Size Guidelines

- **Ramon**: 24x32 pixels (or similar, proportional to a stocky warrior)
- **Bep**: 16x16 pixels (small, round, always near Ramon)
- **Standard enemies**: 16x24 to 24x32 pixels depending on type
- **Bosses**: 48x48 to 96x96+ pixels (large, imposing)
- **Tiles**: 16x16 pixel grid

### 7.3 Color Palettes per World

| World | Dominant Colors | Mood |
|-------|----------------|------|
| 1 — Sa Talaia | Ochre, stone grey, olive green, Mediterranean blue | Warm, natural, open |
| 2 — Mallorca Romana | Stone white, imperial red, laurel green, marble grey | Ordered, grand |
| 3 — El Comte Mal | Charcoal, blood red, sickly green, candlelight orange | Dark, gothic, oppressive |
| 4 — Els Pirates | Midnight blue, sand gold, fire orange, dark wood | Atmospheric, moonlit |
| 5 — S'Invasio | Neon pink, brochure blue, concrete grey, gold | Garish, oversaturated |
| 5.5 — Eivissa | Neon purple, toxic green, black, gold | Electric, aggressive |

### 7.4 Character Sprite Sheets

Each character needs a sprite sheet covering:
- Idle (with idle variations/breathing)
- Walk/run cycle
- Jump (ascending + descending)
- Wall slide
- Attack (sling tap — quick swing)
- Attack (sling charge — visible charge-up + release)
- Damage taken (hit stun)
- Death
- Mask-specific power animations (one per mask)
- Bep: idle variations (chewing, sleeping, startled, talking, glowing)

### 7.5 Tileset Guidelines

- One tileset per world (ground, walls, platforms, decorations, breakables)
- Each tileset must include: solid tiles, one-way platforms, breakable tiles (for Stone Slam), thin walls (for Smoke Vanish), wooden barricades (for Fire Dash)
- Background layers: parallax scrolling (2-3 layers per world)

### 7.6 UI/HUD Visual Design

- Hearts displayed top-left
- Current mask icon displayed top-right (with cooldown indicator if applicable)
- Sling stone count displayed below mask icon
- Special ammo indicator (if equipped) near stone count with recharge visual
- Minimal UI — retro clean, no clutter

---

## 8. AUDIO DIRECTION

### 8.1 Music System Architecture

Music is **mocked and stubbed** for initial development. The audio system must be built so that any music track can be trivially dropped in.

- All music playback goes through a central **AudioManager**
- Each music slot is a **named reference** pointing to a file path (or silence/placeholder)
- Replacing a track means changing a file path in a configuration file or dropping a file into the correct folder — no code changes required
- Supported formats: .ogg, .mp3, .wav

### 8.2 Audio Slot Definitions

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

### 8.3 SFX List

Sound effects needed (also mocked/stubbed with simple placeholder sounds):

```
sling_tap          — melee swing
sling_charge       — charging loop (pitch rises with charge level)
sling_release      — stone fired
stone_hit          — stone impacts enemy/surface
jump               — basic jump
double_jump        — second jump (slightly different sound)
wall_jump          — kick off wall
land               — landing on ground
damage_taken       — Ramon hit
heart_pickup       — health restored
stone_pickup       — currency collected
mask_equip         — swapping dimoni mask
power_stone_slam   — ground pound
power_fire_dash    — dash woosh + fire
power_smoke_vanish — poof/smoke
power_tourist_rage — scream/shockwave
bep_bleat          — Bep's general sound
bep_sneeze         — time portal trigger
portal_open        — time portal opening
boss_intro         — boss appears
boss_hit           — boss takes damage
boss_death         — boss defeated
menu_select        — UI navigation
menu_confirm       — UI confirm
```

### 8.4 How to Replace Placeholder Audio

1. Place the audio file in the appropriate folder (`assets/audio/music/` or `assets/audio/sfx/`)
2. Update the audio configuration file (or name the file to match the slot name)
3. The AudioManager picks it up automatically on next load

No code changes needed. The system is hot-swappable during development.

---

## 9. UI & UX

### 9.1 HUD Layout

```
[Heart][Heart][Heart]                    [Mask Icon]
                                         [Stone: 042]
                                         [Ammo: 3/5]
```

- Top-left: Hearts (current and max, half-heart granularity)
- Top-right: Current dimoni mask icon, sling stone count, special ammo count with recharge indicator
- Minimal, non-intrusive, retro-styled

### 9.2 Dialogue System

- **Text boxes** at the bottom of the screen (classic JRPG style)
- **Character portrait** on the left side of the text box (pixel art, expressive)
- Text appears letter-by-letter (skippable with button press)
- Bep's dialogue is frequent but always short (1-2 lines max)
- All dialogue is optional-feeling — never blocks gameplay for long
- Boss intros are unskippable on first encounter, skippable on retry

### 9.3 Shop Interface

- Llorenç's shop is a dedicated screen (not in-level overlay)
- Two tabs: **Masks** (swap active dimoni power) and **Items** (buy consumables/upgrades)
- Each mask shows: icon, name, power description, button prompt
- Items show: name, effect, cost in sling stones
- Llorenç has optional dialogue for each mask/item (lore tidbits, one-liners)
- Bruna visible in the background. Bep hides behind Ramon if Bruna is on screen.

### 9.4 Pause Menu

- Pause available at any time during gameplay
- Options: Resume, Items (use consumables), Controls, Quit to Menu
- No mid-level saving from pause — pause is just a pause

### 9.5 World Transition Screens

- After boss defeat + Bep's portal: a brief animated cutscene of the portal opening and the characters being pulled in
- Loading screen: pixel art vignette of the next era with the world name and date
- Arrival: brief cutscene of Ramon and Bep arriving, reacting to the new setting

---

## 10. TECHNICAL ARCHITECTURE

### 10.1 Pygame Structure Overview

- Main game loop: input → update → render at 60 FPS
- Scene/state-based architecture (menu, gameplay, dialogue, shop, cutscene, boss)
- All game logic separated from rendering

### 10.2 Game States & Scene Management

```
MAIN_MENU → WORLD_SELECT (after first completion) → GAMEPLAY → DIALOGUE
     ↕              ↕                                    ↕         ↕
  SETTINGS       CREDITS                              PAUSE      SHOP
                                                        ↕
                                                    GAME_OVER
```

- State machine with push/pop stack (e.g., GAMEPLAY → push PAUSE → pop back to GAMEPLAY)
- Transitions between states are handled by a central scene manager

### 10.3 Sprite & Animation System

- Sprite sheets loaded and sliced into frames
- Animation defined as frame sequences with per-frame duration
- State-driven animation (idle, walk, jump, attack, etc.)
- Animation controller per entity, driven by game state

### 10.4 Tilemap & Level Format

- Tile-based levels using a standard format (Tiled .tmx or custom JSON)
- Layers: background, midground (collision), foreground (decoration), entities (spawn points)
- Collision layer defines solid, one-way, breakable, and phase-through tiles
- Levels are data files, not code — editable externally

### 10.5 Collision System

- Axis-aligned bounding box (AABB) collision
- Separate collision layers for: terrain, enemies, projectiles, triggers
- Wall jump detection: check for wall collision while airborne + jump input
- Phase-through (Smoke Vanish): temporarily disable enemy/thin-wall collision

### 10.6 Audio Manager

- Centralized AudioManager class
- Named slots for music and SFX (see Section 8)
- Configuration-driven: a single file maps slot names to file paths
- Methods: play_music(slot), stop_music(), play_sfx(slot)
- Graceful fallback: if a file is missing, log a warning and play silence — never crash
- Volume controls accessible from settings

### 10.7 Save System

- **Save trigger**: Automatic at the end of each level (after the level-complete screen)
- **No mid-level saves**
- **Save data**: Current world, current level, collected masks, current max hearts, sling stone count, purchased upgrades, special ammo state
- **Death behavior**: Restart current level with pre-level-start state (stones and hearts as they were when the level began)
- **Storage**: Local file (JSON or similar), single save slot (expandable later)

### 10.8 Performance Targets

- 60 FPS on modest hardware (the game is pixel art with simple physics — performance should not be an issue)
- Pygame's sprite groups for efficient rendering
- No heavy computation per frame — all physics is simple AABB
- Asset loading: per-world, loaded on world transition, not all at once
