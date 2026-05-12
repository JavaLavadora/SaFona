# 58 — Background: World 1 Cave System

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

ENVIRONMENT: Underground cave system. Stalactite cavern, underground water,
  bioluminescent hints, torch glow reflections on water surface.
  Dark and atmospheric.

PALETTE (use ONLY these 15 colors — RGB values):
  24,16,8      Cave darkness / deep void
  24,16,32     Dark void purple tint
  48,24,16     Dark rock warm
  40,32,56     Dark stalactite cool
  48,32,40     Cave rock mid-dark
  80,40,16     Rock face shadow
  56,56,32     Mossy rock accent
  80,48,48     Stone reddish mid
  112,56,24    Rock ochre mid
  120,72,56    Warm stone detail
  96,96,32     Cave moss highlight
  144,72,32    Stalactite amber
  176,96,40    Torch glow shadow
  208,128,56   Torch warm light
  240,168,80   Torch bright / water reflect

SIZE: 384x216 pixels (full native resolution, single image)

COMPOSITION:
  - Foreground: Stalagmite silhouettes
  - Midground: Cave walls with mineral deposits, distant stalactites
  - Background: Deep cave void, faint distant glow
  - Water: Reflective underground pool/stream in lower portion
  - Lighting: Warm torch glow patches in darkness

STYLE RULES:
  - Parallax-ready: designed to scroll slightly behind gameplay
  - Less detailed than foreground tiles — atmospheric depth
  - Top-left light source consistent with sprites
  - No anti-aliasing — clean pixel art
  - Fill the ENTIRE 384x216 canvas — no transparent areas
```
