# Balchar articulated walk — leg and boot size review

**Artist:** Na Margalida (Graphic Designer & Pixel Artist)

**Packaging / verification:** N'Andreu (Engine Programmer)

**Date:** 2026-09-10

**Branch:** `art/balchar-walk-articulated`

**Status:** Toni accepts the motion loop, but his latest feedback rejects the volatile leg/foot sizes. **The size repair has no visual approval; style remains pending.** [PR #133](https://github.com/JavaLavadora/SaFona/pull/133) remains draft. En Pau and En Miquel reviewed `7afe219`, the pre-size-repair state; their follow-up on this repair is pending. No integration or merge is authorized.

## Deliverables

All paths below are relative to the SaFona workspace root. The original, motion checkpoint, and original before strip are unchanged.

| File | Dimensions | Frames / purpose |
| --- | --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | 48×64 RGBA | Approved original baseline from earlier work: all 23 frames, 8 layers, unchanged |
| [assets/sprites/player/balchar_walk_candidate.aseprite](../../assets/sprites/player/balchar_walk_candidate.aseprite) | 48×64 RGBA | Size-repaired candidate: 23 frames, 12 editable layers; walk is frames 5–10 |
| [assets/sprites/player/balchar_walk_motion_approved.aseprite](../../assets/sprites/player/balchar_walk_motion_approved.aseprite) | 48×64 RGBA | Immutable motion checkpoint from `7c59699`, not final appearance approval |
| [assets/sprites/player/balchar_walk_before_size_fix.aseprite](../../assets/sprites/player/balchar_walk_before_size_fix.aseprite) | 48×64 RGBA | Separate immutable rollback; byte-identical to the candidate at `7afe219` |
| [assets/sprites/player/preview/walk_articulated/before.png](../../assets/sprites/player/preview/walk_articulated/before.png) | 288×64 | Exact transparent strip of the original walk, frames 5–10 |
| [assets/sprites/player/preview/walk_articulated/walk_after.png](../../assets/sprites/player/preview/walk_articulated/walk_after.png) | 288×64 | Six 48×64 cells, transparent horizontal strip |
| [assets/sprites/player/preview/walk_articulated/walk_after_6x.png](../../assets/sprites/player/preview/walk_articulated/walk_after_6x.png) | 1728×384 | Same strip on a checkerboard, nearest-neighbor 6× |
| [assets/sprites/player/preview/walk_articulated/walk_after.gif](../../assets/sprites/player/preview/walk_articulated/walk_after.gif) | 288×384 | Six-frame 6× preview on a neutral checkerboard |
| [assets/sprites/player/preview/walk_articulated/before_after_6x.png](../../assets/sprites/player/preview/walk_articulated/before_after_6x.png) | 1728×768 | Approved source above; candidate below, on a checkerboard |
| [assets/sprites/player/preview/walk_articulated/legs_reference_comparison_10x.png](../../assets/sprites/player/preview/walk_articulated/legs_reference_comparison_10x.png) | 2880×570 | Actual rows: original / pre-size checkpoint / current; full-width crops at y45–63, nearest-neighbor 10× |
| [assets/sprites/player/preview/walk_articulated/size_stability_comparison_10x.png](../../assets/sprites/player/preview/walk_articulated/size_stability_comparison_10x.png) | 2880×380 | Pre-size checkpoint above / current below; full-width crops at y45–63, nearest-neighbor 10× |
| [assets/sprites/player/preview/walk_articulated/boot_registration_sheet_8x.png](../../assets/sprites/player/preview/walk_articulated/boot_registration_sheet_8x.png) | 1152×512 | Isolated, registered boots across six phases; rows: near before / near after / far before / far after, nearest-neighbor 8× |

**Replaces:** No runtime asset. The candidate remains separate, with origin `(0, 0)`, the original 48×64 canvas, and planted soles at `y=63`. No runtime PNGs, manifests, game code, or original artwork were changed.

**Rollback:** The pre-size checkpoint preserves the exact incoming candidate independently of the older motion checkpoint. Other local checkpoints, backups, diagnostics, and scripts are excluded and untouched.

## Size-repair scope and visual limits

The artist's two-stage anatomy/volume repair changes **only 12 cel images**: frames **5–10** on `walk_leg_far_L` and `walk_leg_near_R`. The earlier appearance pass is the disputed pre-size state, not an approved finish. The source design remains the reference.

The artist reconstructed knees using fixed **6 px thigh / 6.5 px shin guides**, rather than preserving the earlier guessed knee coordinates. Foot trajectories and gait timing remain unchanged. Shared flat, leaning, and heel-raised boot profiles replace individually drawn outlines. **The boots still have squarer contours than the reference**; size consistency is not proof of full polish or style approval. Toni has already been shown the latest PNG.

All other parts preserve the incoming pre-size candidate exactly: arms, sling, head/eyes, clothing, palette, layer order, and cel placement. The four walk-only layers remain `walk_leg_far_L`, `walk_leg_near_R`, `walk_arm_far_L`, and `walk_sling_followthrough`, each with six editable cels. The candidate is not flattened or quantized.

**Inherited distinction from the original:** Clothing uses the source-frame-5 template with a one-pixel low dip in frames 6 and 9; torso lean is minimal. The previously reviewed 67 collar-pixel differences at y34–35 remain, not additional head or clothing edits.

### Boot measurements: evidence and limits

- Artist-reported profile areas: **41 / 43 / 43 pixels**, compared with **32–45** previously and **40** for the sampled original boot.
- Independently counted foreground pixels in the registration PNG: near before `45,45,45,39,32,35`; near after `41,43,43,43,43,41`; far before `39,32,35,45,45,45`; far after `43,43,41,41,43,43`. Every foreground pixel matches its claimed source layer/frame under translation; every 8× block is exact. Current near/far opposite-phase silhouettes match in registered coordinates.
- These are checks of the supplied diagnostic masks, **not independent anatomical segmentation** of the source. No separate latest measurement masks/helpers were located in the inspected asset and MCP temporary directories. The original sample area and shaft-normal estimates were not independently remeasured.
- Artist-reported minimum shaft-normal widths for the three profiles: **4.03 / 4.27 / 4.47 px** overall, including joins; **3.02 / 3.20 / 3.35 px** for the interior. These geometric estimates do not establish visual quality.

## Timing and contact geometry

Each of frames **5–10 is 100 ms**: a **600 ms** cycle with the original forward walk tag. Grounded soles end at **y=63**, recovering feet at **y=62** in frames 6/9, and passing feet at **y=60** in frames 7/10. Support-foot baseline extents move backward three pixels per stance frame; outline pixels need not form a solid interval.

Contact-pose silhouette spacing is **2 pixels in frame 5 / 3 in frame 8** at y56. The narrower baseline-only measurement is different: y63 retains **3 / 4 transparent pixels**, respectively. No baseline bridge is present. The older 3/4 figure must not be presented as the full boot-to-boot negative-space clearance.

## Read-only verification

Independent Aseprite MCP checks compare the current candidate with the **pre-size checkpoint**, unless stated otherwise:

- **276 layer/frame slots = 208 present cels + 68 empty slots.** Exactly **12 present cel images changed; 196 present cel images are byte-identical**. Empty slots are counted separately. Raw changed pixels span **x16–36, y47–63**, exclusively in the two leg layers, frames 5–10; y47 edits are hidden in the composite.
- **Cel metadata preserved:** image dimensions/mode, position, opacity, z-index, color, and user data. All **21,528 linked/unlinked pairs** among the 208 present cels match.
- **Sprite/layer properties** checked include canvas/color mode, transparent index, grid/pixel ratio, layer order/names, visibility/editability, opacity, blend mode, flags, color, and user data. **23 durations, nine tags, and 15 palette entries/placement** match. Durations and tags also match the original and motion checkpoint.
- **17 non-walk renders** match both the pre-size checkpoint and original. All **67,872 protected composite pixels** outside the walk crop x10–38/y48–63 match the pre-size checkpoint. The **600 changed composite pixels** lie within x16–36/y49–63.
- **Source colors / alpha:** Every nontransparent candidate cel color occurs in the original; all **20 partially transparent walk pixels** match the pre-size checkpoint. No new partial-alpha pixels were introduced.
- **PNG exports:** Native before/after strips exactly match original/current in-memory renders. The 6× after strip and before/after comparison match exact checkerboard composites and scaling. Both 10× comparisons match full-width y45–63 crops and scaling.
- **Reference-sheet labeling discrepancy:** Its middle row matches the **pre-size checkpoint exactly**, not the motion checkpoint (436 native pixels differ from that older checkpoint). The actual row order is documented above; packaging did not regenerate or relabel the image itself.
- **GIF metadata only:** Reopened as data, with no GIF image transport: six **288×384** frames, each **100 ms**, **600 ms** total.

Packaging made no artwork, timing, palette, or export writes and used no Python or external generation. No sprite or preview was saved by verification. Earlier En Pau/En Miquel original-source checks remain historical evidence; this follow-up independently verifies the size-repair delta rather than reclassifying empty slots as cels.

## Content hashes

| Artifact | SHA-256 |
| --- | --- |
| [assets/sprites/player/balchar.aseprite](../../assets/sprites/player/balchar.aseprite) | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |
| First local backup (.bak), excluded from PR | `0fdbbe9a1f730eff0d5ebb0b301a69989136c27e43cb9e492c16276b1fa551ca` |
| Second local backup (.bak2), excluded from PR | `f23aeb30d1fe56071e1c138f8df02fe762ec4f2a3f2f85cb58c79e747951d739` |
| [assets/sprites/player/balchar_walk_motion_approved.aseprite](../../assets/sprites/player/balchar_walk_motion_approved.aseprite) | `32ece2a7d0cba26385d8bbd469198cacf44b7819b5a3dc166f503b8ec93b6ca8` |
| [assets/sprites/player/balchar_walk_before_size_fix.aseprite](../../assets/sprites/player/balchar_walk_before_size_fix.aseprite) | `fb7cbc1142125ed3efca7558b55c70c032ddbe182c47d565facf3947fcb00f1d` |
| [assets/sprites/player/balchar_walk_candidate.aseprite](../../assets/sprites/player/balchar_walk_candidate.aseprite) | `c9e3b9ba52a3449f9c13de23448bea67882711b756113fec9f0f91f5cd1b328d` |

## Review handoff

The packaging delta is ten explicitly selected files: candidate, pre-size rollback, two new diagnostics, five refreshed standard previews, and this report. The original, motion checkpoint, original before strip, runtime assets, and unrelated local files are not included in this delta. The existing feature-branch worktree is preserved; no stash, cleanup, process management, or master changes are part of packaging. Runtime tests and a game launch were not run because this is art-only review packaging.

Open the committed PNGs and [animated GIF](../../assets/sprites/player/preview/walk_articulated/walk_after.gif) directly, or use a local preview server for playback. No game/display service or forwarded port is required. The editable candidate and both immutable checkpoints support direct Aseprite comparison.

**Next gate:** Toni's size/style decision and En Pau/En Miquel follow-up review. The size complaint is not approval of this repair. [Issue #132](https://github.com/JavaLavadora/SaFona/issues/132) remains open for visual acceptance. No further art pass, runtime installation, or merge without explicit authorization.