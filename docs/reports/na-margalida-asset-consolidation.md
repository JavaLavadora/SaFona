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

## Handoff

- En Pau and En Miquel: PR review (max 3 review rounds per CLAUDE.md).
- Na Francina (PM): once reviewers approve, please coordinate user signoff
  before merge (mandatory per workflow rule #4).
