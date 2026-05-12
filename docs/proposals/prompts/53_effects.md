# 53 — Effects: All VFX

> **No reference sprite required.** Standalone effect sprites.

---

```
Create a SNES-style 16-bit pixel art effect sprite sheet.

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

PALETTE (use ONLY these 12 colors — RGB values):
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

Generate the following effects as separate groups on the sheet:

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
Label or number each group clearly.
```
