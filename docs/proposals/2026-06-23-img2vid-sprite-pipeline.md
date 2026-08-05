# Img2Vid Sprite Generation Pipeline — Design

**Status:** Draft for user review
**Date:** 2026-06-23
**Author:** Na Francina (PM), brainstorming with Toni

---

## Motivation

The current sprite generation flow produces N static keyframes per animation from a single AI sprite sheet. Two problems:

1. AI-generated keyframes are stiff and the in-between motion has to be invented downstream. Feeding each keyframe to img2vid *separately* does not fix this: img2vid on a lone mid-animation pose produces arbitrary ambient motion, not the intended pose progression, and N unrelated clips cannot be stitched into one coherent cycle. The whole point of img2vid is to **create** the motion — so the seed must be a single, stable, identity-locked still, and the motion must come from the prompt.
2. The "GLOBAL STYLE CONSTRAINTS" block at the top of every prompt is noise — image AIs don't respect abstract style directives, and including it dilutes the directives they *do* respect (palette, identity lock, reference image).

The new pipeline:

- **Slims the prompts** — drop the global constraints block; keep only the directives AI actually respects.
- **Seeds img2vid from the immutable master idle** — each animation is produced by feeding the character's one master idle still (see "Master Character Generation") to img2vid together with that animation's prompt. img2vid creates the in-between motion from a single identity-locked seed, yielding **one** continuous-motion video per animation from which any number of frames can be sampled. There is no per-animation sprite sheet and no sheet-splitting step.
- **Persists every intermediate artifact** so failure modes are debuggable per stage.

The shipping format and downstream game code do not change. The pipeline replaces *the source* of sprite sheets.

---

## Pipeline Overview

Four stages plus a one-time prerequisite. Two of the four stages are existing/manual, two are new tools.

The **seed** is the character's immutable master idle still (see "Master Character Generation" — generated once per character, never regenerated per animation). It has two roles here: it is the img2vid seed for *every* animation, and it is the scale/anchor reference during assembly. It lives once per character at `<source_dir>/idle.png` (the same still `tools/process_character_sprites.py` already uses), *outside* the per-animation working subtree.

```
Prereq    Master idle still (one-time per character, immutable)     [existing]
            → <source_dir>/idle.png   (img2vid seed + scale/anchor ref)

Stage 1   Prompt (asset_prompts/shared.md or world1.md)             [docs change]
            ↓
Stage 2   Image→Video: master idle + animation prompt → ONE video   [manual, hybrid-ready]
            ↓                                                     → 01_video.mp4
Stage 3   tools/dump_video_frames.py + manual prune                 [NEW + user]
            ↓                                                     → 02_dumps/
Stage 4   tools/assemble_sprite_sheet.py                            [NEW, automated]
            ↓                                                     → 03_assembled_raw.png
          tools/process_character_sprites.py <character>.json       [canonical]
                                                                  → 04_assembled_final.png
                                                                  → assets/sprites/...
```

**Key invariant:** Stage 4's output is shaped to match what the canonical `tools/process_character_sprites.py` already expects: chroma-green background where **every pixel is *exactly* `(0, 255, 0)` or a palette color — no semi-transparent edges, no intermediate green values**; target frame dimensions; palette-quantized against `assets/palettes/<character>.gpl`. Downstream is unchanged.

**Re-runnability:** Each stage is an independent CLI reading from / writing to known folders. Any stage can be re-run in isolation without re-running earlier ones.

---

## Folder Layout & Debug Artifacts

Working directory per animation:

```
assets/ai_sources/img2vid/<character>/<animation>/
├── 01_video.mp4                 ← Stage 2 output (user drops the img2vid MP4 here)
├── 02_dumps/                    ← Stage 3 output (Kth-frame dumps from 01_video.mp4)
│   ├── dump_0000.png
│   ├── dump_0001.png
│   └── dump_NNNN.png
│       ← USER PRUNES IN PLACE: delete frames you don't want
├── 03_assembled_raw.png         ← Stage 4 output BEFORE process_character_sprites.py
│                                  (bg removed, palette-quantized, packed sheet)
└── 04_assembled_final.png       ← After process_character_sprites.py (canonical chain)
```

The img2vid **seed / scale reference** is *not* in this per-animation subtree: it is the character's single master idle still at `<source_dir>/idle.png` (e.g. `assets/ai_sources/balchar/idle.png`), generated once per character and reused for every animation.

**Conventions:**

- **Numbered prefixes** = pipeline order obvious at a glance.
- **Stage N's output is Stage N+1's input** — no coupling, every stage re-runnable.
- **`02_dumps/` is deterministic** from `01_video.mp4` + K. If the user prunes too aggressively, `dump_video_frames.py --reset` re-creates it.
- **Pruning is "delete in place"** — fewer steps, `--reset` makes it safe.
- **`03_assembled_raw.png` is the debug checkpoint** — compared against `04_assembled_final.png` to localize bugs to assembly vs. process-script.
- **`assets/ai_sources/img2vid/` is gitignored.** Final committed artifact remains the game sprite in `assets/sprites/...`.

**Frame-to-sheet ordering rule:** the assemble script reads the surviving PNGs in `02_dumps/` in filename order and packs them left-to-right. Total frame count = number of surviving dumps. The user controls the final frame count purely by which dumps they keep — no rigid quota.

---

## Per-Stage Tooling

### Stage 1 — Slim prompts (docs change, no code)
See "Prompt Restructuring" and "Documentation Updates" sections below.

### Stage 2 — Image→Video (manual today, API-ready)
User uploads the character's **master idle still** (`<source_dir>/idle.png`) to Meta AI img2vid (free, web-only) together with the animation's prompt, downloads the resulting MP4, and drops it as `01_video.mp4` in the work folder. One video per animation — img2vid creates the motion from the single idle seed.

**Hybrid-ready:** if a paid API (Runway/Luma/Pika) is adopted later, only this stage's actor changes — the pipeline stays identical.

**Recommended:** keep videos short (~1-2 seconds) to minimize identity drift (see Risk R2).

### Stage 3 — `tools/dump_video_frames.py` (NEW)
Thin wrapper over ffmpeg. Dumps every Kth frame from the single `01_video.mp4`:

```
ffmpeg -i 01_video.mp4 -vf "select=not(mod(n\,K))" -fps_mode vfr 02_dumps/dump_%04d.png
```

(Note: `-fps_mode vfr` replaces the deprecated `-vsync vfr`; requires ffmpeg >= 5.1.)

**CLI:**
- `python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]`
- `--k` (default 10) — extract every Kth frame.
- `--reset` — wipe and re-extract (safety net for over-pruning).

Reads `01_video.mp4` from the animation's work folder and writes to `02_dumps/`; errors loud if the video is missing.

### Stage 4 — `tools/assemble_sprite_sheet.py` (NEW, the substantive one)

Reads the surviving PNGs in `02_dumps/` in filename order. Reads the character JSON
(`tools/sprite_defs/characters/<character>.json`) for `frame_width`,
`frame_height`, `source_dir`, and `output_dir`. Computes the scale/anchor
reference **once** from the character's master idle still
(`<source_dir>/idle.png`) — the same still that seeded every img2vid video:

```
Setup (once, from the master idle):
  • Open <source_dir>/idle.png
  • Combined chroma + rembg mask (same combinator as --bg-mode both — see R1)
    + tight bbox crop
  • Validate the bbox is sensible:
      - bbox missing                → raise "master idle at <path> has no
                                      foreground after chroma-key; manually
                                      inspect and re-generate if needed."
      - bbox height < 50% of canvas → raise (same message). Catches
                                      "rembg/chroma ate most of the character."
  • Record:
      source_bbox_height   (character body height in the master idle)
      source_anchor_y      (where bbox bottom sat in the canvas)

Per surviving dump frame in 02_dumps/:
  1. Background-remove                  → RGBA, transparent background
                                          (--bg-mode {rembg,chroma,both}, default both)
  2. Tight crop to alpha bbox (+ small margin)
  3. Downsample so cropped height == source_bbox_height
                                          (two-pass: bilinear → NEAREST)
  4. Palette quantize → snap to character's .gpl palette
                                          (parse_gpl(assets/palettes/<character>.gpl)
                                          — same parser as tools/clean_sprites.py,
                                          single source of truth)
  5. Composite onto chroma-green canvas of character frame dims
     with cropped bottom at source_anchor_y
                                          (placement, not sizing — anchor lives only here)
  6. POSTCONDITION enforcement: hard alpha threshold so the canvas contains
     ONLY exact (0, 255, 0) chroma OR exact palette colors. For every output
     pixel: alpha >= 128 → keep the palette-quantized RGB; alpha < 128 →
     replace with (0, 255, 0, 255). No semi-transparent edges, no blended
     pixels survive into 03_assembled_raw.png.

After all frames processed:
  7. Pack horizontal → 03_assembled_raw.png   (debug checkpoint)
  8. Write the same sheet to <source_dir>/<animation>.png so the canonical
     processing script finds it as a fresh AI source.
  9. Invoke `python tools/process_character_sprites.py
     tools/sprite_defs/characters/<character>.json` as a subprocess.
  10. Verify the resolved output file exists after the subprocess returns;
      RAISE (not warn) if missing. The canonical script always exists; if
      it's not on disk the repo is broken.

      Resolve the expected filename the same way process_character_sprites.py
      does — look up the animation's JSON entry by `source == <animation>.png`
      and use `entry.get("output", entry["source"])`. Do NOT assume the output
      is `f"{animation}.png"`: balchar.json's sling_attack entry sets
      `"output": "sling.png"`, so <output_dir>/sling_attack.png never exists
      even on a fully successful run — the real file lands at
      <output_dir>/sling.png.
     → 04_assembled_final.png + game asset (actual filename per the entry's
       `output` field, e.g. sling.png for sling_attack)
```

**Why scale/anchor come from the master idle, not character JSON:**
The master idle still is the immutable authority for the character's size and ground-line, and it is the same seed every animation's img2vid video was generated from — so anchoring every animation's frames to it keeps scale and baseline mutually consistent across the whole character. Per-animation fine-tuning (e.g. jump/fall vertical placement, `scale_pct`) is still handled downstream by `process_character_sprites.py`'s per-entry `vertical_snap` and `scale_pct`; Stage 4 only needs to deliver frames at a consistent reference scale. No per-animation override flag is needed here.

**CLI:** `python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}] [--warn-scale-pct 15]`

### Dependencies added
- `rembg>=2.0.50,<3.0` (background removal, MIT, runs locally) — ~150MB U2Net
  model is downloaded on first run; pinned to keep the default model stable.
- `onnxruntime>=1.16,<2.0` — rembg requires this to run the U2Net model.
- `scipy>=1.11,<2.0` — `remove_background`'s connected-component rescue
  (the `--bg-mode both` combinator, R1 mitigation) uses `scipy.ndimage` to
  label and dilate mask regions. Not present in `pyproject.toml` today;
  Task 4 must add it there when it implements `remove_background`.
- `ffmpeg` system binary, **>= 5.1** (for the `-fps_mode` flag used in Stage 3).
- Everything else (Pillow, numpy) already in the project.

---

## Prompt Restructuring

Apply to every prompt in `docs/asset_prompts/shared.md` (sections 1.1–18.x) and `docs/asset_prompts/world1.md` (sections 3.x–8.x).

**Drop from each prompt:**

```
GLOBAL STYLE CONSTRAINTS (DO NOT VIOLATE):
- Style:         Authentic SNES-era 16-bit pixel art
- Perspective:   Strict side view (2D platformer)
- Light source:  Top-left, consistent across all assets
- Shading:       2-3 tones per material, no pillow shading
- Pixel density: Moderate, readable at 1x scale
- Outlines:      Clean, dark outline color from palette
- Palette:       Use ONLY the approved palette listed below
- Rendering:     Pixel-perfect, no blur, no anti-aliasing, no gradients
- Aesthetic:     Pre-Roman Mediterranean (Balearic-inspired)
- Background:    Solid bright green (#00FF00) for chroma-key
- Layout:        Single horizontal row, poses numbered, clear spacing
```

**Keep in each prompt:**

- `CRITICAL IDENTITY LOCK:` block (anchors to master idle reference — AI does respect this)
- `REFERENCE: [ATTACH ... MASTER IDLE SPRITE HERE]`
- `PALETTE` block with concrete RGB values (AI respects concrete colors)
- `SPRITE CONSTRAINTS` (sheet size, frame count, facing)
- `BODY SIZE RULE` and other sprite-specific rules
- `ANIMATION DESCRIPTION` — per-frame breakdown
- `RULES:` tail

**Update to `docs/asset_generation_guide.md` Section 0 — Global Style Lock:**

Flip the existing note that says the block is "copied verbatim into every prompt." New wording:

> This block is reference for humans only. It is **not** copied into prompts — AI image generators do not respect abstract style directives at this level, and including them dilutes the directives they *do* respect (palette, identity lock, reference image, frame layout). Style consistency comes from the palette block, the identity lock, and the reference image.

Same flip in `docs/asset_prompts/shared.md` "Global style block" section.

---

## Documentation Updates

Four files. No new docs created.

### `docs/asset_generation_guide.md` (single workflow source of truth)
- **Section 0 — Global Style Lock:** the note flip described above.
- **"How to add a new asset" (top):** insert img2vid steps into the numbered workflow.
- **Section 4 — Same Character, New Animation:** add the img2vid stage between prompt authoring and final processing (~10 lines + the diagram from "Pipeline Overview" above), making clear the master idle is the img2vid seed.
- **Section 8 — Processing pipeline & JSON config format:** update the pipeline diagram with the new stages; add Quick Start commands for the two new CLIs; add a short "Debug artifacts" subsection naming `03_assembled_raw.png` as the checkpoint.
- **Section 9 — Asset directory structure:** document `assets/ai_sources/img2vid/<character>/<animation>/` and its `01_…` → `04_…` layout.

### `docs/asset_prompts/shared.md`
- **"Global style block" section:** note flip (reference-only, not prompt content).
- **Each per-asset prompt (1.1 through 18.x):** delete the `GLOBAL STYLE CONSTRAINTS` block. Keep IDENTITY LOCK, PALETTE, SPRITE CONSTRAINTS, BODY SIZE RULE, ANIMATION DESCRIPTION, RULES.

### `docs/asset_prompts/world1.md`
- **"Style chain (World 1)" section:** drop any "copied verbatim" claim.
- **Each per-asset prompt (3.x through 8.x):** delete GLOBAL STYLE CONSTRAINTS block. Same retain-list.

### `tools/sprite_defs/README.md`
- Replace the overview pipeline diagram with the new one (from "Pipeline Overview" section above).
- Add the two new CLIs to Quick Start with their flags.

### Files NOT touched
- `tools/sprite_defs/balchar_ai_prompt.md` — historical processing notes per CLAUDE.md.
- `tools/sprite_defs/characters/*.json` — processing configs unchanged.

---

## Risks & Open Issues

### R1 — Background removal eats thin features (sling cord, headband ribbon)
**Fail mode:** rembg/U2Net was trained on photos; thin pixel-art features can be silently classified as background. A naive logical-OR with chroma would amplify R4 (it lets every anti-aliased green edge survive as foreground).
**Mitigation:** `--bg-mode {rembg,chroma,both}` flag. `both` uses **rembg as the primary mask**, then performs a **connected-component rescue**: chroma-mask components that are 4-connected to (i.e. touch) the rembg foreground (after 1px dilation) are added back. Components that are *not* touching rembg foreground — e.g. anti-aliased green-edge halos — are discarded. Default `both`.
**Fallback:** if `03_assembled_raw.png` shows missing cord, set `--bg-mode chroma` and re-run assemble. If still wrong, the source frame is bad — regenerate the video.

### R2 — Identity drift across the video
**Fail mode:** img2vid models morph face/proportions over time. By second 3 of a 4-second clip, the character may look subtly different.
**Mitigation:** documented best practice — generate **short** videos (~1-2 sec) and prune toward the early end of `02_dumps/`.
**Fallback:** if good motion only appears mid-clip but face has drifted, accept the cost and either pick the pose anyway or regenerate the video with a different seed.

### R3 — Scale/position drift within the video
**Fail mode:** img2vid subtly zooms or pans through the clip, so later dumps sit at a different scale than the master idle.
**Mitigation:** assemble script logs each frame's bbox dimensions vs. the master idle's. `--warn-scale-pct N` (default 15) emits a warning if any frame's bbox differs from the master idle by more than N%.
**Fallback:** user sees warning, drops the drifty frames, re-runs assemble.

### R4 — Antialiasing/blur survives downsampling
**Fail mode:** video frames are continuous-tone; even with two-pass downsample + quantization, some frames are fuzzy at sprite scale.
**Mitigation:** the existing `clean_sprites.py` step (already in the pipeline) does outline enforcement and palette tightening — final cleanup pass.
**Fallback:** delete the offending dump, re-run assemble.

### R5 — Manual img2vid bottleneck
**Fail mode:** every animation = N manual web sessions = hours.
**Mitigation:** Stage 2 treats `01_video.mp4` as a drop zone. The actor doesn't matter to the pipeline — swap to API any time. (One video per animation instead of N per-keyframe videos already cuts the manual sessions by the frame count.)
**Fallback:** adopt a paid API (Runway, Luma, Pika) if pain exceeds budget.

### R6 — Disk usage from dumps
**Fail mode:** 1 video × ~100 frames × ~60 animations × ~1MB ≈ 6GB if everything's kept.
**Mitigation:** add `assets/ai_sources/img2vid/` to `.gitignore` (targeted — existing `assets/ai_sources/*` PNGs remain tracked). Work folder is scratch; only the final game sprite in `assets/sprites/...` is committed.
**Fallback:** future `tools/clean_sprite_work.py --older-than 7d` housekeeping (not in v1).

### R7 — rembg model drift
**Fail mode:** rembg auto-downloads its U2Net model on first run. A future model version (or a future rembg release switching defaults) could subtly alter foreground masks across runs.
**Mitigation:** pin `rembg>=2.0.50,<3.0` and `onnxruntime>=1.16,<2.0`. Stage 4 explicitly requests the `u2net` session rather than the floating default.
**Fallback:** check `~/.u2net/` model file hash if results drift between machines.

### R8 — Double-quantization between Stage 4 and clean_sprites.py
**Fail mode:** Stage 4 palette-quantizes; `clean_sprites.py` palette-quantizes again. If the two read different palette sources, drift compounds silently.
**Mitigation:** both use `parse_gpl(assets/palettes/<character>.gpl)` as the **single source of truth**. Re-quantization against the same palette is idempotent.
**Fallback:** if drift surfaces, drop Stage 4's quantization step and rely entirely on `clean_sprites.py` for palette enforcement.

### R9 — ffmpeg flag deprecation
**Fail mode:** earlier ffmpeg versions used `-vsync vfr`; this was deprecated in 5.1 in favor of `-fps_mode vfr`. Older spec/plan text used the deprecated flag.
**Mitigation:** Stage 3 uses the new flag; the spec documents ffmpeg >= 5.1 in the install steps.
**Fallback:** if a deployment environment has older ffmpeg, override via env var (not in v1).

### Chain script orchestration (resolved)
Stage 4 invokes `tools/process_character_sprites.py <character.json>`. That script and `tools/clean_sprites.py` are chained by the existing `tools/reprocess_all_sprites.sh` for batch runs (Phase 1 = `process_character_sprites.py` for every config; Phase 3/4 = `clean_sprites.py` per output PNG); for single-animation runs, Stage 4 invokes only `process_character_sprites.py` and leaves `clean_sprites.py` for the user to run if needed. This is documented in the asset generation guide.

---

## Out of Scope (Explicitly)

- Replacing existing `tools/process_character_sprites.py` or `tools/clean_sprites.py` — they remain the final-cleanup chain.
- An automated frame-quality scorer — pruning stays manual (Section 3 decision).
- A new per-character JSON schema — existing `tools/sprite_defs/characters/*.json` is reused.
- Moving prompts out of `docs/asset_prompts/*.md` — they stay there per the CLAUDE.md rule.
- Switching to a paid img2vid API — designed-for, not implemented in v1.

---

## Implementation Notes

Per CLAUDE.md, the PM (Na Francina) does not write code. Implementation is delegated to N'Andreu (engine programmer) in a feature branch with PR review by En Pau + En Miquel before user testing.

The work decomposes naturally into small PRs that can ship sequentially:

1. **Docs + prompt cleanup** — slim prompts, flip the "copied verbatim" note, update workflow docs. Zero code, immediate value (slimmer prompts can be used today with the *old* pipeline too).
2. **`dump_video_frames.py`** — smallest new tool, adds ffmpeg system dep.
3. **`assemble_sprite_sheet.py`** — the substantive new tool, adds rembg dep, wires into the canonical `tools/process_character_sprites.py`.
4. **End-to-end test** — pick one animation (suggested: Balchar idle or sling attack), run the full pipeline manually, verify `04_assembled_final.png` looks correct, screenshot the result for user approval.

A detailed implementation plan (task breakdown, test approach, file-by-file changes) will be produced by the writing-plans skill in a separate doc once this design is approved.
