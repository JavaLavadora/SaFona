# 56 — Tileset: World 1 Talayot (Es Talayot Sagrat)

> **Reference sprite required:** Attach the Balchar MASTER idle sprite (generated in step 01) so tile contrast and shading matches the player character.

---

```
Create a SNES-style 16-bit pixel art TILESET.

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

ENVIRONMENT: Interior of ancient stone tower. Precisely cut limestone blocks,
  faint carved bull motifs, torch-lit amber glow, stone archways.
  Warmer than cave, more architectural than outdoor.

REFERENCE: [ATTACH THE BALCHAR MASTER IDLE SPRITE HERE — for contrast/shading match]

PALETTE (use ONLY these 15 colors — RGB values):
  32,24,16     Dark outline
  32,72,16     Dark moss
  48,96,16     Moss shadow
  80,128,40    Moss base
  96,152,56    Moss highlight
  96,80,48     Earth dark
  120,96,56    Stone deep shadow
  144,120,80   Stone shadow
  168,144,96   Stone base
  184,152,96   Stone warm
  192,160,104  Stone mid
  200,168,112  Stone light
  208,176,112  Stone bright
  224,192,136  Stone highlight
  240,200,128  Sunlit stone

TILE CONSTRAINTS:
  - Tile size:    16x16 pixels
  - Layout:       4 base tiles in a single horizontal row (64x16 total)
  - Tile 1:       Wall corner (cut stone + edge treatment)
  - Tile 2:       Wall top edge (carved stone block top)
  - Tile 3:       Interior wall fill (precisely cut blocks)
  - Tile 4:       Single architectural block
  - Designed for auto-tiling (16 variants generated from these 4)

STYLE RULES:
  - Match character contrast and shading from Balchar's sprites
  - Top-left light source
  - Moderate texture — carved stone blocks, not rough
  - Warm amber tones, architectural precision

BACKGROUND: Solid green (#00FF00)
```
