# Taula Gate Sprite Generation Prompt

Used to generate the AI reference image for level-end taula gate sprite.
Source image: `assets/ai_sources/taula_gate/taula_gate.png`
Processing config: `tools/sprite_defs/characters/taula_gate.json`
Output: `assets/environment/taula_gate.png` (32x48, single frame)

## Prompt

Pixel art sprite, 16-bit SNES style, solid bright green (#00FF00) background. Single taula gate viewed from side, T-shaped megalithic monument forming a doorway.

One thick vertical limestone pillar supporting wide horizontal capstone, clear doorway opening tall enough for warrior character (about 48 pixels tall), pillar roughly one-third width of capstone. Weathered ancient grey limestone with subtle warm undertones (NOT blue-grey), small patches of green-brown moss on capstone and upper pillar, fine cracks and mortar-line texture, solid and enduring.

Style: Based on Menorcan taula monuments (Torralba d'en Salort, Torre d'en Galmés). Balearic talayotic architecture, ancient monumental stone but not ruined. Clean pixel art, no anti-aliasing, no smoothing.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- Single sprite region detected
- Scaled to fit 32x48 frame, bottom-aligned
- Output: single image (32x48)
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/taula_gate.json`
