# Bonfire Sprite Generation Prompt

Used to generate the AI reference image for save point bonfire sprites.
Source image: `assets/ai_sources/bonfire/bonfire.png`
Processing config: `tools/sprite_defs/characters/bonfire.json`
Output: `assets/environment/bonfire.png` (48x32, 2 frames of 24x32)

## Prompt

Pixel art sprite sheet, 16-bit SNES style, solid bright green (#00FF00) background. 2 frames in a horizontal row, evenly spaced, same scale. Small bonfire save point:

1) Unlit — small pile of rough-hewn grey limestone rocks with dry sun-bleached wood and brush on top, no flame, cold and dormant
2) Lit — identical rock and wood base, warm orange-yellow flame rising from wood, 3-4 flame colors (dark orange base, bright orange middle, yellow tips), small ember dots above

Style: Balearic Mediterranean. Warm grey limestone rocks (NOT blue-grey), dry earth tones for wood, knee-height scale (16-20 pixels tall). Clean pixel art, no anti-aliasing, no smoothing. Both sprites must have identical base structure, only flame differs. Clearly separated with green space between them.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- 2 sprite regions detected via connected components on non-green mask
- Both frames scaled uniformly to fit 24x32 frame, bottom-aligned
- Output: single horizontal sprite sheet (48x32), frame 0 = unlit, frame 1 = lit
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/bonfire.json`
