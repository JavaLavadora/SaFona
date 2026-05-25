# 01 — Balchar: Master Idle Sprite

> **This is the FIRST asset to generate.** Balchar's idle is the master reference for the entire game world. No reference sprite needed — this IS the reference.

---

```
Create a SNES-style 16-bit pixel art sprite.

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

PALETTE (use ONLY these 15 colors — RGB values):
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
Design must be clean, readable, and reusable for all animations.
All future poses must match this exact design — proportions, face, clothing, colors.
```

**Sprite Anatomy Map (save this for all future Balchar prompts):**

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
