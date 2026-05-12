# 16 — Bou de Pedra: Idle Phase 3

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
  - Only change: rune glow shifts to red, exposed weak point in chest

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

  Phase 3 change: Rune cracks glow red (224,40,40). Exposed glowing red
  core visible in chest area. Stone surface shows more cracks and damage.
  Most aggressive appearance. Maximum energy discharge look.

SPRITE CONSTRAINTS:
  - Sheet size:  160x36 (4 frames in a row)
  - Frame count: 4
  - Frame size:  40x36 each
  - Facing:      RIGHT

ANIMATION FRAMES:
  Frame 1: Enraged stance — same base pose, but rune cracks glow deep red.
           Large crack in chest exposes glowing red core (3-4px bright area).
           Stone surface visibly damaged with more crack lines.
           Heavy forward lean, head low, horns thrust forward.

  Frame 2: Violent heave — chest surges upward (2px), core pulses bright
           (use 248,240,120 for core highlight, 224,40,40 for surrounding).
           Red energy flares out from cracks. Head lifts aggressively.
           Whole body shifts forward (1px) as if about to charge.

  Frame 3: Core pulse peak — chest at maximum, core at maximum brightness.
           Red glow bleeds through multiple crack lines across the body.
           Head drops and horns angle down — full threat display.
           Stone fragments appear to separate slightly at major cracks.

  Frame 4: Recoil — chest drops back (2px), core dims slightly but stays
           visible. Energy recedes into cracks. Body settles back but
           remains tense. Front legs stamp (1px) with restless energy.
           The exposed core never fully dims — it stays visible as the
           weak point the player needs to target.

IMPORTANT ANIMATION NOTES:
  - Most aggressive idle of all three phases — this bull is FURIOUS
  - The exposed chest core is the KEY visual feature of Phase 3
  - Core must be clearly visible in ALL 4 frames (it's the weak point)
  - Red glow pulsing is dramatic — more contrast between dim and bright
  - Motion is heavier than Phase 2: bigger heaves, more stamp energy
  - Stone structure is IDENTICAL to Phase 1 — only damage, color, and core change
  - Body silhouette stays nearly identical across all 4 frames

BACKGROUND: Solid green (#00FF00)
```
