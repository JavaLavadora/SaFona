# 15 — Bou de Pedra: Idle Phase 2

> **Reference sprite required:** Attach the Bou de Pedra Phase 1 MASTER idle sprite (generated in step 14) as visual reference.

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
  - Must match the Phase 1 MASTER idle sprite EXACTLY in structure and shape
  - Same stone bull body, same proportions, same horn shape
  - Only change: rune glow color shifts from amber to orange, more agitated motion

REFERENCE: [ATTACH THE BOU DE PEDRA PHASE 1 MASTER IDLE SPRITE HERE]

PALETTE (use ONLY these 12 colors — RGB values):
  144,144,144  Stone base / Phase 1 accent
  176,176,176  Stone highlight
  104,104,112  Stone dark
  72,72,80     Stone darkest
  56,56,64     Crack lines
  224,200,56   Rune glow neutral
  248,240,120  Rune glow bright
  224,144,40   Phase 2 accent (fiery orange)
  224,40,40    Phase 3 accent (enraged red)
  120,112,96   Horn base
  88,80,72     Horn dark
  64,88,48     Moss accent

  Phase 2 change: Replace most neutral amber rune glow (224,200,56) areas
  with orange glow (224,144,40). Stone structure is IDENTICAL to Phase 1.
  More energy visible in cracks. Bull appears more agitated.
  DO NOT USE red (224,40,40) in Phase 2.

SPRITE CONSTRAINTS:
  - Sheet size:  160x36 (4 frames in a row)
  - Frame count: 4
  - Frame size:  40x36 each
  - Facing:      RIGHT

ANIMATION FRAMES:
  Frame 1: Agitated stance — same base pose as Phase 1, but rune cracks
           glow orange instead of amber. More cracks visible with energy.
           Weight slightly forward, more aggressive posture.

  Frame 2: Heave in — chest rises (1-2px), orange glow intensifies.
           Head dips slightly as if snorting. Energy pulses inward
           through the cracks, some glow bright (248,240,120).

  Frame 3: Heave peak — chest at maximum, orange glow at brightest.
           Head pushes forward (1px), horns angled aggressively.
           Additional crack lines visible where stone is stressed.

  Frame 4: Settle back — chest drops, glow returns to baseline orange.
           Slight stamp motion in front legs (1px shift).
           Head returns to neutral but maintains forward lean.

IMPORTANT ANIMATION NOTES:
  - Faster-feeling than Phase 1 — the bull is angry, breathing heavier
  - Orange glow pulsing is more pronounced than Phase 1's amber
  - Stone structure is IDENTICAL to Phase 1 — only color and energy change
  - Subtle motion differences from Phase 1: more forward lean, more head dip
  - Body silhouette stays nearly identical across all 4 frames

BACKGROUND: Solid green (#00FF00)
```
