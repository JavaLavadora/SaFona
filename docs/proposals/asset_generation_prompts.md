# Sa Fona — AI Asset Generation Prompts

All prompts follow the [Asset Style Guide](asset_style_guide.md).
Palettes reference `.gpl` files in `assets/palettes/`.

**Style chain (World 1):** Ramon (master) -> Bou de Pedra (boss) -> All enemies/NPCs

**Generation rules:**
- Background: Solid bright green `#00FF00` for chroma-key removal
- No anti-aliasing, no blur, no gradients
- Characters face RIGHT by default
- Poses numbered and arranged in a single horizontal row
- Clean pixel edges, clear green space between poses

---

## Global Style Block

> Copy this verbatim into every prompt.

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

---

# 1. RAMON (Player Character)

**Palette** (`assets/palettes/ramon.gpl` — 15 colors):

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

### 1.1 Ramon — Master Idle Sprite (GENERATE FIRST)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

CHARACTER IDENTITY:
  - Name:    Ramon
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
This sprite is the MASTER reference for all of Ramon's animations.
Design must be clean, readable, and reusable. All future poses must match
this exact design — proportions, face, clothing, colors.
```

**Sprite Anatomy Map — Ramon:**

```
- Headroom:      Y 0-10 reserved for overhead content in other animations
- Head:          Y 10-20 (fixed)
- Torso:         Y 20-32 (fixed vertical)
- Belt/sash:     Absolute Y = 30
- Feet baseline: Absolute Y = 47
- Width:         ~14px body core within 32px frame

Allowed to move: arms, sling, torso rotation, cloth sway
Forbidden: head position, leg length, belt height, palette changes
```

### 1.2 Ramon — Walk Cycle

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

PALETTE: (same 15 colors as idle — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  192x48 (6 frames)
  - Frame count: 6
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.

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

### 1.3 Ramon — Jump (2 frames)

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER idle sprite EXACTLY
  - Same palette (15 colors), same proportions, same design

PALETTE: (same 15 colors as idle — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.
Extended limbs may use the full frame height including headroom.

ANIMATION DESCRIPTION:
  Frame 1: Rising — legs tucked slightly, arms up, sling trailing behind,
           body angled slightly upward
  Frame 2: Falling — legs extended down, arms slightly above head,
           sling streaming upward, body angled slightly downward

RULES:
  - Same identity lock rules as all Ramon animations
  - Background: solid green (#00FF00)
```

### 1.4 Ramon — Wall Slide (2 frames)

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Ramon animations).

PALETTE: (same 15 colors — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT (body pressed against wall to the right)

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.

ANIMATION DESCRIPTION:
  Frame 1: Sliding down — body pressed flat against wall (right side),
           both hands touching wall surface, legs slightly bent,
           slow descent pose
  Frame 2: Slight variation — legs position shifts slightly for friction effect

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

### 1.5 Ramon — Wall Jump (2 frames)

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Ramon animations).

PALETTE: (same 15 colors — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  64x48 (2 frames)
  - Frame count: 2
  - Frame size:  32x48 each
  - Facing:      RIGHT (jumping away from wall to the left)

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.
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

### 1.6 Ramon — Sling Attack (3 frames)

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Ramon animations).

PALETTE: (same 15 colors — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  96x48 (3 frames)
  - Frame count: 3
  - Frame size:  32x48 each
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.
The sling cord extends above the head into the headroom area. The CHARACTER BODY stays the same size as idle — only the sling uses the extra space.

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

### 1.7 Ramon — Hit (1 frame)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Ramon animations).

PALETTE: (same 15 colors — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  32x48 (1 frame)
  - Frame size:  32x48
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.
Recoil pose may use headroom. Body proportions stay identical to idle.

ANIMATION DESCRIPTION:
  Single frame: Recoil — body bent backward from impact,
  arms flung slightly outward, grimacing expression,
  slight backward lean as if struck in the chest.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

### 1.8 Ramon — Death (1 frame)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK (same as all Ramon animations).

PALETTE: (same 15 colors — see Ramon palette above)

SPRITE CONSTRAINTS:
  - Sheet size:  32x48 (1 frame)
  - Frame size:  32x48
  - Facing:      RIGHT

BODY SIZE RULE: Character body must be the SAME SIZE as the master idle sprite. The frame has headroom above — do NOT resize the body to fill the frame.
Horizontal pose uses width, not headroom.

ANIMATION DESCRIPTION:
  Single frame: Collapsed — body slumped on the ground,
  lying on back or side, limbs limp, sling dropped nearby.
  Clear "defeated" pose, not graphic.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```

---

# 2. BEP (Companion — Myotragus)

**Palette** (`assets/palettes/bep.gpl` — 9 colors):

```
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

### 2.1 Bep — Master Idle Sprite (GENERATE FIRST)

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
  - Must belong to the same world as Ramon (the player character)
  - Same shading logic and pixel density as Ramon
  - Same outline treatment (dark outline color)

SPRITE CONSTRAINTS:
  - Sprite sheet: 4 frames in horizontal row
  - Total size:   64x16
  - Frame size:   16x16 each
  - Facing:       RIGHT
  - Animation:    Idle — subtle ear twitch, slight body sway, occasional blink

BACKGROUND: Solid green (#00FF00)

IMPORTANT:
This is the MASTER reference for Bep. All future Bep animations must match exactly.
```

### 2.2 Bep — Walk (4 frames)

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

### 2.3 Bep — Jump (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
PALETTE: (same 9 colors)

Sheet: 16x16 (1 frame). Facing RIGHT.

Pose: All four hooves tucked under body, ears perked up,
eyes wide, slight upward arc. Compact mid-air pose.

Background: solid green (#00FF00)
```

### 2.4 Bep — Scared (1 frame)

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

### 2.5 Bep — Excited (1 frame)

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

---

# 3. BOU DE PEDRA (World 1 Boss)

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

**Reference character: Ramon** (same world, same era — Bou is the first non-player character
to be generated for World 1, establishing the enemy visual tone).

### 3.1 Bou de Pedra — Master Idle Phase 1 (GENERATE FIRST)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Ramon (talayotic Balearic, Bronze Age)
  - Same shading logic and pixel density as Ramon
  - Same outline treatment
  - Different identity: Ramon is human, Bou is a stone construct

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
  - Sheet size:  40x36 (1 frame)
  - Frame size:  40x36
  - Facing:      RIGHT (facing the player)

BACKGROUND: Solid green (#00FF00)

IMPORTANT:
This is the MASTER reference for the boss. All boss animations and phase
variants must match this base design. The phase progression adds color
accents but does NOT change the stone structure.
```

### 3.2 Bou de Pedra — Idle Phase 2

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — same stone bull as Phase 1 MASTER, exact same structure.

PALETTE: Same 12 colors, but now INCLUDE the Phase 2 accent (224,144,40 fiery orange).
  Replace some neutral amber rune glow areas with orange glow.
  Stone structure and shape is IDENTICAL to Phase 1.

Sheet: 40x36 (1 frame). Facing RIGHT.

Phase 2 visual change: Rune cracks glow orange instead of amber.
Stone surface unchanged. More energy visible in cracks. Bull appears more agitated.

Background: solid green (#00FF00)
```

### 3.3 Bou de Pedra — Idle Phase 3

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK — same stone bull, exact same structure.

PALETTE: Same 12 colors, now INCLUDE Phase 3 accent (224,40,40 enraged red).
  Rune cracks glow red. Exposed glowing red core visible in chest area.
  Stone surface shows more cracks. Most aggressive appearance.

Sheet: 40x36 (1 frame). Facing RIGHT.

Phase 3 visual change: Red glowing cracks, exposed red weak point in chest,
stone surface more fractured. Maximum energy discharge look.

Background: solid green (#00FF00)
```

### 3.4 Bou de Pedra — Rush Attack (2 frames)

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

### 3.5 Bou de Pedra — Headbutt (2 frames)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Wind-up — head pulled back, body coiled, preparing to strike
  Frame 2: Impact — head thrust forward and down, horns at strike point,
           body extended, shockwave implied

Background: solid green (#00FF00)
```

### 3.6 Bou de Pedra — Stomp (2 frames)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 80x36 (2 frames). Frame size: 40x36. Facing RIGHT.

  Frame 1: Raised — front legs lifted high, body rearing up
  Frame 2: Impact — front legs slammed down, shockwave lines implied at ground level

Background: solid green (#00FF00)
```

### 3.7 Bou de Pedra — Hurl (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Head tossing motion — flinging a rock projectile with horns,
head angled upward in throwing arc, rock departing from horn tips.

Background: solid green (#00FF00)
```

### 3.8 Bou de Pedra — Stunned (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Dazed — head lowered and swaying, legs wobbling slightly spread,
cracks in stone more visible, energy glow dimmed. Vulnerable state.

Background: solid green (#00FF00)
```

### 3.9 Bou de Pedra — Death (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Crumbling — stone blocks separating and falling apart,
energy fading from cracks, collapse in progress. Head tilted down,
legs buckling. Not fully destroyed — mid-collapse moment.

Background: solid green (#00FF00)
```

### 3.10 Bou de Pedra — Transition (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Full 12 colors.

Sheet: 40x36 (1 frame). Facing RIGHT.

Pose: Phase transition — bull roaring/bellowing, head thrown back,
energy surging through all cracks simultaneously (bright glow everywhere),
stone vibrating. Dramatic power-up moment between phases.

Background: solid green (#00FF00)
```

### 3.11 Boss Arena Props

```
GLOBAL STYLE CONSTRAINTS APPLY.
PALETTE: Same Bou de Pedra 12 colors (stone + energy).

PILLAR INTACT:
  - Size: 16x48 (1 frame)
  - Description: Tall stone pillar, rough-hewn limestone matching the boss arena.
    Subtle rune markings. Structurally solid.

PILLAR DESTROYED:
  - Size: 16x48 (1 frame)
  - Description: Same pillar but broken — top half shattered,
    rubble at base, broken stone edges. Cracks visible.

ROCK PROJECTILE:
  - Size: 8x8 (1 frame)
  - Description: Small rough stone chunk hurled by the boss.
    Angular, grey stone with slight moss.

SHOCKWAVE:
  - Size: 16x8 (1 frame)
  - Description: Ground impact wave — expanding arc of dust and stone debris
    at ground level. Horizontal spread.

PULSE:
  - Size: 24x16 (1 frame)
  - Description: Energy pulse emanating from boss — circular expanding ring
    of amber/orange energy.

SHADOW:
  - Size: 16x6 (1 frame)
  - Description: Simple dark elliptical shadow cast beneath the boss.

Background: solid green (#00FF00) for all props.
```

---

# 4. POSSESSED SHEEP (Enemy)

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

**Reference: Bou de Pedra** (boss of the world — style anchor for all World 1 enemies).
Despite being a different creature (sheep vs stone bull), the pixel art style,
shading logic, and outline treatment must be indistinguishable.

### 4.1 Possessed Sheep — Master Idle (GENERATE FIRST)

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
  - Culture:       Talayotic Balearic (same era as Ramon)
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

### 4.2 Possessed Sheep — Walk (4 frames)

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

### 4.3 Possessed Sheep — Charge (2 frames)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 32x16 (2 frames). Frame size: 16x16. Facing RIGHT.

  Frame 1: Head lowered, horns forward, legs coiled, about to launch
  Frame 2: Full charge — body horizontal, legs in full sprint, head-down ram attack

Background: solid green (#00FF00)
```

### 4.4 Possessed Sheep — Hit (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 16x16 (1 frame). Facing RIGHT.
Pose: Recoil — body knocked back, wool puffed out, eyes squinted.

Background: solid green (#00FF00)
```

### 4.5 Possessed Sheep — Death (1 frame)

```
GLOBAL STYLE CONSTRAINTS APPLY.
CRITICAL IDENTITY LOCK. PALETTE: Same 8 colors.

Sheet: 16x16 (1 frame). Facing RIGHT.
Pose: Collapsed on side, eyes closed (no longer glowing red),
dimoni energy dissipating. Looks like a normal sleeping sheep.

Background: solid green (#00FF00)
```

---

# 5. RIVAL WARRIOR (Enemy)

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

**Reference: Bou de Pedra** (World 1 boss — style anchor).

### 5.1 Rival Warrior — Master Idle (GENERATE FIRST)

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
  - Culture:       Competing talayotic tribe (same Balearic Bronze Age as Ramon)
  - Differentiators: Human fighter with stone weapons and animal hide armor.
                     Slightly taller and leaner than Ramon.
                     Darker skin, messy dark hair with war paint stripes on face.

VISUAL DETAILS:
  - Body:      Lean warrior build, slightly taller than Ramon
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

### 5.2 Rival Warrior — Walk (4 frames)

```
CRITICAL IDENTITY LOCK — match Rival Warrior MASTER idle.
PALETTE: Same 12 colors.
Sheet: 64x24 (4 frames). Frame size: 16x24. Facing RIGHT.
Patrol walk — weapon at side, alert stance, deliberate stride.
Background: solid green (#00FF00)
```

### 5.3 Rival Warrior — Attack (2 frames)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 32x24 (2 frames). Frame size: 16x24. Facing RIGHT.
  Frame 1: Wind-up — club raised overhead
  Frame 2: Swing down — club striking forward/down
Background: solid green (#00FF00)
```

### 5.4 Rival Warrior — Block (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Defensive — club held horizontally to block, body braced.
Background: solid green (#00FF00)
```

### 5.5 Rival Warrior — Hit (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Struck — body recoiling backward, weapon arm dropping.
Background: solid green (#00FF00)
```

### 5.6 Rival Warrior — Death (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 16x24 (1 frame). Facing RIGHT.
Pose: Collapsed — fallen to the ground, weapon dropped beside body.
Background: solid green (#00FF00)
```

---

# 6. STONE GUARDIAN (Enemy)

**Palette** (`assets/palettes/stone_guardian.gpl` — 9 colors):

```
128 128 136  Stone base
152 152 152  Stone light
 96  96 104  Stone dark
 80  80  88  Stone very dark
 80 200  80  Eye glow
120 248 120  Eye bright
 72  96  56  Moss
 88 120  72  Moss light
 56  56  64  Crack
```

**Reference: Bou de Pedra** (both are stone constructs animated by dimoni energy — closest
visual relative in the world).

### 6.1 Stone Guardian — Master Idle (GENERATE FIRST)

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
  80,200,80    Eye glow
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

### 6.2 Stone Guardian — Walk (3 frames)

```
CRITICAL IDENTITY LOCK — match Stone Guardian MASTER idle.
PALETTE: Same 9 colors.
Sheet: 72x32 (3 frames). Frame size: 24x32. Facing RIGHT.
Heavy lumbering walk — slow, deliberate, ground-shaking implied.
Each step is a heavy stomp. Body barely sways. Arms swing minimally.
Background: solid green (#00FF00)
```

### 6.3 Stone Guardian — Attack (2 frames)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 48x32 (2 frames). Frame size: 24x32. Facing RIGHT.
  Frame 1: Arm raised — massive stone fist pulled back overhead
  Frame 2: Arm sweep — wide horizontal sweep with stone fist, ground-level arc
Background: solid green (#00FF00)
```

### 6.4 Stone Guardian — Hit (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 24x32 (1 frame). Facing RIGHT.
Pose: Stone chips flying off — body rocked backward slightly,
cracks more visible from impact. Green eyes flicker.
Background: solid green (#00FF00)
```

### 6.5 Stone Guardian — Death (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 9 colors.
Sheet: 24x32 (1 frame). Facing RIGHT.
Pose: Crumbling apart — stone blocks separating, green eye glow fading,
collapsing into rubble pile. Mid-collapse moment.
Background: solid green (#00FF00)
```

---

# 7. DIMONI DE SANT JOAN (NPC)

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

### 7.1 Dimoni — Master Idle (GENERATE FIRST)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Ramon
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
  - Sheet size:  24x40 (1 frame)
  - Frame size:  24x40
  - Facing:      RIGHT
  - Pose:        Standing imperiously, one hand raised, fiery aura flickering

BACKGROUND: Solid green (#00FF00)
```

### 7.2 Dimoni — Laugh (1 frame)

```
CRITICAL IDENTITY LOCK — match Dimoni MASTER idle.
PALETTE: Same 12 colors.
Sheet: 24x40 (1 frame). Facing RIGHT.
Pose: Head thrown back laughing, mouth open, flames flare up around body.
Background: solid green (#00FF00)
```

### 7.3 Dimoni — Grant (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 24x40 (1 frame). Facing RIGHT.
Pose: Arms extended forward, palms open, energy flowing outward — granting a power.
Generous but still menacing posture.
Background: solid green (#00FF00)
```

### 7.4 Dimoni — Angry (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 24x40 (1 frame). Facing RIGHT.
Pose: Hunched forward aggressively, eyes blazing brighter, flames intensified,
fists clenched. Rage posture.
Background: solid green (#00FF00)
```

---

# 8. LLORENÇ (NPC — Shopkeeper)

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

### 8.1 Llorenç — Master Idle (GENERATE FIRST)

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as Ramon
  - Same shading logic and pixel density
  - Same outline treatment
  - Friendly NPC — warmer body language than enemies

CHARACTER IDENTITY:
  - Name:    Llorenç
  - Role:    Friendly NPC shopkeeper / scholar from Menorca
  - Culture: Talayotic warrior-scholar (same era as Ramon)
  - Differentiators: Slightly taller and leaner than Ramon, friendly expression,
                     cream linen shirt, olive green vest, terracotta apron,
                     leather satchel. Enthusiastic about artifacts.

VISUAL DETAILS:
  - Body:      Lean, slightly taller than Ramon
  - Clothing:  Cream linen shirt, olive green vest over it, terracotta apron
  - Hair:      Dark hair and beard
  - Expression: Friendly, enthusiastic (contrast to Ramon's grumpiness)
  - Accessories: Leather satchel visible at side
  - Size:      20x36 pixels

PALETTE (use ONLY these 12 colors):
  192,136,80   Skin base
  168,112,64   Skin shadow
  64,40,24     Hair / beard
  32,24,16     Eyes
  240,232,208  Shirt (cream linen)
  216,208,184  Shirt shadow
  56,104,72    Vest (olive green)
  40,80,56     Vest shadow
  184,56,40    Apron (terracotta)
  152,40,32    Apron shadow
  88,64,40     Pants (brown)
  112,80,48    Boots

SPRITE CONSTRAINTS:
  - Sheet size:  20x36 (1 frame)
  - Frame size:  20x36
  - Facing:      RIGHT
  - Pose:        Standing relaxed, one hand on satchel, friendly smile

BACKGROUND: Solid green (#00FF00)
```

### 8.2 Llorenç — Talk (1 frame)

```
CRITICAL IDENTITY LOCK — match Llorenç MASTER idle.
PALETTE: Same 12 colors.
Sheet: 20x36 (1 frame). Facing RIGHT.
Pose: Animated talking — one hand gesturing enthusiastically, mouth open, leaning forward.
Background: solid green (#00FF00)
```

### 8.3 Llorenç — Shop (1 frame)

```
CRITICAL IDENTITY LOCK. PALETTE: Same 12 colors.
Sheet: 20x36 (1 frame). Facing RIGHT.
Pose: Behind counter pose — hands on surface, satchel open showing wares,
inviting gesture. Shopkeeper mode.
Background: solid green (#00FF00)
```

---

# 9. PICKUPS

### 9.1 Heart Pickup (2 frames)

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

### 9.2 Stone Pickup / Currency (2 frames)

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

---

# 10. BREAKABLES

### 10.1 Pot (intact + break)

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

### 10.2 Crate (intact + break)

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

# 11. PROJECTILES

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

# 12. EFFECTS

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

DUST — 8x8 (4 frames):
  Small puff of dust/debris. Frames show expansion and dissipation.
  Use dust white/grey/dark colors.

IMPACT — 12x12 (3 frames):
  Hit impact flash. Frames: bright flash → expanding ring → fade.
  Use flash yellow/orange colors.

DIMONI AURA — 16x16 (3 frames):
  Pulsing supernatural aura. Purple energy fluctuation.
  Use portal purple/bright/deep colors.

PORTAL — 24x32 (4 frames):
  Swirling time portal. Tall oval shape with energy spiraling inward.
  Use all portal colors. Frames show rotation.

ANTICIPATION GLOW — 8x8 (2 frames):
  Subtle charge-up glow before an attack. Use flash/orange colors.

STONE DEBRIS — 8x8 (3 frames):
  Small stone chunks scattering from broken stone. Use dust colors.
  Frames show pieces flying outward and settling.

Background: solid green (#00FF00) for all effects.
```

---

# 13. TILESETS

### 13.1 World 1 — Outdoor (Sa Talaia)

**Palette** (`assets/palettes/tileset_world1.gpl` — 15 colors):

```
Create a SNES-style 16-bit pixel art TILESET.

GLOBAL STYLE CONSTRAINTS APPLY.

ENVIRONMENT: Outdoor talayotic Mediterranean landscape.
  Limestone terrain with grass, ancient stone towers (talayots),
  rocky outcrops, Mediterranean vegetation. Warm sunlit colors.

PALETTE: Use the 15 colors from tileset_world1.gpl:
  (warm limestone browns, grass greens, sandy highlights, dark outline)

TILE CONSTRAINTS:
  - Tile size:    16x16 pixels
  - Layout:       4 base tiles in a single horizontal row (64x16 total)
  - Tile 1:       Top-left corner (grass top + stone side)
  - Tile 2:       Top edge (grass surface)
  - Tile 3:       Interior fill (solid stone)
  - Tile 4:       Single isolated block (all sides exposed)
  - Designed for auto-tiling (16 variants generated from these 4)

STYLE RULES:
  - Match character contrast and shading from Ramon's sprites
  - Top-left light source
  - Moderate texture — visible stone grain but not noisy
  - Grass on top surfaces, stone on sides and interior

Background: solid green (#00FF00)
```

### 13.2 World 1 — Cave (Sa Cova des Foner)

**Palette** (`assets/palettes/tileset_world1_cave.gpl` — 15 colors):

```
Same structure as outdoor tileset but:

ENVIRONMENT: Dark cave interior. Stalactites, mossy cave walls,
  mineral deposits, damp stone. Cool blue-grey tones.

PALETTE: Use 15 colors from tileset_world1_cave.gpl:
  (cool grey-blue stone, deep shadows, cave moss greens)

Same 4-tile layout (64x16 total), 16x16 each.
  Tile 1: Cave ceiling corner (stalactite + wall)
  Tile 2: Cave ceiling edge (rough stone ceiling)
  Tile 3: Interior cave rock (solid dark stone)
  Tile 4: Isolated cave block

Background: solid green (#00FF00)
```

### 13.3 World 1 — Talayot (Es Talayot Sagrat)

**Palette** (`assets/palettes/tileset_world1_talayot.gpl` — 15 colors):

```
Same structure as outdoor tileset but:

ENVIRONMENT: Interior of ancient stone tower. Precisely cut limestone blocks,
  faint carved bull motifs, torch-lit amber glow, stone archways.
  Warmer than cave, more architectural than outdoor.

PALETTE: Use 15 colors from tileset_world1_talayot.gpl:
  (warm stone browns, golden highlights, dark moss)

Same 4-tile layout (64x16 total), 16x16 each.
  Tile 1: Wall corner (cut stone + edge treatment)
  Tile 2: Wall top edge (carved stone block top)
  Tile 3: Interior wall fill (precisely cut blocks)
  Tile 4: Single architectural block

Background: solid green (#00FF00)
```

---

# 14. BACKGROUNDS

### 14.1 World 1 — Outdoor Landscape

**Palette** (`assets/palettes/bg_world1.gpl` — 15 colors):

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

### 14.2 World 1 — Cave System

**Palette** (`assets/palettes/bg_world1_cave.gpl` — 15 colors):

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

### 14.3 World 1 — Talayot Interior

**Palette** (`assets/palettes/bg_world1_talayot.gpl` — 15 colors):

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

# 15. GENERATION ORDER

Follow this order to maintain the style chain:

1. **Ramon idle** (master reference for the entire world)
2. **Ramon all other animations** (walk, jump, wall slide, wall jump, sling, hit, death)
3. **Bep idle** (companion, references Ramon's world style)
4. **Bep all other animations**
5. **Bou de Pedra idle Phase 1** (boss, references Ramon — establishes enemy visual tone)
6. **Bou de Pedra all phases and animations**
7. **Bou de Pedra arena props** (pillars, rock, shockwave, pulse, shadow)
8. **Stone Guardian** (references Bou — both are stone constructs)
9. **Rival Warrior** (references Bou's world style)
10. **Possessed Sheep** (references Bou's world style)
11. **Dimoni** (NPC, references Ramon's world)
12. **Llorenç** (NPC, references Ramon's world)
13. **Pickups** (heart, stone)
14. **Breakables** (pot, crate)
15. **Projectiles** (3 tiers)
16. **Effects** (dust, impact, aura, portal, debris)
17. **Tilesets** (outdoor, cave, talayot)
18. **Backgrounds** (outdoor, cave, talayot)

---

# 16. POST-GENERATION

After generating each asset:

1. Place raw AI output in `assets/ai_sources/<asset_name>/image.png`
2. Run the appropriate processing script from `tools/`
3. Run `tools/clean_sprites.py` with the matching palette and `--verbose`
4. Verify quality control checklist (Section 7 of style guide)
5. Minor manual touch-ups in a pixel editor if needed (the cleanup tool handles ~90%)
