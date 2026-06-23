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

## Round 2 — per-world split

**Trigger**: user feedback — the consolidated `docs/asset_prompts.md` was
2,547 lines and would multiply ×5 once Worlds 2-5 are populated. Splitting
before merge prevents the file from becoming unmanageable.

### What changed

Replaced the single `docs/asset_prompts.md` with a per-world folder:

```
docs/asset_prompts/
├── shared.md   (1,253 lines) — cross-world assets
└── world1.md   (1,440 lines) — World 1 (Sa Talaia) assets
```

Total 2,693 lines vs. the original 2,547 — the extra 146 lines come from
two file headers, two TOCs, two scope statements, and cross-references
between the files. No prompt content was lost.

### Split rule

- **`shared.md`** gets anything that appears across worlds:
  - Balchar (player) — all 9 animations including crouch, sling, hit, death
  - Bep (companion) — all 6 animations including curse glow
  - Player ground shadow (3 sizes)
  - Player projectiles (slingstones — Tier 1/2/3)
  - Pickups (heart, stone, shield orb)
  - Breakables (pot, crate)
  - Generic effects (dust, impact, portal, anticipation, debris) — palette
    `effects.gpl` is shared even though the Dimoni aura row uses it
  - UI elements (HUD hearts, stone icon, mask icon, dialogue frame, shop
    frame, boss health bar, charge indicator)
  - Title screen + Game Over screen
  - Dialogue portraits for Balchar (4) and Bep (4)
  - Frame-size convention + global style block + cross-world generation rules
  - Post-generation pipeline (§ 22)

- **`world1.md`** gets W1-specific content:
  - Bou de Pedra (boss) — all 3 phases + 7 attack animations + arena props
  - W1 enemies (Stone Guardian, Rival Warrior, Possessed Sheep) — bodies
    AND their attack effect overlays (§ 13.1 dust sweep, § 13.2 slash trail)
  - W1 NPCs (Dimoni de Sant Joan, Llorenç) + portraits (3 each)
  - W1 Dimoni aura effect (uses shared `effects.gpl` palette)
  - W1 tilesets (outdoor / cave / talayot) including the canonical
    color-correction pipeline (luminance remap onto warm stone
    `(130,112,82) → (215,195,155)`, multi-step downscale,
    16 auto-tile variants, edge darkening)
  - W1 backgrounds (outdoor / cave / talayot)
  - W1 environment props (bonfire, taula gate) + processing notes
  - W1 style chain and W1 generation order

### Edge cases (judgment calls)

| Edge case | Decision | Reason |
|-----------|----------|--------|
| Bep curse-glow aura | Stay in `shared.md` § 2.6 with a "W1 narrative tie" note pointing at the Dimoni section in `world1.md` | The sprite IS Bep (cross-world). The narrative tie is W1; the visual element is cross-world. |
| Dimoni aura effect (16x16 portal-purple glow) | Live in `world1.md` (new "Dimoni aura effect (W1)" section between § 8 and § 13), with a callout that it uses the shared `effects.gpl` palette block in `shared.md` § 12 | The effect is W1-specific (tied to the Dimoni); but the palette is generic. Cross-referencing both files keeps the generation flow clear. |
| Boss arena props (pillars, rock projectile, shockwave, pulse, shadow) | `world1.md` § 3.11 | Scoped to the Bou de Pedra arena. Future bosses bring their own arena props in their own world file. |
| Boss health bar UI | Stay in `shared.md` § 18.6 with a "cross-world caveat: currently styled for W1" note | The UI control is cross-world; only its current visual styling is W1-specific. Per-world variants can be added later. |
| Roman Legionary stab flash (§ 13.3) | Stage in `world1.md` § 13.3 with a "Future-world note: move to `world2.md` when that file exists" callout | Legionary is W2. There is no `world2.md` yet. Staging in `world1.md` keeps it alongside the other two attack effect overlays so the pipeline section reads cleanly; it'll move when W2 is created. |
| § 21 Generation order | `world1.md` § 21 | The order is W1-specific. Each future world gets its own generation order in its own file. The W1 order references shared sections (Balchar, Bep, projectiles, pickups, UI) by file path. |

### Section numbering

Preserved 1-22 across the split so existing PR / Issue / docstring
references keep working:

- `shared.md`: §§ 1, 2, 9, 10, 11, 12 (generic), 17 (Balchar/Bep portraits),
  18, 19, 20, 22.
- `world1.md`: §§ 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17.3-17.4 (W1 NPC
  portraits), 21, plus the "Dimoni aura effect (W1)" subsection.

### Content preservation check

- All 45 `[ATTACH ... MASTER IDLE SPRITE HERE]` operational markers preserved
  (8 Balchar + 5 Bep + 10 Bou + 4 Stone Guardian + 5 Rival + 4 Sheep +
  3 Dimoni + 2 Llorenç + 1 Balchar portrait + 1 Bep portrait + 1 Dimoni
  portrait + 1 Llorenç portrait = 45).
- All palette blocks preserved (Balchar 15, Bep 9, Bou 12, Stone Guardian 9,
  Rival 12, Sheep 8, Dimoni 12, Llorenç 12, heart 4, stone 5, pot 6, crate
  5, projectiles 8, effects 12).
- Tileset color-correction RGB endpoints and multi-step downscale recipe
  preserved verbatim in `world1.md` § 15.1.
- Bonfire + taula gate processing notes preserved.
- Design rationale (30% block, 1.0s tell, drop tables, charge tier color
  alignment) preserved in `world1.md` and `shared.md` respectively.

### Discoverability updates (round 2)

- `CLAUDE.md` — Key Documents and Asset & Sprite Generation sections now
  describe the folder + the shared/per-world rule.
- `README.md` — Documentation index row points at the folder with inline
  links to both files.
- `.claude/agents/na-margalida-graphic-designer.md` — MANDATORY section
  describes both files and where new prompts go.
- `tools/sprite_defs/README.md` — short pointer updated.
- `docs/asset_generation_guide.md` — added a "Where does this prompt go?"
  subsection under "How to add a new asset" giving the shared-vs-per-world
  decision rule. Updated every internal link (§ 1 Balchar →
  `asset_prompts/shared.md`, §§ 13 / 15 → `asset_prompts/world1.md`).
  Rewrote the future-worlds guidance to say "create `world<N>.md`",
  matching the new convention.
- `docs/proposals/attack_effect_system_proposal.md` § 7 pointer updated to
  `asset_prompts/world1.md` § 13 with a note on the W2-staged Legionary.

### Open questions (round 2)

None blocking. Edge cases were resolvable with judgment per the spec.

One soft note for future-me / future worlds: when `world2.md` is created,
move `world1.md` § 13.3 (Roman Legionary stab flash) into it. The
`world1.md` callout already documents this.

### Verification

- Repo grep `asset_prompts\.md` (with the `.md`) returns hits only inside
  this report file (intentional — Round 2 history). All live surfaces
  point at `docs/asset_prompts/`.
- Line-count math: 1,253 + 1,440 = 2,693 vs. original 2,547. +146 lines
  from per-file headers, TOCs, scope statements, and cross-references —
  expected and within spec ("≈ 2547 minus duplicate headers" allowing for
  added cross-file references).
- Game not launched (docs-only — no code touched).
- This is round 3 of max 3 review rounds (round 1 = consolidation review,
  round 2 = En Pau / En Miquel fixes, round 3 = per-world split). It must
  count.
