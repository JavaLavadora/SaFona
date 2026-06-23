# Sa Fona — Asset Prompts (Master Reference)

**Single source of truth for every AI image prompt used to generate Sa Fona art.**

If you find prompt content **outside this file**, it is a bug — file an Issue.

For the workflow, processing pipeline, and "how to add a new asset" instructions, see
[`asset_generation_guide.md`](asset_generation_guide.md). This file is **prompts only**.

Framed as **"all assets, World 1 populated"** — future worlds (W2, W3...) slot in
under their own headings without restructuring.

---

## How to use this file

1. Find the asset section below.
2. Copy the prompt block verbatim into your AI image generator.
3. Where the prompt says `[ATTACH MASTER IDLE SPRITE HERE]`, attach the matching
   PNG from `assets/sprites/<character>/idle.png` as a visual reference image.
4. Save the AI output to `assets/ai_sources/<asset_name>/image.png`.
5. Run the matching processing config — see the guide.

### `[ATTACH MASTER IDLE SPRITE HERE]` convention

Every animation prompt that follows a master idle includes this operational marker.
It is **not** part of the text the AI sees — it tells the human operator to attach
the previously-generated master idle PNG as a reference image alongside the text
prompt. This is how style/identity is enforced across animations.

For the FIRST asset in a style chain (the master idle itself), there is no
reference; you set the identity in that pass. All later assets reference it.

---

## Frame-size convention (read this once)

There are **three different "sizes"** documented per asset. They are not in conflict —
they are different layers:

1. **Hitbox size** — the collision rect in code (e.g. `PLAYER_WIDTH=24`,
   `PLAYER_HEIGHT=32`). The game uses this for physics and hit detection.
2. **AI prompt source size** — what the AI is asked to draw (e.g. 32x48 per
   frame for Balchar). Usually larger than the hitbox to leave headroom for
   raised arms, slings, jump poses, etc.
3. **JSON config output size** — the final sprite-sheet frame size set in
   `tools/sprite_defs/characters/*.json` (e.g. `frame_width: 48`, `frame_height: 64`
   for Balchar). Typically **2x** the AI source so the processed sprite has room
   to be cleaned and palette-corrected without losing detail.

When the prompt says "32x48 per frame" and the JSON says "48x64", that's
expected. The processor scales and snaps.

---

## Global style block

Copy this verbatim into **every** prompt. It is the backbone of style consistency.

```
GLOBAL STYLE CONSTRAINTS (DO NOT VIOLATE):

- Style:         Authentic SNES-era 16-bit pixel art
- Perspective:   Strict side view (2D platformer)
- Light source:  Top-left, consistent across all assets
- Shading:       2-3 tones per material, no pillow shading
- Pixel density: Moderate, readable at 1x scale
- Outlines:      Clean, dark outline color from palette
- Palette:       Use ONLY the approved palette listed below
- Rendering:     Pixel-perfect, no blur, no anti-aliasing, no gradients
- Aesthetic:     Pre-Roman Mediterranean (Balearic-inspired)
- Background:    Solid bright green (#00FF00) for chroma-key
- Layout:        Single horizontal row, poses numbered, clear spacing
```

### Generation rules

- Background: Solid bright green `#00FF00` for chroma-key removal.
- No anti-aliasing, no blur, no gradients.
- Characters face **RIGHT** by default (the game flips for left-facing).
- Poses numbered and arranged in a single horizontal row, evenly spaced.
- Clean pixel edges, clear green space between poses.

### Style chain (World 1)

```
Balchar (master) -> Bep -> Bou de Pedra (boss)
                          -> Stone Guardian
                          -> Rival Warrior
                          -> Possessed Sheep
                          -> Dimoni (NPC)
                          -> Llorenç (NPC)
```

Generate in this order so each asset inherits the established visual identity.
Full generation order is at the bottom of this document.

---

# Table of contents

- [1. Balchar (player)](#1-balchar-player-character) — idle, walk, jump, wall slide, wall jump, sling, hit, death, crouch
- [2. Bep (companion)](#2-bep-companion--myotragus) — idle, walk, jump, scared, excited, glow
- [3. Bou de Pedra (W1 boss)](#3-bou-de-pedra-world-1-boss) — 3 phase idles + attacks + arena props
- [4. Stone Guardian (enemy)](#4-stone-guardian-enemy) — idle, walk, attack, hit, death
- [5. Rival Warrior (enemy)](#5-rival-warrior-enemy) — idle, walk, attack, block, hit, death
- [6. Possessed Sheep (enemy)](#6-possessed-sheep-enemy) — idle, walk, charge, hit, death
- [7. Dimoni (NPC)](#7-dimoni-de-sant-joan-npc) — idle, laugh, grant, angry
- [8. Llorenç (NPC)](#8-llorenç-npc--shopkeeper) — idle, talk, shop
- [9. Pickups](#9-pickups) — heart, stone, shield orb
- [10. Breakables](#10-breakables) — pot, crate (with drop tables)
- [11. Projectiles](#11-projectiles) — tier 1/2/3 sling stones
- [12. Effects](#12-effects) — dust, impact, aura, portal, anticipation, debris
- [13. Attack effect overlays](#13-attack-effect-overlays) — Stone Guardian sweep, Rival slash, Legionary flash
- [14. Environment props](#14-environment-props) — bonfire, taula gate
- [15. Tilesets](#15-tilesets) — outdoor, cave, talayot
- [16. Backgrounds](#16-backgrounds) — outdoor, cave, talayot
- [17. Dialogue portraits](#17-dialogue-portraits) — Balchar (4), Bep (4), Dimoni (3), Llorenç (3)
- [18. UI elements](#18-ui-elements) — HUD hearts, stone icon, mask icon, dialogue frame, shop frame, boss health bar, charge indicator
- [19. Title and Game Over screens](#19-title-and-game-over-screens)
- [20. Player ground shadow](#20-player-ground-shadow)
- [21. Generation order](#21-generation-order)
- [22. Post-generation](#22-post-generation)

---

# 1. Balchar (player character)

**Hitbox**: `PLAYER_WIDTH=24`, `PLAYER_HEIGHT=32`
**AI prompt source size**: 32x48 per frame (8px headroom above body)
**Processed output size** (from `tools/sprite_defs/characters/balchar.json`): 48x64 per frame

**Palette** (`assets/palettes/balchar.gpl` — 15 colors):

```
248 248 240  Tunic highlight
240 232 216  Headwrap / eye white / tunic base
208 200 192  Headwrap shadow / tunic mid-shadow
192 192 176  Tunic deep crease
200 136  72  Skin base
176 112  56  Skin shadow / bracers / mouth
152  96  48  Skin dark / boot mid
 32  24  16  Pupil / dark outline
224  56  48  Red sash bright
192  40  32  Red sash base
152  32  24  Red sash dark
136  88  48  Leather dark / sling cord light
 96  72  48  Pants mid / boot dark
 88  64  40  Pants base / sling cord
 64  48  32  Pants / boots darkest
```

**Sprite anatomy map** (non-negotiable across all Balchar animations):

```
- Headroom:      Y 0-10 reserved for overhead content in other animations
- Head:          Y 10-20 (fixed)
- Torso:         Y 20-32 (fixed vertical)
- Belt/sash:     Absolute Y = 30
- Feet baseline: Absolute Y = 47
- Width:         ~14px body core within 32px frame

Allowed to move: arms, sling, torso rotation, cloth sway
Forbidden:       head position, leg length, belt height, palette changes
```

## 1.1 Balchar — Master Idle (GENERATE FIRST)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

CHARACTER IDENTITY:
  - Name:    Balchar
  - Culture: Talayotic Balearic civilization (pre-Roman Mallorca)
  - Era:     Bronze Age / Iron Age Mediterranean
  - Role:    Slinger warrior, reluctant hero

VISUAL DETAILS:
  - Clothing:    Knee-length white robe/tunic with V-neck showing chest,
                 bright red sash/belt at waist
  - Accessories: Leather brown arm bracers on forearms,
                 fona (Balearic sling — long braided cord with pouch) held in right hand
  - Hair/Headgear: Medium-length dark hair swept backwards held by cloth headband
  - Body type:   Stocky, determined warrior build
  - Expression:  Perpetually unimpressed, grumpy
  - Skin:        Deeply tanned olive

PALETTE (use ONLY these 15 colors):
  248,248,240  Tunic highlight
  240,232,216  Headwrap / eye white / tunic base
  208,200,192  Headwrap shadow / tunic mid-shadow
  192,192,176  Tunic deep crease
  200,136,72   Skin base
  176,112,56   Skin shadow / bracers / mouth
  152,96,48    Skin dark / boot mid
  32,24,16     Pupil / dark outline
  224,56,48    Red sash bright
  192,40,32    Red sash base
  152,32,24    Red sash dark
  136,88,48    Leather dark / sling cord light
  96,72,48     Pants mid / boot dark
  88,64,40     Pants base / sling cord
  64,48,32     Pants / boots darkest

SPRITE CONSTRAINTS:
  - Sprite sheet: 4 frames in horizontal row
  - Total size:   128x48
  - Frame size:   32x48 each
  - Facing:       RIGHT
  - Animation:    Idle breathing — subtle chest rise/fall, sling sways slightly

BACKGROUND: Solid green (#00FF00)

BODY SIZE RULE:
The character body occupies the lower 2/3 of the frame height.
The upper 1/3 is intentional headroom for animations that extend above
the head (sling overhead, raised arms, jump poses). Do NOT scale the body
to fill the entire frame — leave headroom.

IMPORTANT:
This sprite is the MASTER reference for all of Balchar's animations.
Design must be clean, readable, and reusable. All future poses must match
this exact design — proportions, face, clothing, colors.
```

## 1.2 Balchar — Walk Cycle (6 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER idle sprite EXACTLY
  - Same proportions, face, hair, headband, tunic, sash, bracers, sling
  - Same palette (15 colors), no new colors
  - Same head position (Y 10-20), belt height (Y 30), feet baseline (Y 47)
  - No redesign, no reinterpretation

REFERENCE: Use the provided MASTER idle sprite as visual authority

PALETTE: (same 15 colors as idle — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  192x48 (6 frames)
  - Frame count: 6
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle
sprite. The frame has headroom above — do NOT resize the body to fill the frame.

ANIMATION DESCRIPTION:
  Frame 1: Contact — right foot forward, left foot back, slight lean forward
  Frame 2: Low point — weight transfers to right foot, body dips slightly
  Frame 3: Passing — left leg swings forward past right, body upright
  Frame 4: Contact — left foot forward, right foot back, slight lean forward
  Frame 5: Low point — weight transfers to left foot, body dips slightly
  Frame 6: Passing — right leg swings forward past left, body upright

  Sling held loosely at side, swings naturally with walk motion.

RULES:
  - Only legs, arms, and slight torso bob may change
  - Head stays at fixed Y position
  - Maintain readable silhouette at all frames
  - Background: solid green (#00FF00)
```

## 1.3 Balchar — Jump (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER idle sprite EXACTLY
  - Same palette (15 colors), same proportions, same design

PALETTE: (same 15 colors as idle — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.
The frame has headroom above — do NOT resize the body to fill the frame.
Extended limbs may use the full frame height including headroom.

ANIMATION DESCRIPTION:
  Frame 1: Rising — legs tucked slightly, arms up, sling trailing behind,
           body angled slightly upward
  Frame 2: Falling — legs extended down, arms slightly above head,
           sling streaming upward, body angled slightly downward

RULES:
  - Same identity lock rules as all Balchar animations
  - Background: solid green (#00FF00)
```

## 1.4 Balchar — Wall Slide (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Balchar animations).

PALETTE: (same 15 colors — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT (body pressed against wall to the right)

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.

ANIMATION DESCRIPTION:
  Frame 1: Sliding down — body pressed flat against wall (right side),
           both hands touching wall surface, legs slightly bent,
           slow descent pose
  Frame 2: Slight variation — legs position shifts slightly for friction effect

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

## 1.5 Balchar — Wall Jump (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Balchar animations).

PALETTE: (same 15 colors — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT (jumping away from wall to the left)

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.
Dynamic pose may use full frame including headroom.

ANIMATION DESCRIPTION:
  Frame 1: Push-off — legs coiled against wall, body leaning away,
           arms reaching in jump direction
  Frame 2: Airborne — body fully extended away from wall, legs trailing,
           dynamic diagonal pose

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

## 1.6 Balchar — Sling Attack (3 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Balchar animations).

PALETTE: (same 15 colors — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  96x48 (3 frames)
  - Frame count: 3
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.
The sling cord extends above the head into the headroom area. The CHARACTER
BODY stays the same size as idle — only the sling uses the extra space.

ANIMATION DESCRIPTION:
  Frame 1: Wind-up — right arm pulled back with sling extended behind,
           body rotated slightly away from target, weight on back foot
  Frame 2: Mid-rotation — sling swinging overhead in arc,
           body rotating toward target, dynamic motion blur implied by sling position
  Frame 3: Release — arm fully extended forward, sling snapping forward,
           body leaning into throw, weight shifted to front foot

  The fona (sling) is the key element — show the cord and pouch clearly in each phase.

RULES:
  - Same identity lock
  - Sling must be clearly visible and readable in all 3 frames
  - Background: solid green (#00FF00)
```

## 1.7 Balchar — Hit (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Balchar animations).

PALETTE: (same 15 colors — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  32x48 (1 frame)
  - Frame size:  32x48
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.
Recoil pose may use headroom. Body proportions stay identical to idle.

ANIMATION DESCRIPTION:
  Single frame: Recoil — body bent backward from impact,
  arms flung slightly outward, grimacing expression,
  slight backward lean as if struck in the chest.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

## 1.8 Balchar — Death (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Balchar animations).

PALETTE: (same 15 colors — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  32x48 (1 frame)
  - Frame size:  32x48
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite.
Horizontal pose uses width, not headroom.

ANIMATION DESCRIPTION:
  Single frame: Collapsed — body slumped on the ground,
  lying on back or side, limbs limp, sling dropped nearby.
  Clear "defeated" pose, not graphic.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

## 1.9 Balchar — Crouch (2 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER idle sprite EXACTLY
  - Same proportions, face, hair, headband, tunic, sash, bracers, sling
  - Same palette (15 colors), no new colors
  - Same head position relative to body, belt height, clothing details
  - No redesign, no reinterpretation

PALETTE: (same 15 colors as idle — see Balchar palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle
sprite. The body occupies the lower 2/3 of the frame height. The upper 1/3
is intentional headroom. Do NOT scale the body to fill the entire frame.

ANIMATION FRAMES:
  Frame 1: Crouch idle — Balchar crouching low, knees bent deeply,
           torso hunched forward, head ducked down. One hand on ground
           for balance, sling held loosely in the other. Compact pose —
           character height is roughly HALF of standing height.
           Feet remain at the same baseline as idle (Y 47).

  Frame 2: Crouch idle variant — slight shift in weight or arm position
           for subtle idle animation while crouching.

IMPORTANT POSE NOTES:
  - The crouch must make Balchar significantly shorter (roughly half height)
  - Knees bent, body compressed downward
  - Head is lower than standing position (ducking under obstacles)
  - Feet stay planted at the same Y baseline as all other animations
  - The crouch pose should look like he's hiding or ducking, not sitting

BACKGROUND: Solid green (#00FF00)
```

---

# 2. Bep (companion — myotragus)

**Hitbox**: `COMPANION_WIDTH=16`, `COMPANION_HEIGHT=16`
**AI prompt source size**: 16x16 per frame

**Palette** (`assets/palettes/bep.gpl` — 9 colors).
The `.gpl` file should be authored following the same GIMP palette convention
as `assets/palettes/balchar.gpl`:

```
GIMP Palette
Name: Bep
Columns: 0
#
160 128  88  Fur base
192 160 120  Fur highlight
128 104  72  Fur dark
224 208 200  Face / eye white
 32  24  16  Pupil
104  72  48  Nose
200 184 160  Horn light
168 152 128  Horn dark
 80  56  32  Hooves
```

## 2.1 Bep — Master Idle (GENERATE FIRST) — 4 frames

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

CHARACTER IDENTITY:
  - Name:    Bep
  - Culture: Myotragus balearicus (extinct Balearic bovid)
  - Era:     Bronze Age Mediterranean
  - Role:    Companion creature, comic relief

VISUAL DETAILS:
  - Body:        Very small, round compact body with short woolly brown-grey fur
  - Head:        Two small forward-curving horns on top
  - Eyes:        Large dark expressive eyes (most prominent feature)
  - Limbs:       Tiny hooves, short stubby legs
  - Tail:        Short stubby tail
  - Overall:     Looks like a sheep-goat hybrid — cute and slightly hapless
  - Expression:  Cheerful, eager, wide-eyed

PALETTE (use ONLY these 9 colors):
  160,128,88   Fur base
  192,160,120  Fur highlight
  128,104,72   Fur dark
  224,208,200  Face / eye white
  32,24,16     Pupil
  104,72,48    Nose
  200,184,160  Horn light
  168,152,128  Horn dark
  80,56,32     Hooves

STYLE CONSISTENCY:
  - Must belong to the same world as Balchar (the player character)
  - Same shading logic and pixel density as Balchar
  - Same outline treatment (dark outline color)

SPRITE CONSTRAINTS:
  - Sprite sheet: 4 frames in horizontal row
  - Total size:   64x16
  - Frame size:   16x16 each
  - Facing:       RIGHT
  - Animation:    Idle — frames vary subtly:
                    Frame 1: Standing, neutral
                    Frame 2: Head tilted slightly, one ear flicked, curious
                    Frame 3: Mouth chewing slightly, content
                    Frame 4: Eyes half-closed (mid-blink)

BACKGROUND: Solid green (#00FF00)

IMPORTANT:
This is the MASTER reference for Bep. All future Bep animations must match exactly.
```

## 2.2 Bep — Walk (4 frames)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.

PALETTE: (same 9 colors — see Bep palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x16 (4 frames)
  - Frame size:  16x16 each
  - Facing:      RIGHT

ANIMATION DESCRIPTION:
  Frame 1: Right front hoof forward, left back hoof forward (diagonal gait)
  Frame 2: All hooves pass center, body slightly higher
  Frame 3: Left front hoof forward, right back hoof forward
  Frame 4: All hooves pass center, body slightly lower
  Trotting motion — bouncy and cheerful. Ears bob with movement.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

## 2.3 Bep — Jump (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
PALETTE: (same 9 colors)

Sheet: 16x16 (1 frame). Facing RIGHT.

Pose: All four hooves tucked under body, ears perked up,
eyes wide, slight upward arc. Compact mid-air pose.

Background: solid green (#00FF00)
```

## 2.4 Bep — Scared (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
PALETTE: (same 9 colors)

Sheet: 16x16 (1 frame). Facing RIGHT.

Pose: Body low and crouched, ears flattened back,
eyes squeezed shut or wide with fear, tail tucked.
Trembling pose — clearly frightened.

Background: solid green (#00FF00)
```

## 2.5 Bep — Excited (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
PALETTE: (same 9 colors)

Sheet: 16x16 (1 frame). Facing RIGHT.

Pose: Body upright and bouncy, ears straight up,
eyes wide and sparkly, front hooves slightly off ground.
Tail wagging. Enthusiastic energy.

Background: solid green (#00FF00)
```

## 2.6 Bep — Curse Glow Aura (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
PALETTE: (same 9 colors, plus a thin glow overlay in dimoni aura colors)

Sheet: 16x16 (1 frame). Facing RIGHT.

Pose: Same idle stance as the master, but surrounded by a subtle magical
glow outline (the dimoni curse). The aura is a 1-2 pixel halo of soft
purple-red glow that traces the silhouette. Bep's body is unchanged —
only the aura is added.

Output file: glow.png — used as a curse-effect overlay layer.

Background: solid green (#00FF00)
```

---

# 3. Bou de Pedra (World 1 boss)

**Hitbox**: 40x36
**Processed output size** (from `boss_bou_de_pedra.json`): 80x72 per frame

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
character generated for World 1, establishing the enemy visual tone).

## 3.1 Bou de Pedra — Master Idle Phase 1 (GENERATE FIRST) — 4 frames

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

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
GLOBAL STYLE CONSTRAINTS APPLY.
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
GLOBAL STYLE CONSTRAINTS APPLY.
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

## 3.4 Bou de Pedra — Rush Attack (2 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — same stone bull design.
PALETTE: Full 12 colors (show current phase glow as appropriate).

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Charging pose — head lowered, horns forward, legs in running stride,
           dust implied at hooves, body angled forward aggressively
  Frame 2: Full stride — opposite leg configuration, maximum forward momentum

Background: solid green (#00FF00)
```

## 3.5 Bou de Pedra — Headbutt (2 frames)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
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
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Raised — front legs lifted high, body rearing up
  Frame 2: Impact — front legs slammed down, shockwave lines implied at ground level

Background: solid green (#00FF00)
```

## 3.7 Bou de Pedra — Hurl (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Head tossing motion — flinging a rock projectile with horns,
head angled upward in throwing arc, rock departing from horn tips.

Background: solid green (#00FF00)
```

## 3.8 Bou de Pedra — Stunned (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Dazed — head lowered and swaying, legs wobbling slightly spread,
cracks in stone more visible, energy glow dimmed. Vulnerable state.

Background: solid green (#00FF00)
```

## 3.9 Bou de Pedra — Death (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Crumbling — stone blocks separating and falling apart,
energy fading from cracks, collapse in progress. Head tilted down,
legs buckling. Not fully destroyed — mid-collapse moment.

Background: solid green (#00FF00)
```

## 3.10 Bou de Pedra — Transition (1 frame)

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Phase transition — bull roaring/bellowing, head thrown back,
energy surging through all cracks simultaneously (bright glow everywhere),
stone vibrating. Dramatic power-up moment between phases.

Background: solid green (#00FF00)
```

## 3.11 Bou de Pedra — Arena Props

> Reference: [ATTACH BOU PHASE 1 MASTER IDLE SPRITE HERE — for stone material match]

```
Create a SNES-style 16-bit pixel art prop sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

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

GLOBAL STYLE CONSTRAINTS APPLY.

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

GLOBAL STYLE CONSTRAINTS APPLY.

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

GLOBAL STYLE CONSTRAINTS APPLY.

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
GLOBAL STYLE CONSTRAINTS APPLY.
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
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 32x16 (2 frames). Frame size: 16x16. Facing RIGHT.

  Frame 1: Head lowered, horns forward, legs coiled, about to launch
  Frame 2: Full charge — body horizontal, legs in full sprint, head-down ram attack

Background: solid green (#00FF00)
```

## 6.4 Possessed Sheep — Hit (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 16x16 (1 frame). Facing RIGHT.
Pose: Recoil — body knocked back, wool puffed out, eyes squinted.

Background: solid green (#00FF00)
```

## 6.5 Possessed Sheep — Death (1 frame)

> Reference: [ATTACH MASTER IDLE SPRITE HERE]

```
GLOBAL STYLE CONSTRAINTS APPLY.
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

GLOBAL STYLE CONSTRAINTS APPLY.

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

GLOBAL STYLE CONSTRAINTS APPLY.

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

# 9. Pickups

## 9.1 Heart Pickup (2 frames)

**Hitbox**: `PICKUP_WIDTH=12`, `PICKUP_HEIGHT=12`

**Palette** (`assets/palettes/pickups_heart.gpl` — 4 colors):

```
Create a SNES-style 16-bit pixel art sprite sheet.
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (4 colors only):
  224,40,40    Heart red
  248,80,80    Heart light
  176,32,32    Heart dark
  248,184,184  Highlight

Sheet: 24x12 (2 frames). Frame size: 12x12.
  Frame 1: Heart shape — classic pixel heart, full and glowing
  Frame 2: Slight pulse — heart slightly larger or brighter (pickup sparkle)

Background: solid green (#00FF00)
```

## 9.2 Stone Pickup / Currency (2 frames)

**Hitbox**: 12x12

**Palette** (`assets/palettes/pickups_stone.gpl` — 5 colors):

```
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (5 colors only):
  160,152,144  Stone base
  184,184,168  Stone light
  128,128,112  Stone dark
  112,104,88   Stone shadow
  200,192,184  Highlight

Sheet: 24x12 (2 frames). Frame size: 12x12.
  Frame 1: Small round polished sling stone — smooth, collectible-looking
  Frame 2: Slight sparkle/gleam variation

Background: solid green (#00FF00)
```

## 9.3 Shield Orb Pickup (2 frames)

**Hitbox**: 12x12

> Future pickup — generate the art now so it's ready when the gameplay code
> implements it.

```
GLOBAL STYLE CONSTRAINTS APPLY.

Pixel art of a magical shield orb pickup, 16-bit SNES style, on a solid bright
green (#00FF00) background. Show 2 frames side by side:

  Frame 1: Orb normal — a glowing translucent blue sphere with a shield icon
           inside, magical sparkles around it
  Frame 2: Orb pulse — same orb but slightly brighter, sparkles in different positions

Sheet: 24x12 (2 frames). Frame size: 12x12.
Should look clearly distinct from heart and stone pickups.

Background: solid green (#00FF00)
```

---

# 10. Breakables

**Hitbox**: `BREAKABLE_WIDTH=16`, `BREAKABLE_HEIGHT=16`

### Drop tables

| Object | Drops |
|--------|-------|
| Pot    | 1-3 stones |
| Crate  | 2-4 stones |

These drop tables are referenced by the gameplay/economy systems; the art is
only the visual layer.

## 10.1 Pot (intact + break)

**Palette** (`assets/palettes/breakables_pot.gpl` — 6 colors):

```
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (6 colors):
  184,120,56   Clay body
  200,144,72   Clay light
  152,96,48    Clay dark
  128,80,32    Clay shadow
  168,112,56   Rim
  192,136,72   Rim light

POT INTACT — 16x16 (1 frame):
  Mediterranean clay pot/amphora. Round body, narrow neck, small handles.
  Warm terracotta colors. Looks breakable.

POT BREAK — 16x16 (1 frame):
  Same pot shattered — shards flying outward, broken rim piece,
  scattered clay fragments. Mid-explosion moment.

Background: solid green (#00FF00)
```

## 10.2 Crate (intact + break)

**Palette** (`assets/palettes/breakables_crate.gpl` — 5 colors):

```
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (5 colors):
  160,120,72   Wood base
  184,144,88   Wood light
  128,96,56    Wood dark
  112,80,48    Wood shadow
  96,72,40     Nails / metal

CRATE INTACT — 16x16 (1 frame):
  Wooden storage crate. Square, planked sides, visible nails/binding.
  Mediterranean rustic. Looks breakable.

CRATE BREAK — 16x16 (1 frame):
  Same crate shattered — planks flying, splinters, nails scattering.
  Mid-explosion moment.

Background: solid green (#00FF00)
```

---

# 11. Projectiles

**Hitbox**: `projectile_width=8`, `projectile_height=8`

**Tier colors (canonical)**: Tier 1 = grey stone (no glow), Tier 2 = **blue glow**,
Tier 3 = **gold glow**. (This is the locked palette — earlier drafts described
Tier 2 as orange and Tier 3 as white-red; that is superseded.)

**Palette** (`assets/palettes/projectiles.gpl` — 8 colors):

```
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (8 colors):
  160,160,152  Tier 1 stone base
  128,128,120  Tier 1 stone shadow
  192,192,184  Tier 1 stone highlight
  80,144,224   Tier 2 blue glow
  120,184,248  Tier 2 blue bright
  216,184,56   Tier 3 gold glow
  248,224,96   Tier 3 gold bright
  96,96,88     Dark outline

TIER 1 — 8x8 (1 frame):
  Basic sling stone. Small rough grey stone, angular. No glow. Simple.

TIER 2 — 8x8 (1 frame):
  Enhanced sling stone. Same grey stone base but with blue energy glow
  surrounding it. Magical enhancement visible.

TIER 3 — 8x8 (1 frame):
  Master sling stone. Grey stone base with gold energy glow.
  Most powerful, brightest glow.

Background: solid green (#00FF00)
```

---

# 12. Effects

**Effect-group canonical sizes**: aura 16x16, portal 24x32. If actual in-game
usage of an effect disagrees with these sizes, flag for review — do not silently
resize.

**Palette** (`assets/palettes/effects.gpl` — 12 colors):

```
GLOBAL STYLE CONSTRAINTS APPLY.

PALETTE (12 colors):
  240,240,232  Dust white
  200,200,192  Dust grey
  160,152,144  Dust dark
  248,240,120  Flash yellow
  248,208,56   Flash orange-yellow
  152,72,200   Portal purple
  192,112,240  Portal bright
  104,40,152   Portal deep
  72,200,80    Aura green
  120,240,120  Aura bright
  48,144,56    Aura dark
  248,152,48   Orange spark

DUST (8x8, 4 frames in a row = 32x8 total):
  Small puff of dust/debris. Frames show expansion and dissipation.
  Use dust white/grey/dark colors.

IMPACT (12x12, 3 frames in a row = 36x12 total):
  Hit impact flash. Frames: bright flash → expanding ring → fade.
  Use flash yellow/orange colors.

DIMONI AURA (16x16, 3 frames in a row = 48x16 total):
  Pulsing supernatural aura. Purple energy fluctuation.
  Use portal purple/bright/deep colors.

PORTAL (24x32, 4 frames in a row = 96x32 total):
  Swirling time portal. Tall oval shape with energy spiraling inward.
  Use all portal colors. Frames show rotation.

ANTICIPATION GLOW (8x8, 2 frames in a row = 16x8 total):
  Subtle charge-up glow before an attack. Use flash/orange colors.

STONE DEBRIS (8x8, 3 frames in a row = 24x8 total):
  Small stone chunks scattering from broken stone. Use dust colors.
  Frames show pieces flying outward and settling.

BACKGROUND: Solid green (#00FF00) for all effects.

LAYOUT: Arrange each effect group in its own row, stacked vertically.
Each row's total width equals (group frame width) × (frame count).
Label or number each group clearly.
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

GLOBAL STYLE CONSTRAINTS APPLY.

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

# 17. Dialogue portraits

The dialogue system uses **44x44 pixel** portrait boxes. Each portrait is a
square headshot — face + upper shoulders — facing slightly LEFT (toward the
dialogue text). Portrait names below match the `"portrait"` field values used
by `sa_fona/data/dialogue/world1_dialogue.json` and `world2_dialogue.json`.

## 17.1 Balchar Portraits (4)

> Reference: [ATTACH BALCHAR MASTER IDLE SPRITE HERE]

```
Pixel art portrait set of Balchar the Balearic slinger, 16-bit SNES style,
on a solid bright green (#00FF00) background. Show 4 face portraits in a
single horizontal row, each a square headshot:

  1) balchar_neutral    — straight-faced, slightly bored, deadpan, facing
                          slightly left (toward the dialogue text)
  2) balchar_annoyed    — furrowed brow, slight frown, exasperated (default mood)
  3) balchar_surprised  — eyebrows raised, mouth slightly open, caught off guard
  4) balchar_determined — narrowed eyes, set jaw, ready for battle

Character: medium-length dark hair swept back with cloth headband, deeply
tanned olive skin, strong jaw, perpetually unimpressed default expression.
Close-up face and upper shoulders only. Each portrait 44x44 pixels.
Consistent face proportions across all expressions.
```

**Output files** (used in `world1_dialogue.json` as `"portrait"` field values):
`balchar_neutral.png`, `balchar_annoyed.png`, `balchar_surprised.png`, `balchar_determined.png` — each 44x44.

## 17.2 Bep Portraits (4)

> Reference: [ATTACH BEP MASTER IDLE SPRITE HERE]

```
Pixel art portrait set of Bep the myotragus companion, 16-bit SNES style,
on a solid bright green (#00FF00) background. Show 4 portraits in a row:

  1) bep_neutral  — friendly round face, large dark eyes, small forward-curving
                    horns visible, calm expression, facing slightly left
  2) bep_excited  — same face but eyes wide and sparkling, mouth open in a
                    happy bleat, ears perked up
  3) bep_scared   — eyes huge with fear, ears flattened back, mouth in a
                    worried "O" shape, trembling
  4) bep_sleepy   — half-closed droopy eyes, content sleepy smile

Character: round face of a small sheep-goat creature, large expressive dark
eyes (the dominant feature), two small forward-curving horns on top, woolly
brown-grey fur around the face, small ears. Bep's emotions are always dialed
up to 11. Each portrait 44x44 pixels.
```

**Output files**: `bep_neutral.png`, `bep_excited.png`, `bep_scared.png`, `bep_sleepy.png` — each 44x44.

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

# 18. UI elements

All UI elements live in `assets/ui/`. They sit on top of the gameplay layer and
must read clearly at small size.

## 18.1 HUD Heart Icons

**Code constant**: heart sprites are read by the HUD renderer at 12x12.

```
Pixel art of HUD heart icons in three states, 16-bit SNES style, on a solid
bright green (#00FF00) background. Show in a horizontal row:

  1) Full heart  — a classic red heart shape, filled solid red with a lighter
                   highlight, clean iconic look
  2) Half heart  — left half filled red, right half dark/empty with just an outline
  3) Empty heart — just the heart outline in dark red/maroon, interior is
                   dark/transparent

Each heart approximately 12x12 pixels. Must be readable at small size — these
sit in the top-left corner of the screen.
```

**Output files**: `heart_full.png`, `heart_half.png`, `heart_empty.png` — each 12x12.

## 18.2 HUD Stone Counter Icon

```
Pixel art of a small stone icon for the HUD counter, 16-bit SNES style, on a
solid bright green (#00FF00) background:

  1) A tiny sling stone icon, warm grey, round, with a subtle "x" format
     indicator space next to it

Approximately 10x10 pixels. Must be readable at tiny size — sits next to the
stone count number.
```

**Output file**: `stone_icon.png` — 10x10.

## 18.3 Mask HUD Icon (Stone Slam)

**Code constant**: `_MASK_ICON_SIZE = 14`

```
Pixel art of the Stone Slam dimoni mask icon for the HUD, 16-bit SNES style,
on a solid bright green (#00FF00) background:

  1) Active mask   — a small ancient stone mask with amber glowing eyes,
                     carved from limestone, primitive angular design with
                     horn-like protrusions at top, warm golden glow around it
  2) Cooldown mask — same mask but dimmed, grey-toned, amber eyes dark,
                     semi-transparent overlay effect

Each approximately 14x14 pixels. Represents the Stone Slam mask power in the
HUD top-right corner.
```

**Output files**: `mask_stone_slam_active.png`, `mask_stone_slam_cooldown.png` — each 14x14.

## 18.4 Dialogue Box Frame (9-slice)

```
Pixel art of a dialogue box frame/border as a 9-slice tileable UI element,
16-bit SNES style, on a solid bright green (#00FF00) background:

A rectangular frame with: dark blue-black semi-transparent interior, warm
golden/bronze ornate border (2-3 pixels wide), slightly rounded corners with
small decorative knots or Mediterranean geometric patterns at corners. The
frame should be provided as a 9-slice grid: top-left corner, top edge
(tileable), top-right corner, left edge (tileable), center (tileable fill),
right edge (tileable), bottom-left corner, bottom edge, bottom-right corner.

Overall sample frame approximately 64x32 pixels showing all 9 sections.
The style should evoke ancient Mediterranean craftsmanship.
```

**Output**: 9-slice dialogue frame pieces for the dialogue box UI.

## 18.5 Shop UI Frame

```
Pixel art of a shop menu frame, 16-bit SNES style, on a solid bright green
(#00FF00) background:

A larger rectangular frame for the shop overlay. Dark blue-black
semi-transparent background, golden/bronze ornate border (matching dialogue
box style), tab indicators at top (two tabs: "Items" and "Masks"), cursor
arrow indicator, item slot background. Show the frame with placeholder
content layout: header area with tabs, scrollable item list area, footer area
with stone count.

Overall approximately 200x140 pixels showing the full shop layout.
```

**Output**: Shop frame pieces and UI elements.

## 18.6 Boss Health Bar UI

```
Pixel art of a boss health bar frame, 16-bit SNES style, on a solid bright
green (#00FF00) background:

  1) Health bar frame — a long horizontal ornate frame for the boss health
                        bar, dark background with golden/bronze borders
                        matching the dialogue box style, carved stone aesthetic,
                        approximately 300x12 pixels
  2) Health fill segment — a tileable red/green/orange fill texture for inside
                           the bar, 1 pixel wide by 8 pixels tall, with slight
                           texture
  3) Phase marker      — a small vertical divider line with a tiny diamond
                         or arrow shape

The health bar sits at the bottom of the screen during boss fights.
```

**Output**: Boss health bar frame and fill elements.

## 18.7 Charge Indicator

**Code constants**: `_INDICATOR_WIDTH = 12`, `_INDICATOR_HEIGHT = 4` (base size).
Higher tiers widen to 16 and 20 respectively.

**Tier colors**: Colors aligned with projectile glow tiers (§ 11) for visual
coherence — the charge indicator and the projectile it spawns share the same
tier color so charge level reads consistently. Tier 1 = white / grey baseline
(neutral, pre-charge), Tier 2 = **blue**, Tier 3 = **gold**.

```
Pixel art of sling charge tier indicators, 16-bit SNES style, on a solid
bright green (#00FF00) background. Show in a horizontal row:

  1) Tier 1 glow — a small faint white/grey energy bar/circle above the
                   player's head, dim and understated, 12x4 pixels. Baseline
                   pre-charge feedback — neutral light grey #C0C0C0 with a
                   pale white core #F0F0F0.
  2) Tier 2 glow — a brighter blue energy bar, slightly wider (16x4 pixels),
                   more intense. Uses the same blue family as the Tier 2
                   projectile (§ 11): light-blue → blue gradient,
                   #78B8F8 bright core to #5090E0 outer edge.
  3) Tier 3 glow — a blazing gold energy bar, widest (20x4 pixels), with
                   small bright spark particles, dramatic. Uses the same
                   gold family as the Tier 3 projectile (§ 11): yellow →
                   gold gradient, #F8E060 bright core to #D8B838 outer edge.
                   Sparks are 1px white #FFFFFF.

These float above Balchar's head while charging the sling. The intent is that
the player sees the same color in the indicator as they will see on the stone
they're about to fire — charge level reads at a glance.
```

**Output files**: `charge_tier1.png` (12x4), `charge_tier2.png` (16x4), `charge_tier3.png` (20x4).

---

# 19. Title and Game Over screens

## 19.1 Title Screen Logo

```
Pixel art title logo reading "SA FONA", 16-bit SNES style, on a solid bright
green (#00FF00) background:

Large decorative text "SA FONA" in a Mediterranean/ancient stone carved
style. Letters appear carved from warm limestone with slight 3D depth/bevel
effect. Subtle amber glow behind the text. A small silhouette of a sling
(fona) integrated into or below the title. Approximately 200x60 pixels.
The title should feel ancient, warm, and inviting — like carved stone lit by
firelight.
```

**Output**: `title_logo.png`.

## 19.2 Game Over Screen

```
Pixel art "GAME OVER" text, 16-bit SNES style, on a solid bright green
(#00FF00) background:

Large dramatic text "GAME OVER" in dark red stone with cracks, crumbling
edges. Below it, a small prompt area for "Press any key to restart" in
lighter grey stone. Approximately 200x80 pixels total.
```

**Output**: `game_over.png`.

---

# 20. Player ground shadow

```
Pixel art of an elliptical ground shadow for a 2D platformer character,
16-bit SNES style, on a solid bright green (#00FF00) background. Show 3
sizes in a horizontal row:

  1) Small shadow  — a dark semi-transparent ellipse, approximately 12x4
                     pixels, soft edges fading outward, dark grey/black at
                     ~40% opacity
  2) Medium shadow — same style ellipse, approximately 18x5 pixels, slightly
                     lighter (character is higher off ground)
  3) Large shadow  — same style ellipse, approximately 24x6 pixels, lightest
                     (character is at max jump height)

The shadow should look natural on stone/grass terrain. Pure black with
varying transparency levels.
```

**Output**: `player_shadow.png` — 3 frames (24x6 each, smaller ones centered).
Renders below the player's feet, scaling/fading based on distance from ground.

---

# 21. Generation order

Follow this order so each asset inherits the established style:

1. **Balchar idle** (master reference for the entire world)
2. Balchar all other animations (walk, jump, wall slide, wall jump, sling, hit, death, crouch)
3. **Bep idle** (companion, references Balchar's world style)
4. Bep all other animations + curse glow
5. **Bou de Pedra idle Phase 1** (boss, references Balchar — establishes enemy visual tone)
6. Bou de Pedra all phases and animations
7. Bou de Pedra arena props (pillars, rock, shockwave, pulse, shadow)
8. **Stone Guardian** (references Bou — both are stone constructs)
9. **Rival Warrior** (references Bou's world style)
10. **Possessed Sheep** (references Bou's world style)
11. **Dimoni** (NPC, references Balchar's world)
12. **Llorenç** (NPC, references Balchar's world)
13. **Pickups** (heart, stone, shield orb)
14. **Breakables** (pot, crate)
15. **Projectiles** (3 tiers)
16. **Effects** (dust, impact, aura, portal, anticipation, debris)
17. **Attack effect overlays** (Stone Guardian sweep, Rival slash, Legionary flash)
18. **Environment props** (bonfire, taula gate)
19. **Tilesets** (outdoor, cave, talayot)
20. **Backgrounds** (outdoor, cave, talayot)
21. **Dialogue portraits** (Balchar, Bep, Dimoni, Llorenç)
22. **UI elements** (hearts, stone icon, mask icon, dialogue/shop frames, boss bar, charge indicator)
23. **Title + Game Over screens**
24. **Player ground shadow**

---

# 22. Post-generation

After generating each asset:

1. Place raw AI output in `assets/ai_sources/<asset_name>/image.png`.
2. Run the appropriate processing script from `tools/`. The matching JSON
   config lives in `tools/sprite_defs/characters/`.
3. Run `tools/clean_sprites.py` with the matching palette and `--verbose`
   to enforce palette lock and dark outline.
4. Verify against the **Quality Control Checklist** in
   [`asset_generation_guide.md`](asset_generation_guide.md#7-quality-control-checklist).
5. Minor manual touch-ups in a pixel editor if needed (the cleanup tool handles ~90%).
