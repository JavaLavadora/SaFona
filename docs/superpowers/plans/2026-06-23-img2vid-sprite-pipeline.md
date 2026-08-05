# Img2Vid Sprite Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current "AI image → postprocess" sprite pipeline with one that inserts an image-to-video stage, samples frames from the video, then assembles a palette-locked sprite sheet. Drop unused style noise from prompts. Persist every intermediate artifact for debuggability.

**Architecture:** Two new single-purpose CLIs under `tools/` chained via well-known folder paths under `assets/ai_sources/img2vid/<character>/<animation>/`. Each stage reads from `0N_*` and writes to `0(N+1)_*`. The img2vid **seed** is the character's immutable master idle still (`<source_dir>/idle.png`), fed to img2vid with each animation's prompt to produce one video per animation; the same still is the scale/anchor reference during assembly. The canonical `tools/process_character_sprites.py` (JSON-driven) and `tools/clean_sprites.py` stay as the final cleanup chain — Stage 4 hands off to them unchanged.

**Tech Stack:** Python 3, Pillow, numpy, rembg (new dep), ffmpeg (provided by the `dev` extra via `imageio-ffmpeg`; `pip install -e ".[dev]"` — system ffmpeg is an optional fallback), pytest. Project uses the `safona` conda env.

**Spec:** `docs/proposals/2026-06-23-img2vid-sprite-pipeline.md`

## Global Constraints

- **No master commits.** Every Task ships as its own feature branch + PR. PR titles prefixed `[img2vid-Tx]`. Reviewers: En Pau + En Miquel.
- **No PR merge without explicit Toni approval.** Reviewer approval alone is NOT sufficient (CLAUDE.md Rule #1).
- **Worktree isolation.** Work in a git worktree per CLAUDE.md memory `feedback_worktree_isolation.md` — never edit the main checkout.
- **Conda env.** `conda activate safona` before any pip/pytest invocation.
- **Docstrings:** Google style.
- **Tests:** small and concise (CLAUDE.md). Use `tests/test_clean_sprites.py` as the conventions reference (sys.path manipulation, fixtures via tmp_path).
- **Final game asset path unchanged.** `assets/sprites/<character>/<animation>.png` remains the shipped artifact. Stage 4 chains to existing process scripts which write there.
- **No new doc files.** All docs live in the existing locations per CLAUDE.md: `docs/asset_generation_guide.md`, `docs/asset_prompts/shared.md`, `docs/asset_prompts/world1.md`, `tools/sprite_defs/README.md`.

## File Structure (full picture across all tasks)

```
Created:
  tools/dump_video_frames.py
  tools/assemble_sprite_sheet.py
  tests/test_dump_video_frames.py
  tests/test_assemble_sprite_sheet.py

Modified:
  docs/asset_generation_guide.md       (Section 0, Section 4, Section 8, Section 9, top "How to add a new asset")
  docs/asset_prompts/shared.md         (Global style block section + every per-asset prompt)
  docs/asset_prompts/world1.md         (Style chain section + every per-asset prompt)
  tools/sprite_defs/README.md          (pipeline diagram + Quick Start)
  .gitignore                           (add assets/ai_sources/img2vid/**)
  pyproject.toml                       (add rembg dependency)
```

Each Task touches a disjoint slice of these files, so they can land as independent PRs in any order (except Task 4 depends on 1-3).

---

### Task 1: Docs & prompt cleanup

**Files:**
- Modify: `docs/asset_generation_guide.md` (Sections 0, 4, 8, 9 and top "How to add a new asset")
- Modify: `docs/asset_prompts/shared.md` (Global style block section + drop the GLOBAL STYLE CONSTRAINTS block from every per-asset prompt, sections 1.x through 18.x)
- Modify: `docs/asset_prompts/world1.md` (Style chain section + drop GLOBAL STYLE CONSTRAINTS from every per-asset prompt, sections 3.x through 8.x)
- Modify: `tools/sprite_defs/README.md` (pipeline diagram + Quick Start additions)
- Modify: `.gitignore` (add `assets/ai_sources/img2vid/**`)

**Interfaces:**
- Consumes: nothing
- Produces: documented workflow that Tasks 2-4 will implement. The new CLIs referenced in the docs do not exist yet at the end of this Task; the doc edits forward-reference them by exact name.

**Why this Task can land first:** the prompt slim-down improves the *existing* pipeline too — slimmer prompts work today with the old scripts. Zero code risk. Ships value immediately.

- [ ] **Step 1: Create worktree and branch**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t1 -b feat/img2vid-t1-docs master
cd ../safona-img2vid-t1
```

- [ ] **Step 2: Update `docs/asset_generation_guide.md` Section 0 note**

Replace the note in Section 0 (around the "GLOBAL STYLE CONSTRAINTS" block) that currently states this block is "copied verbatim into every prompt" with:

```
This block is reference for humans only. It is **not** copied into prompts —
AI image generators do not respect abstract style directives at this level,
and including them dilutes the directives they *do* respect (palette,
identity lock, reference image, frame layout). Style consistency comes from
the palette block, the identity lock, and the reference image.
```

- [ ] **Step 3: Update `docs/asset_generation_guide.md` "How to add a new asset" (top section)**

Insert numbered steps for the img2vid workflow between "prompt authored" and "run processing scripts". The img2vid seed is the character's immutable master idle still at `<source_dir>/idle.png` (from Section 2), reused for every animation. New step list:

```
1. Upload the master idle still (<source_dir>/idle.png) to Meta AI img2vid
   (or future API) together with this animation's prompt. img2vid creates
   the motion from that single seed. Save the resulting MP4 as
   assets/ai_sources/img2vid/<character>/<animation>/01_video.mp4.
   (The prompt itself was already written into docs/asset_prompts/ in the
   outer "Add the prompt section" step above — don't duplicate that here.)
2. Run: python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]
   → produces 02_dumps/dump_*.png
3. Browse 02_dumps/; delete frames you don't want (keep the ones that best
   trace the animation cycle, in filename order).
4. Run: python tools/assemble_sprite_sheet.py <character> <animation>
   → produces 03_assembled_raw.png (debug checkpoint) AND chains into
   tools/process_character_sprites.py tools/sprite_defs/characters/<character>.json,
   which produces 04_assembled_final.png and the final game asset under
   assets/sprites/<character>/.
```

- [ ] **Step 4: Update `docs/asset_generation_guide.md` Section 4 ("Same Character, New Animation")**

Add a subsection "Img2Vid stage" between the AI-generation and processing parts of Section 4. Body:

```
The character's immutable master idle still (<source_dir>/idle.png) is fed
through an image-to-video AI *together with each animation's prompt* to
produce ONE continuous-motion video per animation. img2vid creates the
in-between motion from the single idle seed — there is no per-animation
sprite sheet to generate or split. Frames are dumped from the video,
pruned, and assembled into the final sprite sheet. See Section 8 for the
CLI commands. process_character_sprites.py consumes the assembled sheet the
same way it consumes any AI source.
```

- [ ] **Step 5: Update `docs/asset_generation_guide.md` Section 8 (Processing pipeline)**

Replace the existing pipeline diagram with the new one (copy from the spec's "Pipeline Overview" section, the Prereq master-idle line and `Stage 1` through the `tools/process_character_sprites.py <character>.json` chain).

Add Quick Start commands directly under the diagram:

```bash
# Stage 3 — dump frames from the single animation video (every Kth frame)
python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]

# Stage 4 — assemble cleaned sprite sheet
python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}]
```

Append a "Debug artifacts" subsection naming `03_assembled_raw.png` as the checkpoint to inspect when the final asset looks wrong.

- [ ] **Step 6: Update `docs/asset_generation_guide.md` Section 9 (Asset directory structure)**

Append the img2vid working layout:

```
assets/ai_sources/img2vid/<character>/<animation>/
├── 01_video.mp4              # Stage 2 output (user drops the img2vid MP4 here)
├── 02_dumps/                 # Stage 3 output (user prunes in place)
├── 03_assembled_raw.png      # Stage 4 output (debug checkpoint)
└── 04_assembled_final.png    # After tools/process_character_sprites.py <char>.json
```

Note the img2vid seed / scale reference is NOT in this subtree — it is the
character's master idle still at `<source_dir>/idle.png`, reused for every
animation. This whole `img2vid/` subtree is gitignored.

- [ ] **Step 7: Update `docs/asset_prompts/shared.md` "Global style block" section**

Apply the same note flip as `docs/asset_generation_guide.md` Section 0 (Step 2): the block is reference-only, not copied into prompts.

- [ ] **Step 8: Drop GLOBAL STYLE CONSTRAINTS from every prompt in `shared.md`**

For each section 1.1 through 18.x in `shared.md`, locate the prompt body (the fenced code block following the `## X.Y Title` header). The per-world consolidation has already collapsed the full GSC block to a single-line reference `GLOBAL STYLE CONSTRAINTS APPLY.` per prompt — this task deletes that one-line reference from every prompt (~40+ prompts).

Keep ALL other prompt content: identity lock, reference attachment, palette block, sprite constraints, body size rule, animation description, rules tail.

Verification after each prompt: prompt still parses as a single fenced code block; identity lock + palette + animation description are intact.

- [ ] **Step 9: Update `docs/asset_prompts/world1.md` style chain section**

Same note flip in the "Style chain (World 1)" section.

- [ ] **Step 10: Drop GLOBAL STYLE CONSTRAINTS from every prompt in `world1.md`**

Apply the same removal as Step 8 to every section 3.x through 8.x.

- [ ] **Step 11: Update `tools/sprite_defs/README.md`**

Replace the Overview pipeline diagram with the new one from the spec. Append the two new CLIs to the Quick Start section (same commands as Step 5).

- [ ] **Step 12: Update `.gitignore`**

Append:

```
# img2vid scratch working folders — only final assets/sprites are committed
assets/ai_sources/img2vid/**
```

- [ ] **Step 13: Verify with git diff**

```bash
git diff --stat
```

Expected: 5 files modified, line deletions roughly proportional to the prompt count (~40+ prompts × 1 reference line = ~40-70 deletions on prompt files, plus modest additions on `docs/asset_generation_guide.md` and `tools/sprite_defs/README.md`). The actual round-1 diff hit ~66 deletions on the prompt files, which matches the single-line-reference model.

- [ ] **Step 14: Commit and open PR**

```bash
git add docs/asset_generation_guide.md docs/asset_prompts/shared.md \
        docs/asset_prompts/world1.md tools/sprite_defs/README.md .gitignore
git commit -m "$(cat <<'EOF'
docs(img2vid): drop GLOBAL STYLE CONSTRAINTS block, document new pipeline

Slims every prompt by removing the global style block — AI generators
do not respect abstract style directives at this level. Documents the
new img2vid pipeline workflow, CLIs, and folder layout. Ignores the
img2vid scratch directory.

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t1-docs
gh pr create --title "[img2vid-T1] Docs & prompt cleanup" --body "..."
```

- [ ] **Step 15: Clean up worktree after PR pushed**

```bash
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t1
```

---

### Dropped: `tools/split_sprite_sheet.py` (was Task 2)

**DROPPED — the corrected pipeline (master idle -> one video per animation)
has no sheet-split stage.** The single seed is the master idle still, and
img2vid produces one continuous-motion video per animation; there is no
per-animation sprite sheet to slice, so `tools/split_sprite_sheet.py` and
`tests/test_split_sprite_sheet.py` are not created.

---

### Task 2: `tools/dump_video_frames.py`

**Files:**
- Create: `tools/dump_video_frames.py`
- Create: `tests/test_dump_video_frames.py`

**Interfaces:**
- Consumes: the single `01_video.mp4` the user dropped in the animation work folder (Stage 2 output). There is no split-frame layout to validate against — img2vid produced one video for the whole animation.
- Produces:
  - CLI `python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]`
  - Reads: `assets/ai_sources/img2vid/<character>/<animation>/01_video.mp4`.
  - Writes: `02_dumps/dump_0000.png` ... by invoking ffmpeg with `select=not(mod(n\\,K))`.
  - `--reset` wipes the `02_dumps/` folder before extracting.

- [ ] **Step 1: Create worktree and branch**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t2 -b feat/img2vid-t2-dump master
cd ../safona-img2vid-t2
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_dump_video_frames.py`:

```python
"""Tests for tools/dump_video_frames.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.dump_video_frames import (
    build_ffmpeg_command,
    dump_video,
)


def test_build_ffmpeg_command_uses_select_modulo(tmp_path: Path):
    video = tmp_path / "01_video.mp4"
    out_dir = tmp_path / "02_dumps"
    cmd = build_ffmpeg_command(video, out_dir, k=10)

    assert cmd[0] == "ffmpeg"
    assert "-i" in cmd
    assert str(video) in cmd
    select_arg = next(arg for arg in cmd if "select=" in arg)
    assert "not(mod(n\\,10))" in select_arg
    # Stage 3 must use -fps_mode vfr (the post-ffmpeg-5.1 replacement for
    # -vsync vfr). The deprecated flag would warn on modern ffmpeg.
    assert "-fps_mode" in cmd
    assert "vfr" in cmd
    assert "-vsync" not in cmd
    assert str(out_dir / "dump_%04d.png") in cmd


def test_dump_video_invokes_ffmpeg_and_resets(tmp_path: Path):
    video = tmp_path / "01_video.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "02_dumps"
    out_dir.mkdir(parents=True)
    (out_dir / "stale.png").write_bytes(b"")  # leftover from previous run

    with patch("tools.dump_video_frames.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        dump_video(video, out_dir, k=10, reset=True)

    assert not (out_dir / "stale.png").exists()
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"


def test_dump_video_errors_when_video_missing(tmp_path: Path):
    video = tmp_path / "01_video.mp4"  # does not exist
    out_dir = tmp_path / "02_dumps"

    with pytest.raises(FileNotFoundError, match="01_video.mp4"):
        dump_video(video, out_dir, k=10, reset=False)
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
pytest tests/test_dump_video_frames.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 4: Implement `tools/dump_video_frames.py`**

```python
"""Dump frames from the img2vid animation video for visual pruning.

Stage 3 of the img2vid sprite pipeline. Runs ffmpeg to extract every Kth
frame from the single 01_video.mp4 (produced by feeding the master idle to
img2vid with the animation's prompt) into the 02_dumps/ folder. The user
then manually deletes dumps they don't want.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"


def build_ffmpeg_command(video: Path, out_dir: Path, k: int) -> list[str]:
    """Return the ffmpeg argv that extracts every Kth frame.

    Args:
        video: Path to the source MP4 (01_video.mp4).
        out_dir: Destination directory (must exist; caller creates).
        k: Extract every Kth frame.

    Returns:
        argv list ready for subprocess.run.
    """
    return [
        "ffmpeg",
        "-loglevel", "error",
        "-i", str(video),
        "-vf", f"select=not(mod(n\\,{k}))",
        "-fps_mode", "vfr",  # -vsync vfr was deprecated in ffmpeg 5.1
        str(out_dir / "dump_%04d.png"),
    ]


def dump_video(video: Path, out_dir: Path, k: int, reset: bool) -> int:
    """Extract every Kth frame from the single animation video.

    Args:
        video: Source MP4 path (01_video.mp4).
        out_dir: 02_dumps/ folder.
        k: Extract every Kth frame.
        reset: If True, wipe out_dir contents first.

    Returns:
        Number of dump_*.png files in out_dir after extraction.

    Raises:
        FileNotFoundError: If the source video does not exist.
    """
    if not video.exists():
        raise FileNotFoundError(
            f"expected the img2vid output at {video} (01_video.mp4); drop the "
            f"downloaded MP4 there before running Stage 3."
        )
    if reset and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_ffmpeg_command(video, out_dir, k)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {video}")

    return len(list(out_dir.glob("dump_*.png")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character")
    parser.add_argument("animation")
    parser.add_argument("--k", type=int, default=10,
                        help="Extract every Kth frame (default: 10)")
    parser.add_argument("--reset", action="store_true",
                        help="Wipe the 02_dumps/ folder before extracting")
    args = parser.parse_args()

    work_dir = WORK_ROOT / args.character / args.animation
    video = work_dir / "01_video.mp4"
    dump_dir = work_dir / "02_dumps"

    n = dump_video(video, dump_dir, args.k, args.reset)
    print(f"{video.name}: {n} frames -> {dump_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
pytest tests/test_dump_video_frames.py -v
```

Expected: 3 tests pass.

- [ ] **Step 6: Commit, push, open PR, clean up worktree**

```bash
git add tools/dump_video_frames.py tests/test_dump_video_frames.py
git commit -m "$(cat <<'EOF'
feat(img2vid): add tools/dump_video_frames.py (Stage 3)

Extracts every Kth frame from the single 01_video.mp4 into 02_dumps/ for
manual pruning. Supports --reset to safely re-extract after over-pruning.

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t2-dump
gh pr create --title "[img2vid-T2] tools/dump_video_frames.py (Stage 3)" --body "..."
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t2
```

---

### Task 3: `tools/assemble_sprite_sheet.py`

**Files:**
- Create: `tools/assemble_sprite_sheet.py`
- Create: `tests/test_assemble_sprite_sheet.py`
- Modify: `pyproject.toml` (add `rembg`, `onnxruntime`, and `scipy` dependencies)

**Interfaces:**
- Consumes: the character's master idle still `<source_dir>/idle.png` (scale/anchor reference, computed once) and Task 2's `02_dumps/dump_*.png` (flat set of pruned frames to process).
- Produces:
  - CLI `python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}] [--warn-scale-pct 15]`
  - Writes: `03_assembled_raw.png` (debug checkpoint) AND `<source_dir>/<animation>.png` (where the canonical script expects its input), then invokes `tools/process_character_sprites.py tools/sprite_defs/characters/<character>.json` as a subprocess to produce `04_assembled_final.png` and the final asset under the animation's *resolved output filename* — `entry.get("output", entry["source"])` from the character JSON, the same lookup `process_character_sprites.py` performs internally. This is **not** always `<output_dir>/<animation>.png`: balchar.json's `sling_attack` entry sets `"output": "sling.png"`, so the real file lands at `<output_dir>/sling.png`.

- [ ] **Step 1: Create worktree, branch, install rembg + scipy**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t3 -b feat/img2vid-t3-assemble master
cd ../safona-img2vid-t3
conda activate safona
pip install "rembg>=2.0.50,<3.0" "onnxruntime>=1.16,<2.0" "scipy>=1.11,<2.0"
```

- [ ] **Step 2: Add rembg + onnxruntime + scipy to `pyproject.toml`**

Open `pyproject.toml`, find the `dependencies` (or equivalent) list, add:

```
"rembg>=2.0.50,<3.0",     # U2Net by default — model is downloaded on first run
"onnxruntime>=1.16,<2.0", # rembg requires this for the model
"scipy>=1.11,<2.0",       # remove_background's connected-component rescue
                          # (--bg-mode both combinator) imports scipy.ndimage
```

Pin them: a future rembg major could swap the default model and silently
change Stage 4 output (R7). `scipy` is required because `remove_background`
does `from scipy import ndimage` for the rembg-primary + chroma-rescue
combinator — without this entry, this task hits
`ModuleNotFoundError: scipy` on a clean checkout. Run `pip install -e .` to
confirm install works from the file.

- [ ] **Step 3: Write the failing tests**

Create `tests/test_assemble_sprite_sheet.py`:

```python
"""Tests for tools/assemble_sprite_sheet.py."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.assemble_sprite_sheet import (
    chroma_key_mask,
    composite_onto_canvas,
    compute_source_anchor,
    downsample_to_height,
    pack_horizontal,
    palette_quantize,
    resolve_output_filename,
)


def _solid_rgba(w: int, h: int, color: tuple[int, int, int, int]) -> Image.Image:
    return Image.new("RGBA", (w, h), color)


def test_chroma_key_mask_marks_green_as_background():
    img = _solid_rgba(4, 4, (0, 255, 0, 255))
    # Put one non-green pixel
    img.putpixel((1, 1), (200, 100, 50, 255))

    mask = chroma_key_mask(img)
    assert mask.shape == (4, 4)
    assert mask[1, 1] == 1  # foreground
    assert mask[0, 0] == 0  # background (green)


def test_downsample_to_height_preserves_aspect():
    img = Image.new("RGBA", (100, 200), (255, 0, 0, 255))
    out = downsample_to_height(img, target_height=40)
    assert out.height == 40
    # 100/200 = 0.5 → width should be 20
    assert out.width == 20


def test_palette_quantize_snaps_to_nearest_color():
    # palette is (N, 3) np.ndarray to match parse_gpl's return type
    palette = np.array([(0, 0, 0), (255, 255, 255), (255, 0, 0)])
    img = Image.new("RGBA", (2, 1))
    img.putpixel((0, 0), (10, 10, 10, 255))     # nearest to black
    img.putpixel((1, 0), (250, 5, 5, 255))      # nearest to red

    out = palette_quantize(img, palette)
    assert out.getpixel((0, 0))[:3] == (0, 0, 0)
    assert out.getpixel((1, 0))[:3] == (255, 0, 0)


def test_compute_source_anchor_returns_bbox_height_and_y():
    """A 32x48 frame with a 30-px-tall body at the bottom."""
    img = Image.new("RGBA", (32, 48), (0, 255, 0, 255))
    for y in range(18, 48):
        for x in range(10, 22):
            img.putpixel((x, y), (200, 100, 50, 255))

    height, anchor_y = compute_source_anchor(img)
    assert height == 30
    assert anchor_y == 47  # last row that contained foreground


def test_composite_onto_canvas_anchors_at_y():
    canvas_w, canvas_h = 32, 48
    char = Image.new("RGBA", (12, 30), (200, 100, 50, 255))

    out = composite_onto_canvas(char, canvas_w, canvas_h, anchor_y=47)
    # Bottom row should contain the character color
    assert out.getpixel((canvas_w // 2, 47))[:3] == (200, 100, 50)
    # Top row should still be chroma green
    assert out.getpixel((canvas_w // 2, 0))[:3] == (0, 255, 0)


def test_pack_horizontal_concatenates_in_order(tmp_path: Path):
    frames = [
        Image.new("RGBA", (10, 20), (255, 0, 0, 255)),
        Image.new("RGBA", (10, 20), (0, 255, 0, 255)),
        Image.new("RGBA", (10, 20), (0, 0, 255, 255)),
    ]
    out = pack_horizontal(frames)
    assert out.size == (30, 20)
    assert out.getpixel((5, 10))[:3] == (255, 0, 0)
    assert out.getpixel((15, 10))[:3] == (0, 255, 0)
    assert out.getpixel((25, 10))[:3] == (0, 0, 255)


def test_composite_emits_only_chroma_or_palette_colors():
    """Postcondition: 03_assembled_raw.png must contain ONLY exact (0,255,0)
    chroma or exact palette colors — no semi-transparent edges, no blended
    pixels. Downstream chroma-key in process_character_sprites.py relies on
    this invariant (it only removes pixels where G-R > 40 and G-B > 40, so
    anti-aliased green edges would bake green-tinted pixels into the asset).
    """
    palette = [(200, 100, 50), (100, 50, 25)]
    char = Image.new("RGBA", (4, 6), (200, 100, 50, 255))
    # Introduce a semi-transparent edge to force the threshold path:
    for y in range(6):
        char.putpixel((0, y), (200, 100, 50, 64))  # alpha 64 < 128 → chroma

    out = composite_onto_canvas(char, 8, 8, anchor_y=7)
    arr = np.array(out)
    allowed = {(0, 255, 0, 255)} | {(*c, 255) for c in palette}
    seen = {tuple(p) for p in arr.reshape(-1, 4)}
    assert seen.issubset(allowed), (
        f"composite leaked non-allowed colors: {seen - allowed}"
    )


def test_resolve_output_filename_uses_output_field_when_present():
    """balchar.json's sling_attack entry sets "output": "sling.png" — the
    expected output filename must come from that field, not from
    f"{animation}.png", or chain_process_script raises FileNotFoundError on
    every successful run.
    """
    config = {
        "animations": [
            {"source": "idle.png", "frames": 4},
            {"source": "sling_attack.png", "output": "sling.png", "frames": 3},
        ]
    }
    assert resolve_output_filename(config, "sling_attack") == "sling.png"


def test_resolve_output_filename_falls_back_to_source():
    config = {"animations": [{"source": "idle.png", "frames": 4}]}
    assert resolve_output_filename(config, "idle") == "idle.png"


def test_resolve_output_filename_errors_on_unknown_animation():
    config = {"animations": [{"source": "idle.png", "frames": 4}]}
    with pytest.raises(KeyError, match="unknown"):
        resolve_output_filename(config, "unknown")
```

- [ ] **Step 4: Run tests to confirm they fail**

```bash
pytest tests/test_assemble_sprite_sheet.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 5: Implement `tools/assemble_sprite_sheet.py`**

```python
"""Assemble a clean sprite sheet from img2vid dump frames.

Stage 4 of the img2vid sprite pipeline. For each surviving dump frame in
02_dumps/, removes the background, scales the character to the master idle's
body height, palette-quantizes against the character's .gpl palette, and
composites onto a chroma-green canvas the SIZE OF THE MASTER IDLE (i.e. at
source resolution, like the existing AI sources — not the final game frame
size), anchored at the master idle's baseline. Packs the processed frames
into 03_assembled_raw.png, copies the same sheet into
<source_dir>/<animation>.png, then invokes the canonical
tools/process_character_sprites.py <character>.json as a subprocess for
final cleanup.

Emitting a source-resolution sheet lets process_character_sprites.py own the
single downscale to frame_width×frame_height, exactly as it does for any
other AI source. Scale and anchor come from the character's immutable master
idle still (<source_dir>/idle.png) — the same seed every img2vid video was
generated from — NOT from per-animation config. Anchoring every animation to
the one master idle keeps scale and baseline mutually consistent across the
whole character; per-animation vertical placement, scale_pct, and the final
game-frame downscale are all applied downstream by
process_character_sprites.py.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage  # connected-component rescue for --bg-mode both

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"
CHAR_DEF_ROOT = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"
PALETTE_ROOT = PROJECT_ROOT / "assets" / "palettes"

CHROMA_GREEN = (0, 255, 0)
CHROMA_GREEN_RGBA = (0, 255, 0, 255)
ALPHA_THRESHOLD = 128  # postcondition: alpha < 128 → snap to chroma


def chroma_key_mask(img: Image.Image, threshold: int = 40) -> np.ndarray:
    """Return a 0/1 mask where 1 == foreground (non-green).

    Uses the same heuristic as the existing chroma-key pipeline:
    a pixel is background when g - r > threshold and g - b > threshold.
    """
    arr = np.array(img.convert("RGB"))
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    bg = (g - r > threshold) & (g - b > threshold) & (g > 80)
    return (~bg).astype(np.uint8)


def rembg_mask(img: Image.Image) -> np.ndarray:
    """Return a 0/1 foreground mask via rembg/U2Net."""
    from rembg import remove

    cut = remove(img)
    if cut.mode != "RGBA":
        cut = cut.convert("RGBA")
    alpha = np.array(cut)[..., 3]
    return (alpha > 16).astype(np.uint8)


def apply_mask(img: Image.Image, mask: np.ndarray) -> Image.Image:
    """Return an RGBA image where mask==0 pixels are fully transparent."""
    rgba = np.array(img.convert("RGBA"))
    rgba[..., 3] = mask * 255
    return Image.fromarray(rgba, mode="RGBA")


def remove_background(img: Image.Image, mode: str) -> Image.Image:
    """Remove the background using the requested strategy.

    For "both", uses rembg as the primary mask and rescues thin chroma-mask
    components (e.g. sling cord, headband ribbon) that are 4-connected to the
    rembg foreground. Chroma components NOT touching the rembg foreground —
    e.g. anti-aliased green-edge halos — are discarded. This defends R1 (thin
    features) without amplifying R4 (AA edges).
    """
    if mode == "chroma":
        mask = chroma_key_mask(img)
    elif mode == "rembg":
        mask = rembg_mask(img)
    elif mode == "both":
        rembg = rembg_mask(img)
        chroma = chroma_key_mask(img)
        # Components present in chroma but absent from rembg:
        missing = chroma & ~rembg
        labels, n = ndimage.label(missing, structure=np.ones((3, 3)))
        # Dilate rembg by 1px so "touching" includes diagonal neighbours.
        rembg_neighborhood = ndimage.binary_dilation(rembg.astype(bool))
        keep = np.zeros_like(rembg, dtype=bool)
        for label_id in range(1, n + 1):
            region = labels == label_id
            if (region & rembg_neighborhood).any():
                keep |= region
        mask = (rembg.astype(bool) | keep).astype(np.uint8)
    else:
        raise ValueError(f"unknown bg-mode: {mode}")
    return apply_mask(img, mask)


def tight_crop(img: Image.Image, padding: int = 0) -> Image.Image:
    """Crop to the bounding box of non-transparent pixels (+ padding)."""
    bbox = img.getbbox()
    if bbox is None:
        return img
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)
    return img.crop((left, top, right, bottom))


def compute_source_anchor(
    source_frame: Image.Image, source_path: Path | str = "<unknown>"
) -> tuple[int, int]:
    """From the master idle still, derive (bbox_height, anchor_y).

    bbox_height: height of the character body in the master idle.
    anchor_y:   y-coordinate of the bbox bottom in the master idle canvas.
                Used to place every dump frame at the same baseline.

    Uses the chroma mask (NOT rembg) for the anchor: the master idle is a
    clean, single, immutable still on a solid green background, which is
    exactly where chroma is the reliable signal — so the anchor never depends
    on loading the U2Net model. The bbox-height sanity clamp below still
    catches a masking failure (e.g. a chroma artifact eating most of the
    character) and defends R3 at the anchor stage.

    Raises:
        ValueError: if the master idle has no foreground after masking, or
                    if the bbox height is below 50% of canvas height (signals
                    the chroma key ate most of the character).
    """
    masked = remove_background(source_frame, "chroma")
    bbox = masked.getbbox()
    if bbox is None:
        raise ValueError(
            f"master idle at {source_path} has no foreground after "
            f"chroma-key; manually inspect and re-generate if needed."
        )
    left, top, right, bottom = bbox
    bbox_h = bottom - top
    if bbox_h < source_frame.height * 0.5:
        raise ValueError(
            f"master idle at {source_path} has no foreground after "
            f"chroma-key; manually inspect and re-generate if needed. "
            f"(bbox height {bbox_h}px is < 50% of canvas height "
            f"{source_frame.height}px — likely a masking failure.)"
        )
    return (bbox_h, bottom - 1)


def downsample_to_height(img: Image.Image, target_height: int) -> Image.Image:
    """Downsample preserving aspect; bilinear pre-pass then NEAREST snap."""
    if img.height == target_height:
        return img
    ratio = target_height / img.height
    target_width = max(1, int(round(img.width * ratio)))
    pre = img.resize((target_width * 2, target_height * 2), Image.BILINEAR)
    return pre.resize((target_width, target_height), Image.NEAREST)


def palette_quantize(img: Image.Image, palette: np.ndarray) -> Image.Image:
    """Snap each opaque pixel to its nearest palette color.

    `palette` is an (N, 3) array of RGB triplets, matching the shape returned
    by tools.clean_sprites.parse_gpl.
    """
    rgba = np.array(img.convert("RGBA"))
    rgb = rgba[..., :3].astype(int)
    alpha = rgba[..., 3]

    pal = np.asarray(palette, dtype=int)
    # Distance from every pixel to every palette color
    diffs = rgb[..., None, :] - pal[None, None, :, :]
    dists = (diffs * diffs).sum(axis=-1)
    nearest = np.argmin(dists, axis=-1)
    quantized = pal[nearest]

    out = np.zeros_like(rgba)
    out[..., :3] = quantized
    out[..., 3] = alpha
    return Image.fromarray(out.astype(np.uint8), mode="RGBA")


def composite_onto_canvas(
    char: Image.Image, canvas_w: int, canvas_h: int, anchor_y: int
) -> Image.Image:
    """Paste the character onto a chroma-green canvas with its bottom at anchor_y.

    POSTCONDITION: every output pixel is either exactly (0, 255, 0, 255)
    chroma OR a fully-opaque palette color. No semi-transparent edges, no
    blended green-tinted boundary pixels. The downstream chroma-key in
    process_character_sprites.py only removes pixels where (G-R > 40) and
    (G-B > 40), so anti-aliased green edges would bake green-tinted pixels
    into the final asset if this postcondition were relaxed.

    The threshold is applied to the character's OWN alpha BEFORE the paste:
      alpha >= 128 → keep the palette-quantized RGB, paste at full opacity.
      alpha <  128 → drop the pixel, so the chroma canvas shows through.
    Thresholding after the paste would be too late — a soft edge would have
    already blended its palette RGB with the green canvas into an off-palette
    green-tinted colour that then survives the threshold.
    """
    # Harden the character's own alpha to a binary 0/255 mask first, so no
    # soft edge ever blends with the green canvas.
    char = char.convert("RGBA")
    arr = np.array(char)
    arr[..., 3] = np.where(arr[..., 3] >= ALPHA_THRESHOLD, 255, 0).astype(np.uint8)
    hard_char = Image.fromarray(arr, mode="RGBA")

    canvas = Image.new("RGBA", (canvas_w, canvas_h), CHROMA_GREEN_RGBA)
    paste_x = (canvas_w - hard_char.width) // 2
    paste_y = anchor_y - hard_char.height + 1
    # Use the hardened alpha as the paste mask: 255 → char RGB, 0 → chroma.
    canvas.paste(hard_char, (paste_x, paste_y), hard_char)
    return canvas


def pack_horizontal(frames: list[Image.Image]) -> Image.Image:
    """Concatenate frames into a single horizontal sheet."""
    if not frames:
        raise ValueError("no frames to pack")
    h = max(f.height for f in frames)
    total_w = sum(f.width for f in frames)
    sheet = Image.new("RGBA", (total_w, h), CHROMA_GREEN_RGBA)
    x = 0
    for f in frames:
        sheet.paste(f, (x, h - f.height), f if f.mode == "RGBA" else None)
        x += f.width
    return sheet


def load_palette_for(character: str) -> np.ndarray:
    """Load the character's palette from assets/palettes/<character>.gpl.

    Uses the same parser as tools/clean_sprites.py so Stage 4 and the final
    cleanup quantize against identical color sets (idempotent). Returns an
    (N, 3) np.ndarray of RGB triplets.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from tools.clean_sprites import parse_gpl  # single source of truth
    palette_path = PALETTE_ROOT / f"{character}.gpl"
    return parse_gpl(palette_path)


def load_character_config(char_json_path: Path) -> dict:
    return json.loads(char_json_path.read_text())


def assemble(
    character: str,
    animation: str,
    bg_mode: str,
    warn_scale_pct: float,
) -> tuple[Path, Path]:
    """Run the full Stage 4 pipeline.

    Emits a SOURCE-RESOLUTION sheet (each frame sized to the master idle's
    own canvas, like the existing 1536×1024-style AI sources), NOT the final
    game frame size. process_character_sprites.py performs the sole downscale
    to frame_width×frame_height, exactly as it does for any other AI source —
    so Stage 4 must not pre-shrink frames to the game frame size or the
    character would be clipped off-canvas and then downscaled twice.

    Returns:
        (raw_checkpoint, source_dir_copy) — the debug checkpoint
        03_assembled_raw.png AND the same sheet copied into
        <source_dir>/<animation>.png (where the canonical processing script
        looks for its input).

    Raises:
        ValueError: if animation == "idle" — the idle animation IS the master
            idle seed (<source_dir>/idle.png); it is authored once and is not
            regenerated through img2vid, so Stage 4 must never overwrite it.
    """
    if animation == "idle":
        raise ValueError(
            "the 'idle' animation is the immutable master idle seed "
            "(<source_dir>/idle.png); it is not generated through the img2vid "
            "pipeline. Run the pipeline for the other animations only."
        )

    work_dir = WORK_ROOT / character / animation
    dump_dir = work_dir / "02_dumps"
    raw_out = work_dir / "03_assembled_raw.png"

    char_json = CHAR_DEF_ROOT / f"{character}.json"
    config = load_character_config(char_json)
    source_dir = (PROJECT_ROOT / config["source_dir"]).resolve()
    palette = load_palette_for(character)

    # Scale/anchor reference: the character's immutable master idle still.
    # Computed once and applied to every dump frame so the whole animation
    # shares one baseline and scale. The idle's own dimensions are also the
    # Stage-4 canvas size, so the output sheet is at source resolution and
    # process_character_sprites.py owns the single downscale to the game frame.
    master_idle_path = source_dir / "idle.png"
    master_idle = Image.open(master_idle_path).convert("RGBA")
    canvas_w, canvas_h = master_idle.width, master_idle.height
    source_bbox_h, source_anchor_y = compute_source_anchor(
        master_idle, master_idle_path
    )

    all_processed: list[Image.Image] = []
    for dump_path in sorted(dump_dir.glob("dump_*.png")):
        raw = Image.open(dump_path).convert("RGBA")
        no_bg = remove_background(raw, bg_mode)
        cropped = tight_crop(no_bg, padding=1)
        if cropped.height == 0:
            print(f"warn: empty crop for {dump_path}, skipping")
            continue

        # Drift check: compare the character's height as a FRACTION of its
        # own frame in each pixel space (video-native dump vs idle.png-native)
        # before diffing, so the warning reflects genuine zoom/pan drift and
        # not a resolution difference between the clip and the master idle.
        frame_frac = cropped.height / max(raw.height, 1)
        idle_frac = source_bbox_h / max(canvas_h, 1)
        drift_pct = 100.0 * (frame_frac / max(idle_frac, 1e-6) - 1.0)
        if abs(drift_pct) > warn_scale_pct:
            print(f"warn: {dump_path.name} character height differs from the "
                  f"master idle by {drift_pct:+.1f}% (each as a fraction of "
                  f"its own frame)")

        scaled = downsample_to_height(cropped, source_bbox_h)
        quantized = palette_quantize(scaled, palette)
        composed = composite_onto_canvas(
            quantized, canvas_w, canvas_h, source_anchor_y
        )
        all_processed.append(composed)

    sheet = pack_horizontal(all_processed)
    sheet.save(raw_out)
    print(f"Wrote {raw_out} ({len(all_processed)} frames)")

    # Copy into the character's source_dir where the canonical processing
    # script looks for its input (it expects <animation>.png there).
    source_dir.mkdir(parents=True, exist_ok=True)
    source_copy = source_dir / f"{animation}.png"
    sheet.save(source_copy)
    print(f"Copied → {source_copy} (canonical script input)")
    return raw_out, source_copy


def resolve_output_filename(config: dict, animation: str) -> str:
    """Resolve the output filename the same way process_character_sprites.py does.

    process_character_sprites.py:336 resolves each animation's output as
    ``entry.get("output", entry["source"])`` — most entries omit `output` and
    fall back to `source`, but some (e.g. balchar.json's `sling_attack` entry,
    which sets `"output": "sling.png"`) rename the shipped asset. Assuming
    the output is always `f"{animation}.png"` is wrong whenever an entry sets
    an explicit `output`, so this helper must mirror the same lookup instead
    of re-deriving the filename from `animation` alone.

    Args:
        config: Parsed character JSON (as returned by load_character_config).
        animation: Animation name (matches `source` field minus `.png`).

    Returns:
        The output filename (e.g. "sling.png"), including the `.png` suffix.

    Raises:
        KeyError: If no animation entry matches.
    """
    target = f"{animation}.png"
    for entry in config.get("animations", []):
        if entry.get("source") == target:
            return entry.get("output", entry["source"])
    raise KeyError(f"unknown animation '{animation}' in character config")


def chain_process_script(character: str, animation: str) -> Path:
    """Invoke the canonical tools/process_character_sprites.py and verify output.

    The canonical script is always required. If it's missing, the repo is
    broken — raise loudly rather than silently skipping (which would cause
    every non-Balchar character to ship with no final asset).

    process_character_sprites.py walks EVERY animation entry in the JSON and
    exits 1 if any source PNG is missing. On a partially-generated character
    (only idle.png plus the one animation we just assembled), that non-zero
    exit is expected and does NOT mean our target failed — so this must NOT
    use check=True. Success is defined as "the animation's resolved output
    file exists under <output_dir> after the run"; that check (below) is the
    authority, and it raises if the target is missing.
    """
    script = PROJECT_ROOT / "tools" / "process_character_sprites.py"
    if not script.exists():
        raise FileNotFoundError(
            f"canonical processing script not found at {script}; the repo is "
            f"broken. (Stage 4 expects this script to always exist; do not "
            f"add silent-skip fallbacks here.)"
        )
    char_json = CHAR_DEF_ROOT / f"{character}.json"
    # check=False on purpose: a non-zero exit only means some OTHER animation's
    # source is absent, which is normal mid-generation. The target-output check
    # below decides success/failure for the animation we care about.
    subprocess.run(
        [sys.executable, str(script), str(char_json)], check=False
    )

    # Verify the output file actually landed where we expect. Resolve the
    # filename via the JSON entry's `output` field (falling back to
    # `source`) — NOT `f"{animation}.png"` — since entries such as
    # balchar.json's sling_attack (`"output": "sling.png"`) rename the
    # shipped asset relative to the source/animation name.
    config = load_character_config(char_json)
    output_dir = (PROJECT_ROOT / config["output_dir"]).resolve()
    expected_output = output_dir / resolve_output_filename(config, animation)
    if not expected_output.exists():
        raise FileNotFoundError(
            f"canonical script returned 0 but expected output "
            f"{expected_output} is missing. Inspect the script's logs and the "
            f"character JSON's animation entry for `{animation}.png` "
            f"(check its `output` field)."
        )
    return expected_output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character")
    parser.add_argument("animation")
    parser.add_argument("--bg-mode", choices=["rembg", "chroma", "both"], default="both")
    parser.add_argument("--warn-scale-pct", type=float, default=15.0)
    parser.add_argument("--no-chain", action="store_true",
                        help="Skip the canonical process_character_sprites.py chain")
    args = parser.parse_args()

    raw, _source_copy = assemble(
        args.character, args.animation, args.bg_mode, args.warn_scale_pct
    )
    if not args.no_chain:
        final = chain_process_script(args.character, args.animation)
        print(f"Final asset → {final}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests to confirm they pass**

```bash
pytest tests/test_assemble_sprite_sheet.py -v
```

Expected: 10 tests pass. (The `rembg` import is lazy — unit tests cover chroma path, downsample, quantize, anchor, composite, pack, and output-filename resolution, without exercising the rembg model.)

- [ ] **Step 7: Run the full project test suite to check for regressions**

```bash
pytest -q
```

Expected: all tests pass. No existing test should regress.

- [ ] **Step 8: Commit, push, open PR, clean up worktree**

```bash
git add tools/assemble_sprite_sheet.py tests/test_assemble_sprite_sheet.py pyproject.toml
git commit -m "$(cat <<'EOF'
feat(img2vid): add tools/assemble_sprite_sheet.py (Stage 4)

Assembles a clean sprite sheet from img2vid dump frames. Per surviving
frame: rembg-primary + connected-component chroma rescue for bg removal
(both by default), tight crop, scale to the master idle's body height,
palette quantize against assets/palettes/<character>.gpl (same parser as
clean_sprites.py — idempotent), composite onto a source-resolution
chroma-green canvas (master idle dims — process_character_sprites.py owns
the single downscale to the game frame) anchored at the master idle's
baseline with a hard alpha-threshold postcondition. Pack horizontal, write
03_assembled_raw.png plus a copy into
the character's source_dir, then invoke tools/process_character_sprites.py
<character>.json as a subprocess and verify the final output landed at the
animation's resolved output filename in output_dir
(entry.get("output", entry["source"]), not f"{animation}.png").

Scale and anchor come from the character's immutable master idle still
(<source_dir>/idle.png) — one shared reference, no per-animation config.

Adds pinned rembg>=2.0.50,<3.0, onnxruntime>=1.16,<2.0, and scipy>=1.11,<2.0
dependencies.

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t3-assemble
gh pr create --title "[img2vid-T3] tools/assemble_sprite_sheet.py (Stage 4)" --body "..."
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t3
```

---

### Task 4: End-to-end manual verification (no code, no PR)

**Files:** none modified.

**Interfaces:** consumes the merged outcomes of Tasks 1-3. Produces a screenshot + a written report for Toni to approve before declaring the deliverable done.

This Task is operational, not code. Once Tasks 1-3 have been merged (with Toni's approval per the workflow), the assigned developer (or the PM) runs the full pipeline on one real animation to confirm end-to-end behavior.

- [ ] **Step 1: Pick the verification target — Balchar sling attack**

Reason: the spec example was sling attack; it's a non-trivial animation (3 frames per balchar.json) with multiple body parts and a visible sling cord (R1 risk surface). Confirm the character's master idle still exists at `assets/ai_sources/balchar/idle.png` — it is the img2vid seed and the assembly scale/anchor reference.

- [ ] **Step 2: Generate the img2vid clip from the master idle**

Upload the master idle still `assets/ai_sources/balchar/idle.png` to Meta AI img2vid together with the slimmed sling-attack prompt from `docs/asset_prompts/shared.md` section 1.6 (Balchar Sling Attack). img2vid creates the motion from that single seed. Keep the clip short (1-2 seconds) per the spec's R2 mitigation. Download the resulting MP4 as:

```
assets/ai_sources/img2vid/balchar/sling_attack/01_video.mp4
```

- [ ] **Step 3: Run Stage 3 (dump)**

```bash
conda activate safona
python tools/dump_video_frames.py balchar sling_attack --k 10
ls assets/ai_sources/img2vid/balchar/sling_attack/02_dumps/
```

Expected: `dump_0000.png`, `dump_0001.png`, ... (~10 frames).

- [ ] **Step 4: Manually prune dumps**

Open `02_dumps/` in the file manager. Delete frames that are blurry, off-model, or duplicates. Keep the ones that best trace the sling-attack cycle, in filename order — they become the sprite-sheet frames left-to-right.

- [ ] **Step 5: Run Stage 4 (assemble)**

```bash
python tools/assemble_sprite_sheet.py balchar sling_attack --bg-mode both
```

Expected output (on stdout): per-frame log of any scale warnings, then `Wrote .../03_assembled_raw.png (N frames)` followed by the existing process script's output.

- [ ] **Step 6: Visual inspection of debug checkpoint**

Open `03_assembled_raw.png`. Check:
- All surviving frames present, in playback order
- Character on chroma-green background
- Palette looks clean (no off-palette colors)
- Sling cord visible in all frames where it should be (R1 check)
- Feet at consistent baseline across frames

If any check fails, refer to spec Section "Risks & Open Issues" for the matching fallback, fix, and re-run Stage 4 only (re-runnability invariant from Section 2).

- [ ] **Step 7: Compare against the final asset (`04_assembled_final.png` in debug terms)**

`balchar.json`'s `sling_attack` entry sets `"output": "sling.png"`, so the actual file to open is `assets/sprites/balchar/sling.png` — **not** `sling_attack.png`. Open it side-by-side with `03_assembled_raw.png`. Differences should be limited to what the canonical `process_character_sprites.py` normally does (outline tightening, palette enforcement). If the final asset looks worse than `03`, the bug is in `tools/process_character_sprites.py` or `tools/clean_sprites.py`, not the new pipeline.

- [ ] **Step 8: Launch the game and verify in-engine**

Per CLAUDE.md, hand off to the user (Toni) for in-engine testing. Do not start Xvfb/x11vnc/websockify from the agent side per CLAUDE.md memory `feedback_no_launch_game.md`. Provide branch name (`master`, since by this point all three Task PRs should be merged) and direct Toni to launch via `run.sh`.

- [ ] **Step 9: Report and await user sign-off**

Write a short report at `docs/reports/2026-06-23-img2vid-pipeline-verification.md`. Open a GitHub Issue summarizing the result and asking for explicit approval. Wait for "approved" from Toni before declaring the deliverable done (CLAUDE.md Rule #1.4).

---

## Self-Review

**Spec coverage:**
- Pipeline overview → Architecture summary + per-Task implementation (Tasks 2-3). ✓
- Folder layout → Task 1 (docs) + .gitignore + each Task's CLI defaults. ✓
- Per-stage tooling → Tasks 2, 3 (`split_sprite_sheet.py` dropped — no sheet to split). ✓
- Prompt restructuring → Task 1 Steps 7-10. ✓
- Documentation updates → Task 1 Steps 2-11. ✓
- All nine risks (R1-R9) → Mitigations baked into Task 3 (`--bg-mode` connected-component rescue, `--warn-scale-pct`, hard postcondition, `parse_gpl` single source of truth, pinned rembg+onnxruntime+scipy), Task 2 (`-fps_mode vfr` for R9), Task 4 Step 6 inspection checklist, and Task 1 Step 12 (.gitignore for R6). ✓
- Chain orchestration (resolved) → Task 3's `chain_process_script` calls the canonical `tools/process_character_sprites.py <character>.json` and hard-errors if either the script or the expected output is missing, resolving the expected output filename via `resolve_output_filename` (`entry.get("output", entry["source"])`) — the same lookup `process_character_sprites.py` performs — rather than assuming `f"{animation}.png"`. ✓
- Out-of-scope items → respected (no schema changes to character JSONs, no new prompt locations, no replacement of existing process scripts). ✓

**Placeholder scan:** No "TODO", "TBD", "implement later". `load_palette_for` reads directly from `assets/palettes/<character>.gpl` via `tools.clean_sprites.parse_gpl` — the single source of truth shared with the final cleanup chain.

**Type consistency:** Function names referenced across tests and impl match (`build_ffmpeg_command`, `dump_video`, `chroma_key_mask`, `downsample_to_height`, `palette_quantize`, `compute_source_anchor`, `composite_onto_canvas`, `pack_horizontal`, `resolve_output_filename`). Folder names match across all tasks (`01_video.mp4`, `02_dumps`, `03_assembled_raw.png`, `04_assembled_final.png`). The scale/anchor reference is the master idle still at `<source_dir>/idle.png`. Character JSON field names (`frame_width`, `frame_height`, `source_dir`, `output_dir`, `animations[].source`, `animations[].output`) match the actual `tools/sprite_defs/characters/balchar.json` schema verified during design.

---

## Execution Handoff

Per CLAUDE.md Rule #1.1, the PM (Na Francina) does not write or modify code. This plan must be executed by a developer agent (N'Andreu). The PM will dispatch N'Andreu with worktree isolation (per CLAUDE.md memory `feedback_worktree_isolation.md`), monitor PR progress, ensure review by En Pau + En Miquel, and gate merges on explicit Toni approval.

**Suggested PR sequence:** Tasks 1 → 2 → 3 ship as three sequential PRs (each landing before the next starts), since Task 3's tests reference no new infrastructure beyond what Task 2 establishes (work folder layout). Task 4 (end-to-end verification) runs once Task 3 is merged. There is no sheet-split task — the corrected pipeline has no sheet to split.

Task 1 is the highest-value first ship — it improves the existing pipeline today without any code risk, and can be reviewed by En Pau / En Miquel as a pure docs PR.
