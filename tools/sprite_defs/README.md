# tools/sprite_defs/

Processing configs only. **All AI prompts live in
[`docs/asset_prompts/`](../../docs/asset_prompts/)** (split per world:
`shared.md` for cross-world assets, `world1.md` and future per-world files
for world-specific assets). Workflow, methodology, processing pipeline,
JSON config format, and QC checklist live in
[`docs/asset_generation_guide.md`](../../docs/asset_generation_guide.md).

This folder contains:

- `characters/*.json` — per-character processing configs consumed by
  `tools/process_character_sprites.py`. See the guide for the config format
  and tuning workflow.
- `balchar_ai_prompt.md` — archival v1/v2/v3 historical processing notes
  for Balchar (kept for reference).

## Pipeline overview

```
Prereq    Master idle still (one-time per character, immutable)   [existing]
            → <source_dir>/idle.png  (img2vid seed + scale/anchor ref)

Stage 1   Prompt (asset_prompts/shared.md or world1.md)           [docs]
            ↓
Stage 2   Image→Video: master idle + animation prompt → ONE video [manual, hybrid-ready]
            ↓                                                     → 01_video.mp4
Stage 3   tools/dump_video_frames.py + manual prune               [NEW + user]
            ↓                                                     → 02_dumps/
Stage 4   tools/assemble_sprite_sheet.py                          [NEW, automated]
            ↓                                                     → 03_assembled_raw.png
          tools/process_character_sprites.py <character>.json     [canonical]
                                                                  → 04_assembled_final.png
                                                                  → assets/sprites/...
```

The seed is the character's immutable master idle still, reused for every
animation. Per-animation work folders live under
`assets/ai_sources/img2vid/<character>/<animation>/` and are gitignored.
Each stage is an independent CLI: any stage can be re-run in isolation
without re-running earlier ones.

## Quick start

```bash
conda activate safona

# Stage 3 — dump frames from the single animation video (every Kth frame)
# (02_dumps/ is always wiped first, so a re-run leaves no stale frames)
python tools/dump_video_frames.py <character> <animation> [--k 10]

# Stage 4 — assemble cleaned sprite sheet (chains into the canonical
# tools/process_character_sprites.py tools/sprite_defs/characters/<character>.json)
python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}]

# Legacy entry point (full batch, all characters)
bash tools/reprocess_all_sprites.sh
```

See [`docs/asset_generation_guide.md`](../../docs/asset_generation_guide.md)
for the full workflow, debug-artifact conventions, and JSON config format.
