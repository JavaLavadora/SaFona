# Save Point & Level End Sprite Replacements

## Summary

Replace the colored-rectangle placeholders for save points and level-end markers with sprite-based visuals:
- **Save point**: A bonfire — unlit by default, switches to lit once the player activates it.
- **Level end**: A taula entrance viewed from the side, always visible.

Sprites are purely visual overlays (no collision). They are sized to look natural in the game world (bonfire at leg height, taula large enough for the character to fit through) but the invisible trigger rect stays unchanged.

## Assets

### Placeholder Sprites (Developer-Drawn)

Two simple colored-shape PNGs for initial development, placed in `assets/environment/`:

| File | Approx Size | Description |
|------|-------------|-------------|
| `bonfire.png` | ~48x32 px (2 frames of 24x32) | Horizontal sprite sheet: frame 0 = unlit (logs/stones), frame 1 = lit (same base + flame) |
| `taula_gate.png` | ~48x64 px | Side-view taula: vertical pillar + horizontal capstone |

Sizes are approximate — exact dimensions will be tuned during implementation to match Balchar's proportions (48x64 frame). The bonfire should sit around his feet; the taula should be tall enough for him to walk through.

### AI Generation Prompts

Saved to `tools/sprite_defs/`:

#### `bonfire_ai_prompt.md`

Prompt for generating two bonfire sprites (unlit + lit) on a green (#00FF00) background:
- 16-bit SNES pixel art style, no anti-aliasing
- Two sprites side by side in a single horizontal row
- Left: unlit bonfire (stacked limestone rocks and dry wood, no flame)
- Right: lit bonfire (same base + warm orange/yellow flickering flame)
- Balearic/Mediterranean feel: warm stone tones, dry scrubland wood
- Scale reference: bonfire should be roughly knee-height relative to a 48x64 character
- Solid bright green (#00FF00) background for chroma-key removal

#### `taula_ai_prompt.md`

Prompt for generating one taula entrance sprite on a green (#00FF00) background:
- 16-bit SNES pixel art style, no anti-aliasing
- Single sprite: side view of a taula (T-shaped megalithic monument)
- Vertical pillar topped by a horizontal capstone, forming a doorway/gate
- Weathered grey limestone with subtle moss/lichen
- Balearic talayotic style — based on real taula monuments from Menorca
- Scale reference: tall enough for a 48x64 character to walk through
- Solid bright green (#00FF00) background for chroma-key removal

### Processing

Use the existing `tools/process_ai_sprites.py` pipeline. Create two config files in `tools/sprite_defs/characters/`:

#### `bonfire.json`
```json
{
  "frame_width": 24,
  "frame_height": 32,
  "source_dir": "assets/ai_sources/bonfire",
  "output_dir": "assets/environment",
  "animations": [
    {"source": "bonfire.png", "frames": 2, "scale_pct": 100, "vertical_snap": "bottom"}
  ]
}
```

Processing splits the two-sprite sheet into `bonfire_unlit.png` (frame 0) and `bonfire_lit.png` (frame 1). Frame dimensions may need tuning after seeing AI output.

#### `taula_gate.json`
```json
{
  "frame_width": 48,
  "frame_height": 64,
  "source_dir": "assets/ai_sources/taula_gate",
  "output_dir": "assets/environment",
  "animations": [
    {"source": "taula_gate.png", "frames": 1, "scale_pct": 100, "vertical_snap": "bottom"}
  ]
}
```

Output: single `taula_gate.png` in `assets/environment/`.

**Post-processing note**: The standard pipeline outputs horizontal sprite sheets. For the bonfire, the two frames (unlit/lit) will be in a single sheet — the rendering code loads them as a frame strip and selects index 0 or 1 based on activation state. No need to split into separate files.

### Asset Manifest

Add entries to `sa_fona/data/asset_manifest.json` under `"sprites"`:

```json
"env_bonfire": {
  "path": "assets/environment/bonfire.png",
  "frame_width": 24,
  "frame_height": 32,
  "frame_count": 2
},
"env_taula_gate": {
  "path": "assets/environment/taula_gate.png",
  "frame_width": 48,
  "frame_height": 64,
  "frame_count": 1
}
```

## Rendering Changes

### File: `sa_fona/scenes/gameplay.py`

#### `_render_save_point_cues()` (lines 697-729)

Replace the rectangle/text drawing with:
1. Load the bonfire frame strip via `load_frame_strip()`.
2. For each save_point trigger:
   - Check if the trigger ID is in the `_activated_save_points` set.
   - Select frame index 0 (unlit) or 1 (lit) accordingly.
   - Position the sprite bottom-centered within the trigger rect.
   - Blit with camera offset.

#### `_render_level_end_cues()` (lines 731-765)

Replace the rectangle/text drawing with:
1. Load the taula gate image via `load_image()` (single frame).
2. For each level_end trigger:
   - Position the sprite bottom-centered within the trigger rect.
   - Blit with camera offset.

### State Tracking

Add a `_activated_save_points: set[int]` to `GameplayScene.__init__()`. When `_on_trigger_save_point()` fires, add the trigger's ID to this set. This determines whether to show the unlit or lit bonfire sprite.

On level load / checkpoint restore, pre-populate the set for the current checkpoint's save point (so the bonfire the player last saved at is already lit).

## Scope Exclusions

- No animation (flame flicker, particles, glow) — static sprite swap only.
- No collision changes — sprites are visual overlays only.
- No changes to trigger logic, save system, or level transition behavior.
- No changes to level JSON format — existing trigger rects are reused as-is.
