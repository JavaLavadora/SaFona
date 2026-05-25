# 54 — Tileset: World 1 Outdoor (Sa Talaia)

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

ENVIRONMENT: Outdoor talayotic Mediterranean landscape.
  Limestone terrain with grass, ancient stone towers (talayots),
  rocky outcrops, Mediterranean vegetation. Warm sunlit colors.

REFERENCE: [ATTACH THE RAMON MASTER IDLE SPRITE HERE — for contrast/shading match]

PALETTE (use ONLY these 15 colors — RGB values):
  32,24,16     Dark outline
  32,72,8      Dark moss
  48,96,16     Grass shadow
  64,96,32     Moss mid
  80,128,40    Grass base
  104,152,56   Grass highlight
  96,80,48     Earth dark
  120,96,56    Limestone deep shadow
  144,120,80   Limestone shadow
  168,144,96   Limestone base
  176,152,104  Limestone warm
  192,160,112  Limestone mid
  208,176,120  Limestone highlight
  224,192,120  Sandstone bright
  240,208,152  Sunlit edge

TILE CONSTRAINTS:
  - Tile size:    16x16 pixels
  - Layout:       4 base tiles in a single horizontal row (64x16 total)
  - Tile 1:       Top-left corner (grass top + stone side)
  - Tile 2:       Top edge (grass surface)
  - Tile 3:       Interior fill (solid stone)
  - Tile 4:       Single isolated block (all sides exposed)
  - Designed for auto-tiling (16 variants generated from these 4)

STYLE RULES:
  - Match character contrast and shading from Balchar's sprites
  - Top-left light source
  - Moderate texture — visible stone grain but not noisy
  - Grass on top surfaces, stone on sides and interior

BACKGROUND: Solid green (#00FF00)
```
