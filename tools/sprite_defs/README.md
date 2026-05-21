# Sprite Processing Workflow

From AI-generated source art to final game sprites in two steps.

## Overview

```
AI source PNGs ──► process_character_sprites.py ──► raw sprite sheets ──► clean_sprites.py ──► final sprites
(green background)     (scaling, placement)          (RGBA PNGs)          (palette, outline)    (game-ready)
```

**Step 1** (`process_character_sprites.py`): Takes AI source images with green
backgrounds, extracts each frame, scales them to your specified size, places
them in a fixed-size frame, and assembles horizontal sprite sheets.

**Step 2** (`clean_sprites.py`): Applies color palette enforcement and optional
pixel outline to the raw sprite sheets.

Both steps are run by `tools/reprocess_all_sprites.sh` for the full batch.

## Quick Start

```bash
conda activate safona

# Process one character
python tools/process_character_sprites.py tools/sprite_defs/characters/ramon.json

# Process all characters
python tools/process_character_sprites.py tools/sprite_defs/characters/*.json

# Verbose mode (shows per-frame crop and scale details)
python tools/process_character_sprites.py -v tools/sprite_defs/characters/ramon.json

# Full pipeline (all characters + palette cleanup + outline)
bash tools/reprocess_all_sprites.sh
```

## Config Format

Each character gets one JSON file in `tools/sprite_defs/characters/`.

```json
{
  "frame_width": 48,
  "frame_height": 64,
  "source_dir": "assets/ai_sources/ramon",
  "output_dir": "assets/sprites/ramon",
  "animations": [
    {"source": "idle.png", "frames": 4, "scale_pct": 80},
    {"source": "walk.png", "frames": 6, "scale_pct": 80},
    {"source": "sling_attack.png", "output": "sling.png", "frames": 3, "scale_pct": 100},
    {"source": "jump.png", "frames": 2, "scale_pct": 85, "vertical_snap": "center"},
    {"source": "death.png", "frames": 1, "scale_pct": 100}
  ]
}
```

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `frame_width` | int | Pixel width of each frame in the output sprite sheet |
| `frame_height` | int | Pixel height of each frame in the output sprite sheet |
| `source_dir` | string | Directory containing per-animation AI source PNGs (green background) |
| `output_dir` | string | Where to write the output sprite sheets |
| `animations` | array | List of animation entries (see below) |

### Animation entry fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | string | *(required)* | Filename of the source image in `source_dir` |
| `output` | string | same as `source` | Output filename (use to rename, e.g. `sling_attack.png` -> `sling.png`) |
| `frames` | int | *(required)* | How many sprite frames to extract from this source image |
| `scale_pct` | number | *(required)* | Percentage of frame height this animation should fill (see below) |
| `vertical_snap` | string | `"bottom"` | Vertical placement: `"top"`, `"bottom"`, or `"center"` |
| `horizontal_snap` | string | `"center"` | Horizontal placement: `"left"`, `"right"`, or `"center"` |

## How `scale_pct` Works

`scale_pct` controls what percentage of the frame height the tallest frame
in this animation occupies.

- `scale_pct: 100` — tallest frame fills the full frame height
- `scale_pct: 80` — tallest frame fills 80% of the frame height

The script computes the actual resize factor internally:

```
target_height = frame_height * (scale_pct / 100)
scale_factor  = target_height / tallest_crop_height
```

All frames within one animation use the same scale factor, so
within-animation proportions are preserved.

### Why you need to set this per animation

AI-generated source images are not drawn to a grid. The idle pose might be
just the body, but the attack pose includes an extended arm or weapon above
the head. If both are set to `scale_pct: 100`, the attack will fill the
frame but the body will appear smaller than in idle (because the arm takes
up space in the frame that idle doesn't need).

The fix: you look at the art, decide which animation needs the most room
(e.g. attack with raised weapon = 100%), and scale the others down to match
the body size (e.g. idle = 80%). This is a visual judgment that only a human
can make.

### Tuning workflow

1. Set all animations to `scale_pct: 100`
2. Run the script and open the output PNGs
3. Compare body sizes across animations — the idle body should look the
   same size as the attack body, walk body, etc.
4. Lower `scale_pct` on animations where the body looks too big, raise it
   where the body looks too small
5. Repeat until satisfied

## How Snapping Works

Snapping controls where the sprite sits inside the fixed-size frame.

### `vertical_snap`

| Value | Placement | Overflow clipping |
|-------|-----------|-------------------|
| `"bottom"` | Feet at bottom of frame | Clips from top (keeps feet) |
| `"top"` | Head at top of frame | Clips from bottom (keeps head) |
| `"center"` | Centered vertically | Clips equally from top and bottom |

### `horizontal_snap`

| Value | Placement | Overflow clipping |
|-------|-----------|-------------------|
| `"center"` | Centered horizontally | Clips equally from left and right |
| `"left"` | Left-aligned | Clips from right |
| `"right"` | Right-aligned | Clips from left |

### Common combinations

- **Walking, idle, attack**: `vertical_snap: "bottom"` — feet on the ground
- **Jumping, wall slide**: `vertical_snap: "center"` — airborne
- **Death**: `vertical_snap: "bottom"` — body on the ground

`horizontal_snap` defaults to `"center"` and rarely needs changing.

## How to Add a New Character

1. Generate AI source PNGs — one PNG per animation, green background,
   sprite frames laid out left-to-right in the image.

2. Place them in `assets/ai_sources/<character_name>/`.

3. Create `tools/sprite_defs/characters/<character_name>.json`:
   ```json
   {
     "frame_width": 48,
     "frame_height": 64,
     "source_dir": "assets/ai_sources/<character_name>",
     "output_dir": "assets/sprites/<category>",
     "animations": [
       {"source": "idle.png", "frames": 4, "scale_pct": 100}
     ]
   }
   ```

4. Run: `python tools/process_character_sprites.py tools/sprite_defs/characters/<character_name>.json`

5. Open the output PNGs, compare body sizes, tune `scale_pct` values.

6. Once happy, run `bash tools/reprocess_all_sprites.sh` for the full
   pipeline (includes palette cleanup and outline).

## Processing Pipeline (internal)

For each animation source, the script:

1. **Removes green background** — heuristic: G > 80, G-R > 40, G-B > 40
2. **Removes small components** — connected components < 5000px (labels, artifacts)
3. **Detects sprite regions** — via connected-component labeling (scipy)
4. **Crops each frame** — tight bounding box around non-transparent pixels
5. **Cleans green fringe** — replaces remaining green edge pixels with neighbor averages
6. **Scales** — LANCZOS interpolation at the computed scale factor
7. **Places in frame** — using vertical_snap / horizontal_snap
8. **Assembles** — frames into a horizontal sprite sheet
9. **Saves** — as RGBA PNG

## Existing Characters

| Config | Frame Size | Animations |
|--------|-----------|------------|
| `ramon.json` | 48x64 | idle, walk, jump, sling, crouch, wall_slide, wall_jump, hit, death |
| `stone_guardian.json` | 48x64 | idle, walk, attack, hit, death |
| `rival_warrior.json` | 32x48 | idle, walk, attack, block, hit, death |
| `possessed_sheep.json` | 32x32 | idle, walk, charge, hit, death |
| `boss_bou_de_pedra.json` | 80x72 | idle_p1/p2/p3, rush, headbutt, stomp, hurl, stunned, transition, death |
| `npc_dimoni.json` | 48x80 | idle |
| `npc_llorencc.json` | 40x72 | idle, talk, shop |
