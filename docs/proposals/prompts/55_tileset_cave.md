# 55 — Tileset: World 1 Cave (Sa Cova des Foner)

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

ENVIRONMENT: Dark cave interior. Stalactites, mossy cave walls,
  mineral deposits, damp stone. Cool blue-grey tones.

REFERENCE: [ATTACH THE BALCHAR MASTER IDLE SPRITE HERE — for contrast/shading match]

PALETTE (use ONLY these 15 colors — RGB values):
  24,16,16     Dark outline
  24,56,32     Deep cave moss
  32,72,40     Cave moss shadow
  40,88,48     Cave moss base
  48,96,56     Cave moss light
  56,64,72     Cave rock deep
  64,72,80     Cave rock dark
  72,80,96     Cave rock shadow
  80,88,104    Cave stone shadow
  88,96,112    Cave stone base
  96,104,120   Cave stone mid
  104,112,128  Cave stone light
  120,128,136  Cave rock bright
  136,144,152  Cave highlight
  160,168,176  Cave rim light

TILE CONSTRAINTS:
  - Tile size:    16x16 pixels
  - Layout:       4 base tiles in a single horizontal row (64x16 total)
  - Tile 1:       Cave ceiling corner (stalactite + wall)
  - Tile 2:       Cave ceiling edge (rough stone ceiling)
  - Tile 3:       Interior cave rock (solid dark stone)
  - Tile 4:       Isolated cave block
  - Designed for auto-tiling (16 variants generated from these 4)

STYLE RULES:
  - Match character contrast and shading from Balchar's sprites
  - Top-left light source
  - Moderate texture — visible stone grain but not noisy
  - Cool blue-grey tones, moss accents

BACKGROUND: Solid green (#00FF00)
```
