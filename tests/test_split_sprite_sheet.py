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
