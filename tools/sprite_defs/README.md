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
