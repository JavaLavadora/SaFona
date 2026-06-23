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
Stage 1   Prompt (asset_prompts/shared.md or world1.md)           [docs]
            ↓
Stage 2   AI sprite sheet generation                              [manual]
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

Work folders live under `assets/ai_sources/img2vid/<character>/<animation>/`
and are gitignored. Each stage is an independent CLI: any stage can be
re-run in isolation without re-running earlier ones.

## Quick start

```bash
conda activate safona

# Stage 3 — slice the AI sheet into per-frame PNGs
python tools/split_sprite_sheet.py <character> <animation>

# Stage 5 — dump frames from each video (every Kth frame)
python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]

# Stage 6 — assemble cleaned sprite sheet (chains into the existing
# process_<character>_ai_sprites.py)
python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}]

# Legacy entry point (full batch, all characters)
bash tools/reprocess_all_sprites.sh
```

See [`docs/asset_generation_guide.md`](../../docs/asset_generation_guide.md)
for the full workflow, debug-artifact conventions, and JSON config format.
