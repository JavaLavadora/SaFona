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
    print(f"Sliced {sheet} -> {len(frames)} frames in {out_dir}")


if __name__ == "__main__":
    main()
