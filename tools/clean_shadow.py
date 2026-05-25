#!/usr/bin/env python
"""Remove ground-shadow artefacts from AI-generated sprite sheets.

For each 24x32 frame the script:
1. Identifies contiguous bands of rows that contain non-transparent pixels.
2. Merges bands separated by only 1 transparent row (these are internal gaps
   in the character body, not body-shadow separators).
3. The merged band group that includes the topmost row with content is the
   character body.
4. All non-transparent pixels in other band groups (disconnected from the
   body by gaps of 2+ transparent rows) are made fully transparent.

This removes the ground shadow baked into AI-generated sprites while
preserving the complete character body even when it contains small
internal transparency gaps.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image
import numpy as np


FRAME_W = 24
FRAME_H = 32
# Maximum gap (in fully-transparent rows) to still consider two bands as
# belonging to the same body.  Gaps wider than this separate body from shadow.
MAX_BODY_GAP = 1


def _find_body_rows(mask: np.ndarray) -> set[int]:
    """Return the set of row indices that belong to the character body.

    Args:
        mask: 2-D boolean array (H x W), True where pixel is non-transparent.

    Returns:
        Set of row indices considered part of the body (topmost merged band).
    """
    h, _ = mask.shape
    row_has_content = [bool(mask[r].any()) for r in range(h)]

    # --- build contiguous bands of content rows ---
    bands: list[tuple[int, int]] = []  # (start_row, end_row) inclusive
    band_start: int | None = None
    for r in range(h):
        if row_has_content[r]:
            if band_start is None:
                band_start = r
        else:
            if band_start is not None:
                bands.append((band_start, r - 1))
                band_start = None
    if band_start is not None:
        bands.append((band_start, h - 1))

    if not bands:
        return set()

    # --- merge bands separated by <= MAX_BODY_GAP transparent rows ---
    merged: list[tuple[int, int]] = [bands[0]]
    for start, end in bands[1:]:
        prev_start, prev_end = merged[-1]
        gap = start - prev_end - 1  # number of transparent rows between
        if gap <= MAX_BODY_GAP:
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    # The body is the first merged group (contains the topmost content)
    body_start, body_end = merged[0]
    return set(range(body_start, body_end + 1))


def clean_sprite_sheet(path: str | Path) -> bool:
    """Remove shadow artefacts from a sprite sheet. Returns True if modified."""
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    h, w, _ = arr.shape
    n_frames = w // FRAME_W
    modified = False

    for f in range(n_frames):
        x0 = f * FRAME_W
        x1 = x0 + FRAME_W
        frame = arr[:FRAME_H, x0:x1]

        mask = frame[:, :, 3] > 0
        body_rows = _find_body_rows(mask)

        n_removed = 0
        for r in range(FRAME_H):
            if r not in body_rows and mask[r].any():
                cols = np.where(mask[r])[0]
                frame[r, cols, 3] = 0
                n_removed += len(cols)

        if n_removed > 0:
            modified = True
            print(f"  Frame {f}: removed {n_removed} shadow pixel(s)")

    if modified:
        result = Image.fromarray(arr)
        result.save(path)
        print(f"  Saved: {path}")
    else:
        print(f"  No changes needed: {path}")

    return modified


def generate_preview(src_path: str | Path, dst_path: str | Path, scale: int = 8) -> None:
    """Generate an upscaled preview PNG using nearest-neighbour resampling."""
    img = Image.open(src_path).convert("RGBA")
    new_size = (img.width * scale, img.height * scale)
    preview = img.resize(new_size, Image.NEAREST)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    preview.save(dst_path)
    print(f"  Preview saved: {dst_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean shadow artefacts from sprite sheets")
    parser.add_argument(
        "--assets-dir",
        default="assets/sprites/balchar",
        help="Directory containing sprite sheets",
    )
    parser.add_argument(
        "--preview-dir",
        default="docs/sprite_preview",
        help="Directory for preview output",
    )
    args = parser.parse_args()

    sprites = ["jump.png", "wall_jump.png"]

    for name in sprites:
        src = os.path.join(args.assets_dir, name)
        if not os.path.exists(src):
            print(f"  SKIP (not found): {src}")
            continue
        print(f"Cleaning {name}...")
        clean_sprite_sheet(src)

        preview_name = name.replace(".png", "_preview.png")
        dst = os.path.join(args.preview_dir, preview_name)
        print(f"Generating preview for {name}...")
        generate_preview(src, dst)


if __name__ == "__main__":
    main()
