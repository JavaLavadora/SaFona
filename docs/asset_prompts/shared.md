# Sa Fona — Asset Prompts (Shared / Cross-World)

**Scope**: This file covers assets that appear across multiple worlds — the
player, the companion, generic pickups and breakables, projectiles, generic
effects, UI, title/game-over screens, and the player's ground shadow.

For **per-world assets** (bosses, enemies, NPCs, tilesets, backgrounds, world
environment props), see the matching world file:

- [`world1.md`](world1.md) — World 1 (Sa Talaia)
- Future: `world2.md` (Romana), `world3.md` (Comte Mal), `world4.md` (Pirates),
  `world5.md` (S'Invasio).

For the workflow, processing pipeline, and "how to add a new asset"
instructions, see [`../asset_generation_guide.md`](../asset_generation_guide.md).
This file is **prompts only**.

If you find prompt content **outside `docs/asset_prompts/`**, it is a bug —
file an Issue.

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

> This convention is the canonical reference for all per-world files too —
> world files link back here rather than restating it.

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

> Per-world files also use this block — they reference it here rather than
> restating it.

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

### Style chains (per-world)

Each world's style chain (which asset references which) lives in that world's
file. The cross-world rule: **Balchar (master)** anchors the entire game's
visual identity. World 1 chains from Balchar; later worlds build on the
visual language established in World 1.

See [`world1.md`](world1.md) for the World 1 style chain and generation order.

---

# Table of contents (shared)

- [1. Balchar (player)](#1-balchar-player-character) — idle, walk, jump, wall slide, wall jump, sling, hit, death, crouch
- [2. Bep (companion)](#2-bep-companion--myotragus) — idle, walk, jump, scared, excited, glow
- [9. Pickups](#9-pickups) — heart, stone, shield orb
- [10. Breakables](#10-breakables) — pot, crate (with drop tables)
- [11. Projectiles](#11-projectiles) — tier 1/2/3 sling stones
- [12. Effects (generic)](#12-effects-generic) — dust, impact, portal, anticipation, debris
- [17. Dialogue portraits (cross-world)](#17-dialogue-portraits-cross-world) — Balchar (4), Bep (4)
- [18. UI elements](#18-ui-elements) — HUD hearts, stone icon, mask icon, dialogue frame, shop frame, boss health bar, charge indicator
- [19. Title and Game Over screens](#19-title-and-game-over-screens)
- [20. Player ground shadow](#20-player-ground-shadow)
- [22. Post-generation](#22-post-generation)

> Section numbering is preserved from the original consolidated file so external
> references (PRs, Issues, docstrings) keep working. Sections **3-8** (per-world
> bosses / enemies / NPCs), **13** (per-enemy attack effects), **14** (world
> environment props), **15** (tilesets), **16** (backgrounds), **17.3-17.4**
> (world NPC portraits), and **21** (per-world generation order) live in the
> matching world file.

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

> **Note (W1 narrative tie)**: the curse-glow aura is a visual layer applied
> to Bep (a cross-world companion) by the **Dimoni de Sant Joan** in World 1.
> The prompt lives here because the sprite IS Bep; the colors of the aura
> match the Dimoni palette (see [`world1.md`](world1.md#7-dimoni-de-sant-joan-npc)).

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

# 12. Effects (generic)

**Scope**: cross-world VFX — dust, impact, portal, anticipation glow, stone
debris. The **Dimoni aura** effect lives with the Dimoni in
[`world1.md` § 12 (Dimoni aura)](world1.md#dimoni-aura-effect-w1) because the
purple-red glow is tied to that W1 supernatural character; it shares the
generic `effects.gpl` palette block below.

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

> Note: the **Dimoni aura** effect (16x16, 3 frames in a row = 48x16,
> uses portal purple/bright/deep) is documented in [`world1.md` § 12 (Dimoni
> aura)](world1.md#dimoni-aura-effect-w1). When generating the full `effects.gpl`
> sheet, include the Dimoni aura row using the palette colors above.

---

# 17. Dialogue portraits (cross-world)

The dialogue system uses **44x44 pixel** portrait boxes. Each portrait is a
square headshot — face + upper shoulders — facing slightly LEFT (toward the
dialogue text). Portrait names below match the `"portrait"` field values used
by `sa_fona/data/dialogue/world1_dialogue.json` and `world2_dialogue.json`.

Per-world NPC portraits (Dimoni, Llorenç, future world NPCs) live in their
matching world file. Balchar and Bep portraits live here because they appear
across all worlds.

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

---

# 18. UI elements

All UI elements live in `assets/ui/`. They sit on top of the gameplay layer and
must read clearly at small size.

> **Cross-world caveat**: the Boss Health Bar (§ 18.6) is currently styled for
> World 1 (carved-stone aesthetic, golden/bronze ornate borders matching the
> dialogue box). When later worlds need a different visual treatment for boss
> arenas (Roman marble, demonic, etc.), add per-world variants in the matching
> world file and reference them here.

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

> **Cross-world caveat**: currently styled for World 1 (carved-stone aesthetic,
> golden/bronze borders). Future worlds may need variants — add to the matching
> world file and reference here.

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

# 22. Post-generation

After generating each asset:

1. Place raw AI output in `assets/ai_sources/<asset_name>/image.png`.
2. Run the appropriate processing script from `tools/`. The matching JSON
   config lives in `tools/sprite_defs/characters/`.
3. Run `tools/clean_sprites.py` with the matching palette and `--verbose`
   to enforce palette lock and dark outline.
4. Verify against the **Quality Control Checklist** in
   [`../asset_generation_guide.md`](../asset_generation_guide.md#7-quality-control-checklist).
5. Minor manual touch-ups in a pixel editor if needed (the cleanup tool handles ~90%).
