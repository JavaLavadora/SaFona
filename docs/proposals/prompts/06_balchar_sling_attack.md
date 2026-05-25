# 06 — Balchar: Sling Attack

> **Reference sprite required:** Attach the Balchar MASTER idle sprite (generated in step 01) as visual reference.

---

```
Create a SNES-style 16-bit pixel art sprite sheet.

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

CRITICAL IDENTITY LOCK:
  - Must match the MASTER idle sprite EXACTLY
  - Same proportions, face, hair, headband, tunic, sash, bracers, sling
  - Same palette (15 colors), no new colors
  - Same head position (Y 10-20), belt height (Y 30), feet baseline (Y 47)
  - No redesign, no reinterpretation

REFERENCE: [ATTACH THE RAMON MASTER IDLE SPRITE HERE]

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
  - Same identity lock rules as all Balchar animations
  - Sling must be clearly visible and readable in all 3 frames
  - Background: solid green (#00FF00)
```
