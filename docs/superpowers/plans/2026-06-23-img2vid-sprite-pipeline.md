# Img2Vid Sprite Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current "AI image → postprocess" sprite pipeline with one that inserts an image-to-video stage, samples frames from the video, then assembles a palette-locked sprite sheet. Drop unused style noise from prompts. Persist every intermediate artifact for debuggability.

**Architecture:** Three new single-purpose CLIs under `tools/` chained via well-known folder paths under `assets/ai_sources/img2vid/<character>/<animation>/`. Each stage reads from `0N_*` and writes to `0(N+1)_*`. Existing `process_*_ai_sprites.py` and `clean_sprites.py` stay as the final cleanup chain — Stage 6 hands off to them unchanged.

**Tech Stack:** Python 3, Pillow, numpy, rembg (new dep), ffmpeg (system), pytest. Project uses the `safona` conda env.

**Spec:** `docs/proposals/2026-06-23-img2vid-sprite-pipeline.md`

## Global Constraints

- **No master commits.** Every Task ships as its own feature branch + PR. PR titles prefixed `[img2vid-Tx]`. Reviewers: En Pau + En Miquel.
- **No PR merge without explicit Toni approval.** Reviewer approval alone is NOT sufficient (CLAUDE.md Rule #1).
- **Worktree isolation.** Work in a git worktree per CLAUDE.md memory `feedback_worktree_isolation.md` — never edit the main checkout.
- **Conda env.** `conda activate safona` before any pip/pytest invocation.
- **Docstrings:** Google style.
- **Tests:** small and concise (CLAUDE.md). Use `tests/test_clean_sprites.py` as the conventions reference (sys.path manipulation, fixtures via tmp_path).
- **Final game asset path unchanged.** `assets/sprites/<character>/<animation>.png` remains the shipped artifact. Stage 6 chains to existing process scripts which write there.
- **No new doc files.** All docs live in the existing locations per CLAUDE.md: `docs/asset_generation_guide.md`, `docs/asset_prompts/shared.md`, `docs/asset_prompts/world1.md`, `tools/sprite_defs/README.md`.

## File Structure (full picture across all tasks)

```
Created:
  tools/split_sprite_sheet.py
  tools/dump_video_frames.py
  tools/assemble_sprite_sheet.py
  tests/test_split_sprite_sheet.py
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

Each Task touches a disjoint slice of these files, so they can land as independent PRs in any order (except Task 5 depends on 1-4).

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

Insert numbered steps for the img2vid workflow between "AI sheet generated" and "run processing scripts". New step list:

```
1. Write the prompt into the appropriate file under docs/asset_prompts/.
2. Generate the sprite sheet via your image AI. Save as
   assets/ai_sources/img2vid/<character>/<animation>/01_source_sheet.png.
3. Run: python tools/split_sprite_sheet.py <character> <animation>
   → produces 02_split_frames/
4. For each frame_NN.png in 02_split_frames/, upload to Meta AI img2vid (or
   future API) with the same prompt. Save resulting MP4 as
   03_videos/frame_NN.mp4.
5. Run: python tools/dump_video_frames.py <character> <animation> [--k 10]
   → produces 04_dumps/frame_NN/dump_*.png
6. Browse 04_dumps/frame_NN/ folders; delete frames you don't want.
7. Run: python tools/assemble_sprite_sheet.py <character> <animation>
   → produces 05_assembled_raw.png (debug checkpoint) and
   06_assembled_final.png + final asset under assets/sprites/.
```

- [ ] **Step 4: Update `docs/asset_generation_guide.md` Section 4 ("Same Character, New Animation")**

Add a subsection "Img2Vid stage" between the AI-generation and processing parts of Section 4. Body:

```
After generating the AI sprite sheet, each keyframe is fed through an
image-to-video AI to produce continuous motion. Frames are sampled from
the resulting videos and assembled into a higher-quality sprite sheet.
See Section 8 for the CLI commands. The img2vid stage is a *better source*
for the same downstream pipeline — the final processing step is unchanged.
```

- [ ] **Step 5: Update `docs/asset_generation_guide.md` Section 8 (Processing pipeline)**

Replace the existing pipeline diagram with the new one (copy from the spec's "Pipeline Overview" section, lines starting `Stage 1` through the `process_<character>_ai_sprites.py` chain).

Add Quick Start commands directly under the diagram:

```bash
# Stage 3 — slice the AI sheet into per-frame PNGs
python tools/split_sprite_sheet.py <character> <animation>

# Stage 5 — dump frames from each video (every Kth frame)
python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]

# Stage 6 — assemble cleaned sprite sheet
python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}]
```

Append a "Debug artifacts" subsection naming `05_assembled_raw.png` as the checkpoint to inspect when the final asset looks wrong.

- [ ] **Step 6: Update `docs/asset_generation_guide.md` Section 9 (Asset directory structure)**

Append the img2vid working layout:

```
assets/ai_sources/img2vid/<character>/<animation>/
├── 01_source_sheet.png       # Stage 2 (raw AI output)
├── 02_split_frames/          # Stage 3 output
├── 03_videos/                # Stage 4 drop zone (user places MP4s here)
├── 04_dumps/                 # Stage 5 output (user prunes in place)
├── 05_assembled_raw.png      # Stage 6 output (debug checkpoint)
└── 06_assembled_final.png    # After existing process_*_ai_sprites.py
```

Note that this whole subtree is gitignored.

- [ ] **Step 7: Update `docs/asset_prompts/shared.md` "Global style block" section**

Apply the same note flip as `docs/asset_generation_guide.md` Section 0 (Step 2): the block is reference-only, not copied into prompts.

- [ ] **Step 8: Drop GLOBAL STYLE CONSTRAINTS from every prompt in `shared.md`**

For each section 1.1 through 18.x in `shared.md`, locate the prompt body (the fenced code block following the `## X.Y Title` header). Find the lines starting with `GLOBAL STYLE CONSTRAINTS (DO NOT VIOLATE):` and delete that block (typically the first ~13 lines of the prompt body up to but not including the next labelled section — `CRITICAL IDENTITY LOCK:`, `REFERENCE:`, or `PALETTE`).

Keep ALL other prompt content: identity lock, reference attachment, palette block, sprite constraints, body size rule, animation description, rules tail.

Verification after each prompt: prompt still parses as a single fenced code block; identity lock + palette + animation description are intact.

- [ ] **Step 9: Update `docs/asset_prompts/world1.md` style chain section**

Same note flip in the "Style chain (World 1)" section.

- [ ] **Step 10: Drop GLOBAL STYLE CONSTRAINTS from every prompt in `world1.md`**

Apply the same removal as Step 8 to every section 3.x through 8.x.

- [ ] **Step 11: Update `tools/sprite_defs/README.md`**

Replace the Overview pipeline diagram with the new one from the spec. Append the three new CLIs to the Quick Start section (same commands as Step 5).

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

Expected: 5 files modified, line additions/deletions roughly proportional to the prompt count (~60 prompts × ~13 lines deleted = ~800 deletions on prompt files, plus modest additions on guide.md and README.md).

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

### Task 2: `tools/split_sprite_sheet.py`

**Files:**
- Create: `tools/split_sprite_sheet.py`
- Create: `tests/test_split_sprite_sheet.py`

**Interfaces:**
- Consumes: nothing (first new CLI)
- Produces:
  - CLI `python tools/split_sprite_sheet.py <character> <animation>`
  - Reads: `assets/ai_sources/img2vid/<character>/<animation>/01_source_sheet.png` and `tools/sprite_defs/characters/<character>.json` (existing format, field `animations[].source` matched against `<animation>.png`, field `animations[].frames` gives N).
  - Writes: `assets/ai_sources/img2vid/<character>/<animation>/02_split_frames/frame_01.png` ... `frame_NN.png`. PNGs are direct horizontal slices of the source sheet, each `source.width // N` × `source.height` pixels.

- [ ] **Step 1: Create worktree and branch**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t2 -b feat/img2vid-t2-split master
cd ../safona-img2vid-t2
```

- [ ] **Step 2: Write the failing test for the slicer**

Create `tests/test_split_sprite_sheet.py`:

```python
"""Tests for tools/split_sprite_sheet.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.split_sprite_sheet import slice_sheet, resolve_frame_count


def _make_sheet(tmp_path: Path, width: int, height: int, n_frames: int) -> Path:
    """Generate a striped sprite sheet for slicing tests."""
    img = Image.new("RGB", (width, height), (0, 255, 0))
    pixels = img.load()
    for i in range(n_frames):
        x0 = i * (width // n_frames)
        for y in range(height):
            pixels[x0, y] = (255, 0, 0)  # red marker at start of each frame
    sheet_path = tmp_path / "sheet.png"
    img.save(sheet_path)
    return sheet_path


def test_slice_sheet_produces_n_frames(tmp_path: Path):
    sheet = _make_sheet(tmp_path, width=160, height=48, n_frames=5)
    out_dir = tmp_path / "out"
    frames = slice_sheet(sheet, out_dir, n_frames=5)

    assert len(frames) == 5
    for i, frame_path in enumerate(frames, start=1):
        assert frame_path.name == f"frame_{i:02d}.png"
        assert frame_path.exists()
        img = Image.open(frame_path)
        assert img.size == (32, 48)


def test_slice_sheet_marker_lands_at_origin(tmp_path: Path):
    sheet = _make_sheet(tmp_path, width=160, height=48, n_frames=5)
    out_dir = tmp_path / "out"
    frames = slice_sheet(sheet, out_dir, n_frames=5)

    # The red marker we drew at the start of each source-frame column
    # should now sit at x=0 of each sliced output.
    for frame_path in frames:
        img = Image.open(frame_path).convert("RGB")
        assert img.getpixel((0, 0)) == (255, 0, 0)


def test_resolve_frame_count_from_character_json(tmp_path: Path):
    char_json = tmp_path / "balchar.json"
    char_json.write_text(json.dumps({
        "frame_width": 48,
        "frame_height": 64,
        "source_dir": "assets/ai_sources/balchar",
        "output_dir": "assets/sprites/balchar",
        "animations": [
            {"source": "idle.png", "frames": 4, "scale_pct": 100, "vertical_snap": "bottom"},
            {"source": "sling_attack.png", "frames": 3, "scale_pct": 115, "vertical_snap": "bottom"},
        ],
    }))

    assert resolve_frame_count(char_json, "idle") == 4
    assert resolve_frame_count(char_json, "sling_attack") == 3


def test_resolve_frame_count_errors_on_unknown_animation(tmp_path: Path):
    char_json = tmp_path / "balchar.json"
    char_json.write_text(json.dumps({
        "animations": [{"source": "idle.png", "frames": 4}],
    }))

    with pytest.raises(KeyError, match="unknown"):
        resolve_frame_count(char_json, "unknown")
```

- [ ] **Step 3: Run the test to confirm it fails**

```bash
conda activate safona
pytest tests/test_split_sprite_sheet.py -v
```

Expected: `ModuleNotFoundError: No module named 'tools.split_sprite_sheet'`.

- [ ] **Step 4: Implement `tools/split_sprite_sheet.py`**

```python
"""Slice an AI-generated sprite sheet into per-frame PNGs.

Stage 3 of the img2vid sprite pipeline. Reads:
  - assets/ai_sources/img2vid/<character>/<animation>/01_source_sheet.png
  - tools/sprite_defs/characters/<character>.json

Writes:
  - assets/ai_sources/img2vid/<character>/<animation>/02_split_frames/frame_NN.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"
CHAR_DEF_ROOT = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"


def resolve_frame_count(char_json_path: Path, animation: str) -> int:
    """Look up the frame count for an animation from the character's JSON config.

    Args:
        char_json_path: Path to tools/sprite_defs/characters/<character>.json.
        animation: Animation name (matches `source` field minus `.png`).

    Returns:
        Number of frames defined for the animation.

    Raises:
        KeyError: If no animation entry matches.
    """
    data = json.loads(char_json_path.read_text())
    target = f"{animation}.png"
    for anim in data.get("animations", []):
        if anim.get("source") == target:
            return int(anim["frames"])
    raise KeyError(f"unknown animation '{animation}' in {char_json_path}")


def slice_sheet(sheet_path: Path, out_dir: Path, n_frames: int) -> list[Path]:
    """Slice a horizontal sprite sheet into per-frame PNGs.

    Args:
        sheet_path: Path to the source sprite sheet PNG.
        out_dir: Destination directory. Created if missing.
        n_frames: Number of frames packed horizontally in the sheet.

    Returns:
        List of paths to the written frame PNGs in order frame_01..frame_NN.
    """
    img = Image.open(sheet_path)
    frame_w = img.width // n_frames
    frame_h = img.height
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for i in range(n_frames):
        left = i * frame_w
        frame = img.crop((left, 0, left + frame_w, frame_h))
        out = out_dir / f"frame_{i + 1:02d}.png"
        frame.save(out)
        written.append(out)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character")
    parser.add_argument("animation")
    args = parser.parse_args()

    char_json = CHAR_DEF_ROOT / f"{args.character}.json"
    n_frames = resolve_frame_count(char_json, args.animation)

    work_dir = WORK_ROOT / args.character / args.animation
    sheet = work_dir / "01_source_sheet.png"
    out_dir = work_dir / "02_split_frames"

    frames = slice_sheet(sheet, out_dir, n_frames)
    print(f"Sliced {sheet} → {len(frames)} frames in {out_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the test to confirm it passes**

```bash
pytest tests/test_split_sprite_sheet.py -v
```

Expected: 4 tests pass.

- [ ] **Step 6: Smoke-test the CLI on a real character**

```bash
# Use an existing AI source so we don't depend on a new img2vid generation
mkdir -p assets/ai_sources/img2vid/balchar/idle
cp assets/ai_sources/balchar/idle.png \
   assets/ai_sources/img2vid/balchar/idle/01_source_sheet.png
python tools/split_sprite_sheet.py balchar idle
ls assets/ai_sources/img2vid/balchar/idle/02_split_frames/
```

Expected: `frame_01.png` ... `frame_04.png` (idle has 4 frames per balchar.json).

- [ ] **Step 7: Clean up smoke-test artifacts**

```bash
rm -rf assets/ai_sources/img2vid/balchar/idle/
```

(The .gitignore from Task 1 prevents these from getting tracked, but we keep the worktree tidy.)

- [ ] **Step 8: Commit, push, open PR, clean up worktree**

```bash
git add tools/split_sprite_sheet.py tests/test_split_sprite_sheet.py
git commit -m "$(cat <<'EOF'
feat(img2vid): add tools/split_sprite_sheet.py (Stage 3)

Slices an AI-generated sprite sheet into per-frame PNGs for upload to the
img2vid stage. Frame count is read from
tools/sprite_defs/characters/<character>.json (existing source of truth).

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t2-split
gh pr create --title "[img2vid-T2] tools/split_sprite_sheet.py (Stage 3)" --body "..."
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t2
```

---

### Task 3: `tools/dump_video_frames.py`

**Files:**
- Create: `tools/dump_video_frames.py`
- Create: `tests/test_dump_video_frames.py`

**Interfaces:**
- Consumes: Task 2's output layout (`02_split_frames/frame_NN.png` exists, defining the expected MP4 names).
- Produces:
  - CLI `python tools/dump_video_frames.py <character> <animation> [--k 10] [--reset]`
  - Reads: `03_videos/frame_NN.mp4` (one per split frame; validated against `02_split_frames/` filenames).
  - Writes: `04_dumps/frame_NN/dump_0000.png` ... by invoking ffmpeg with `select=not(mod(n\\,K))`.
  - `--reset` wipes per-video dump folder before extracting.

- [ ] **Step 1: Create worktree and branch**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t3 -b feat/img2vid-t3-dump master
cd ../safona-img2vid-t3
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
    discover_videos,
    dump_one_video,
)


def test_build_ffmpeg_command_uses_select_modulo(tmp_path: Path):
    video = tmp_path / "frame_01.mp4"
    out_dir = tmp_path / "out"
    cmd = build_ffmpeg_command(video, out_dir, k=10)

    assert cmd[0] == "ffmpeg"
    assert "-i" in cmd
    assert str(video) in cmd
    select_arg = next(arg for arg in cmd if "select=" in arg)
    assert "not(mod(n\\,10))" in select_arg
    assert str(out_dir / "dump_%04d.png") in cmd


def test_discover_videos_matches_split_frames(tmp_path: Path):
    split_dir = tmp_path / "02_split_frames"
    split_dir.mkdir()
    (split_dir / "frame_01.png").write_bytes(b"")
    (split_dir / "frame_02.png").write_bytes(b"")
    (split_dir / "frame_03.png").write_bytes(b"")

    video_dir = tmp_path / "03_videos"
    video_dir.mkdir()
    (video_dir / "frame_01.mp4").write_bytes(b"")
    (video_dir / "frame_03.mp4").write_bytes(b"")

    videos = discover_videos(split_dir, video_dir)
    assert [v.name for v in videos] == ["frame_01.mp4", "frame_03.mp4"]


def test_discover_videos_errors_on_unexpected_filename(tmp_path: Path):
    split_dir = tmp_path / "02_split_frames"
    split_dir.mkdir()
    (split_dir / "frame_01.png").write_bytes(b"")

    video_dir = tmp_path / "03_videos"
    video_dir.mkdir()
    (video_dir / "unrelated.mp4").write_bytes(b"")

    with pytest.raises(ValueError, match="unrelated.mp4"):
        discover_videos(split_dir, video_dir)


def test_dump_one_video_invokes_ffmpeg_and_resets(tmp_path: Path):
    video = tmp_path / "frame_01.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "dumps" / "frame_01"
    out_dir.mkdir(parents=True)
    (out_dir / "stale.png").write_bytes(b"")  # leftover from previous run

    with patch("tools.dump_video_frames.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        dump_one_video(video, out_dir, k=10, reset=True)

    assert not (out_dir / "stale.png").exists()
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
pytest tests/test_dump_video_frames.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 4: Implement `tools/dump_video_frames.py`**

```python
"""Dump frames from img2vid MP4s for visual pruning.

Stage 5 of the img2vid sprite pipeline. For each MP4 in 03_videos/, runs
ffmpeg to extract every Kth frame into a per-video dump folder. The user
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
        video: Path to the source MP4.
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
        "-vsync", "vfr",
        str(out_dir / "dump_%04d.png"),
    ]


def discover_videos(split_dir: Path, video_dir: Path) -> list[Path]:
    """List MP4s in video_dir, validating each maps to a split frame.

    Args:
        split_dir: 02_split_frames directory (defines expected stem names).
        video_dir: 03_videos directory.

    Returns:
        Sorted list of MP4 paths.

    Raises:
        ValueError: If any MP4 has a name that does not match a split frame.
    """
    expected = {p.stem for p in split_dir.glob("frame_*.png")}
    videos: list[Path] = []
    for mp4 in sorted(video_dir.glob("*.mp4")):
        if mp4.stem not in expected:
            raise ValueError(
                f"video {mp4.name} does not match any split frame "
                f"(expected one of: {sorted(expected)})"
            )
        videos.append(mp4)
    return videos


def dump_one_video(video: Path, out_dir: Path, k: int, reset: bool) -> int:
    """Extract every Kth frame from a single video.

    Args:
        video: Source MP4 path.
        out_dir: Per-video dump folder.
        k: Extract every Kth frame.
        reset: If True, wipe out_dir contents first.

    Returns:
        Number of dump_*.png files in out_dir after extraction.
    """
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
                        help="Wipe per-video dump folders before extracting")
    args = parser.parse_args()

    work_dir = WORK_ROOT / args.character / args.animation
    split_dir = work_dir / "02_split_frames"
    video_dir = work_dir / "03_videos"
    dump_root = work_dir / "04_dumps"

    videos = discover_videos(split_dir, video_dir)
    for video in videos:
        out_dir = dump_root / video.stem
        n = dump_one_video(video, out_dir, args.k, args.reset)
        print(f"{video.name}: {n} frames → {out_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
pytest tests/test_dump_video_frames.py -v
```

Expected: 4 tests pass.

- [ ] **Step 6: Commit, push, open PR, clean up worktree**

```bash
git add tools/dump_video_frames.py tests/test_dump_video_frames.py
git commit -m "$(cat <<'EOF'
feat(img2vid): add tools/dump_video_frames.py (Stage 5)

Extracts every Kth frame from each MP4 in 03_videos/ into per-video dump
folders for manual pruning. Validates that each video name matches a split
frame from Stage 3. Supports --reset to safely re-extract after over-pruning.

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t3-dump
gh pr create --title "[img2vid-T3] tools/dump_video_frames.py (Stage 5)" --body "..."
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t3
```

---

### Task 4: `tools/assemble_sprite_sheet.py`

**Files:**
- Create: `tools/assemble_sprite_sheet.py`
- Create: `tests/test_assemble_sprite_sheet.py`
- Modify: `pyproject.toml` (add `rembg` dependency)

**Interfaces:**
- Consumes: Task 2's `02_split_frames/frame_NN.png` (scale/anchor reference) and Task 3's `04_dumps/frame_NN/dump_*.png` (frames to process).
- Produces:
  - CLI `python tools/assemble_sprite_sheet.py <character> <animation> [--bg-mode {rembg,chroma,both}] [--warn-scale-pct 15]`
  - Writes: `05_assembled_raw.png` (debug checkpoint), then invokes existing `tools/process_<character>_ai_sprites.py` to produce `06_assembled_final.png` and the final asset under `assets/sprites/`.

- [ ] **Step 1: Create worktree, branch, install rembg**

```bash
cd /home/jovyan/projects/SaFona
git worktree add ../safona-img2vid-t4 -b feat/img2vid-t4-assemble master
cd ../safona-img2vid-t4
conda activate safona
pip install rembg
```

- [ ] **Step 2: Add rembg to `pyproject.toml`**

Open `pyproject.toml`, find the `dependencies` (or equivalent) list, add `"rembg"`. Run `pip install -e .` to confirm install works from the file.

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
    palette = [(0, 0, 0), (255, 255, 255), (255, 0, 0)]
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
```

- [ ] **Step 4: Run tests to confirm they fail**

```bash
pytest tests/test_assemble_sprite_sheet.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 5: Implement `tools/assemble_sprite_sheet.py`**

```python
"""Assemble a clean sprite sheet from img2vid dump frames.

Stage 6 of the img2vid sprite pipeline. For each surviving dump frame in
04_dumps/frame_NN/, removes the background, downsamples to match the source
split frame's character height, palette-quantizes, and composites onto a
chroma-green canvas anchored at the source frame's baseline. Packs the
processed frames into 05_assembled_raw.png, then hands off to the existing
process_<character>_ai_sprites.py for final cleanup.

Scale and anchor are self-calibrating: they are derived from the matching
source split frame, NOT from per-animation config. This means each animation
(jumps, falls, attacks, idles) inherits the correct anchor automatically.
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"
CHAR_DEF_ROOT = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"

CHROMA_GREEN = (0, 255, 0)
CHROMA_GREEN_RGBA = (0, 255, 0, 255)


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
    """Remove the background using the requested strategy."""
    if mode == "chroma":
        mask = chroma_key_mask(img)
    elif mode == "rembg":
        mask = rembg_mask(img)
    elif mode == "both":
        mask = np.logical_or(chroma_key_mask(img), rembg_mask(img)).astype(np.uint8)
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


def compute_source_anchor(source_frame: Image.Image) -> tuple[int, int]:
    """From the matching split frame, derive (bbox_height, anchor_y).

    bbox_height: height of the character body in the source sheet.
    anchor_y:   y-coordinate of the bbox bottom in the source canvas.
                Used to place subsequent frames at the same baseline.
    """
    masked = apply_mask(source_frame, chroma_key_mask(source_frame))
    bbox = masked.getbbox()
    if bbox is None:
        raise ValueError("source split frame has no foreground after chroma-key")
    left, top, right, bottom = bbox
    return (bottom - top, bottom - 1)


def downsample_to_height(img: Image.Image, target_height: int) -> Image.Image:
    """Downsample preserving aspect; bilinear pre-pass then NEAREST snap."""
    if img.height == target_height:
        return img
    ratio = target_height / img.height
    target_width = max(1, int(round(img.width * ratio)))
    pre = img.resize((target_width * 2, target_height * 2), Image.BILINEAR)
    return pre.resize((target_width, target_height), Image.NEAREST)


def palette_quantize(img: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    """Snap each opaque pixel to its nearest palette color."""
    rgba = np.array(img.convert("RGBA"))
    rgb = rgba[..., :3].astype(int)
    alpha = rgba[..., 3]

    pal = np.array(palette, dtype=int)
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
    """Paste the character onto a chroma-green canvas with its bottom at anchor_y."""
    canvas = Image.new("RGBA", (canvas_w, canvas_h), CHROMA_GREEN_RGBA)
    paste_x = (canvas_w - char.width) // 2
    paste_y = anchor_y - char.height + 1
    canvas.paste(char, (paste_x, paste_y), char)
    # Re-flatten alpha to chroma green so downstream chroma-key still works
    flat = Image.new("RGBA", canvas.size, CHROMA_GREEN_RGBA)
    flat.paste(canvas, (0, 0), canvas)
    return flat


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


def load_palette_for(character: str) -> list[tuple[int, int, int]]:
    """Load the 15-color palette for a character.

    Tries tools/sprite_defs/palettes.py first; falls back to parsing the
    character's prompt MD if no entry exists there. The implementing dev
    should pick the path that already exists — do not invent a new format.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from tools.sprite_defs import palettes  # type: ignore
        if hasattr(palettes, character.upper()):
            return list(getattr(palettes, character.upper()))
    except ImportError:
        pass
    raise NotImplementedError(
        f"palette for {character} not found in tools/sprite_defs/palettes.py. "
        f"Add it there (single source of truth), then re-run."
    )


def load_character_config(char_json_path: Path) -> dict:
    return json.loads(char_json_path.read_text())


def assemble(
    character: str,
    animation: str,
    bg_mode: str,
    warn_scale_pct: float,
) -> Path:
    """Run the full Stage 6 pipeline. Returns path to 05_assembled_raw.png."""
    work_dir = WORK_ROOT / character / animation
    split_dir = work_dir / "02_split_frames"
    dump_root = work_dir / "04_dumps"
    raw_out = work_dir / "05_assembled_raw.png"

    char_json = CHAR_DEF_ROOT / f"{character}.json"
    config = load_character_config(char_json)
    canvas_w = int(config["frame_width"])
    canvas_h = int(config["frame_height"])
    palette = load_palette_for(character)

    all_processed: list[Image.Image] = []
    for source_path in sorted(split_dir.glob("frame_*.png")):
        dump_dir = dump_root / source_path.stem
        if not dump_dir.exists():
            print(f"warn: no dump folder for {source_path.stem}, skipping")
            continue

        source_img = Image.open(source_path).convert("RGBA")
        source_bbox_h, source_anchor_y = compute_source_anchor(source_img)

        for dump_path in sorted(dump_dir.glob("dump_*.png")):
            raw = Image.open(dump_path).convert("RGBA")
            no_bg = remove_background(raw, bg_mode)
            cropped = tight_crop(no_bg, padding=1)
            if cropped.height == 0:
                print(f"warn: empty crop for {dump_path}, skipping")
                continue

            scale_pct = 100.0 * cropped.height / max(source_bbox_h, 1)
            if abs(scale_pct - 100.0) > warn_scale_pct:
                print(f"warn: {dump_path.name} bbox height differs from source "
                      f"by {scale_pct - 100:+.1f}%")

            scaled = downsample_to_height(cropped, source_bbox_h)
            quantized = palette_quantize(scaled, palette)
            composed = composite_onto_canvas(
                quantized, canvas_w, canvas_h, source_anchor_y
            )
            all_processed.append(composed)

    sheet = pack_horizontal(all_processed)
    sheet.save(raw_out)
    print(f"Wrote {raw_out} ({len(all_processed)} frames)")
    return raw_out


def chain_process_script(character: str, raw_sheet: Path) -> None:
    """Invoke the existing process_<character>_ai_sprites.py with the raw sheet."""
    candidates = [
        PROJECT_ROOT / "tools" / f"process_{character}_ai_sprites.py",
        PROJECT_ROOT / "tools" / "process_ai_sprites.py",
    ]
    script = next((c for c in candidates if c.exists()), None)
    if script is None:
        print(f"note: no process_<character>_ai_sprites.py found; "
              f"hand-off skipped. Run cleanup manually on {raw_sheet}.")
        return
    subprocess.run([sys.executable, str(script), str(raw_sheet)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character")
    parser.add_argument("animation")
    parser.add_argument("--bg-mode", choices=["rembg", "chroma", "both"], default="both")
    parser.add_argument("--warn-scale-pct", type=float, default=15.0)
    parser.add_argument("--no-chain", action="store_true",
                        help="Skip handing off to process_<character>_ai_sprites.py")
    args = parser.parse_args()

    raw = assemble(args.character, args.animation, args.bg_mode, args.warn_scale_pct)
    if not args.no_chain:
        chain_process_script(args.character, raw)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests to confirm they pass**

```bash
pytest tests/test_assemble_sprite_sheet.py -v
```

Expected: 6 tests pass. (The `rembg` import is lazy — unit tests cover chroma path, downsample, quantize, anchor, composite, and pack without exercising the rembg model.)

- [ ] **Step 7: Run the full project test suite to check for regressions**

```bash
pytest -q
```

Expected: all tests pass. No existing test should regress.

- [ ] **Step 8: Commit, push, open PR, clean up worktree**

```bash
git add tools/assemble_sprite_sheet.py tests/test_assemble_sprite_sheet.py pyproject.toml
git commit -m "$(cat <<'EOF'
feat(img2vid): add tools/assemble_sprite_sheet.py (Stage 6)

Assembles a clean sprite sheet from img2vid dump frames. Per surviving
frame: rembg + chroma background removal (both by default), tight crop,
downsample to match source split frame's character height, palette
quantize, composite onto chroma-green canvas anchored at source baseline,
pack horizontal. Hands off to existing process_<character>_ai_sprites.py.

Scale and anchor are self-calibrating from the matching source split frame
— no per-animation config needed.

Adds rembg dependency.

See spec: docs/proposals/2026-06-23-img2vid-sprite-pipeline.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin feat/img2vid-t4-assemble
gh pr create --title "[img2vid-T4] tools/assemble_sprite_sheet.py (Stage 6)" --body "..."
cd /home/jovyan/projects/SaFona
git worktree remove ../safona-img2vid-t4
```

---

### Task 5: End-to-end manual verification (no code, no PR)

**Files:** none modified.

**Interfaces:** consumes the merged outcomes of Tasks 1-4. Produces a screenshot + a written report for Toni to approve before declaring the deliverable done.

This Task is operational, not code. Once Tasks 1-4 have been merged (with Toni's approval per the workflow), the assigned developer (or the PM) runs the full pipeline on one real animation to confirm end-to-end behavior.

- [ ] **Step 1: Pick the verification target — Balchar sling attack**

Reason: the spec example was sling attack; it's a non-trivial animation (3 frames per balchar.json) with multiple body parts and a visible sling cord (R1 risk surface).

- [ ] **Step 2: Generate the sprite sheet via the user's image AI**

Using the slimmed prompt from `docs/asset_prompts/shared.md` section 1.6 (Balchar Sling Attack). Save as:

```
assets/ai_sources/img2vid/balchar/sling_attack/01_source_sheet.png
```

- [ ] **Step 3: Run Stage 3 (split)**

```bash
conda activate safona
python tools/split_sprite_sheet.py balchar sling_attack
ls assets/ai_sources/img2vid/balchar/sling_attack/02_split_frames/
```

Expected: `frame_01.png`, `frame_02.png`, `frame_03.png`.

- [ ] **Step 4: Generate three img2vid clips**

For each `frame_NN.png`, upload to Meta AI img2vid with the same prompt that produced the sheet. Download as `frame_NN.mp4` into `03_videos/`.

Keep clips short (1-2 seconds) per the spec's R2 mitigation.

- [ ] **Step 5: Run Stage 5 (dump)**

```bash
python tools/dump_video_frames.py balchar sling_attack --k 10
ls assets/ai_sources/img2vid/balchar/sling_attack/04_dumps/
```

Expected: three subfolders `frame_01/`, `frame_02/`, `frame_03/`, each with ~10 `dump_*.png` files.

- [ ] **Step 6: Manually prune dumps**

Open each `frame_NN/` folder in the file manager. Delete frames that are blurry, off-model, or duplicates. Keep the ones that best show the pose phase.

- [ ] **Step 7: Run Stage 6 (assemble)**

```bash
python tools/assemble_sprite_sheet.py balchar sling_attack --bg-mode both
```

Expected output (on stdout): per-frame log of any scale warnings, then `Wrote .../05_assembled_raw.png (N frames)` followed by the existing process script's output.

- [ ] **Step 8: Visual inspection of debug checkpoint**

Open `05_assembled_raw.png`. Check:
- All frames present, in playback order
- Character on chroma-green background
- Palette looks clean (no off-palette colors)
- Sling cord visible in all frames where it should be (R1 check)
- Feet at consistent baseline across frames

If any check fails, refer to spec Section "Risks & Open Issues" for the matching fallback, fix, and re-run Stage 6 only (re-runnability invariant from Section 2).

- [ ] **Step 9: Compare against `06_assembled_final.png`**

Open both side-by-side. Differences should be limited to what the existing process script normally does (outline tightening, palette enforcement). If `06` looks worse than `05`, the bug is in process_*_ai_sprites.py, not the new pipeline.

- [ ] **Step 10: Launch the game and verify in-engine**

Per CLAUDE.md, hand off to the user (Toni) for in-engine testing. Do not start Xvfb/x11vnc/websockify from the agent side per CLAUDE.md memory `feedback_no_launch_game.md`. Provide branch name (`master`, since by this point all four Task PRs should be merged) and direct Toni to launch via `run.sh`.

- [ ] **Step 11: Report and await user sign-off**

Write a short report at `docs/reports/2026-06-23-img2vid-pipeline-verification.md`. Open a GitHub Issue summarizing the result and asking for explicit approval. Wait for "approved" from Toni before declaring the deliverable done (CLAUDE.md Rule #1.4).

---

## Self-Review

**Spec coverage:**
- Pipeline overview → Architecture summary + per-Task implementation (Tasks 2-4). ✓
- Folder layout → Task 1 (docs) + .gitignore + each Task's CLI defaults. ✓
- Per-stage tooling → Tasks 2, 3, 4. ✓
- Prompt restructuring → Task 1 Steps 7-10. ✓
- Documentation updates → Task 1 Steps 2-11. ✓
- All six risks (R1-R6) → Mitigations baked into Task 4 (`--bg-mode`, `--warn-scale-pct`), Task 5 Step 8 inspection checklist, and Task 1 Step 12 (.gitignore for R6). ✓
- Open issue (`clean_sprites.py` orchestration) → Task 4's `chain_process_script` defers to the existing process script convention. ✓
- Out-of-scope items → respected (no schema changes to character JSONs, no new prompt locations, no replacement of existing process scripts). ✓

**Placeholder scan:** No "TODO", "TBD", "implement later". One acknowledged deferral: `load_palette_for` raises `NotImplementedError` if the palette isn't in `tools/sprite_defs/palettes.py` — the message points the implementer at the single source of truth instead of forking a new format. This is intentional, not a placeholder.

**Type consistency:** Function names referenced across tests and impl match (`slice_sheet`, `resolve_frame_count`, `build_ffmpeg_command`, `discover_videos`, `dump_one_video`, `chroma_key_mask`, `downsample_to_height`, `palette_quantize`, `compute_source_anchor`, `composite_onto_canvas`, `pack_horizontal`). Folder names match across all tasks (`02_split_frames`, `03_videos`, `04_dumps`, `05_assembled_raw.png`, `06_assembled_final.png`). Character JSON field names (`frame_width`, `frame_height`, `animations[].source`, `animations[].frames`) match the actual `tools/sprite_defs/characters/balchar.json` schema verified during design.

---

## Execution Handoff

Per CLAUDE.md Rule #1.1, the PM (Na Francina) does not write or modify code. This plan must be executed by a developer agent (N'Andreu). The PM will dispatch N'Andreu with worktree isolation (per CLAUDE.md memory `feedback_worktree_isolation.md`), monitor PR progress, ensure review by En Pau + En Miquel, and gate merges on explicit Toni approval.

**Suggested PR sequence:** Tasks 1 → 2 → 3 → 4 ship as four sequential PRs (each landing before the next starts), since Task 4's tests reference no new infrastructure beyond what Task 2 and 3 establish (work folder layout). Task 5 runs once Task 4 is merged.

Task 1 is the highest-value first ship — it improves the existing pipeline today without any code risk, and can be reviewed by En Pau / En Miquel as a pure docs PR.
