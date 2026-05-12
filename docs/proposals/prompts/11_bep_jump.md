# 11 — Bep: Jump

> **Reference sprite required:** Attach the Bep MASTER idle sprite (generated in step 09) as visual reference.

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

CRITICAL IDENTITY LOCK — must match Bep MASTER idle exactly.
  - Same proportions, face, fur, horns, hooves, eyes
  - Same palette (9 colors), no new colors

REFERENCE: [ATTACH THE BEP MASTER IDLE SPRITE HERE]

PALETTE (use ONLY these 9 colors — RGB values):
  160,128,88   Fur base
  192,160,120  Fur highlight
  128,104,72   Fur dark
  224,208,200  Face / eye white
  32,24,16     Pupil
  104,72,48    Nose
  200,184,160  Horn light
  168,152,128  Horn dark
  80,56,32     Hooves

SPRITE CONSTRAINTS:
  - Sheet size:  16x16 (1 frame)
  - Frame size:  16x16
  - Facing:      RIGHT

ANIMATION DESCRIPTION:
  Single frame: All four hooves tucked under body, ears perked up,
  eyes wide, slight upward arc. Compact mid-air pose.

RULES:
  - Same identity lock
  - Background: solid green (#00FF00)
```
