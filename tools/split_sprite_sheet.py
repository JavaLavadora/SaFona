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
import logging
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"
CHAR_DEF_ROOT = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


def resolve_frame_count(char_json_path: Path, animation: str) -> int:
    """Look up the frame count for an animation from the character's JSON config.

    Args:
        char_json_path: Path to tools/sprite_defs/characters/<character>.json.
        animation: Animation name (matches `source` field minus `.png`).

    Returns:
        Number of frames defined for the animation.

    Raises:
        FileNotFoundError: If char_json_path does not exist.
        KeyError: If no animation entry matches.
    """
    if not char_json_path.exists():
        raise FileNotFoundError(
            f"Character JSON not found: {char_json_path} "
            f"(expected tools/sprite_defs/characters/<character>.json)"
        )
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

    Raises:
        FileNotFoundError: If sheet_path does not exist.
        ValueError: If the sheet width is not evenly divisible by n_frames
            (would silently drop trailing pixel columns).
    """
    if not sheet_path.exists():
        raise FileNotFoundError(
            f"Source sprite sheet not found: {sheet_path} "
            f"(expected 01_source_sheet.png in this animation's work directory)"
        )
    img = Image.open(sheet_path)
    if img.width % n_frames != 0:
        raise ValueError(
            f"Sheet width {img.width}px is not evenly divisible by "
            f"{n_frames} frames (remainder {img.width % n_frames}px would be "
            f"dropped) — sheet: {sheet_path}. Regenerate the sheet at an exact "
            f"multiple width or fix the 'frames' count in the character JSON."
        )
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
    """Entry point."""
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
    log.info("Sliced %s -> %d frames in %s", sheet, len(frames), out_dir)


if __name__ == "__main__":
    main()
