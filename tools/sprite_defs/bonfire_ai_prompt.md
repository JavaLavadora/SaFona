# Bonfire Sprite Generation Prompt

Used to generate the AI reference image for save point bonfire sprites.
Source image: `assets/ai_sources/bonfire/bonfire.png`
Processing config: `tools/sprite_defs/characters/bonfire.json`
Output: `assets/environment/bonfire.png` (48x32, 2 frames of 24x32)

## Prompt

Pixel art of two bonfire sprites, 16-bit SNES style, on a solid bright green (#00FF00) background. Show both sprites in a single horizontal row, evenly spaced, at the same scale:

1) Unlit bonfire — a small pile of stacked rough-hewn limestone rocks with dry scrubland wood and kindling arranged on top, no flame, no glow, cold and dormant. The wood is sun-bleached Mediterranean driftwood and dry brush.

2) Lit bonfire — the exact same rock and wood arrangement as sprite 1, but now burning with a warm orange-yellow flame rising from the wood. The flame should be simple and stylized (3-4 colors: dark orange base, bright orange middle, yellow tips). Small ember dots above the flame.

Style: Balearic island Mediterranean feel. Warm grey limestone rocks (NOT blue-grey), dry earth tones for wood. The bonfire should be small — roughly knee-height for a warrior character (about 16-20 pixels tall). Clean pixel art, no anti-aliasing, no smoothing. Both sprites must have identical base rocks and wood — only difference is the flame on sprite 2. Clearly separated with green space between them.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- 2 sprite regions detected via connected components on non-green mask
- Both frames scaled uniformly to fit 24x32 frame, bottom-aligned
- Output: single horizontal sprite sheet (48x32), frame 0 = unlit, frame 1 = lit
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/bonfire.json`
