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
    {"source": "death.png", "frames": 1, "anchor": "center", "independent_scale": true}
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
| `independent_scale` | bool | `false` | If true, this animation gets its own scale instead of the shared one |

## How Scaling Works

The tool uses a **single shared scale factor** across all animations for a
character (except those marked `independent_scale`). This ensures body
proportions are perfectly consistent -- the idle, walk, attack, etc. all
look like the same character at the same size.

1. All source images are loaded and each sprite frame is cropped to its
   tight bounding box.

2. The **global maximum width and height** are found across ALL cropped
   frames from ALL shared-scale animations.

3. One scale factor is computed:
   ```
   shared_scale = min((frame_width - 2) / global_max_w,
                      (frame_height - 2) / global_max_h)
   ```
   The `-2` provides a 1px margin on each side of the frame.

4. Every frame of every shared-scale animation is scaled by `shared_scale`.
   The tallest/widest animation fills the frame; shorter animations
   naturally have proportional headroom.

5. Animations with `independent_scale: true` (typically death poses) compute
   their own scale from their own max crop dimensions. They don't affect the
   shared scale and aren't affected by it.

6. If a scaled frame overflows the target frame (because another animation's
   crops drove a larger shared scale), it is **clipped** -- not rescaled.
   This preserves the uniform scale.

## How Anchoring Works

- **`"ground"`**: The sprite is centered horizontally and bottom-aligned.
  The feet sit on the bottom edge of the frame. Use for standing, walking,
  attacking, crouching -- any pose where the character is on the ground.

- **`"center"`**: The sprite is centered both horizontally and vertically.
  Use for airborne poses (jump, wall_slide, wall_jump) and death animations.

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
