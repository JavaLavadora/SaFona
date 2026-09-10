# Balchar articulated walk — leg appearance review

**Artist:** Na Margalida (Graphic Designer & Pixel Artist)

**Packaging / verification:** N'Andreu (Engine Programmer)

**Date:** 2026-09-10

**Branch:** `art/balchar-walk-articulated`

**Status:** Toni's feedback accepts the motion loop; **motion is locked, leg/boot appearance review is pending**. [PR #133](https://github.com/JavaLavadora/SaFona/pull/133) remains draft. En Pau and En Miquel reviewed the previous commit `7c59699`; review of this appearance follow-up is pending. No integration or merge is authorized.

## Deliverables

All paths below are relative to the SaFona workspace root. The original and before strip are unchanged from the previous commit.

| File | Dimensions | Frames / purpose |
| --- | --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | 48×64 RGBA | Approved original baseline from earlier work: all 23 frames, 8 layers, unchanged |
| [assets/sprites/player/balchar_walk_candidate.aseprite](../../assets/sprites/player/balchar_walk_candidate.aseprite) | 48×64 RGBA | Appearance candidate: 23 frames, 12 editable layers; walk is frames 5–10 |
| [assets/sprites/player/balchar_walk_motion_approved.aseprite](../../assets/sprites/player/balchar_walk_motion_approved.aseprite) | 48×64 RGBA | Immutable pre-appearance rollback; byte-identical to the previous committed candidate |
| [assets/sprites/player/preview/walk_articulated/before.png](../../assets/sprites/player/preview/walk_articulated/before.png) | 288×64 | Exact transparent strip of the original walk, frames 5–10 |
| [assets/sprites/player/preview/walk_articulated/walk_after.png](../../assets/sprites/player/preview/walk_articulated/walk_after.png) | 288×64 | Six 48×64 cells, transparent horizontal strip |
| [assets/sprites/player/preview/walk_articulated/walk_after_6x.png](../../assets/sprites/player/preview/walk_articulated/walk_after_6x.png) | 1728×384 | Same strip, transparent, nearest-neighbor 6× |
| [assets/sprites/player/preview/walk_articulated/walk_after.gif](../../assets/sprites/player/preview/walk_articulated/walk_after.gif) | 288×384 | Six-frame 6× preview on a neutral checkerboard |
| [assets/sprites/player/preview/walk_articulated/before_after_6x.png](../../assets/sprites/player/preview/walk_articulated/before_after_6x.png) | 1728×768 | Approved source above; candidate below, on a checkerboard |
| [assets/sprites/player/preview/walk_articulated/legs_reference_comparison_10x.png](../../assets/sprites/player/preview/walk_articulated/legs_reference_comparison_10x.png) | 1740×480 | Three rows: original / motion checkpoint / refined candidate; six crops per row, x10–38 and y48–63 inclusive, nearest-neighbor 10× |

**Replaces:** No runtime asset. The candidate remains separate, with origin `(0, 0)`, the original 48×64 canvas, and planted soles at `y=63`. No runtime PNGs, manifests, game code, or original artwork were changed.

**Rollback:** The committed motion checkpoint preserves the exact pre-appearance candidate. It is not final appearance approval. Other local checkpoints, backups, diagnostics, and scripts are excluded and untouched.

## Appearance scope

The artist refined **only 12 cels**: frames **5–10** on `walk_leg_far_L` and `walk_leg_near_R`. The reference comparison emphasizes exposed warm knees, fuller calves, and stepped boots drawn from the source design. **Trailing boots remain more angular than the reference**; this is a known visual acceptance gate, not a technical error. Toni has been shown the PNGs. No further artwork iteration is authorized without user feedback.

All other art parts retain the motion checkpoint exactly: arms, sling, head/eyes, clothing, palette, layer order, and cel placement. The candidate is not flattened. Its four walk-only layers remain `walk_leg_far_L`, `walk_leg_near_R`, `walk_arm_far_L`, and `walk_sling_followthrough`, each with six cels.

**Inherited distinction from the original:** Clothing uses the source-frame-5 template with a one-pixel low dip in frames 6 and 9; torso lean is minimal. The previously reviewed 67 collar-pixel differences at y34–35 remain, not additional head or clothing edits. Motion acceptance is Toni's feedback, not a claim that static checks establish artistic quality.

Packaging made no artwork or timing edits and used no Python, external generation, or export writes.

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

Frame 5 retains three transparent baseline pixels (x25–27); frame 8 retains four (x25–28). No baseline bridges were found. All 18 leg/far-arm cels are four-connected, with no detached islands.

## Read-only verification

Independent Aseprite MCP checks compared the appearance candidate with the immutable motion checkpoint:

- **12 changed cels; 196 other cels byte-identical; 68 empty slots preserved.** Changes are confined to x10–38, y48–63 in the two leg layers, frames 5–10.
- **All cel metadata preserved:** image dimensions/mode, position, opacity, z-index, and user data. **21,528 linked/unlinked cel-pair relationships** match.
- **Sprite/layer properties, 23 durations, nine animation tags, and 15 palette entries/placement** match. Durations and tags also match the original. The palette remains swatches, not an indexed-color clamp.
- **17 non-walk renders and all 67,872 composite pixels outside the permitted walk crop** are identical. There are 436 changed composite pixels inside the crop.
- **Source colors / alpha:** Every nontransparent candidate cel color occurs in the original. All 20 partially transparent walk pixels match the checkpoint; no new partial-alpha pixels were introduced.
- **Timing / geometry:** The support spans and swing-foot bottoms in the table, 3/4-pixel contact gaps, and limb connectivity pass.
- **PNG exports:** Native before/after strips exactly match fresh in-memory renders of the original/candidate. The enlarged after strip is exact nearest-neighbor 6×. Both rows of the 6× comparison match their renders over its checkerboard. The three-row leg comparison exactly matches the original/checkpoint/candidate crops at 10×.
- **GIF metadata only:** Reopened as data, not displayed through image transport: six 288×384 frames, each 100 ms, 600 ms total.

No sprite or preview was saved by verification. Earlier En Pau/En Miquel checks of the motion checkpoint established preservation against the original: 136 original-layer non-walk cel slots, 17 non-walk renders, and 46 head cels. The appearance delta leaves those areas unchanged.

## Content hashes

| Artifact | SHA-256 |
| --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |
| Second local backup (.bak2), excluded from PR | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |
| [assets/sprites/player/balchar_walk_motion_approved.aseprite](../../assets/sprites/player/balchar_walk_motion_approved.aseprite) | `32ece2a7d0cba26385d8bbd469198cacf44b7819b5a3dc166f503b8ec93b6ca8` |
| [assets/sprites/player/balchar_walk_candidate.aseprite](../../assets/sprites/player/balchar_walk_candidate.aseprite) | `fb7cbc1142125ed3efca7558b55c70c032ddbe182c47d565facf3947fcb00f1d` |

## Review handoff

This follow-up contains exactly eight files: the candidate, motion rollback, leg comparison, four updated after/comparison exports, and this report. The tracked original and before strip remain untouched; no other files are included. Runtime tests and a game launch were not run because this is asset-review packaging only.

Open the committed PNGs and [animated GIF](../../assets/sprites/player/preview/walk_articulated/walk_after.gif) directly, or use a local preview server for playback. No game/display service is required. The editable candidate and immutable motion checkpoint support direct Aseprite comparison without session-specific services.

**Next gate:** Toni's appearance decision against the three-row reference comparison, plus En Pau/En Miquel follow-up review. [Issue #132](https://github.com/JavaLavadora/SaFona/issues/132) remains open. No further art pass, runtime installation, or merge without explicit authorization.