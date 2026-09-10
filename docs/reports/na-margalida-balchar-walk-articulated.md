# Balchar articulated walk — visual approval checkpoint

**Artist:** Na Margalida (Graphic Designer & Pixel Artist)

**Date:** 2026-09-10

**Branch:** `art/balchar-walk-articulated`

**Status:** Third contour refinement complete; **draft review package, not approved for integration**. **WAIT for Toni's explicit visual approval.** En Pau and En Miquel reviews are also pending; no merge or original-asset installation is authorized.

## Deliverables

All paths below are relative to the SaFona workspace root.

| File | Dimensions | Frames / purpose |
| --- | --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | 48×64 RGBA | Approved original baseline from earlier work: all 23 frames, 8 layers, unchanged |
| [assets/sprites/player/balchar_walk_candidate.aseprite](../../assets/sprites/player/balchar_walk_candidate.aseprite) | 48×64 RGBA | 23 frames, 12 editable layers; walk is frames 5–10 |
| [assets/sprites/player/preview/walk_articulated/before.png](../../assets/sprites/player/preview/walk_articulated/before.png) | 288×64 | Exact transparent strip of the original walk, frames 5–10 |
| [assets/sprites/player/preview/walk_articulated/walk_after.png](../../assets/sprites/player/preview/walk_articulated/walk_after.png) | 288×64 | Six 48×64 cells, transparent horizontal strip |
| [assets/sprites/player/preview/walk_articulated/walk_after_6x.png](../../assets/sprites/player/preview/walk_articulated/walk_after_6x.png) | 1728×384 | Same strip, transparent, nearest-neighbor 6× |
| [assets/sprites/player/preview/walk_articulated/walk_after.gif](../../assets/sprites/player/preview/walk_articulated/walk_after.gif) | 288×384 | Six-frame 6× preview on a neutral checkerboard |
| [assets/sprites/player/preview/walk_articulated/before_after_6x.png](../../assets/sprites/player/preview/walk_articulated/before_after_6x.png) | 1728×768 | Approved source above; candidate below, on a checkerboard |

**Replaces:** Nothing. Both editable projects were previously untracked local work: this PR adds the complete baseline project and a separate alternative, not a runtime replacement. No runtime PNGs, manifests, or game code were changed. Candidate origin remains `(0, 0)`, with the original 48×64 canvas and planted soles at `y=63`.

**Preservation / rollback:** The original and both local backups are intentionally unchanged. No rollback is needed because nothing is installed. Keep the candidate separate; any future integration requires explicit authorization. Earlier artwork checkpoints, intermediate backups, diagnostics, and scripts remain local and are excluded from this package.

## Artwork method and layer changes

Artwork was drawn directly through Aseprite MCP using inline Lua `Image:drawPixel` operations. There was no Python, CLI image generation, external image service, cropped-boot rotation, or whole-limb cut-out translation. The saved candidate is not flattened. Enlarged previews use separate images/a temporary preview sprite, not a resized candidate.

- **Both legs:** Separate pixel-row contours for the twelve boots, plus localized knee highlights. Ankles taper to three or four pixels; heels have a one-pixel contour step, insteps slope into low toe tips, and cuff/calf highlights use varied source shades. Trailing toes end at x24 in both contacts. Far limbs retain darker source colors rather than a black silhouette.
- **Near arm:** Tapered elbow/forearm contours, textured bracers, and three-pixel fist cores with a one-pixel thumb in the original `arm_back` walk cels. Forearms are approximately four pixels wide. These cels retain `zIndex=8`; the third refinement preserves the received sleeve/shoulder pixels through y40.
- **Far arm:** Separate elbow, bracer, and small-fist drawings on `walk_arm_far_L`; the existing shoulder attachment remains intact. The third refinement removes no clothing from `arm_front`.
- **Clothing:** Source frame 5 supplies the detailed clothing/sleeve template across the six walk poses. `torso`, `belt`, `arm_front`, and the salvaged tunic area in `legs` retain that template's pixel detail. Waist/cloth and lower near-arm content dip one pixel in frames 6 and 9, with a connection below the fixed neck. This stabilizes clothing rather than preserving each original walk frame's incidental fold variations.
- **Original `legs` layer:** Holds salvaged cloth only in walk frames. Obsolete limbs, the hanging accessory fragment, and the artificial bottom baseline were cleared from those cels.
- **Sling:** The existing short cord and pouch were repositioned to follow the refined hands in frames 7–10; frames 5–6 remain unchanged.
- **Head:** `headband_ribbon` and `hair_face` remain untouched.

The optional contact chest shift was deliberately omitted: preserving the overlapping tunic fragments took priority over adding lean. The artist verified all 24 clothing cels on `torso`, `belt`, `arm_front`, and `legs` against the retained second-pass checkpoint. The existing low-frame dip remains.

Four added layers contain exactly six cels each, exclusively in frames 5–10:

1. `walk_leg_far_L`
2. `walk_leg_near_R`
3. `walk_arm_far_L`
4. `walk_sling_followthrough`

The eight original named layers retain their relative stack order. Far leg is below near leg; both are below retained clothing. The sling is independently editable.

## Pose timing and anchors

| Source frame | Pose | Support sole x-range | Swing-foot bottom |
| --- | --- | --- | --- |
| 5 | Right/near contact | Right: 28–34 | Both feet contact |
| 6 | Low onto right | Right: 25–31 | Left: y=62 |
| 7 | Left passing | Right: 22–28 | Left: y=60 |
| 8 | Left/far contact | Left: 29–35 | Both feet contact |
| 9 | Low onto left | Left: 26–32 | Right: y=62 |
| 10 | Right passing | Left: 23–29 | Right: y=60 |

Each frame is **100 ms**; cycle length is **600 ms**. The original forward walk tag is preserved. Each support sole moves backward exactly three pixels per frame through its stance. Passing boots end at y60, three pixels above the y63 baseline, with the swinging knee ahead of the supporting leg. Arms oppose the leg contacts.

Frame 5's trailing ankle spans x17–20 at y59, centered at x18.5. Its toe ends at x24, leaving three transparent baseline pixels (x25–27) before the near sole. Frame 8 leaves four (x25–28) before the far sole. Both contact composites were checked for baseline bridges. The two leg layers and the far-arm layer are each four-connected in every walk frame; no detached joint or boot islands were found.

The GIF was reopened for metadata validation: six 288×384 checkerboard frames at 100 ms each. Animated preview playback is available through the local browser preview server; successful browser playback is **not** Toni's visual approval.

## Palette and preservation checks

The candidate remains RGBA. Its 15 palette entries are retained **as swatches**, not used to clamp image colors. Every nontransparent cel color occurs in the source. Boot/calf accents include `#BF8441`, `#CB9D61`, `#B98E62`, and `#A47D54` alongside the source's darker leather shades. Near-arm clusters use `#A66A2F`, `#D78D3A`, `#EFA247`, and `#FAB759`. No GDD-palette conversion or palette cleanup was performed. GIF palette encoding affects only that preview, not the RGBA candidate or PNGs.

Independent read-only Aseprite MCP checks by N'Andreu during packaging confirmed:

- **136/136 original-layer non-walk cel slots:** Identical pixel bytes, image size/mode, position, opacity, and z-index.
- **17/17 non-walk composite frames:** Pixel-identical.
- **1,088 non-walk cel-pair checks:** Linked/unlinked relationships preserved.
- **23/23 frame durations, 9/9 animation tags, 15/15 palette entries:** Preserved, including palette frame placement, tag ranges/direction/repeats/color, and original layer properties.
- **46/46 head-layer cels across all 23 frames:** Pixel- and cel-metadata-identical. Walk composite pixels through `y=33`, including the face and eyes, are unchanged. The inherited clothing-template stabilization differs from the original in 67 pixels across collar rows `y=34–35`; the artist reports no additional clothing or collar edits in the third refinement.
- **New layers:** No cels outside the walk range.
- **Transparency:** Newly drawn pixels are fully opaque over a transparent canvas. The 20 partially transparent source pixels across the six original walk composites remain identical at their original coordinates; they were not hardened or recolored.
- **Native PNGs:** Before and after strips are pixel-identical to fresh in-memory renders of their respective projects. The transparent enlarged strip is exact integer 6× nearest-neighbor; the comparison matches both renders composited over its checkerboard at 6×.
- **GIF metadata:** Six 288×384 frames, each 100 ms; 600 ms cycle.

No files were saved by these checks. Protected source hashes are unchanged:

| Protected file | SHA-256 |
| --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |
| First local backup (.bak), excluded from PR | `0fdbbe9a1f730eff0d5ebb0b301a69989136c27e43cb9e492c16276b1fa551ca` |
| Second local backup (.bak2), excluded from PR | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |

| Review candidate | SHA-256 |
| --- | --- |
| Third contour refinement | `32ece2a7d0cba26385d8bbd469198cacf44b7819b5a3dc166f503b8ec93b6ca8` |

The retained first and second passes serve only as local checkpoints. The third refinement includes limb-contour, color, and sling-position changes; packaging makes no artwork changes.

## Visual observations and open concerns

The requested before/after comparison and native-size PNG strip were inspected after export. Contact silhouettes have separated soles; the boot tips are low and the hands have smaller thumbed contours. Compared with the detailed source torso, the limbs still have simpler clusters. PNG inspection, metadata checks, and browser preview availability do not constitute final artistic approval.

**Remaining concerns**, covered by existing [Issue #132](https://github.com/JavaLavadora/SaFona/issues/132):

- Torso lean remains minimal; the optional chest shift was omitted to protect clothing. The one-pixel low dip in frames 6 and 9 remains.
- The trailing feet use a lifted heel and a three-pixel toe contact. Their weight, calf volume, and comparatively simple limb texture still need Toni's judgment at native scale and during playback.
- The frame 10→5 transition and overall rhythm still require Toni's playback review.

## Review handoff

This art-only draft targets `master` from `art/balchar-walk-articulated`; master remains unchanged. The package contains the seven artifacts listed above and this report only. No source code, validation scripts, runtime assets, or additional documentation are introduced. Runtime tests and a game launch are not applicable to this packaging-only change and were not run.

Review the native before/after strips, the 6× comparison, and the animated GIF linked above; open the separate candidate in Aseprite to inspect editable layers. The existing local browser preview server remains running; no game or display service is required for this review.

En Pau (Senior Engineer) and En Miquel (Software Architect) must review next. **WAIT for Toni's explicit visual approval before any integration or merge.** [Issue #132](https://github.com/JavaLavadora/SaFona/issues/132) remains open; neither this report nor the draft PR closes or approves the artwork.