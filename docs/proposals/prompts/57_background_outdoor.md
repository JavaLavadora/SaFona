# 57 — Background: World 1 Outdoor Landscape

> **No reference sprite required.** Full-canvas background, no chroma key.

---

```
Create a SNES-style 16-bit pixel art BACKGROUND.

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

NOTE: This is a full-canvas background — do NOT use green chroma key.
Fill the ENTIRE canvas with the scene.

ENVIRONMENT: Outdoor Mallorcan Mediterranean landscape.
  Rolling green hills, limestone outcrops, distant sea,
  warm golden sunset/horizon, Mediterranean vegetation, blue sky.

PALETTE (use ONLY these 15 colors — RGB values):
  24,56,32     Dark foliage / deep shadow
  80,64,64     Rock shadow / cliff dark
  64,96,32     Forest shadow green
  144,96,32    Dirt path mid / rock warm
  136,112,96   Stone mid-tone
  120,128,24   Field green mid
  96,160,24    Grass bright green
  176,152,96   Sunlit stone / dry grass
  88,160,216   Sky blue base
  176,168,24   Olive canopy highlight
  224,160,40   Sunset horizon glow
  232,176,96   Golden haze / warm highlight
  160,200,200  Atmosphere haze / sky pale
  248,216,120  Horizon light / warm sky
  216,224,176  Sky highlight / bright haze

SIZE: 384x216 pixels (full native resolution, single image)

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
  - Fill the ENTIRE 384x216 canvas — no transparent areas
```
