# Img2Vid Sprite Generation Pipeline — Design

**Status:** Draft for user review
**Date:** 2026-06-23
**Author:** Na Francina (PM), brainstorming with Toni

---

## Motivation

The current sprite generation flow produces N static frames per animation from a single AI image. Two problems:

1. AI-generated keyframes are stiff and the in-between motion has to be invented downstream.
2. The "GLOBAL STYLE CONSTRAINTS" block at the top of every prompt is noise — image AIs don't respect abstract style directives, and including it dilutes the directives they *do* respect (palette, identity lock, reference image).

The new pipeline:

- **Slims the prompts** — drop the global constraints block; keep only the directives AI actually respects.
- **Inserts an image-to-video stage** — each AI-generated keyframe is fed (with its prompt) to an img2vid AI. The resulting video gives a continuous-motion source from which any number of frames can be sampled.
- **Persists every intermediate artifact** so failure modes are debuggable per stage.

The shipping format and downstream game code do not change. The pipeline replaces *the source* of sprite sheets.

---

## Pipeline Overview

Six stages. Three are existing tools we reuse, three are new.

```
Stage 1   Prompt (asset_prompts/shared.md or world1.md)           [docs change]
            ↓
Stage 2   AI sprite sheet generation                              [existing, manual]
            ↓                                                     → 01_source_sheet.png
Stage 3   tools/split_sprite_sheet.py                             [NEW, automated]
            ↓                                                     → 02_split_frames/
Stage 4   Image→Video (Meta AI today, API later)                  [manual, hybrid-ready]
            ↓                                                     → 03_videos/
Stage 5   tools/dump_video_frames.py + manual prune               [NEW + user]
            ↓                                                     → 04_dumps/
Stage 6   tools/assemble_sprite_sheet.py                          [NEW, automated]
            ↓                                                     → 05_assembled_raw.png
          Existing process_<character>_ai_sprites.py + clean_sprites.py
                                                                  → 06_assembled_final.png
                                                                  → assets/sprites/...
```

**Key invariant:** Stage 6's output is shaped to match what the existing `process_*_ai_sprites.py` already expects (chroma-green background, target frame dimensions, palette-quantized). Downstream is unchanged.

**Re-runnability:** Each stage is an independent CLI reading from / writing to known folders. Any stage can be re-run in isolation without re-running earlier ones.

---

## Folder Layout & Debug Artifacts

Working directory per animation:

```
assets/ai_sources/img2vid/<character>/<animation>/
├── 01_source_sheet.png          ← Stage 2 input (raw AI output, untouched)
├── 02_split_frames/             ← Stage 3 output
│   ├── frame_01.png
│   ├── frame_02.png
│   └── frame_NN.png
├── 03_videos/                   ← Stage 4 drop zone (user places MP4s here)
│   ├── frame_01.mp4
│   ├── frame_02.mp4
│   └── frame_NN.mp4
├── 04_dumps/                    ← Stage 5 output (Kth-frame dumps, per video)
│   ├── frame_01/
│   │   ├── dump_0000.png
│   │   └── dump_NNNN.png
│   ├── frame_02/...
│   └── frame_NN/...
│       ← USER PRUNES IN PLACE: delete frames you don't want
├── 05_assembled_raw.png         ← Stage 6 output BEFORE process_*_ai_sprites.py
│                                  (bg removed, palette-quantized, packed sheet)
└── 06_assembled_final.png       ← After process_*_ai_sprites.py + clean_sprites.py
```

**Conventions:**

- **Numbered prefixes** = pipeline order obvious at a glance.
- **Stage N's output is Stage N+1's input** — no coupling, every stage re-runnable.
- **`04_dumps/` is deterministic** from `03_videos/` + K. If the user prunes too aggressively, `dump_video_frames.py --reset` re-creates it.
- **Pruning is "delete in place"** — fewer steps, `--reset` makes it safe.
- **`05_assembled_raw.png` is the debug checkpoint** — compared against `06_assembled_final.png` to localize bugs to assembly vs. process-script.
- **`assets/ai_sources/img2vid/` is gitignored.** Final committed artifact remains the game sprite in `assets/sprites/...`.

**Frame-to-sheet ordering rule:** the assemble script walks `04_dumps/frame_01/`, `frame_02/`, ... in numeric order, and within each folder reads PNGs in filename order. Total frame count = sum of surviving frames. Users can keep 3 frames from video 1, 1 from video 2, etc. — no rigid per-video quota.

---

## Per-Stage Tooling

### Stage 1 — Slim prompts (docs change, no code)
See "Prompt Restructuring" and "Documentation Updates" sections below.

### Stage 2 — AI sprite sheet (unchanged)
Manual: user pastes the (now slimmer) prompt into their image AI, downloads the sprite sheet, drops it as `01_source_sheet.png` in the work folder.

### Stage 3 — `tools/split_sprite_sheet.py` (NEW)
**Trivial.** Reads `01_source_sheet.png` + frame count from `tools/sprite_defs/characters/<character>.json` (existing source of truth — `animations[].frames`) → slices into N PNGs in `02_split_frames/`. PIL crop loop, ~30 lines.

**CLI:** `python tools/split_sprite_sheet.py <character> <animation>`
where `<animation>` matches the `source` field in the JSON minus `.png` (e.g. `sling_attack` for `sling_attack.png`).

### Stage 4 — Image→Video (manual today, API-ready)
User uploads each `02_split_frames/frame_NN.png` to Meta AI img2vid (free, web-only) with the prompt that generated the sprite sheet, downloads the resulting MP4, places it in `03_videos/` as `frame_NN.mp4`.

**Hybrid-ready:** if a paid API (Runway/Luma/Pika) is adopted later, only this stage's actor changes — the pipeline stays identical.

**Recommended:** keep videos short (~1-2 seconds) to minimize identity drift (see Risk R2).

### Stage 5 — `tools/dump_video_frames.py` (NEW)
Thin wrapper over ffmpeg. For each MP4 in `03_videos/`:

```
ffmpeg -i 03_videos/frame_NN.mp4 -vf "select=not(mod(n\,K))" -vsync vfr 04_dumps/frame_NN/dump_%04d.png
```

**CLI:**
- `python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]`
- `--k` (default 10) — extract every Kth frame.
- `--reset` — wipe and re-extract (safety net for over-pruning).

Validates that each MP4 in `03_videos/` corresponds to an existing split frame; errors loud on mismatched filenames.

### Stage 6 — `tools/assemble_sprite_sheet.py` (NEW, the substantive one)

Walks `04_dumps/frame_*/` in numeric order. For each video, computes a per-video scale/anchor reference from the matching `02_split_frames/frame_NN.png`:

```
Setup per video:
  • Open 02_split_frames/frame_NN.png
  • rembg + tight bbox crop
  • Record:
      source_bbox_height   (character body height in the AI's sheet)
      source_anchor_y      (where bbox bottom sat in the canvas)

Per surviving dump frame in 04_dumps/frame_NN/:
  1. rembg                              → RGBA, transparent background
                                          (--bg-mode {rembg,chroma,both}, default both)
  2. Tight crop to alpha bbox (+ small margin)
  3. Downsample so cropped height == source_bbox_height
                                          (two-pass: bilinear → NEAREST)
  4. Palette quantize → snap to 15-color palette
                                          (palette read from sprite_defs or prompt)
  5. Composite onto chroma-green canvas of character frame dims
     with cropped bottom at source_anchor_y
                                          (placement, not sizing — anchor lives only here)

After all frames processed:
  6. Pack horizontal → 05_assembled_raw.png
  7. Hand off to existing process_<character>_ai_sprites.py
     (and clean_sprites.py if that's how the project already chains)
     → 06_assembled_final.png + game asset
```

**Why scale/anchor come from the source split frame, not character JSON:**
The AI's own sprite sheet defines the correct character size and ground-line for this specific animation. Self-calibrating per animation means jumps, falls, attacks, idles all inherit the right anchor automatically. No per-animation override flag needed.

**CLI:** `python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}] [--warn-scale-pct 15]`

### Dependencies added
- `rembg` (background removal, MIT, runs locally) — ~150MB U2Net model on first run.
- `ffmpeg` (system binary) — documented in install steps.
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
- **Section 4 — Same Character, New Animation:** add the img2vid stage between AI sheet generation and final processing (~10 lines + the diagram from "Pipeline Overview" above).
- **Section 8 — Processing pipeline & JSON config format:** update the pipeline diagram with the new stages; add Quick Start commands for the three new CLIs; add a short "Debug artifacts" subsection naming `05_assembled_raw.png` as the checkpoint.
- **Section 9 — Asset directory structure:** document `assets/ai_sources/img2vid/<character>/<animation>/` and its `01_…` → `06_…` layout.

### `docs/asset_prompts/shared.md`
- **"Global style block" section:** note flip (reference-only, not prompt content).
- **Each per-asset prompt (1.1 through 18.x):** delete the `GLOBAL STYLE CONSTRAINTS` block. Keep IDENTITY LOCK, PALETTE, SPRITE CONSTRAINTS, BODY SIZE RULE, ANIMATION DESCRIPTION, RULES.

### `docs/asset_prompts/world1.md`
- **"Style chain (World 1)" section:** drop any "copied verbatim" claim.
- **Each per-asset prompt (3.x through 8.x):** delete GLOBAL STYLE CONSTRAINTS block. Same retain-list.

### `tools/sprite_defs/README.md`
- Replace the overview pipeline diagram with the new one (from "Pipeline Overview" section above).
- Add the three new CLIs to Quick Start with their flags.

### Files NOT touched
- `tools/sprite_defs/balchar_ai_prompt.md` — historical processing notes per CLAUDE.md.
- `tools/sprite_defs/characters/*.json` — processing configs unchanged.

---

## Risks & Open Issues

### R1 — Background removal eats thin features (sling cord, headband ribbon)
**Fail mode:** rembg/U2Net was trained on photos; thin pixel-art features can be silently classified as background.
**Mitigation:** `--bg-mode {rembg,chroma,both}` flag. `both` runs rembg AND a chroma-distance pass, keeping a pixel if EITHER mask says foreground. Default `both`.
**Fallback:** if `05_assembled_raw.png` shows missing cord, set `--bg-mode chroma` and re-run assemble. If still wrong, the source frame is bad — regenerate that video.

### R2 — Identity drift across the video
**Fail mode:** img2vid models morph face/proportions over time. By second 3 of a 4-second clip, the character may look subtly different.
**Mitigation:** documented best practice — generate **short** videos (~1-2 sec) and prune toward the early end of `04_dumps/`.
**Fallback:** if good motion only appears mid-clip but face has drifted, accept the cost and either pick the pose anyway or regenerate the video with a different seed.

### R3 — Scale/position drift within a single video
**Fail mode:** AI subtly zooms or pans through the clip. Source-frame anchoring corrects between-video drift but not within-video.
**Mitigation:** assemble script logs each frame's bbox dimensions vs. the source's. `--warn-scale-pct N` (default 15) emits a warning if any frame's bbox differs from source by more than N%.
**Fallback:** user sees warning, drops the drifty frames, re-runs assemble.

### R4 — Antialiasing/blur survives downsampling
**Fail mode:** video frames are continuous-tone; even with two-pass downsample + quantization, some frames are fuzzy at sprite scale.
**Mitigation:** the existing `clean_sprites.py` step (already in the pipeline) does outline enforcement and palette tightening — final cleanup pass.
**Fallback:** delete the offending dump, re-run assemble.

### R5 — Manual img2vid bottleneck
**Fail mode:** every animation = N manual web sessions = hours.
**Mitigation:** Stage 4 treats `03_videos/` as a drop zone. The actor doesn't matter to the pipeline — swap to API any time.
**Fallback:** adopt a paid API (Runway, Luma, Pika) if pain exceeds budget.

### R6 — Disk usage from dumps
**Fail mode:** 5 videos × ~100 frames × ~60 animations × ~1MB ≈ 30GB if everything's kept.
**Mitigation:** add `assets/ai_sources/img2vid/` to `.gitignore` (targeted — existing `assets/ai_sources/*` PNGs remain tracked). Work folder is scratch; only the final game sprite in `assets/sprites/...` is committed.
**Fallback:** future `tools/clean_sprite_work.py --older-than 7d` housekeeping (not in v1).

### Open issue — clean_sprites.py orchestration
`tools/sprite_defs/README.md` shows the existing flow as `process_character_sprites.py` then `clean_sprites.py`, with `tools/reprocess_all_sprites.sh` chaining them. The implementing developer should follow whichever chaining convention is already in place when wiring Stage 6 into `process_<character>_ai_sprites.py` — do not reinvent the final-cleanup chain.

---

## Out of Scope (Explicitly)

- Replacing existing `process_*_ai_sprites.py` or `clean_sprites.py` — they remain the final-cleanup step.
- An automated frame-quality scorer — pruning stays manual (Section 3 decision).
- A new per-character JSON schema — existing `tools/sprite_defs/characters/*.json` is reused.
- Moving prompts out of `docs/asset_prompts/*.md` — they stay there per the CLAUDE.md rule.
- Switching to a paid img2vid API — designed-for, not implemented in v1.

---

## Implementation Notes

Per CLAUDE.md, the PM (Na Francina) does not write code. Implementation is delegated to N'Andreu (engine programmer) in a feature branch with PR review by En Pau + En Miquel before user testing.

The work decomposes naturally into small PRs that can ship sequentially:

1. **Docs + prompt cleanup** — slim prompts, flip the "copied verbatim" note, update workflow docs. Zero code, immediate value (slimmer prompts can be used today with the *old* pipeline too).
2. **`split_sprite_sheet.py`** — smallest new tool, no new dependencies.
3. **`dump_video_frames.py`** — second-smallest, adds ffmpeg system dep.
4. **`assemble_sprite_sheet.py`** — the substantive new tool, adds rembg dep, wires into existing `process_*_ai_sprites.py`.
5. **End-to-end test** — pick one animation (suggested: Balchar idle or sling attack), run the full pipeline manually, verify `06_assembled_final.png` looks correct, screenshot the result for user approval.

A detailed implementation plan (task breakdown, test approach, file-by-file changes) will be produced by the writing-plans skill in a separate doc once this design is approved.
