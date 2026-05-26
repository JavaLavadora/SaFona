# Taula Gate Sprite Generation Prompt

Used to generate the AI reference image for level-end taula gate sprite.
Source image: `assets/ai_sources/taula_gate/taula_gate.png`
Processing config: `tools/sprite_defs/characters/taula_gate.json`
Output: `assets/environment/taula_gate.png` (32x48, single frame)

## Prompt

Pixel art of a taula monument viewed from the side, 16-bit SNES style, on a solid bright green (#00FF00) background. Single sprite:

A T-shaped megalithic stone monument (taula) seen from the side, forming a doorway or gate. One thick vertical limestone pillar supports a wide horizontal capstone across the top. The proportions should form a clear doorway opening — tall enough for a warrior character to walk through (about 48 pixels tall). The pillar is roughly one-third the width of the capstone.

The stone is weathered ancient grey limestone with subtle warm undertones — NOT blue-grey. Small patches of green-brown moss or lichen on the capstone and upper pillar. Fine cracks and mortar-line texture in the stone. The monument should look ancient and monumental but not ruined — solid, heavy, enduring.

Style: Based on real taula monuments from Menorca (Torralba d'en Salort, Torre d'en Galmés). Balearic talayotic architecture. Clean pixel art, no anti-aliasing, no smoothing. Solid bright green (#00FF00) background for chroma-key removal.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- Single sprite region detected
- Scaled to fit 32x48 frame, bottom-aligned
- Output: single image (32x48)
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/taula_gate.json`
