# Sa Fona — Asset Prompts (World 1: Sa Talaia)

**Scope**: This file covers World 1 — Sa Talaia (talayotic Balearic, Bronze
Age Mallorca). It contains the W1 boss, all W1 enemies (with their attack
effect overlays), W1 NPCs, W1 tilesets and backgrounds, W1 environment props,
W1 NPC portraits, the W1 dimoni-aura effect, and the W1 generation order.

For cross-world assets (Balchar, Bep, generic pickups, breakables,
projectiles, generic effects, UI, title/game-over screens, ground shadow,
and the **Frame-size convention** + **Global style block**), see
[`shared.md`](shared.md). World files reference the shared conventions and
palettes; the W1 prompts here build on them.

For the workflow, processing pipeline, and "how to add a new asset"
instructions, see [`../asset_generation_guide.md`](../asset_generation_guide.md).

If you find prompt content **outside `docs/asset_prompts/`**, it is a bug —
file an Issue.

---

## Scope statement

This file is **prompts only** for World 1 assets. Conventions (frame-size
3-layer rule, global style block, `[ATTACH MASTER IDLE SPRITE HERE]` marker,
generation rules) live once in [`shared.md`](shared.md) and apply equally
here.

---

## Style chain (World 1)

```
Balchar (master) -> Bep -> Bou de Pedra (boss)
                          -> Stone Guardian
                          -> Rival Warrior
                          -> Possessed Sheep
                          -> Dimoni (NPC)
                          -> Llorenç (NPC)
```

Generate in this order so each asset inherits the established visual identity.
Full generation order is at [§ 21 below](#21-generation-order-world-1).

---

# Table of contents (World 1)

- [3. Bou de Pedra (W1 boss)](#3-bou-de-pedra-world-1-boss) — 3 phase idles + attacks + arena props
- [4. Stone Guardian (enemy)](#4-stone-guardian-enemy) — idle, walk, attack, hit, death
- [5. Rival Warrior (enemy)](#5-rival-warrior-enemy) — idle, walk, attack, block, hit, death
- [6. Possessed Sheep (enemy)](#6-possessed-sheep-enemy) — idle, walk, charge, hit, death
- [7. Dimoni de Sant Joan (NPC)](#7-dimoni-de-sant-joan-npc) — idle, laugh, grant, angry
- [8. Llorenç (NPC — Shopkeeper)](#8-llorenç-npc--shopkeeper) — idle, talk, shop
- [12. Dimoni aura effect (W1)](#dimoni-aura-effect-w1)
- [13. Attack effect overlays (W1 enemies)](#13-attack-effect-overlays) — Stone Guardian sweep, Rival slash
- [14. Environment props (W1)](#14-environment-props) — bonfire, taula gate
- [15. Tilesets (W1)](#15-tilesets) — outdoor, cave, talayot
- [16. Backgrounds (W1)](#16-backgrounds) — outdoor, cave, talayot
- [17. Dialogue portraits (W1 NPCs)](#17-dialogue-portraits-w1-npcs) — Dimoni (3), Llorenç (3)
- [21. Generation order (World 1)](#21-generation-order-world-1)

> Section numbering follows the original consolidated file so external
> references (PRs, Issues, code docstrings) keep working. Cross-world sections
> (1, 2, 9, 10, 11, 12 generic, 17 cross-world portraits, 18, 19, 20, 22)
> live in [`shared.md`](shared.md).

---

# 3. Bou de Pedra (World 1 boss)

**Hitbox**: 40x36
**Processed output size** (from `boss_bou_de_pedra.json`): 80x72 per frame

**Editable finals**:
[Bou de Pedra source index](../../assets/ai_sources/boss_bou_de_pedra/README.md).
Ten native 80x72 RGBA files contain 25 frames in total. The three phase idles
retain their aligned ground registration; all sources retain the existing
alpha cleanup, and rush retains the polished neck/leg joins. No additional
cleanup, redraw, rescaling, or palette clamp is part of consolidation; see the
[approved-source exception](../asset_generation_guide.md#1-global-palette-lock).
The 40x36 prompt grid below is separate from the native 80x72 canvas.

Native editor durations: rush 100 ms per frame, every other animation 250 ms
per frame. Non-idle 250 ms values are editor-preview defaults, **not runtime
attack/recovery timing**. Runtime PNGs/configs still contain two rush frames;
the engine manifest also has separate legacy death/hurl metadata. Integration
requires an explicit PNG/config/manifest update, not reinterpretation of these
source files as runtime-ready replacements.

**Palette** (`assets/palettes/bou_de_pedra.gpl` — 12 colors):

```
144 144 144  Stone base / Phase 1 accent
176 176 176  Stone highlight
104 104 112  Stone dark
 72  72  80  Stone darkest
 56  56  64  Crack lines
224 200  56  Rune glow neutral
248 240 120  Rune glow bright
224 144  40  Phase 2 accent (fiery orange)
224  40  40  Phase 3 accent (enraged red)
120 112  96  Horn base
 88  80  72  Horn dark
 64  88  48  Moss accent
```

**Reference character**: Balchar (same world, same era — Bou is the first non-player
character generated for World 1, establishing the enemy visual tone). See
[`shared.md` § 1.1](shared.md#11-balchar--master-idle-generate-first) for the
Balchar master idle.

## 3.1 Bou de Pedra — Master Idle Phase 1 (GENERATE FIRST) — 4 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Balchar (talayotic Balearic, Bronze Age)
  - Same shading logic and pixel density as Balchar
  - Same outline treatment
  - Different identity: Balchar is human, Bou is a stone construct

CHARACTER IDENTITY:
  - Name:        Es Bou de Pedra (The Stone Bull)
  - Role:        World 1 Boss — animated stone bull guardian
  - Culture:     Talayotic bronze-age bull worship figurines
  - Inspiration: Mediterranean limestone carved into bull form

VISUAL DETAILS:
  - Body:        Giant bull shape built from rough-hewn limestone blocks
  - Horns:       Massive curved stone horns
  - Features:    No organic features — purely stone and magical energy
  - Details:     Glowing amber/yellow energy visible in cracks between stone segments
                 (dimoni energy animating it). Patches of moss on stone surface.
  - Phase 1:     Grey stone, neutral amber rune glow, calm but imposing
  - Expression:  Eyeless — menace conveyed through posture and glowing cracks

PALETTE (use ONLY these 12 colors):
  144,144,144  Stone base
  176,176,176  Stone highlight
  104,104,112  Stone dark
  72,72,80     Stone darkest
  56,56,64     Crack lines
  224,200,56   Rune glow neutral
  248,240,120  Rune glow bright
  224,144,40   Phase 2 accent (DO NOT USE in Phase 1)
  224,40,40    Phase 3 accent (DO NOT USE in Phase 1)
  120,112,96   Horn base
  88,80,72     Horn dark
  64,88,48     Moss accent

  Phase 1 uses: stone colors + neutral rune glow + horns + moss. No orange/red.

SPRITE CONSTRAINTS:
  - Sheet size:  160x36 (4 frames)
  - Frame size:  40x36 each
  - Facing:      RIGHT (facing the player)
  - Animation:   Breathing-like stone expansion + rune glow pulsing across 4 frames

BACKGROUND: Solid green (#00FF00)

IMPORTANT:
This is the MASTER reference for the boss. All boss animations and phase
variants must match this base design. The phase progression adds color
accents but does NOT change the stone structure.
```

## 3.2 Bou de Pedra — Idle Phase 2 (4 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — same stone bull as Phase 1 MASTER, exact same structure.

PALETTE: Same 12 colors, but now INCLUDE the Phase 2 accent (224,144,40 fiery orange).
  Replace some neutral amber rune glow areas with orange glow.
  Stone structure and shape is IDENTICAL to Phase 1.

Sheet: 160x36 (4 frames). Frame size: 40x36. Facing RIGHT.

Phase 2 visual change: Rune cracks glow orange instead of amber.
Stone surface unchanged. More energy visible in cracks. Bull appears more agitated.
Frames cycle the orange glow pulsing brighter/dimmer.

Background: solid green (#00FF00)
```

## 3.3 Bou de Pedra — Idle Phase 3 (4 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — same stone bull, exact same structure.

PALETTE: Same 12 colors, now INCLUDE Phase 3 accent (224,40,40 enraged red).
  Rune cracks glow red. Exposed glowing red core visible in chest area.
  Stone surface shows more cracks. Most aggressive appearance.

Sheet: 160x36 (4 frames). Frame size: 40x36. Facing RIGHT.

Phase 3 visual change: Red glowing cracks, exposed red weak point in chest,
stone surface more fractured. Maximum energy discharge look. Frames cycle
the red core pulsing intensely.

Background: solid green (#00FF00)
```

## 3.4 Bou de Pedra — Rush Attack (4 frames)

> Reference: [ATTACH BOU IDLE_P3 FRAME 1 HERE]

Native source: [rush.aseprite](../../assets/ai_sources/boss_bou_de_pedra/rush.aseprite),
tag `rush`, frames 1-4; **4 x 100 ms = 400 ms** cycle. Reference
[idle_p3.aseprite](../../assets/ai_sources/boss_bou_de_pedra/idle_p3.aseprite)
frame 1. The lowered head/horns and torso stay fixed through the cycle; limb
articulation supplies the contact, compression, hindpush, and gather phases.
Five editable layers retain the body, head/horns, near legs, far legs, and tail.

```
CRITICAL IDENTITY LOCK — same stone bull design.
Use Bou idle_p3 frame 1 as the explicit reference baseline for proportions,
silhouette, crack topology, horn shape, and face profile.
PALETTE: Preserve the provided idle_p3 frame 1 red-orange glow and existing
colors; no additional palette clamp for Aseprite edit.

Sheet: 160x36 (4 frames) at source resolution (40x36 per frame).
Native export target: 320x72 sheet (80x72 per frame).
Facing RIGHT.
Preview timing (editor only): 4x100ms.

Preserve identity stability across all frames: red-cracked, stocky stone bull;
no anatomy drift, no horn-length drift, no body-mass drift.

  Frame 1 (contact): front hoof contact and weight transfer; head lowered,
                     horns forward; initial forward bite into the rush
  Frame 2 (compression): forelegs absorb weight below the fixed lowered head
                         and torso; no body-compression squash
  Frame 3 (hindpush): rear-leg drive and extension; strongest propulsion,
                      consistent body anchor, no cel horizontal displacement
  Frame 4 (gather/seam): recovery/gather step that resets limb spacing with a
                         clean seam into Frame 1 (no pop)

Background: solid green (#00FF00)
```

## 3.5 Bou de Pedra — Headbutt (2 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Wind-up — head pulled back, body coiled, preparing to strike
  Frame 2: Impact — head thrust forward and down, horns at strike point,
           body extended, shockwave implied

Background: solid green (#00FF00)
```

## 3.6 Bou de Pedra — Stomp (2 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Raised — front legs lifted high, body rearing up
  Frame 2: Impact — front legs slammed down, shockwave lines implied at ground level

Background: solid green (#00FF00)
```

## 3.7 Bou de Pedra — Hurl (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Head tossing motion — flinging a rock projectile with horns,
head angled upward in throwing arc, rock departing from horn tips.

Background: solid green (#00FF00)
```

## 3.8 Bou de Pedra — Stunned (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Dazed — head lowered and swaying, legs wobbling slightly spread,
cracks in stone more visible, energy glow dimmed. Vulnerable state.

Background: solid green (#00FF00)
```

## 3.9 Bou de Pedra — Death (2 frames)

Native source: [death.aseprite](../../assets/ai_sources/boss_bou_de_pedra/death.aseprite),
two 80x72 frames at 250 ms each. This is the source timeline; the engine
manifest's legacy one-frame entry is not updated by source consolidation.

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Crumbling — stone blocks separating and falling apart,
           energy fading from cracks, collapse in progress. Head tilted down,
           legs buckling. Not fully destroyed — mid-collapse moment.
  Frame 2: Remaining collapse fragments and debris.

Background: solid green (#00FF00)
```

## 3.10 Bou de Pedra — Transition (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Phase transition — bull roaring/bellowing, head thrown back,
energy surging through all cracks simultaneously (bright glow everywhere),
stone vibrating. Dramatic power-up moment between phases.

Background: solid green (#00FF00)
```

## 3.11 Bou de Pedra — Arena Props

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE — for stone material match]

> **Cross-world note**: boss arena props (pillars, projectile, shockwave,
> pulse, shadow) are scoped to the Bou de Pedra arena and therefore live in
> this W1 file. Future bosses bring their own arena props in their world file.

```
Create a SNES-style 16-bit pixel art prop sheet.

STYLE: Must match the Bou de Pedra boss — same stone material, same shading,
same outline treatment. These are props in the boss arena.

PALETTE (use ONLY these 12 colors — same as Bou de Pedra):
  144,144,144  Stone base / Phase 1 accent
  176,176,176  Stone highlight
  104,104,112  Stone dark
  72,72,80     Stone darkest
  56,56,64     Crack lines
  224,200,56   Rune glow neutral
  248,240,120  Rune glow bright
  224,144,40   Phase 2 accent (fiery orange)
  224,40,40    Phase 3 accent (enraged red)
  120,112,96   Horn base
  88,80,72     Horn dark
  64,88,48     Moss accent

Generate the following 6 props, each as a separate image on the sheet:

PILLAR INTACT (16x48):
  Tall stone pillar, rough-hewn limestone matching the boss arena.
  Subtle rune markings. Structurally solid.

PILLAR DESTROYED (16x48):
  Same pillar but broken — top half shattered, rubble at base,
  broken stone edges. Cracks visible.

ROCK PROJECTILE (8x8):
  Small rough stone chunk hurled by the boss.
  Angular, grey stone with slight moss.

SHOCKWAVE (16x8):
  Ground impact wave — expanding arc of dust and stone debris
  at ground level. Horizontal spread.

PULSE (24x16):
  Energy pulse emanating from boss — circular expanding ring
  of amber/orange energy.

SHADOW (16x6):
  Simple dark elliptical shadow cast beneath the boss.

BACKGROUND: Solid green (#00FF00) for all props.

LAYOUT: Arrange all 6 props in a single row with clear green spacing between them.
Total sheet width should accommodate all props with gaps.
```

---

# 4. Stone Guardian (enemy)

**Hitbox**: 24x32
**Processed output size**: 48x64 per frame

**Palette** (`assets/palettes/stone_guardian.gpl` — 9 colors):

```
128 128 136  Stone base
152 152 152  Stone light
 96  96 104  Stone dark
 80  80  88  Stone very dark
 80 200  80  Eye glow            <- GREEN (not amber)
120 248 120  Eye bright
 72  96  56  Moss
 88 120  72  Moss light
 56  56  64  Crack
```

**Reference**: Bou de Pedra (both are stone constructs animated by dimoni energy —
closest visual relative). Note: the Stone Guardian has **GREEN** glowing eyes
(palette color `80,200,80`), distinguishing it from the boss's amber/orange.

## 4.1 Stone Guardian — Master Idle (GENERATE FIRST) — 2 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Bou de Pedra (World 1 boss)
  - Same shading logic, pixel density, and outline treatment
  - Shares the "animated stone" visual language with the boss but is a
    humanoid shape rather than a bull shape. Smaller and simpler.

CHARACTER IDENTITY:
  - Role:          Heavy enemy — animated stone golem
  - Culture:       Talayotic stone guardian, dimoni energy animated
  - Differentiators: Humanoid (not bull). Massive rough-hewn dark grey limestone blocks.
                     Glowing GREEN eyes (not amber like boss). No face — just a vaguely
                     head-shaped block on top. Very heavy, slow-looking.

VISUAL DETAILS:
  - Body:    Massive humanoid built from rough limestone blocks
  - Head:    Featureless stone block, no face
  - Eyes:    Glowing green energy (key visual)
  - Arms:    Heavy stone fists
  - Details: Cracks between stone segments, patches of moss
  - Size:    Large — 24x32 pixels

PALETTE (use ONLY these 9 colors):
  128,128,136  Stone base
  152,152,152  Stone light
  96,96,104    Stone dark
  80,80,88     Stone very dark
  80,200,80    Eye glow            <- GREEN
  120,248,120  Eye bright
  72,96,56     Moss
  88,120,72    Moss light
  56,56,64     Crack

SPRITE CONSTRAINTS:
  - Sheet size:  48x32 (2 frames)
  - Frame size:  24x32 each
  - Facing:      RIGHT
  - Animation:   Idle — slow breathing-like stone expansion, green eyes pulsing

BACKGROUND: Solid green (#00FF00)
```

## 4.2 Stone Guardian — Walk (3 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — match Stone Guardian MASTER idle.
PALETTE: Same 9 colors.
Sheet: 72x32 (3 frames). Frame size: 24x32. Facing RIGHT.
Heavy lumbering walk — slow, deliberate, ground-shaking implied.
Each step is a heavy stomp. Body barely sways. Arms swing minimally.
Background: solid green (#00FF00)
```

## 4.3 Stone Guardian — Attack (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 48x32 (2 frames). Frame size: 24x32. Facing RIGHT.
  Frame 1: Attack tell — arm raised high, massive stone fist pulled back overhead,
           green eyes blazing brighter. (Important: tell duration is 1.0s in-game,
           giving the player time to react. Design this frame to read as a
           clear "windup" pose.)
  Frame 2: Arm sweep — wide horizontal sweep with stone fist, ground-level arc
Background: solid green (#00FF00)
```

## 4.4 Stone Guardian — Hit (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 24x32 (1 frame). Facing RIGHT.
Pose: Stone chips flying off — body rocked backward slightly,
cracks more visible from impact. Green eyes flicker.
Background: solid green (#00FF00)
```

## 4.5 Stone Guardian — Death (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 24x32 (1 frame). Facing RIGHT.
Pose: Crumbling apart — stone blocks separating, green eye glow fading,
collapsing into rubble pile. Mid-collapse moment.
Background: solid green (#00FF00)
```

---

# 5. Rival Warrior (enemy)

**Hitbox**: 16x24
**Processed output size**: 32x48 per frame

**Design rationale**: The Rival Warrior has a **30% block chance** in combat —
the `block.png` frame is therefore not decorative, it shows up in real
gameplay regularly and must read clearly as a defensive stance.

**Palette** (`assets/palettes/rival_warrior.gpl` — 12 colors):

```
112  72  40  Skin
 88  56  32  Skin shadow / legs shadow
224 208 200  Eye white
 32  24  16  Pupil
 48  32  24  Hair dark
 72  48  32  Hair highlight
144  96  56  Hide armor
120  88  48  Armor shadow
 96  72  40  Leather strap / legs
160 152 128  Weapon stone
136 128 112  Weapon shadow
 80  56  32  Feet
```

**Reference**: Bou de Pedra (World 1 boss — style anchor).

## 5.1 Rival Warrior — Master Idle (GENERATE FIRST) — 2 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Bou de Pedra (World 1 boss)
  - Same shading logic and pixel density
  - Same outline treatment
  - Different creature: human warrior vs stone bull — but same visual world

CHARACTER IDENTITY:
  - Role:          Mid-tier enemy — hostile tribal warrior
  - Culture:       Competing talayotic tribe (same Balearic Bronze Age as Balchar)
  - Differentiators: Human fighter with stone weapons and animal hide armor.
                     Slightly taller and leaner than Balchar.
                     Darker skin, messy dark hair with war paint stripes on face.

VISUAL DETAILS:
  - Body:      Lean warrior build, slightly taller than Balchar
  - Clothing:  Dark brown animal hide armor/tunic, leather arm wrappings
  - Weapon:    Stone club held in one hand
  - Hair:      Messy dark hair, no headband
  - Face:      War paint stripes, hostile expression
  - Skin:      Darker tanned
  - Feet:      Leather foot wrappings

PALETTE (use ONLY these 12 colors):
  112,72,40    Skin
  88,56,32     Skin shadow / legs shadow
  224,208,200  Eye white
  32,24,16     Pupil
  48,32,24     Hair dark
  72,48,32     Hair highlight
  144,96,56    Hide armor
  120,88,48    Armor shadow
  96,72,40     Leather strap / legs
  160,152,128  Weapon stone
  136,128,112  Weapon shadow
  80,56,32     Feet

SPRITE CONSTRAINTS:
  - Sheet size:  32x24 (2 frames)
  - Frame size:  16x24 each
  - Facing:      RIGHT
  - Animation:   Idle — combat-ready stance, weapon held at side, slight sway

BACKGROUND: Solid green (#00FF00)

IMPORTANT: Different identity, indistinguishable style.
```

## 5.2 Rival Warrior — Walk (4 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — match Rival Warrior MASTER idle.
PALETTE: Same 12 colors.
Sheet: 64x24 (4 frames). Frame size: 16x24. Facing RIGHT.
Patrol walk — weapon at side, alert stance, deliberate stride.
Background: solid green (#00FF00)
```

## 5.3 Rival Warrior — Attack (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 32x24 (2 frames). Frame size: 16x24. Facing RIGHT.
  Frame 1: Wind-up — club raised overhead
  Frame 2: Swing down — club striking forward/down
Background: solid green (#00FF00)
```

## 5.4 Rival Warrior — Block (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Defensive — club held horizontally to block, body braced.
(Design note: appears in ~30% of incoming attacks; must read as block at a glance.)
Background: solid green (#00FF00)
```

## 5.5 Rival Warrior — Hit (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Struck — body recoiling backward, weapon arm dropping.
Background: solid green (#00FF00)
```

## 5.6 Rival Warrior — Death (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Collapsed — fallen to the ground, weapon dropped beside body.
Background: solid green (#00FF00)
```

---

# 6. Possessed Sheep (enemy)

**Hitbox**: 16x16
**Processed output size**: 32x32 per frame

**Palette** (`assets/palettes/possessed_sheep.gpl` — 8 colors):

```
232 232 224  Wool light
208 208 192  Wool mid
184 184 168  Wool dark
184 160 144  Face / body
224  48  48  Eye (possessed red)
248  96  80  Eye glow
 88  64  48  Hoof
184 168 144  Horn
```

**Reference**: Bou de Pedra (boss of the world — style anchor for all World 1 enemies).
Despite being a different creature (sheep vs stone bull), the pixel art style,
shading logic, and outline treatment must be indistinguishable.

## 6.1 Possessed Sheep — Master Idle (GENERATE FIRST) — 2 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Bou de Pedra (World 1 boss)
  - Same shading logic and pixel density
  - Same outline treatment
  - Different creature: sheep (organic, wool) vs bull (stone construct)

CHARACTER IDENTITY:
  - Role:          Common enemy — corrupted Mediterranean sheep
  - Culture:       Talayotic Balearic (same era as Balchar)
  - Differentiators: Small woolly body, glowing red possessed eyes,
                     hunched aggressive stance. NOT a stone creature —
                     this is an organic animal corrupted by dimoni energy.

VISUAL DETAILS:
  - Body:   White-grey woolly sheep, small and round
  - Eyes:   Glowing red (key visual — shows possession)
  - Horns:  Small curved horns
  - Stance: Hunched, aggressive, ready to charge
  - Size:   Small — fits in 16x16

PALETTE (use ONLY these 8 colors):
  232,232,224  Wool light
  208,208,192  Wool mid
  184,184,168  Wool dark
  184,160,144  Face / body
  224,48,48    Eye (possessed red)
  248,96,80    Eye glow
  88,64,48     Hoof
  184,168,144  Horn

SPRITE CONSTRAINTS:
  - Sheet size:  32x16 (2 frames)
  - Frame size:  16x16 each
  - Facing:      RIGHT
  - Animation:   Idle — slight wool ruffle, menacing stance

BACKGROUND: Solid green (#00FF00)

IMPORTANT: Different identity, indistinguishable style from other World 1 assets.
```

## 6.2 Possessed Sheep — Walk (4 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — match Possessed Sheep MASTER idle.
PALETTE: Same 8 colors.

Sheet: 64x16 (4 frames). Frame size: 16x16. Facing RIGHT.

  Frame 1-4: Trotting gait — aggressive forward lean, hooves alternating,
  wool bouncing, red eyes always visible and glowing.
  Faster and more aggressive than a normal sheep walk.

Background: solid green (#00FF00)
```

## 6.3 Possessed Sheep — Charge (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 32x16 (2 frames). Frame size: 16x16. Facing RIGHT.

  Frame 1: Head lowered, horns forward, legs coiled, about to launch
  Frame 2: Full charge — body horizontal, legs in full sprint, head-down ram attack

Background: solid green (#00FF00)
```

## 6.4 Possessed Sheep — Hit (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 16x16 (1 frame). Facing RIGHT.
Pose: Recoil — body knocked back, wool puffed out, eyes squinted.

Background: solid green (#00FF00)
```

## 6.5 Possessed Sheep — Death (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 16x16 (1 frame). Facing RIGHT.
Pose: Collapsed on side, eyes closed (no longer glowing red),
dimoni energy dissipating. Looks like a normal sleeping sheep.

Background: solid green (#00FF00)
```

---

# 7. Dimoni de Sant Joan (NPC)

**Hitbox / source size**: 24x40

**Palette** (`assets/palettes/dimoni.gpl` — 12 colors):

```
 72  24  56  Dark body base
 48  16  40  Body shadow
200  48  32  Fiery red accent
240  96  40  Orange fire glow
248 232  56  Glowing eyes
248 200  32  Eye outer glow
104  40  88  Purple mid
136  56 112  Purple highlight
 56  16  32  Horns dark
 88  32  48  Horns light
 32   8  24  Cloak darkest
232 128  40  Flame tips
```

## 7.1 Dimoni — Master Idle (GENERATE FIRST) — 4 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Balchar
  - Same shading logic and pixel density
  - Same outline treatment
  - Supernatural character — darker and more dramatic than human characters
    but still consistent pixel art style

CHARACTER IDENTITY:
  - Name:    Dimoni de Sant Joan
  - Role:    Supernatural NPC — the demon who cursed Bep
  - Culture: Traditional Mallorcan dimoni from Correfoc festivals
  - Differentiators: Red-purple demonic figure with ram horns, fiery aura,
                     tattered robes. Supernatural, theatrical, dramatic.

VISUAL DETAILS:
  - Body:        Lean demonic form, dark red-purple skin
  - Horns:       Ram-like curved horns
  - Eyes:        Glowing yellow, intense
  - Clothing:    Tattered dark robes/loincloth
  - Aura:        Fiery glow around body (orange/red flame tips)
  - Expression:  Menacing, theatrical
  - Size:        Tall — 24x40 pixels

PALETTE (use ONLY these 12 colors):
  72,24,56     Dark body base
  48,16,40     Body shadow
  200,48,32    Fiery red accent
  240,96,40    Orange fire glow
  248,232,56   Glowing eyes
  248,200,32   Eye outer glow
  104,40,88    Purple mid
  136,56,112   Purple highlight
  56,16,32     Horns dark
  88,32,48     Horns light
  32,8,24      Cloak darkest
  232,128,40   Flame tips

SPRITE CONSTRAINTS:
  - Sheet size:  96x40 (4 frames)
  - Frame size:  24x40 each
  - Facing:      RIGHT
  - Pose:        Standing imperiously, one hand raised, fiery aura flickering
                 across the 4 frames (subtle flame motion).

BACKGROUND: Solid green (#00FF00)
```

## 7.2 Dimoni — Laugh (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — match Dimoni MASTER idle.
PALETTE: Same 12 colors.
Sheet: 48x40 (2 frames). Frame size: 24x40. Facing RIGHT.
Pose: Head thrown back laughing, mouth open, flames flare up around body.
Frames cycle the flame surge for animated laughter.
Background: solid green (#00FF00)
```

## 7.3 Dimoni — Grant (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 48x40 (2 frames). Frame size: 24x40. Facing RIGHT.
Pose: Arms extended forward, palms open, energy flowing outward — granting a power.
Generous but still menacing posture. Two frames showing the energy pulse.
Background: solid green (#00FF00)
```

## 7.4 Dimoni — Angry (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 48x40 (2 frames). Frame size: 24x40. Facing RIGHT.
Pose: Hunched forward aggressively, eyes blazing brighter, flames intensified,
fists clenched. Rage posture. Two frames showing eye/flame intensification.
Background: solid green (#00FF00)
```

---

# 8. Llorenç (NPC — Shopkeeper)

**Hitbox**: `_NPC_WIDTH=20`, `_NPC_HEIGHT=36`
**Processed output size** (from `npc_llorencc.json`): 40x72 per frame

**Visual identity**: Llorenç is a Menorcan warrior-scholar.
**Costume (canonical)**: cream linen shirt + olive green vest + terracotta apron +
leather satchel. (This supersedes any earlier "leather tunic + scrolls" description.)

**Palette** (`assets/palettes/llorencc.gpl` — 12 colors):

```
192 136  80  Skin base
168 112  64  Skin shadow
 64  40  24  Hair / beard
 32  24  16  Eyes
240 232 208  Shirt (cream linen)
216 208 184  Shirt shadow
 56 104  72  Vest (olive green)
 40  80  56  Vest shadow
184  56  40  Apron (terracotta)
152  40  32  Apron shadow
 88  64  40  Pants (brown)
112  80  48  Boots
```

## 8.1 Llorenç — Master Idle (GENERATE FIRST) — 4 frames

```
Create a SNES-style 16-bit pixel art sprite.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Balchar
  - Same shading logic and pixel density
  - Same outline treatment
  - Friendly NPC — warmer body language than enemies

CHARACTER IDENTITY:
  - Name:    Llorenç
  - Role:    Friendly NPC shopkeeper / scholar from Menorca
  - Culture: Talayotic warrior-scholar (same era as Balchar)
  - Differentiators: Slightly taller and leaner than Balchar, friendly expression,
                     cream linen shirt, olive green vest, terracotta apron,
                     leather satchel. Enthusiastic about artifacts.

VISUAL DETAILS:
  - Body:      Lean, slightly taller than Balchar
  - Clothing:  Cream linen shirt, olive green vest over it, terracotta apron
  - Hair:      Dark hair and beard
  - Expression: Friendly, enthusiastic (contrast to Balchar's grumpiness)
  - Accessories: Leather satchel visible at side
  - Size:      20x36 pixels

PALETTE (use ONLY these 12 colors):
  192,136,80   Skin base
  168,112,64   Skin shadow
  64,40,24     Hair / beard
  32,24,16     Eyes
  240,232,208  Shirt (cream linen)
  216,208,184  Shirt shadow
  56,104,72   Vest (olive green)
  40,80,56     Vest shadow
  184,56,40    Apron (terracotta)
  152,40,32    Apron shadow
  88,64,40     Pants (brown)
  112,80,48    Boots

SPRITE CONSTRAINTS:
  - Sheet size:  80x36 (4 frames)
  - Frame size:  20x36 each
  - Facing:      RIGHT
  - Pose:        Standing relaxed, one hand on satchel, friendly smile.
                 Frames cycle subtle weight shift / hand movement.

BACKGROUND: Solid green (#00FF00)
```

## 8.2 Llorenç — Talk (4 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK — match Llorenç MASTER idle.
PALETTE: Same 12 colors.
Sheet: 80x36 (4 frames). Frame size: 20x36. Facing RIGHT.
Pose: Animated talking — one hand gesturing enthusiastically, mouth open,
leaning forward. 4 frames cycling the gesture for animated dialogue.
Background: solid green (#00FF00)
```

## 8.3 Llorenç — Shop (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 40x36 (2 frames). Frame size: 20x36. Facing RIGHT.
Pose: Behind counter — hands on surface, satchel open showing wares,
inviting gesture. Shopkeeper mode. 2 frames for subtle motion.
Background: solid green (#00FF00)
```

---

# Dimoni aura effect (W1) {#dimoni-aura-effect-w1}

> The Dimoni aura is a W1-specific VFX (tied to the Dimoni de Sant Joan).
> It uses the cross-world `effects.gpl` palette block — see
> [`shared.md` § 12 (Effects — generic)](shared.md#12-effects-generic).
> Generate it as one row in the same effects sheet that holds dust, impact,
> portal, anticipation glow, and stone debris.

```
DIMONI AURA (16x16, 3 frames in a row = 48x16 total):
  Pulsing supernatural aura. Purple energy fluctuation.
  Use portal purple/bright/deep colors from effects.gpl:
    152,72,200   Portal purple
    192,112,240  Portal bright
    104,40,152   Portal deep

  Frames cycle the pulse brighter/dimmer.

BACKGROUND: Solid green (#00FF00).
```

---

# 13. Attack effect overlays

These are **per-enemy attack VFX** — simple motion trails / impact flashes
that play over an enemy's attack hitbox to telegraph the danger zone.
No body parts, no weapons — pure VFX.

**Pipeline**:

1. Generate each effect using the prompts below.
2. Place the output PNG in `assets/ai_sources/{enemy_name}/`.
3. Process with: `python tools/process_character_sprites.py tools/sprite_defs/characters/{enemy_name}_effects.json`
4. Output lands in `assets/sprites/enemies/effects/`.
5. Update `sa_fona/data/asset_manifest.json` with the correct frame dimensions.
6. Update `sa_fona/data/enemies/world{N}_enemies.json` `attack_effect` block if frame sizes changed.

**General rules**:

- Solid bright green (#00FF00) background.
- All frames in a single horizontal row, evenly spaced, same scale.
- 16-bit SNES-style pixel art, clean pixels, no anti-aliasing.
- Effects face **right** (game flips for left-facing).
- **No body parts, no weapons, no characters** — pure simple VFX.
- Keep it minimal — these are tiny sprites (~24-48px).
- `scale_pct` needs tuning after seeing AI output — start at 85 and adjust.
- Effects anchor at the collision rect edge, offset by `offset_x`/`offset_y` in enemy JSON.

## 13.1 Stone Guardian — Dust Sweep

**Source file**: `assets/ai_sources/stone_guardian/stone_guardian_arm_sweep.png`
**Config**: `tools/sprite_defs/characters/stone_guardian_effects.json`
**Frames**: 3

```
Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00)
background. 3 frames in a horizontal row, evenly spaced. A simple brown dust
sweep arc, no characters or weapons:

  Frame 1: A faint curved dust trail forming, sweeping right
  Frame 2: The dust trail at full opacity, thick arc shape
  Frame 3: The dust fading away

Colors: brown-tan dust with a few darker brown pixels for depth. Simple and clean.
```

## 13.2 Rival Warrior — Slash Trail

**Source file**: `assets/ai_sources/rival_warrior/rival_warrior_spear_thrust.png`
**Config**: `tools/sprite_defs/characters/rival_warrior_effects.json`
**Frames**: 3

```
Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00)
background. 3 frames in a horizontal row, evenly spaced. A simple horizontal
slash trail, no characters or weapons:

  Frame 1: A thin white streak appearing, pointing right
  Frame 2: The streak at full brightness with a few spark pixels
  Frame 3: The streak fading into scattered dots

Colors: white core, pale blue edge. Simple and clean.
```

## 13.3 Roman Legionary — Stab Flash

> **Future-world note**: the Roman Legionary is a **World 2 (Romana)** enemy.
> This prompt is staged here until `world2.md` is created — at that point,
> move § 13.3 into the new file. Kept here so the attack-effect overlays
> stay together and the prompt is not lost.

**Source file**: `assets/ai_sources/legionary/legionary_gladius_stab.png`
**Config**: `tools/sprite_defs/characters/legionary_effects.json`
**Frames**: 3

```
Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00)
background. 3 frames in a horizontal row, evenly spaced. A simple forward
impact flash, no characters or weapons:

  Frame 1: A small bright point of light appearing
  Frame 2: The flash expanding into a small starburst shape
  Frame 3: The flash shrinking and fading

Colors: white-yellow center, pale yellow outer glow. Simple and clean.
```

---

# 14. Environment props

## 14.1 Bonfire (save point)

**Source image**: `assets/ai_sources/bonfire/bonfire.png`
**Processing config**: `tools/sprite_defs/characters/bonfire.json`
**Output**: `assets/environment/bonfire.png` (48x32, 2 frames of 24x32)

```
Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00)
background. 2 frames in a horizontal row, evenly spaced, same scale.
Small bonfire save point:

  Frame 1: Unlit — small pile of rough-hewn grey limestone rocks with dry
           sun-bleached wood and brush on top, no flame, cold and dormant
  Frame 2: Lit — identical rock and wood base, warm orange-yellow flame
           rising from wood, 3-4 flame colors (dark orange base, bright
           orange middle, yellow tips), small ember dots above

Style: Balearic Mediterranean. Warm grey limestone rocks (NOT blue-grey),
dry earth tones for wood, knee-height scale (16-20 pixels tall).
Clean pixel art, no anti-aliasing, no smoothing. Both sprites must have
identical base structure, only flame differs. Clearly separated with green
space between them.
```

**Processing notes**:

- Green background removed via chroma key: `(g - r > 40) and (g - b > 40) and (g > 80)`.
- 2 sprite regions detected via connected components on non-green mask.
- Both frames scaled uniformly to fit 24x32 frame, bottom-aligned.
- Output: single horizontal sprite sheet (48x32), frame 0 = unlit, frame 1 = lit.
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/bonfire.json`.

## 14.2 Taula Gate (level-end portal)

**Source image**: `assets/ai_sources/taula_gate/taula_gate.png`
**Processing config**: `tools/sprite_defs/characters/taula_gate.json`
**Output**: `assets/environment/taula_gate.png` (32x48, single frame)

```
Pixel art sprite, 16-bit SNES style, solid bright green (#00FF00) background.
Single taula gate viewed from side, T-shaped megalithic monument forming a
doorway.

One thick vertical limestone pillar supporting wide horizontal capstone, clear
doorway opening tall enough for warrior character (about 48 pixels tall),
pillar roughly one-third width of capstone. Weathered ancient grey limestone
with subtle warm undertones (NOT blue-grey), small patches of green-brown moss
on capstone and upper pillar, fine cracks and mortar-line texture, solid and
enduring.

Style: Based on Menorcan taula monuments (Torralba d'en Salort, Torre d'en
Galmés). Balearic talayotic architecture, ancient monumental stone but not
ruined. Clean pixel art, no anti-aliasing, no smoothing.
```

**Processing notes**:

- Green background removed via chroma key.
- Single sprite region detected.
- Scaled to fit 32x48 frame, bottom-aligned.
- Output: single image (32x48).
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/taula_gate.json`.

---

# 15. Tilesets

## 15.1 World 1 — Outdoor (Sa Talaia)

**Output**: `assets/tilesets/world1/tileset.png` (256x16, 16 auto-tile variants)
**Processing**: `tools/process_ai_tiles.py`

```
Pixel art tileset for a 2D platformer, 16-bit SNES style, on a solid bright
green (#00FF00) background. Show exactly 4 tiles in a single horizontal row,
evenly spaced, each tile a separate square block:

  1) Top surface tile — grey Mediterranean limestone with short grass/moss on
     top edge, light warm grey stone body with subtle mortar line texture,
     small cracks and color variation
  2) Inner stone tile — solid grey limestone block, no grass, visible mortar
     lines and subtle stone grain, slightly darker than the surface tile
  3) Underground/deep tile — darker grey stone, more worn and cracked,
     minimal detail, the deepest layer
  4) Wall edge tile — grey stone with slight weathering on one side,
     transitional tile between exposed surface and inner stone

Style: Balearic island Mediterranean terrain. Warm neutral grey stone (NOT
blue-grey), subtle ochre undertones. Clean pixel art, no anti-aliasing, no
smoothing. Each tile should be clearly separated with green space between
them. Consistent lighting from top-left. Stone should look like ancient
talayotic construction — rough-hewn limestone blocks.
```

### Tileset processing pipeline (canonical)

- Green background detected via `(g-r > 40) & (g-b > 40) & (g > 80)`.
- 4 tile regions found via `scipy.ndimage.label` on non-green mask.
- Regions smaller than 1000px² filtered out.
- 5px inset crop to avoid green fringe at edges.
- Remaining green pixels (where `g-r > 30` and `g-b > 30` and `g > 100`) replaced with average of non-green neighbors.
- **Color correction** (AI tiles tend blue-grey): luminance extracted and remapped onto warm stone palette:
  - **Dark end: RGB(130, 112, 82)**
  - **Light end: RGB(215, 195, 155)**
  - 8% original color variation preserved for texture.
- **Grass tile**: top 40% mapped to green palette RGB(72,108,50)–(120,155,85), bottom 60% warm stone.
- **Underground tile** additionally darkened by 0.7 factor.
- **Multi-step downscale**: LANCZOS to 48x48 → contrast 1.4x → sharpness 1.5x → NEAREST to 16x16.
- **16 auto-tile variants** built from 4-bit neighbor bitmask (UP=1, DOWN=2, LEFT=4, RIGHT=8).
- **Edge darkening** at 0.75 factor for 2px on exposed sides.

## 15.2 World 1 — Cave (Sa Cova des Foner)

```
Pixel art tileset for a cave interior in a 2D platformer, 16-bit SNES style,
on a solid bright green (#00FF00) background. Show exactly 4 tiles in a
single horizontal row, evenly spaced, each tile a separate square block:

  1) Cave ceiling/floor tile — dark grey-brown limestone with
     stalactite/stalagmite nubs on one edge, damp texture, slightly wet-looking
     highlights
  2) Cave wall tile — solid dark grey cave rock, rough texture, small crystal
     or mineral deposits glinting, deeper darkness
  3) Deep cave tile — very dark stone, almost black with subtle dark purple
     undertones, barely visible texture, the deepest cavern
  4) Cave transition tile — medium grey stone transitioning between cave
     interior and the outdoor tileset, some moss growing on the cave side

Style: underground Mediterranean cave system. Darker and cooler than the
outdoor tileset but still warm-toned (NOT blue). Subtle dampness and mineral
deposits. Should feel ancient and mysterious.
```

Uses the same color-correction + downscale pipeline as the outdoor tileset.

## 15.3 World 1 — Talayot Interior (Es Talayot Sagrat)

```
Pixel art tileset for an ancient stone tower interior in a 2D platformer,
16-bit SNES style, on a solid bright green (#00FF00) background. Show
exactly 4 tiles in a single horizontal row, evenly spaced:

  1) Talayot wall surface tile — large precisely cut limestone blocks with
     tight mortar joints, carved with faint ancient symbols (spirals, bull
     motifs), warm grey stone, moss growing in crevices
  2) Talayot inner wall tile — solid construction stone, larger blocks than
     outdoor tileset, very precise rectangular cuts (ancient masonry), slight
     amber tint from torchlight
  3) Talayot deep/foundation tile — the oldest darkest stone at the base of
     the tower, rough-hewn megalithic blocks, ancient and weathered, dark
     grey-brown
  4) Talayot edge/platform tile — a carved stone ledge or step, more ornate
     than raw stone, suitable for wall-jump surfaces and platforms

Style: interior of a sacred talayotic tower (talayot). More refined than
natural cave or outdoor terrain. Large precisely-cut stone blocks showing
advanced Bronze Age masonry. Faint carved decorative elements. Warm torchlit
amber undertones. Should feel ancient, sacred, and impressive.
```

Uses the same color-correction + downscale pipeline.

---

# 16. Backgrounds

Single-image parallax backgrounds, designed to scroll slightly behind gameplay.
Size: 384x216 (full native resolution). No chroma key needed — fill the entire
canvas.

## 16.1 World 1 — Outdoor Landscape

```
Create a SNES-style 16-bit pixel art BACKGROUND.

ENVIRONMENT: Outdoor Mallorcan Mediterranean landscape.
  Rolling green hills, limestone outcrops, distant sea,
  warm golden sunset/horizon, Mediterranean vegetation, blue sky.

SIZE: 384x216 pixels (full native resolution, single image)

PALETTE: Use colors from bg_world1.gpl
  (sky blues, warm greens, golden haze, limestone greys, deep foliage)

COMPOSITION (bottom to top):
  - Foreground: Grass and rocky terrain (lower 40px)
  - Midground: Rolling hills with scattered trees and stone formations
  - Background: Distant hills and coastline
  - Sky: Blue gradient from deep blue (top) to warm golden haze (horizon)

STYLE RULES:
  - Parallax-ready: designed to scroll slightly behind gameplay
  - Less detailed than foreground tiles — softer, more atmospheric
  - Top-left light source consistent with sprites
  - No anti-aliasing — clean pixel art even for sky gradients

Background: No chroma key needed — fill entire 384x216 canvas
```

## 16.2 World 1 — Cave System

```
Same format as outdoor background but:

ENVIRONMENT: Underground cave system. Stalactite cavern, underground water,
  bioluminescent hints, torch glow reflections on water surface.
  Dark and atmospheric.

SIZE: 384x216 pixels.
PALETTE: Use bg_world1_cave.gpl colors (deep darks, rock ochres, torch glow).

COMPOSITION:
  - Foreground: Stalagmite silhouettes
  - Midground: Cave walls with mineral deposits, distant stalactites
  - Background: Deep cave void, faint distant glow
  - Water: Reflective underground pool/stream in lower portion
  - Lighting: Warm torch glow patches in darkness
```

## 16.3 World 1 — Talayot Interior

```
Same format as outdoor background but:

ENVIRONMENT: Interior of ancient talayotic tower. Cut stone walls,
  torches in wall sconces, carved symbols (spirals, bull motifs),
  beam of light from above, ceremonial architecture.

SIZE: 384x216 pixels.
PALETTE: Use bg_world1_talayot.gpl colors (stone purples, brick ochres, firelight).

COMPOSITION:
  - Walls: Precisely cut limestone blocks with carved decorations
  - Lighting: Torch sconces on walls, central beam of light from above
  - Details: Spiral and bull carvings, stone archways
  - Atmosphere: Warm amber glow, ancient and sacred feeling
```

---

# 17. Dialogue portraits (W1 NPCs)

Portrait conventions (44x44, square headshot, facing slightly LEFT, name
matching `world1_dialogue.json` field values) are documented in
[`shared.md` § 17 (Dialogue portraits — cross-world)](shared.md#17-dialogue-portraits-cross-world).
Balchar (4) and Bep (4) portraits live there. World 1 NPC portraits live below.

## 17.3 Dimoni Portraits (3)

> Reference: [ATTACH DIMONI MASTER IDLE SPRITE HERE]

```
Pixel art portrait of Es Dimoni de Sant Joan, 16-bit SNES style, on a solid
bright green (#00FF00) background. Show 3 portraits in a row:

  1) dimoni_imposing — dramatic close-up of the demon's face, red skin, large
                       curved ram horns framing the face, sharp angular features,
                       glowing yellow eyes, cruel confident smirk, fiery aura
                       at edges of frame
  2) dimoni_laughing — same face but mouth wide open in mocking laughter,
                       eyes narrowed with cruel amusement
  3) dimoni_grudging — same face but slight grimace, begrudging respect,
                       one eyebrow raised

Each portrait 44x44 pixels. The dimoni should look theatrical and imposing —
based on Mallorcan Correfoc festival demon figures.
```

**Output files**: `dimoni_imposing.png`, `dimoni_laughing.png`, `dimoni_grudging.png` — each 44x44.
Used as the `"Dimoni"` speaker in `post_boss_w1.json`.

## 17.4 Llorenç Portraits (3)

> Reference: [ATTACH LLORENÇ MASTER IDLE SPRITE HERE]

```
Pixel art portrait of Llorenç the Menorcan scholar-warrior NPC, 16-bit SNES
style, on a solid bright green (#00FF00) background. Show 3 portraits in a row:

  1) llorencc_neutral  — calm neutral expression, scholarly look, dark hair,
                         tanned skin, visible satchel strap over shoulder,
                         facing slightly left
  2) llorencc_friendly — warm friendly face, slight smile, same character
  3) llorencc_excited  — same face but eyes lit up with enthusiasm, mouth
                         open explaining something, gesturing with one hand visible

Each portrait 44x44 pixels.
```

**Output files**: `llorencc_neutral.png`, `llorencc_friendly.png`, `llorencc_excited.png` — each 44x44.
`llorencc_neutral` is referenced in `world2_dialogue.json`.

---

# 21. Generation order (World 1)

Follow this order so each asset inherits the established style. Items 1-4
are cross-world (player + companion) — they anchor every world's style chain
and live in [`shared.md`](shared.md). Items 5+ are W1-specific.

1. **Balchar idle** (master reference for the entire world) — see `shared.md` § 1.1
2. Balchar all other animations (walk, jump, wall slide, wall jump, sling, hit, death, crouch)
3. **Bep idle** (companion, references Balchar's world style) — see `shared.md` § 2.1
4. Bep all other animations + curse glow
5. **Bou de Pedra idle Phase 1** (boss, references Balchar — establishes enemy visual tone)
6. Bou de Pedra all phases and animations
7. Bou de Pedra arena props (pillars, rock, shockwave, pulse, shadow)
8. **Stone Guardian** (references Bou — both are stone constructs)
9. **Rival Warrior** (references Bou's world style)
10. **Possessed Sheep** (references Bou's world style)
11. **Dimoni** (NPC, references Balchar's world)
12. **Llorenç** (NPC, references Balchar's world)
13. **Pickups** (heart, stone, shield orb) — see `shared.md` § 9
14. **Breakables** (pot, crate) — see `shared.md` § 10
15. **Projectiles** (3 tiers) — see `shared.md` § 11
16. **Effects** (dust, impact, portal, anticipation, debris) — see `shared.md` § 12;
    add the W1 Dimoni aura row from this file (Dimoni aura effect)
17. **Attack effect overlays** (Stone Guardian sweep, Rival slash; Legionary stab flash is W2-staged)
18. **Environment props** (bonfire, taula gate)
19. **Tilesets** (outdoor, cave, talayot)
20. **Backgrounds** (outdoor, cave, talayot)
21. **Dialogue portraits** (Balchar, Bep in `shared.md`; Dimoni, Llorenç here)
22. **UI elements** (hearts, stone icon, mask icon, dialogue/shop frames, boss bar, charge indicator) — see `shared.md` § 18
23. **Title + Game Over screens** — see `shared.md` § 19
24. **Player ground shadow** — see `shared.md` § 20

For the post-generation pipeline (clean_sprites, palette enforcement, QC),
see [`shared.md` § 22 (Post-generation)](shared.md#22-post-generation).
