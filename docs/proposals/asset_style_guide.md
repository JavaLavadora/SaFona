# Asset Generation & Style Consistency Guide

**SNES-style Mediterranean Platformer — Production-Grade Workflow**

> This guide formalizes a repeatable, production-grade process for generating
> consistent sprites, animations, tiles, and environments using AI tools
> without losing visual identity or style cohesion.

---

## 0. Global Style Lock

**Mandatory for ALL assets.** This block is copied verbatim into every prompt.
It is the backbone of style consistency.

```
GLOBAL STYLE CONSTRAINTS (DO NOT VIOLATE):

- Style:         Authentic SNES-era 16-bit pixel art
- Perspective:   Strict side view (2D platformer)
- Light source:  Top-left, consistent across all assets
- Shading:       2-3 tones per material, no pillow shading
- Pixel density: Moderate, readable at 1x scale
- Outlines:      Clean, dark outline color from palette
- Palette:       Use ONLY the approved global palette
- Rendering:     Pixel-perfect, no blur, no anti-aliasing, no gradients
- Aesthetic:     Pre-Roman Mediterranean (Balearic-inspired)
```

---

## 1. Global Palette Lock

> The palette is a contract, not a suggestion.
> Assets that introduce new colors are invalid.

```
GLOBAL PALETTE (replace with final values according to each asset's pallete gpl file):

Skin:
  - Skin light:    {{SKIN_LIGHT_HEX}}
  - Skin shadow:   {{SKIN_SHADOW_HEX}}

Cloth / Leather:
  - Tunic base:    {{TUNIC_BASE_HEX}}
  - Tunic shadow:  {{TUNIC_SHADOW_HEX}}
  - Belt leather:  {{BELT_HEX}}

Environment:
  - Grass light:   {{GRASS_LIGHT_HEX}}
  - Grass dark:    {{GRASS_DARK_HEX}}
  - Stone light:   {{STONE_LIGHT_HEX}}
  - Stone dark:    {{STONE_DARK_HEX}}

Outline:
  - Outline dark:  {{OUTLINE_HEX}}

RULE: No asset may introduce new hues or shades.
```

---

## 2. Master Character Generation (One-Time Step)

This is the only phase where creative exploration is allowed.
The result becomes immutable.

### Prompt Template — Master Idle Sprite

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

CHARACTER IDENTITY:
  - Name:        {{CHARACTER_NAME}}
  - Culture:     {{CULTURAL_REFERENCE}}
  - Era:         {{HISTORICAL_PERIOD}}
  - Role:        {{CHARACTER_ROLE}}

VISUAL DETAILS:
  - Clothing:    {{CLOTHING_DESCRIPTION}}
  - Accessories: {{ACCESSORIES_LIST}}
  - Hair/Headgear: {{HEAD_DESCRIPTION}}
  - Body type:   {{BODY_TYPE}}

SPRITE CONSTRAINTS:
  - Sprite sheet: {{FRAME_COUNT}} frames
  - Total size:   {{TOTAL_WIDTH}}x{{TOTAL_HEIGHT}}
  - Frame size:   {{FRAME_WIDTH}}x{{FRAME_HEIGHT}}
  - Facing:       {{LEFT_OR_RIGHT}}
  - Animation:    Idle only, subtle breathing

BACKGROUND: Transparent

IMPORTANT:
This sprite is the MASTER reference.
Design must be clean, readable, and reusable for all animations.
```

---

## 3. Sprite Anatomy Map

> Human-defined, non-negotiable.
> This prevents proportion drift and animation corruption.

```
SPRITE ANATOMY MAP — {{CHARACTER_NAME}}

Fixed positions:
  - Head:          X {{X1}}-{{X2}}, Y {{Y1}}-{{Y2}}
  - Torso core:    Fixed vertical placement
  - Belt line:     Absolute Y = {{BELT_Y}}
  - Feet baseline: Absolute Y = {{FEET_Y}}

Allowed to move:
  - Arms
  - Weapons / tools
  - Cloth secondary motion
  - Torso rotation (no vertical translation)

Forbidden:
  - Head movement
  - Leg length changes
  - Belt or gear height changes
  - Palette changes
```

---

## 4. Same Character, New Animation

Used for walk, run, attack, hit, jump, etc.

```
Create a SNES-style 16-bit pixel art sprite sheet.

GLOBAL STYLE CONSTRAINTS APPLY.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER sprite EXACTLY
  - Same proportions, face, hair, clothing, accessories
  - Same palette, no new colors
  - Same head position, belt height, feet baseline
  - No redesign, no reinterpretation

REFERENCE: Use the provided MASTER sprite as visual authority

SPRITE CONSTRAINTS:
  - Sheet size:  {{TOTAL_WIDTH}}x{{TOTAL_HEIGHT}}
  - Frame count: {{FRAME_COUNT}}
  - Frame size:  {{FRAME_WIDTH}}x{{FRAME_HEIGHT}}
  - Facing:      {{LEFT_OR_RIGHT}}

ANIMATION DESCRIPTION:
  {{FRAME_BY_FRAME_DESCRIPTION}}

RULES:
  - Only limbs, weapon, and torso rotation may change
  - Maintain readable silhouette
  - Transparent background
```

---

## 5. New Character, Same Style

For NPCs and enemies: identity changes, style does not.

```
Create a SNES-style 16-bit pixel art sprite.

GLOBAL STYLE CONSTRAINTS APPLY.

STYLE CONSISTENCY RULES:
  - Must belong to the same world as {{REFERENCE_CHARACTER}}
  - Same palette family
  - Same shading logic and pixel density
  - Same outline treatment

CHARACTER IDENTITY:
  - Role:         {{NPC_ROLE}}
  - Culture:      {{CULTURAL_REFERENCE}}
  - Differentiators: {{DIFFERENTIATING_FEATURES}}

SPRITE CONSTRAINTS:
  - Frame size:   {{FRAME_WIDTH}}x{{FRAME_HEIGHT}}
  - Animation:    {{ANIMATION_TYPE}}
  - Facing:       {{LEFT_OR_RIGHT}}

IMPORTANT: Different identity, indistinguishable style.
```

---

## 6. Tileset Generation

```
Create a SNES-style 16-bit pixel art TILESET.

GLOBAL STYLE CONSTRAINTS APPLY.

ENVIRONMENT TYPE: {{ENVIRONMENT_DESCRIPTION}}

TILE CONSTRAINTS:
  - Tile size: {{TILE_SIZE}}x{{TILE_SIZE}}
  - Use shared global palette
  - Moderate texture density
  - Designed for random placement without visible repetition

INCLUDE VARIANTS:
  - Clean tiles
  - Cracked / worn tiles
  - Decorative tiles ({{DECORATION_LIST}})
  - Transition tiles (edges, corners)

STYLE RULES:
  - Match character contrast and shading
  - Same light source
  - Transparent background
```

---

## 7. Quality Control Checklist

Run after every generation pass:

- [ ] Palette unchanged — no new colors introduced
- [ ] Head, belt, feet alignment preserved (characters)
- [ ] Tile density matches reference tiles
- [ ] Shading logic consistent (top-left light source)
- [ ] No accidental new materials or hues

If any check fails: regenerate or hand-fix.

---

## 8. Final Principle

> **Consistency beats perfection.**
> AI accelerates production — art direction protects identity.

This guide exists to make the world feel intentional, cohesive, and believable.
