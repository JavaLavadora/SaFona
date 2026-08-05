# Sa Fona — Asset Generation Guide

**Single source of truth for the asset generation workflow, methodology,
processing pipeline, and QC checklist.**

For the prompts themselves (every AI prompt, copy-paste-ready, organized by
asset and split per world), see [`asset_prompts/`](asset_prompts/):

- [`asset_prompts/shared.md`](asset_prompts/shared.md) — cross-world assets
  (player, companion, generic pickups, projectiles, UI, ground shadow,
  title/game-over) + the canonical **frame-size convention** and **global
  style block**.
- [`asset_prompts/world1.md`](asset_prompts/world1.md) — World 1 (Sa Talaia)
  bosses, enemies, NPCs, tilesets, backgrounds, environment props, W1 NPC
  portraits, W1 attack effects, W1 generation order.
- Future: `world2.md`, `world3.md`, etc.

This file is **workflow only** — it tells you *how* to add an asset; the
prompts files give you *what* to type.

If you find prompt content **outside `docs/asset_prompts/`**, it is a bug —
file an Issue.

---

## How to add a new asset

> **The rule that prevents drift**: All new prompts go into
> `docs/asset_prompts/`. **Do NOT create new prompt files elsewhere in the
> repo.** Not in `tools/sprite_defs/`, not in `docs/proposals/`, not next to
> the JSON config. One folder. One source of truth.

### Where does this prompt go?

Pick the file by asking: **does this asset appear across multiple worlds?**

- **Yes (cross-world)** → `docs/asset_prompts/shared.md`. Examples: player
  (Balchar) and companion (Bep) animations, generic pickups (heart, stone,
  shield orb), breakables (pot, crate), projectiles, generic effects (dust,
  impact, portal, anticipation, debris), UI elements, title and game-over
  screens, player ground shadow, Balchar/Bep dialogue portraits.
- **No (world-specific)** → `docs/asset_prompts/world<N>.md`. Examples: that
  world's boss, enemies (including their attack effect overlays), NPCs
  (including dialogue portraits), tilesets, backgrounds, environment props,
  world-specific effects (e.g. the W1 Dimoni aura), per-world generation
  order.

If a UI element is currently styled for a single world (e.g. the W1 boss
health bar's carved-stone look) but is rendered as a cross-world UI control,
keep the prompt in `shared.md` and add a note that per-world variants live
in the matching world file. The Bep curse-glow aura is a similar case: the
sprite is Bep (cross-world) so the prompt lives in `shared.md`, with a note
linking the W1 narrative tie.

When adding a brand-new world, create `docs/asset_prompts/world<N>.md` and
append a per-world "Generation order" section at the end. Do not restructure
existing files.

### Steps

1. **Decide the asset spec** — talk to En Biel (Game Director) for design
   intent: name, role, visual identity, frame count, animation set, world
   palette. Confirm what placeholder it replaces and what hitbox dimensions
   the gameplay code already uses.
2. **Add the prompt section** to the right file under `docs/asset_prompts/`
   (see the "Where does this prompt go?" rule above) under the matching
   world / category heading. Include:
   - Palette block (RGB values) — author or reference a `.gpl` file in
     `assets/palettes/`.
   - Hitbox size (code constants) + AI prompt source size + JSON config
     output size. See the three-layer frame convention in the prompts file.
   - Identity lock, palette block, sprite constraints, body size rule,
     animation description, rules tail. Do **not** copy the global style
     block into the prompt — see Section 0 above.
   - `[ATTACH MASTER IDLE SPRITE HERE]` marker for any animation that
     follows a master idle.
3. **Generate the master idle FIRST** if this is a new character. The master
   idle becomes the visual authority all other animations reference.
4. **Run the img2vid pipeline** to produce the final sprite sheet. The
   img2vid **seed** is the character's immutable master idle still at
   `<source_dir>/idle.png` (from step 3 / Section 2) — it is fed to img2vid
   for *every* animation and is reused, never regenerated per animation.
   Each numbered sub-step below maps to a folder under
   `assets/ai_sources/img2vid/<character>/<animation>/` (see Section 8 for
   the pipeline diagram and Section 9 for the directory layout). The
   prompt itself was already written in outer step 2 above — don't
   duplicate that here.
   1. Upload the master idle still (`<source_dir>/idle.png`) to Meta AI
      img2vid (or future API) together with this animation's prompt. img2vid
      creates the motion from that single seed. Save the resulting MP4 as
      `assets/ai_sources/img2vid/<character>/<animation>/01_video.mp4`.
   2. Run: `python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]`
      → produces `02_dumps/dump_*.png`.
   3. Browse `02_dumps/`; delete frames you don't want (keep the ones that
      best trace the animation cycle, in filename order).
   4. Run: `python tools/assemble_sprite_sheet.py <character> <animation>`
      → produces `03_assembled_raw.png` (debug checkpoint) AND chains
      into `tools/process_character_sprites.py tools/sprite_defs/characters/<character>.json`,
      which produces the final game asset at
      `assets/sprites/<character>/<output>.png` (a.k.a.
      `04_assembled_final.png` in debug terms), where `<output>` is the
      animation entry's `output` field if set, or `<animation>` otherwise —
      e.g. `balchar.json`'s `sling_attack` entry sets `"output": "sling.png"`,
      so the file lands at `assets/sprites/balchar/sling.png`, not
      `sling_attack.png`.
5. **Add the processing config** at
   `tools/sprite_defs/characters/<asset_name>.json` — see [Processing
   pipeline & JSON config format](#processing-pipeline--json-config-format)
   below. Sub-step 4 above (`assemble_sprite_sheet.py`) chains into the
   canonical `tools/process_character_sprites.py` script, which reads this
   config to find `source_dir`, `output_dir`, and the per-animation entries.
6. **Tune `scale_pct` per animation** by visual inspection until the body
   size matches the master idle across all animations.
7. **Run the palette cleanup**:
   ```bash
   bash tools/reprocess_all_sprites.sh
   ```
8. **Run the QC checklist** (Section 7 below).
9. **Update `sa_fona/data/asset_manifest.json`** if dimensions changed.
10. **Commit + PR** with a screenshot in the description.

**Reminder**: if you wrote a prompt anywhere other than
`docs/asset_prompts/`, delete it and move it into the right file there
(`shared.md` for cross-world, `world<N>.md` for per-world). Future
contributors will not find duplicated prompts and the game will drift
visually.

---

## 0. Global Style Lock

This block is reference for humans only. It is **not** copied into prompts —
AI image generators do not respect abstract style directives at this level,
and including them dilutes the directives they *do* respect (palette,
identity lock, reference image, frame layout). Style consistency comes from
the palette block, the identity lock, and the reference image.

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

Each character/world has its own `.gpl` file in `assets/palettes/`:

| Palette file | Colors | Notes |
|--------------|--------|-------|
| `balchar.gpl` | 15 | Player — anchors the World 1 style |
| `bep.gpl` | 9 | Companion (myotragus) |
| `bou_de_pedra.gpl` | 12 | World 1 boss — Phase 1/2/3 accents included |
| `stone_guardian.gpl` | 9 | Note: green eye glow `80,200,80` |
| `rival_warrior.gpl` | 12 | Tribal warrior |
| `possessed_sheep.gpl` | 8 | Possessed by dimoni energy |
| `dimoni.gpl` | 12 | Supernatural NPC |
| `llorencc.gpl` | 12 | Shopkeeper — cream/olive/terracotta costume |
| `pickups_heart.gpl` | 4 | Heart pickup |
| `pickups_stone.gpl` | 5 | Stone currency |
| `breakables_pot.gpl` | 6 | Pot |
| `breakables_crate.gpl` | 5 | Crate |
| `projectiles.gpl` | 8 | Tier 1 grey, Tier 2 blue glow, Tier 3 gold glow |
| `effects.gpl` | 12 | Dust / impact / aura / portal / sparks |
| `tileset_world1.gpl` | 15 | Outdoor terrain |
| `tileset_world1_cave.gpl` | 15 | Cave interior |
| `tileset_world1_talayot.gpl` | 15 | Talayot interior |
| `bg_world1.gpl` | 15 | Outdoor background |
| `bg_world1_cave.gpl` | 15 | Cave background |
| `bg_world1_talayot.gpl` | 15 | Talayot interior background |

When authoring a new `.gpl`, follow the GIMP Palette convention used for the
existing files (`GIMP Palette` header, `Name: <name>`, `Columns: 0`, then one
`R G B  description` line per color).

---

## 2. Master Character Generation (one-time per character)

The master idle sprite is the only phase where creative exploration is
allowed. The result becomes **immutable** — every subsequent animation locks
to it.

### Prompt template — Master Idle Sprite

```
Create a SNES-style 16-bit pixel art sprite.

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

BACKGROUND: Solid green (#00FF00)

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

See [`docs/asset_prompts/shared.md` § 1](asset_prompts/shared.md#1-balchar-player-character) for a worked example (Balchar's anatomy map).

---

## 4. Same Character, New Animation

Used for walk, run, attack, hit, jump, etc.

```
Create a SNES-style 16-bit pixel art sprite sheet.

CRITICAL IDENTITY LOCK:
  - Must match the MASTER sprite EXACTLY
  - Same proportions, face, hair, clothing, accessories
  - Same palette, no new colors
  - Same head position, belt height, feet baseline
  - No redesign, no reinterpretation

REFERENCE: [ATTACH MASTER IDLE SPRITE HERE]

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
  - Background: Solid green (#00FF00)
```

### The `[ATTACH MASTER IDLE SPRITE HERE]` convention

This bracketed marker is **not** sent to the AI as text — it's an operator
instruction. When you see it, attach the existing master idle PNG as a visual
reference image alongside the text prompt. This is how style identity is
enforced across animations.

### Img2Vid stage

Once the animation prompt is authored, the character's **master idle still**
(`<source_dir>/idle.png`) is fed through an image-to-video AI *together with
that animation's prompt* to produce one continuous-motion video. img2vid
creates the in-between motion from the single idle seed — there is no
per-animation sprite sheet to generate or split. Frames are then sampled
from the video and assembled into the final sprite sheet. See Section 8 for
the CLI commands. The img2vid stage is a *better source* for the same
downstream pipeline — the final processing step is unchanged.

---

## 5. New Character, Same Style

For NPCs and enemies: identity changes, style does not.

```
Create a SNES-style 16-bit pixel art sprite.

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

Tilesets follow a slightly different pipeline because of the auto-tile
variant generation and color correction. See
[`asset_prompts/world1.md` § 15](asset_prompts/world1.md#15-tilesets) for the
World 1 tileset prompts and the canonical processing pipeline
(color-correction RGB endpoints `(130,112,82) → (215,195,155)` plus
multi-step downscale: LANCZOS → 48x48 → contrast 1.4x → sharpness 1.5x →
NEAREST to 16x16).

Template:

```
Create a SNES-style 16-bit pixel art TILESET.

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
  - Background: solid green (#00FF00)
```

---

## 7. Quality Control Checklist

Run after every generation pass:

- [ ] Palette unchanged — no new colors introduced (run `tools/clean_sprites.py --verbose`)
- [ ] Head, belt, feet alignment preserved across all frames (characters)
- [ ] Tile density matches reference tiles
- [ ] Shading logic consistent (top-left light source)
- [ ] No accidental new materials or hues
- [ ] Body size consistent across animations (compare idle vs. attack vs. walk side-by-side)
- [ ] Hitbox size and processed sprite size align with the JSON config
- [ ] `asset_manifest.json` updated if dimensions changed

If any check fails: regenerate or hand-fix.

---

## 8. Processing pipeline & JSON config format

The full pipeline has four stages plus a one-time prerequisite. Two of the
four stages are existing/manual, two are new img2vid tools added on top.

The **seed** is the character's immutable master idle still (Section 2 —
generated once per character, never regenerated per animation). It is the
img2vid seed for *every* animation and the scale/anchor reference during
assembly; it lives at `<source_dir>/idle.png`, outside the per-animation
work folder.

```
Prereq    Master idle still (one-time per character, immutable)   [existing]
            → <source_dir>/idle.png  (img2vid seed + scale/anchor ref)

Stage 1   Prompt (asset_prompts/shared.md or world1.md)           [docs]
            ↓
Stage 2   Image→Video: master idle + animation prompt → ONE video [manual, hybrid-ready]
            ↓                                                     → 01_video.mp4
Stage 3   tools/dump_video_frames.py + manual prune               [NEW + user]
            ↓                                                     → 02_dumps/
Stage 4   tools/assemble_sprite_sheet.py                          [NEW, automated]
            ↓                                                     → 03_assembled_raw.png
          tools/process_character_sprites.py <character>.json     [canonical]
                                                                  → 04_assembled_final.png
                                                                  → assets/sprites/...
```

**Key invariant:** Stage 4's output is shaped to match what the canonical
`tools/process_character_sprites.py` already expects: chroma-green background
where every pixel is *exactly* `(0, 255, 0)` or a palette color (no
semi-transparent edges); target frame dimensions; palette-quantized against
`assets/palettes/<character>.gpl` (same parser as `tools/clean_sprites.py`).
Downstream is unchanged.

**Re-runnability:** Each stage is an independent CLI reading from / writing
to known folders. Any stage can be re-run in isolation without re-running
earlier ones.

### Quick start

```bash
conda activate safona

# Stage 3 — dump frames from the single animation video (every Kth frame)
python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]

# Stage 4 — assemble cleaned sprite sheet (chains into
# tools/process_character_sprites.py <character>.json automatically)
python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}]

# Final character-processing pass (canonical chain — runs automatically
# from Stage 4; shown here in case you want to re-run it manually)
python tools/process_character_sprites.py tools/sprite_defs/characters/balchar.json

# Process all characters
python tools/process_character_sprites.py tools/sprite_defs/characters/*.json

# Verbose mode (shows per-frame crop and scale details)
python tools/process_character_sprites.py -v tools/sprite_defs/characters/balchar.json

# Full pipeline (all characters + palette cleanup + outline)
bash tools/reprocess_all_sprites.sh
```

- Advanced/debug flag (optional): `python tools/assemble_sprite_sheet.py
  <character> <animation> --warn-scale-pct N` warns when any dump frame's
  bbox height differs from the master idle's by more than N%
  (default 15). Useful when chasing R3 scale drift; leave at default for
  normal runs.
- Stage 3 requires ffmpeg >= 5.1 (uses `-fps_mode vfr`, which replaced the
  deprecated `-vsync vfr`).

### Debug artifacts

When the final asset looks wrong, inspect
`assets/ai_sources/img2vid/<character>/<animation>/03_assembled_raw.png`
first. This is the Stage 4 output **before** `tools/process_character_sprites.py`
runs. Comparing it against `04_assembled_final.png` localizes the bug:

- If `03_assembled_raw.png` is already wrong → the bug is in the img2vid
  assembly (background removal, downsample, palette quantize, anchor).
- If `03` looks fine but `04` is worse → the bug is in the canonical
  `tools/process_character_sprites.py` or `tools/clean_sprites.py` chain.

The intermediate `01_video.mp4` and `02_dumps/` are also preserved so any
stage can be re-run in isolation.

### Canonical processing chain (also used for non-img2vid sources)

`tools/process_character_sprites.py` takes AI source images with green
backgrounds, extracts each frame, scales them to your specified size,
places them in a fixed-size frame, and assembles horizontal sprite sheets.
`tools/clean_sprites.py` applies color palette enforcement (from the
character's `.gpl`) and an optional pixel outline to the raw sprite sheets.
Both are run by `tools/reprocess_all_sprites.sh` for the full batch (Phase 1
runs `process_character_sprites.py` for every `tools/sprite_defs/characters/*.json`;
Phase 3/4 runs `clean_sprites.py` per output PNG). Stage 4 of the img2vid
pipeline chains directly into `process_character_sprites.py` for the single
animation being assembled; `clean_sprites.py` is run as part of the batch
script when you want the palette/outline pass over everything.

### JSON config format

Each character gets one JSON file in `tools/sprite_defs/characters/`.

```json
{
  "frame_width": 48,
  "frame_height": 64,
  "source_dir": "assets/ai_sources/balchar",
  "output_dir": "assets/sprites/balchar",
  "animations": [
    {"source": "idle.png", "frames": 4, "scale_pct": 80},
    {"source": "walk.png", "frames": 6, "scale_pct": 80},
    {"source": "sling_attack.png", "output": "sling.png", "frames": 3, "scale_pct": 100},
    {"source": "jump.png", "frames": 2, "scale_pct": 85, "vertical_snap": "center"},
    {"source": "death.png", "frames": 1, "scale_pct": 100}
  ]
}
```

#### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `frame_width` | int | Pixel width of each frame in the output sprite sheet |
| `frame_height` | int | Pixel height of each frame in the output sprite sheet |
| `source_dir` | string | Directory containing per-animation AI source PNGs (green background) |
| `output_dir` | string | Where to write the output sprite sheets |
| `animations` | array | List of animation entries (see below) |

#### Animation entry fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | string | *(required)* | Filename of the source image in `source_dir` |
| `output` | string | same as `source` | Output filename (use to rename, e.g. `sling_attack.png` → `sling.png`) |
| `frames` | int | *(required)* | How many sprite frames to extract from this source image |
| `scale_pct` | number | *(required)* | Percentage of frame height this animation should fill (see below) |
| `vertical_snap` | string | `"bottom"` | Vertical placement: `"top"`, `"bottom"`, or `"center"` |
| `horizontal_snap` | string | `"center"` | Horizontal placement: `"left"`, `"right"`, or `"center"` |

### How `scale_pct` works

`scale_pct` controls what percentage of the frame height the tallest frame
in this animation occupies.

- `scale_pct: 100` — tallest frame fills the full frame height
- `scale_pct: 80` — tallest frame fills 80% of the frame height

The script computes the actual resize factor internally:

```
target_height = frame_height * (scale_pct / 100)
scale_factor  = target_height / tallest_crop_height
```

All frames within one animation use the same scale factor, so within-animation
proportions are preserved.

#### Why you need to set this per animation

AI-generated source images are not drawn to a grid. The idle pose might be
just the body, but the attack pose includes an extended arm or weapon above
the head. If both are set to `scale_pct: 100`, the attack will fill the frame
but the body will appear smaller than in idle (because the arm takes up space
in the frame that idle doesn't need).

**The fix**: look at the art, decide which animation needs the most room
(e.g. attack with raised weapon = 100%), and scale the others down to match
the body size (e.g. idle = 80%). This is a visual judgment that only a human
can make.

#### Tuning workflow

1. Set all animations to `scale_pct: 100`.
2. Run the script and open the output PNGs.
3. Compare body sizes across animations — the idle body should look the same
   size as the attack body, walk body, etc.
4. Lower `scale_pct` on animations where the body looks too big, raise it
   where the body looks too small.
5. Repeat until satisfied.

### How snapping works

Snapping controls where the sprite sits inside the fixed-size frame.

#### `vertical_snap`

| Value | Placement | Overflow clipping |
|-------|-----------|-------------------|
| `"bottom"` | Feet at bottom of frame | Clips from top (keeps feet) |
| `"top"` | Head at top of frame | Clips from bottom (keeps head) |
| `"center"` | Centered vertically | Clips equally from top and bottom |

#### `horizontal_snap`

| Value | Placement | Overflow clipping |
|-------|-----------|-------------------|
| `"center"` | Centered horizontally | Clips equally from left and right |
| `"left"` | Left-aligned | Clips from right |
| `"right"` | Right-aligned | Clips from left |

#### Common combinations

- **Walking, idle, attack**: `vertical_snap: "bottom"` — feet on the ground
- **Jumping, wall slide**: `vertical_snap: "center"` — airborne
- **Death**: `vertical_snap: "bottom"` — body on the ground

`horizontal_snap` defaults to `"center"` and rarely needs changing.

### Processing pipeline (internal steps per animation source)

1. **Removes green background** — heuristic: `G > 80, G-R > 40, G-B > 40`.
2. **Removes small components** — connected components < 5000 px (labels, artifacts).
3. **Detects sprite regions** — via connected-component labeling (scipy).
4. **Crops each frame** — tight bounding box around non-transparent pixels.
5. **Cleans green fringe** — replaces remaining green edge pixels with neighbor averages.
6. **Scales** — LANCZOS interpolation at the computed scale factor.
7. **Places in frame** — using `vertical_snap` / `horizontal_snap`.
8. **Assembles** — frames into a horizontal sprite sheet.
9. **Saves** — as RGBA PNG.

For **tilesets**, see the World 1 tileset pipeline in
[`asset_prompts/world1.md` § 15.1](asset_prompts/world1.md#151-world-1--outdoor-sa-talaia):
includes the color-correction endpoints `(130,112,82) → (215,195,155)` and
the multi-step downscale LANCZOS → 48x48 → contrast 1.4x → sharpness 1.5x →
NEAREST to 16x16.

### Existing JSON configs

| Config | Frame size | Animations |
|--------|-----------|------------|
| `balchar.json` | 48x64 | idle, walk, jump, sling, crouch, wall_slide, wall_jump, hit, death |
| `stone_guardian.json` | 48x64 | idle, walk, attack, hit, death |
| `rival_warrior.json` | 32x48 | idle, walk, attack, block, hit, death |
| `possessed_sheep.json` | 32x32 | idle, walk, charge, hit, death |
| `boss_bou_de_pedra.json` | 80x72 | idle_p1/p2/p3, rush, headbutt, stomp, hurl, stunned, transition, death |
| `npc_dimoni.json` | 48x80 | idle |
| `npc_llorencc.json` | 40x72 | idle, talk, shop |
| `bonfire.json` | 24x32 | unlit / lit |
| `taula_gate.json` | 32x48 | single frame |
| `stone_guardian_effects.json` | varies | attack effect VFX |
| `rival_warrior_effects.json` | varies | attack effect VFX |
| `legionary_effects.json` | varies | attack effect VFX |

Effect configs are separate from body sprites because frame dimensions
differ — see [`asset_prompts/world1.md` § 13](asset_prompts/world1.md#13-attack-effect-overlays).

**Historical note**: `tools/sprite_defs/balchar_ai_prompt.md` is retained as
an archival record of v1/v2/v3 Balchar sprite-processing history. It is
**NOT** an authoritative prompt source — see
[`asset_prompts/shared.md` § 1](asset_prompts/shared.md#1-balchar-player-character)
for the current Balchar prompt. If you find any other prompt files outside
`docs/asset_prompts/`, that is a bug — file an Issue.

---

## 9. Asset directory structure

```
assets/
├── ai_sources/<asset_name>/image.png   # raw AI output
├── palettes/<palette_name>.gpl         # locked color palettes
├── sprites/
│   ├── balchar/
│   ├── enemies/
│   │   ├── stone_guardian/
│   │   ├── rival_warrior/
│   │   ├── possessed_sheep/
│   │   └── effects/                    # attack VFX overlays
│   ├── bosses/
│   └── npcs/
├── environment/                        # bonfire, taula_gate
├── tilesets/world1/
├── backgrounds/world1/
├── portraits/                          # dialogue portraits (44x44)
└── ui/                                 # HUD, frames, title, game over
```

The game's sprite loading system automatically picks up files from these
paths. `sa_fona/data/asset_manifest.json` declares dimensions/frame counts
for each animation; update it if anything changes.

### Img2Vid working layout

```
assets/ai_sources/img2vid/<character>/<animation>/
├── 01_video.mp4              # Stage 2 output (user drops the img2vid MP4 here)
├── 02_dumps/                 # Stage 3 output (Kth-frame dumps; user prunes in place)
├── 03_assembled_raw.png      # Stage 4 output (debug checkpoint)
└── 04_assembled_final.png    # After tools/process_character_sprites.py <char>.json
```

The img2vid seed / scale reference is **not** in this subtree — it is the
character's single master idle still at `<source_dir>/idle.png` (e.g.
`assets/ai_sources/balchar/idle.png`), reused for every animation.

This whole `img2vid/` subtree is **gitignored** — only the final game sprite
in `assets/sprites/...` is committed. Each stage's output is the input of the
next, and any stage can be re-run in isolation.

---

## 10. Design rationale notes (when art ≠ purely decorative)

Some animations exist for gameplay reasons. Document the reason so the art
isn't "downgraded" later by someone who thinks it's filler:

| Asset | Gameplay reason |
|-------|----------------|
| Rival Warrior `block.png` | Triggers on **30%** of incoming attacks — must read clearly as a block |
| Stone Guardian attack tell | **1.0s** tell duration in-game — must read as a clear wind-up so the player can react |
| Pot break | Drop table: **1-3 stones** |
| Crate break | Drop table: **2-4 stones** |
| Bep `glow.png` (curse aura) | Curse-effect overlay layer — Bep idle pose with 1-2px aura halo |
| Boss arena pillars | Destructible — must have intact + destroyed states |
| Stone Guardian eye glow | **Green** (`80,200,80`) — distinguishes from boss's amber |
| Projectile Tier 2 / 3 | Tier 2 = **blue** glow, Tier 3 = **gold** glow — visible charge feedback |

---

## 11. Asset register

### Current (World 1 — populated)

See [`asset_prompts/`](asset_prompts/) for the full list
(`shared.md` + `world1.md`).

### Future assets (placeholders, not yet authored)

- **Bruna** — Llorenç's cow companion (nice-to-have, currently unmodelled)
- **World 2 — Romana** roster (legionaries, centurion boss, Roman tilesets)
- **World 3 — Comte Mal** roster
- **Worlds 4-5** roster

When adding a future world, create a new file
`docs/asset_prompts/world<N>.md` (e.g. `world2.md` for Romana). Do not
restructure existing files — each world gets its own file. The W2+ file
should reference `shared.md` for the frame-size convention and global style
block, then list that world's bosses, enemies, NPCs, tilesets, backgrounds,
environment props, NPC portraits, world-specific effects, and end with a
per-world generation order.

---

## 12. Final principle

> **Consistency beats perfection.**
> AI accelerates production — art direction protects identity.

This guide exists to make the world feel intentional, cohesive, and
believable.
