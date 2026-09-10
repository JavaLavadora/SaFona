# Final character animation sources — local handoff

**N'Andreu (Engine Programmer)** · 2026-09-10

## Delivery and review status

- Branch: `art/final-character-animation-sources`.
- Worktree: `/home/antodiaz/projects/SaFona-worktrees/final-character-animation-sources`.
- Base: `96432105abe5363ff788f6fbe88b41fbda2771c2` (the supplied fetched
  `origin/master`); no old art commits were cherry-picked.
- Local-only delivery. No GitHub requests, push, PR creation, authentication
  changes, or merge. The requester confirms independent En Pau and En Miquel
  art-check PASS results for `ba75af0c`; this documentation-only follow-up
  does not rerun those reviews. The requester handles publication, and user
  approval is required before merge.
- Related existing Balchar tracking: [#132](https://github.com/JavaLavadora/SaFona/issues/132)
  and [#134](https://github.com/JavaLavadora/SaFona/issues/134). These references
  come from existing handoffs; no issue was queried or updated for this task.

## Contents and decisions

There are **20 final Aseprite files and 57 frames**:

- [Balchar index](../../assets/ai_sources/balchar/README.md): ten files,
  32 frames. Nine animation types, with two independent final walk alternatives;
  shared animations appear once, not in duplicated whole-character documents.
- [Bou de Pedra index](../../assets/ai_sources/boss_bou_de_pedra/README.md):
  ten files, 25 frames.
- Four current native PNG strips and four GIF previews: fixed walk, parallel
  walk, sling attack, and rush. The indexes include the motion previews.
- [Balchar manifest](../../assets/ai_sources/balchar/final_manifest.json) and
  [Bou manifest](../../assets/ai_sources/boss_bou_de_pedra/final_manifest.json)
  contain all **20 final SHA-256 hashes**, original source hashes, source tag
  spans, native durations, canonical mappings, and bottom-to-top layer order.
- [Asset workflow](../asset_generation_guide.md),
  [shared specifications](../asset_prompts/shared.md), and
  [World 1 specifications](../asset_prompts/world1.md) distinguish editable
  native sources from raw prompt grids and existing runtime PNGs/configs.

Extraction and previews use Aseprite MCP. Source artwork is not redrawn,
filtered, quantized, recentered, resized, or flattened. Native canvases remain
48x64 for Balchar and 80x72 for Bou. Each document contains one forward tag,
named after the file, spanning its complete local timeline from frame 1.

**Non-obvious layer constraint:** removing unused layers changed sling-frame-3
occlusion in an initial extraction; readback rejected it before delivery.
Cel z-index is relative to absolute layer slots, not just active-layer order.
Fixed walk and sling therefore retain all 15 original slots and z-index values,
including empty spacers. Other animations omit wholly unused layers only.
Saved originals and supplied source snapshots were never modified.

## Exact original snapshots

Independent originals are outside the worktrees under:

`/tmp/safona-final-character-animation-sources-20260910/originals/`

| Snapshot filename | SHA-256 |
| --- | --- |
| `balchar_sling_candidate.aseprite` | `a1bd990c662d98abc8a49b479f02518e5ebc14056599aa9929ef642c995fa656` |
| `balchar_walk_alternate.aseprite` | `521100cd2359fbd591091a7ac17f66f6f04366a4bdf5a3338201cec371f688ba` |
| `bou_de_pedra.aseprite` | `6ea78eb1bbe3f986467d71e1a7f845f71916417b9bf2f5e121df59495b45be55` |

The filenames in the provenance manifests identify these exact source
documents; they are not missing repository links. Splitting changes container
bytes and tag numbering, so final document hashes differ from original hashes.

## Verification results

```text
Aseprite saved/reopened audit:
20 files; 57 rendered frames; 303 retained cels
4,164,096 raw RGBA bytes compared exactly
0 changed rendered frames; 0 changed retained cel bytes
0 linked-image pairs in the selected sources or finals

Independent Node binary/container audit:
20 files; 57 frames; 303 cels; 4,164,096 RGBA bytes: PASS
14,452 partial-alpha pixels and 1,195 hidden-RGB pixels preserved
14 omitted cels are entirely zero RGBA, on wholly unused layers
Layer records, cel geometry/opacity/z-index, durations, palettes and links: PASS
Four GIF frame counts, durations and infinite-loop metadata: PASS

Preservation:
498 unchanged tracked base files: byte-exact
511 original protected main files outside the follow-up scope: byte-exact
67 protected runtime/reference sprite PNGs: byte-exact
20 final Aseprite hashes and all 8 preview files: unchanged by follow-up
Main HEAD, branch and index: unchanged
```

The initial consolidation preserved 529 existing main files. Separate user
authorization on 2026-09-11 covers 15 legacy-file removals and three canonical
specification edits, leaving 511 of that original protected set unchanged.
Historical preservation inventories retain their original scope and results;
the external `followup-*.json` inventories record this additional scope.

The Aseprite audit compares color space/mode, transparent index, palette colors
and placement, tag endpoints/direction/repeats, layer properties/order, absent
cel slots, raw cel dimensions/bytes, positions, opacity, z-index, color/user
data, and all linked/unlinked image relationships. Every rendered frame matches
its original source frame. The independent decoder also checks every omitted
cel for all-zero RGBA, including hidden channels.

Native PNG strips match source renders. Balchar GIFs exactly match the native
opaque-gray composite at 6x nearest-neighbor scale. Bou's 4x GIF quantizes its
1,449 source-composite RGB colors; only that review preview is lossy. The
editable RGBA source and native PNG preserve exact colors. PNGs were displayed;
GIF data was decoded and checked, not claimed as independently watched motion.

Documentation links, manifest hashes/counts/timing, native-versus-runtime
specifications, editor diagnostics, and whitespace checks pass. Documentation
review found no blocking comment/docstring issues. No repository implementation
code or tests were added. Pytest and game launch were deliberately not run for
this source-only task; no gameplay or runtime integration validation is claimed.

## Main-workspace delivery and cleanup

The 32 final asset/index/manifest/preview files are copied byte-identically into
the main workspace, alongside this report. The three canonical specifications
are mirrored byte-identically from the feature branch through scoped text
patches: main's accepted four-frame sling and requested four-frame rush remain,
and unrelated existing text is preserved. Main remains on
`art/balchar-sling-four-frame`, HEAD
`098c7984995c04448d8dbe78d5b470613da7bef7`, with index SHA-256
`d8829583222004d732a1aeb22f9a2357e5d6550629c549ae4955cd9257f514af`.
Authorized tracked deletions and specification edits are unstaged on that old
branch; no user changes are staged.

Exactly **352 files** were individually archived and then removed: the original
337 plus 15 separately authorized legacy files.

| Authorized category | Files |
| --- | ---: |
| Player Balchar projects/checkpoints, including two `.bak` files | 20 |
| Player generated preview tree | 89 |
| Player idle parts | 28 |
| Player cleaned idle parts | 28 |
| Player other-animation parts | 133 |
| Bou projects/checkpoints | 6 |
| Bou generated preview tree | 33 |
| Agent-temporary scripts under `tools/aseprite_scripts/` | 13 |
| Obsolete generated Balchar handoff reports | 2 |

The two removed reports are `docs/reports/balchar-sling-four-frame.md` and
`docs/reports/na-margalida-balchar-walk-articulated.md`; all other pre-existing
reports are preserved. These 15 legacy files are absent from the clean feature
base and are not introduced or deleted in the feature diff. A broad main text
search found references to their paths only in this handoff; no other reference
edits were needed.

No wildcard deletion, reset, stash, broad Git clean, or worktree/branch removal
was used. The cleaned player directory is empty; the boss directory contains
only its pre-existing runtime PNGs. Raw AI inputs, maps, video inputs, runtime
PNGs, processing JSON, engine code/manifest, skills, and user-owned reference
images remain untouched. The user's two pre-existing example-image deletions
remain deletions. Both older art worktrees remain clean at their original
heads (`c5e1052` and `94e4481`).

Recovery archive and exact cleanup inventory:

- `/tmp/safona-final-character-animation-sources-20260910/cleanup-archive/`
  mirrors all 352 removed file paths, including edited preview READMEs and the
  15 legacy files. Every archived file matches its original SHA-256; every
  inventoried source file is absent from main.
- `/tmp/safona-final-character-animation-sources-20260910/cleanup-inventory.json`
  lists every removed path explicitly.
- The same temporary directory contains before/after preservation inventories,
  Aseprite readback results, independent audit results, and the external audit
  helpers. They are not included in the commit. Temporary storage is not a
  permanent backup; preserve it externally if uncommitted history is needed.
- Existing branches/worktrees and their committed checkpoint history remain
  available independently of the temporary archive.

## Review procedure and remaining decisions

1. Open either source index and review its native PNG/GIF links.
2. Open the corresponding Aseprite file; inspect its single tag, local timing,
   and editable layers. Compare against the exact original snapshot and source
   span recorded in the manifest.
3. Verify file hashes against the manifests. Audit reruns preserve artwork but
  rewrite audit outputs; the Node helper can create missing manifests.
  Run the Aseprite helper with `params.audit_only=true`.
4. Review the feature branch, not the old dirty main art branch. No preview
   server or display process was started; direct file review needs no port
   forwarding. Port 6080 is only for a separately launched noVNC game session.

No consolidation blocker remains. Walk selection, final art approval, and
runtime integration are separate user decisions. The runtime still has three
sling frames and two rush frames, and Bou's engine manifest retains legacy
death/hurl metadata. No integration files are modified to disguise that gap.
No new issue was filed because the requester explicitly deferred all GitHub
activity; existing tracking references above remain available to the reviewer.