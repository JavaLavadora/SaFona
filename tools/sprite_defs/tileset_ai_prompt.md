# World 1 Tileset Generation Prompt

Used to generate the AI reference image for World 1 terrain tiles.
Source image: `assets/exmaple_tiles.png`
Processing script: `tools/process_ai_tiles.py`
Output: `assets/tilesets/world1/tileset.png` (256x16, 16 auto-tile variants)

## Prompt

Pixel art tileset for a 2D platformer, 16-bit SNES style, on a solid bright green (#00FF00) background. Show exactly 4 tiles in a single horizontal row, evenly spaced, each tile a separate square block:

1) Top surface tile — grey Mediterranean limestone with short grass/moss on top edge, light warm grey stone body with subtle mortar line texture, small cracks and color variation
2) Inner stone tile — solid grey limestone block, no grass, visible mortar lines and subtle stone grain, slightly darker than the surface tile
3) Underground/deep tile — darker grey stone, more worn and cracked, minimal detail, the deepest layer
4) Wall edge tile — grey stone with slight weathering on one side, transitional tile between exposed surface and inner stone

Style: Balearic island Mediterranean terrain. Warm neutral grey stone (NOT blue-grey), subtle ochre undertones. Clean pixel art, no anti-aliasing, no smoothing. Each tile should be clearly separated with green space between them. Consistent lighting from top-left. Stone should look like ancient talayotic construction — rough-hewn limestone blocks.

## Processing Notes

- Green background detected via `(g-r > 40) & (g-b > 40) & (g > 80)`
- 4 tile regions found via `scipy.ndimage.label` on non-green mask
- Regions smaller than 1000px² filtered out
- 5px inset crop to avoid green fringe at edges
- Remaining green pixels (where `g-r > 30` and `g-b > 30` and `g > 100`) replaced with average of non-green neighbors
- **Color correction**: AI tiles tend blue-grey; luminance extracted and remapped onto warm stone palette:
  - Dark end: RGB(130, 112, 82)
  - Light end: RGB(215, 195, 155)
  - 8% original color variation preserved for texture
- Grass tile: top 40% mapped to green palette RGB(72,108,50)–(120,155,85), bottom 60% warm stone
- Underground tile additionally darkened by 0.7 factor
- Multi-step downscale: LANCZOS to 48x48 → contrast 1.4x → sharpness 1.5x → NEAREST to 16x16
- 16 auto-tile variants built from 4-bit neighbor bitmask (UP=1, DOWN=2, LEFT=4, RIGHT=8)
- Edge darkening at 0.75 factor for 2px on exposed sides
