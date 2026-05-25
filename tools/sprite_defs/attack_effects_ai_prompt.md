# Attack Effect Sprite Generation Prompts

AI prompts for generating attack effect overlay sprites. These are **simple VFX animations** that play over the attack hitbox to give the player a visual cue of the danger zone. No body parts, no weapons — just motion trails and impact flashes.

## Pipeline

1. Generate each effect using the prompts below
2. Place the output PNG in `assets/ai_sources/{enemy_name}/`
3. Process with: `python tools/process_character_sprites.py tools/sprite_defs/characters/{enemy_name}_effects.json`
4. Output lands in `assets/sprites/enemies/effects/`
5. Update `sa_fona/data/asset_manifest.json` with the correct frame dimensions
6. Update `sa_fona/data/enemies/world{N}_enemies.json` `attack_effect` block if frame sizes changed

## General Rules

- Solid bright green (#00FF00) background
- All frames in a single horizontal row, evenly spaced, same scale
- 16-bit SNES-style pixel art, clean pixels, no anti-aliasing
- Effects face **right** (game flips for left-facing)
- **No body parts, no weapons, no characters** — pure simple VFX
- Keep it minimal — these are tiny sprites (~24-48px)

---

## 1. Stone Guardian — Dust Sweep

**Source file:** `assets/ai_sources/stone_guardian/stone_guardian_arm_sweep.png`
**Config:** `tools/sprite_defs/characters/stone_guardian_effects.json`
**Frames:** 3

### Prompt

Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00) background. 3 frames in a horizontal row, evenly spaced. A simple brown dust sweep arc, no characters or weapons:

1) A faint curved dust trail forming, sweeping right
2) The dust trail at full opacity, thick arc shape
3) The dust fading away

Colors: brown-tan dust with a few darker brown pixels for depth. Simple and clean.

---

## 2. Rival Warrior — Slash Trail

**Source file:** `assets/ai_sources/rival_warrior/rival_warrior_spear_thrust.png`
**Config:** `tools/sprite_defs/characters/rival_warrior_effects.json`
**Frames:** 3

### Prompt

Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00) background. 3 frames in a horizontal row, evenly spaced. A simple horizontal slash trail, no characters or weapons:

1) A thin white streak appearing, pointing right
2) The streak at full brightness with a few spark pixels
3) The streak fading into scattered dots

Colors: white core, pale blue edge. Simple and clean.

---

## 3. Roman Legionary — Stab Flash

**Source file:** `assets/ai_sources/legionary/legionary_gladius_stab.png`
**Config:** `tools/sprite_defs/characters/legionary_effects.json`
**Frames:** 3

### Prompt

Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00) background. 3 frames in a horizontal row, evenly spaced. A simple forward impact flash, no characters or weapons:

1) A small bright point of light appearing
2) The flash expanding into a small starburst shape
3) The flash shrinking and fading

Colors: white-yellow center, pale yellow outer glow. Simple and clean.

---

## Processing Notes

- Each effect has its own JSON config (separate from body sprites) — different frame dimensions
- Same green chroma-key removal and scaling pipeline as body sprites
- `scale_pct` needs tuning after seeing AI output — start at 85 and adjust
- Effects anchor at the collision rect edge, offset by `offset_x`/`offset_y` in enemy JSON
- All effects face right; game flips for left-facing enemies
