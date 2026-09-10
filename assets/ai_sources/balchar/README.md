# Balchar — editable animation finals

Ten native **48x64 RGBA** files: nine animation types, with two independent
walk alternatives. Common animations are stored once. Each file has one
forward tag matching its filename, local frames 1 through the listed count,
and repeat value 0. Neither walk is selected for runtime integration.

| File / tag | Frames | Duration per frame | Editable layers |
| --- | ---: | --- | ---: |
| [idle.aseprite](idle.aseprite) / `idle` | 4 | 150 ms | 7 |
| [walk_fixed.aseprite](walk_fixed.aseprite) / `walk_fixed` | 6 | 100 ms; 600 ms cycle | 15 |
| [walk_parallel.aseprite](walk_parallel.aseprite) / `walk_parallel` | 8 | 90 ms; 720 ms cycle | 7 |
| [jump.aseprite](jump.aseprite) / `jump` | 2 | 150 ms | 7 |
| [wall_slide.aseprite](wall_slide.aseprite) / `wall_slide` | 2 | 150 ms | 7 |
| [wall_jump.aseprite](wall_jump.aseprite) / `wall_jump` | 2 | 150 ms | 7 |
| [sling_attack.aseprite](sling_attack.aseprite) / `sling_attack` | 4 | 300, 100, 100, 200 ms | 15 |
| [hit.aseprite](hit.aseprite) / `hit` | 1 | 400 ms | 7 |
| [death.aseprite](death.aseprite) / `death` | 1 | 600 ms | 7 |
| [crouch.aseprite](crouch.aseprite) / `crouch` | 2 | 150 ms | 7 |

Both walk tags map to canonical animation `walk`. The fixed walk preserves
the existing six-pose gait; the parallel walk preserves the eight-pose gait
with solid boot soles, thicker legs, and larger hands. Final idle frame 1 is
the character reference; native foot-contact baseline is y=63. Selection and
art approval are separate from this lossless packaging step.

## Editability and provenance

All retained cel bytes (including partial alpha and hidden RGB), dimensions,
positions, opacity, z-index, palette colors, layer properties/order, timing,
and image-link relationships match the supplied sources. No flattening,
palette clamp, cropping, recentering, or artwork edits are applied.
The fixed walk and sling retain all 15 original layer slots, including empty
ones: their nonzero cel z-index offsets depend on absolute layer positions.
Other files omit only wholly unused layers. Seven-layer animations retain
their body-part separation, not a flattened render.

[final_manifest.json](final_manifest.json) records SHA-256 hashes, native
timelines, layer order, canonical mappings, and original document hashes/tag
spans. Original document names are provenance identifiers, not paths to
checkpoint files in this folder.

## Current review previews

Native strips retain the exact rendered RGBA frames. GIFs are 6x
nearest-neighbor previews on opaque **#585858**, looping forward at source
timing. Their decoded pixels match Aseprite's native gray composite exactly;
they are not editable masters.

| Animation | Native strip | Motion preview |
| --- | --- | --- |
| Fixed walk | [preview/walk_fixed.png](preview/walk_fixed.png) — 288x64 | [preview/walk_fixed.gif](preview/walk_fixed.gif) |
| Parallel walk | [preview/walk_parallel.png](preview/walk_parallel.png) — 384x64 | [preview/walk_parallel.gif](preview/walk_parallel.gif) |
| Sling attack | [preview/sling_attack.png](preview/sling_attack.png) — 192x64 | [preview/sling_attack.gif](preview/sling_attack.gif) |

![Fixed walk](preview/walk_fixed.gif)
![Parallel walk](preview/walk_parallel.gif)
![Sling attack](preview/sling_attack.gif)

## Runtime boundary

Existing raw PNGs and processed game sprites are unchanged. The game does not
load these Aseprite files; the processing config and runtime sling PNG still
describe three sling frames. Walk selection and PNG/config/engine-manifest
integration require a separate change.

See [canonical Balchar specifications](../../../docs/asset_prompts/shared.md#1-balchar-player-character)
and the [asset workflow](../../../docs/asset_generation_guide.md).