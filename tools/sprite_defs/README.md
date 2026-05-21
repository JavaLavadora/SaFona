# Character Sprite Processor

Standalone CLI tool for processing AI-generated sprite source images into
game-ready sprite sheets. Each character is defined by a simple JSON config
file -- no code knowledge required.

## Quick Start

```bash
conda activate safona

# Process one character
python tools/process_character_sprites.py tools/sprite_defs/characters/ramon.json

# Process all characters
python tools/process_character_sprites.py tools/sprite_defs/characters/*.json

# Verbose mode (shows per-frame details)
python tools/process_character_sprites.py -v tools/sprite_defs/characters/ramon.json
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
    {"source": "idle.png", "frames": 4, "anchor": "ground"},
    {"source": "walk.png", "frames": 6, "anchor": "ground"},
    {"source": "jump.png", "frames": 2, "anchor": "center"},
    {"source": "sling_attack.png", "output": "sling.png", "frames": 3, "anchor": "ground"},
    {"source": "death.png", "frames": 1, "anchor": "ground", "independent_scale": true}
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
| `anchor` | string | `"ground"` | Placement mode: `"ground"` or `"center"` |
| `normalize` | bool | `true` | If false, skip body-height normalization (e.g. crouch is intentionally shorter) |
| `independent_scale` | bool | `false` | If true, this animation gets its own scale instead of the shared one |

## How Scaling Works

The tool ensures every animation shows the character at the **same body
height**, compensating for AI-generated source images that draw each
animation at a different size.

### Step 1: Body-height normalization

Idle is the reference. For each ground-anchored animation, the tool
computes a **per-animation pre_scale** = idle_max_height / anim_max_height.
This scales both UP (walk drawn shorter than idle) and DOWN (hit drawn
taller than idle). All frames within one animation share the same pre_scale,
preserving within-animation proportions (e.g. a slam pose is naturally
shorter than a windup pose).

- Center-anchored animations (jump, wall_slide): pre_scale = 1.0
- `"normalize": false` (e.g. crouch): pre_scale = 1.0

### Step 2: Shared scale from ground-anchored animations only

The **global max width and height** are computed from pre-scaled
ground-anchored crops only. Center-anchored animations are excluded --
they don't drive the scale down.

```
shared_scale = min((frame_width - 2) / global_max_w,
                   (frame_height - 2) / global_max_h)
```

### Step 3: Final scale per animation

- Ground-anchored: `final_scale = pre_scale * shared_scale`
- Center-anchored: `final_scale = 1.0 * shared_scale` (same body scale, may overflow and clip)
- Independent: own scale from own dimensions

### Result

Every ground-anchored animation shows the character at the same pixel
height. Center-anchored animations have the correct body proportions but
content that extends beyond the frame is clipped (not rescaled).
Animations with `independent_scale: true` (typically death) get their own
scale and don't affect anything else.

## How Anchoring Works

- **`"ground"`**: The sprite is centered horizontally and bottom-aligned.
  The feet sit on the bottom edge of the frame. Use for standing, walking,
  attacking, crouching -- any pose where the character is on the ground.

- **`"center"`**: The sprite is centered both horizontally and vertically.
  Use for airborne poses (jump, wall_slide, wall_jump).

Death animations should typically use `"anchor": "ground"` with
`"independent_scale": true` -- the body lies on the ground, not floating.

## How to Add a New Character

1. Place source PNGs in `assets/ai_sources/<character_name>/` (one PNG per
   animation, green background, sprites laid out left-to-right).

2. Create `tools/sprite_defs/characters/<character_name>.json` following
   the config format above.

3. Run:
   ```bash
   python tools/process_character_sprites.py tools/sprite_defs/characters/<character_name>.json
   ```

4. Check the output in the configured `output_dir`.

## Processing Pipeline

For each source image, the tool:

1. **Removes green background** -- heuristic: G > 80, G-R > 40, G-B > 40
2. **Removes small components** -- connected components < 5000px (number
   labels, stray artifacts)
3. **Detects sprite regions** -- via `scipy.ndimage.label`
4. **Crops each frame** -- tight bounding box around non-transparent pixels
5. **Cleans green fringe** -- replaces remaining green-ish edge pixels with
   neighbor color averages
6. **Scales** -- using LANCZOS interpolation with the shared (or independent)
   scale factor
7. **Places in frame** -- using the configured anchor mode
8. **Assembles** -- frames into a horizontal sprite sheet
9. **Saves** -- as RGBA PNG

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
