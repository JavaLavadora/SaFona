# Na Margalida — Handoff Report: Asset & Sprite Documentation Consolidation

**Issue**: #123
**Branch**: `docs/asset-consolidation`
**Scope**: Documentation only (no code changed)

## What I did

Consolidated 6+ scattered prompt/asset/sprite documentation sources into two
new files, then updated 5 discoverability surfaces and deleted the old
sources.

### New files

- **`docs/asset_generation_guide.md`** — workflow + methodology +
  processing pipeline + JSON config format + QC checklist. Opens with a
  numbered "How to add a new asset" workflow and the explicit
  "DO NOT create new prompt files elsewhere" rule.
- **`docs/asset_prompts.md`** — every AI prompt currently scattered across
  the old sources. Organized by asset, with a TOC, frame-size convention
  documented at the top, and an explicit `[ATTACH MASTER IDLE SPRITE HERE]`
  operational marker convention.

### Discoverability surfaces updated

1. **`CLAUDE.md`** — added a top-level "Asset & Sprite Generation" section
   pointing at the two new docs and `tools/sprite_defs/characters/`, plus
   two new entries in the Key Documents list and a pointer line in the
   Asset Pipeline section.
2. **`.claude/agents/na-margalida-graphic-designer.md`** — added a
   MANDATORY section at the top mandating reading
   `docs/asset_generation_guide.md` first and stating that new prompts
   ONLY go to `docs/asset_prompts.md` (no new prompt files elsewhere).
3. **`docs/asset_generation_guide.md`** — opens with the "How to add a new
   asset" workflow (11 numbered steps) plus the no-new-files rule.
4. **`tools/sprite_defs/README.md`** — trimmed from ~200 lines to a
   ~13-line pointer; clarifies that the folder is processing configs only.
5. **`README.md`** (repo root) — added a Documentation index table linking
   to the two new asset files alongside the GDD, architecture, roadmap,
   and distribution guide.

### Files deleted

- `docs/proposals/asset_generation_prompts.md`
- `docs/proposals/asset_style_guide.md`
- `docs/proposals/prompts/` (folder of 59 individual prompt files)
- `docs/w1_asset_generation_guide.md`
- `tools/sprite_defs/attack_effects_ai_prompt.md`
- `tools/sprite_defs/bonfire_ai_prompt.md`
- `tools/sprite_defs/taula_gate_ai_prompt.md`
- `tools/sprite_defs/tileset_ai_prompt.md`

### Files kept

- `tools/sprite_defs/balchar_ai_prompt.md` (historical v1/v2/v3 processing notes — archive value)
- All `tools/sprite_defs/characters/*.json` (processing configs — different purpose from prompts)

## Conflict resolutions applied (per the Issue defaults)

| Conflict | Resolution |
|----------|-----------|
| Stone Guardian eye color | **Green** (`80,200,80`) — master prompt wins over w1_guide's amber |
| Projectile Tier 2 glow | **Blue** (`80,144,224` / `120,184,248`) — master prompt wins over w1_guide's orange |
| Projectile Tier 3 glow | **Gold** (`216,184,56` / `248,224,96`) — master prompt wins over w1_guide's white-red |
| Llorenç costume | Cream linen shirt + olive green vest + terracotta apron + leather satchel — master prompt wins over earlier "leather tunic + scrolls" |
| Bou de Pedra idle frame counts | **4 frames** per phase (Phase 1/2/3 idle) — multi-frame wins for richer animation |
| Dimoni idle | **4 frames** — multi-frame wins. Laugh/grant/angry: **2 frames** each |
| Llorenç idle | **4 frames** — multi-frame wins. Talk: **4 frames**. Shop: **2 frames** |
| Effect canonical sizes | Aura **16x16**, portal **24x32** (master values) — flagged in guide that mismatches with in-game usage should be reviewed, not silently resized |
| Bep palette | Authored a 9-color GIMP palette (`assets/palettes/bep.gpl`) spec following Balchar's convention |
| Frame-size convention | Documented the 3 layers at the top of `asset_prompts.md`: hitbox (code constant), AI prompt source size, JSON config output size (typically 2x source) |

## Content preservation checklist

All required unique content was preserved:

- 14 dialogue portraits from w1_guide §13 (Balchar x4, Bep x4, Dimoni x3, Llorenç x3) with portrait names matching `world1_dialogue.json` / `world2_dialogue.json` field values
- 7 UI elements from w1_guide §14 with code-constant refs (`_MASK_ICON_SIZE`, `_INDICATOR_WIDTH/_HEIGHT`, `PICKUP_WIDTH/_HEIGHT`)
- Title screen + Game Over screen
- Player ground shadow (3 sizes)
- Shield orb pickup (12x12)
- Bep curse-glow aura (with `glow.png` filename)
- Drop tables (pot 1-3 stones, crate 2-4 stones)
- Design rationale notes (Rival Warrior 30% block, Stone Guardian 1.0s tell, etc.) in a dedicated table in the guide
- Crouch prompt from `09_balchar_crouch.md` with full identity-lock text
- Layout instructions from `24_bou_de_pedra_arena_props.md` and `53_effects.md` (group widths, vertical stacking)
- Tileset color-correction RGB endpoints `(130,112,82) → (215,195,155)` and multi-step downscale pipeline (LANCZOS → 48x48 → contrast 1.4x → sharpness 1.5x → NEAREST)
- Attack effects (3) — Stone Guardian dust sweep, Rival Warrior slash, Legionary stab flash
- Bonfire prompt + processing notes
- Taula gate prompt + processing notes
- `[ATTACH MASTER IDLE SPRITE HERE]` operational marker convention documented at the top of the prompts file

## Open questions

None blocking. The Issue defaults covered every conflict I encountered.

One soft note: the effect canonical sizes (aura 16x16, portal 24x32) come
from the master prompts file. If in-game code is using different sizes for
these effects, the guide tells future contributors to flag for review
rather than silently resize. I did not audit the code — that would be a
follow-up task if needed.

## Verification

- Game not launched (per Issue: docs-only PR, no code touched).
- Repo grep for stale references to deleted files: clean (no surviving
  links to `docs/proposals/asset_generation_prompts.md`, `asset_style_guide.md`,
  `w1_asset_generation_guide.md`, or the `prompts/` folder).
- All cross-references in the new docs use relative paths
  (`docs/asset_prompts.md`, `asset_generation_guide.md`).

## Round 1 review fixes

En Pau and En Miquel completed round 1. Four findings addressed on the same
branch (`docs/asset-consolidation`):

### Fix 1 — [BLOCKING from En Miquel] `attack_effect_system_proposal.md` § 7

`docs/proposals/attack_effect_system_proposal.md` § 7 contained 5 full AI
prompts (Rival spear thrust, Stone Guardian arm sweep, Legionary stab,
Anticipation glow, Stone debris) that had drifted from the canonical versions
in `docs/asset_prompts.md` § 13. Most notably the Stone Guardian effect: § 7
described a **6-frame** sweep including the arm itself and a shockwave, while
the canonical § 13.1 is a **3-frame simple brown dust no-body-parts** VFX.

**Resolution**: replaced § 7 (lines 206-423, ~218 lines of AI prompts) with a
4-line pointer to `docs/asset_prompts.md` § 13. The design rationale in
§§ 1-6 (visual fantasy, anchor positions, palette references, per-enemy
attack design tables) is preserved — that's design history, not prompt
content. I did the grep En Miquel requested (`GLOBAL STYLE CONSTRAINTS`,
`^Pixel art sprite sheet`, `^Create a SNES-style`) across `docs/proposals/`
after the fix — zero remaining hits in any proposal file.

### Fix 2 — [SUGGESTION from En Pau] Charge indicator color contradiction

`docs/asset_prompts.md` § 18.7 still described Tier 2 = orange and Tier 3 =
white-red (inherited from the deleted `w1_asset_generation_guide.md`), while
§ 11 locks projectile Tier 2 = blue and Tier 3 = gold. Per Issue #123 default
(master prompts win on visual specs), § 18.7 has been updated:

- Tier 1: white / grey baseline (neutral pre-charge)
- Tier 2: light-blue → blue gradient, same family as § 11 Tier 2 projectile
  (`#78B8F8` core, `#5090E0` edge)
- Tier 3: yellow → gold gradient, same family as § 11 Tier 3 projectile
  (`#F8E060` core, `#D8B838` edge), with 1px white spark particles

Added a one-line rationale comment in the section: "Colors aligned with
projectile glow tiers (§ 11) for visual coherence." Same charge level now
shows the same color in the indicator as on the stone fired.

### Fix 3 — [SUGGESTION from En Miquel] Acknowledge retained `balchar_ai_prompt.md`

`docs/asset_generation_guide.md` § 8 now has a "Historical note" paragraph
immediately after the "Existing JSON configs" table, calling out that
`tools/sprite_defs/balchar_ai_prompt.md` is retained as archival v1/v2/v3
processing history and is NOT an authoritative prompt source — pointing
readers at `docs/asset_prompts.md` § 1 instead. Wording matches the existing
"if you find prompts outside this file it's a bug" theme.

### Fix 4 — [SUGGESTION from En Pau] PR body line counts

PR body said `asset_generation_guide.md` was ~480 lines and
`asset_prompts.md` was ~1690. Actual line counts at the head of the branch
are 580 (now 586 after fix 3) and 2,533 respectively. Updated the PR body
via `gh pr edit 124` to reflect reality.

### Llorenç path-encoding note (En Miquel, noted but not actioned)

En Miquel flagged the ASCII/UTF-8 inconsistency in deleted Llorenç filenames
(`45_llorenc_idle.md` vs. `45_llorenç_idle.md`). File deletion succeeded
cleanly; the new `asset_prompts.md` keeps ç in section headings (prose, not
paths). No action this PR — captured for future filename-hygiene practice.

### En Pau effect-canonical-sizes follow-up (FUTURE)

En Pau requested a follow-up Issue to cross-check effect canonical sizes
(aura 16x16, portal 24x32) against `tools/sprite_defs/characters/*_effects.json`
configs in a separate PR. Not in scope for this consolidation. Will file
once this PR merges.

## Handoff

- En Pau and En Miquel: round 2 re-review (round 1 of 3 used).
- Na Francina (PM): once reviewers approve, please coordinate user signoff
  before merge (mandatory per workflow rule #4).
