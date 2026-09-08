"""Tests for tools/export_sprite_gif.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import tools.export_sprite_gif as mod
from tools.export_sprite_gif import (
    build_parser,
    export_sprite_gif,
    frames_to_gif,
    preview_gif_path,
    resolve_animation_entry,
    slice_frames,
)

FRAME_W = 8
FRAME_H = 10


def _make_sheet(frames: int, width: int | None = None, height: int | None = None) -> Image.Image:
    """Build a synthetic RGBA strip; each frame a distinct opaque colour."""
    w = width if width is not None else FRAME_W * frames
    h = height if height is not None else FRAME_H
    sheet = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(frames):
        colour = (10 + i * 20, 30, 40, 255)
        block = Image.new("RGBA", (FRAME_W, FRAME_H), colour)
        sheet.paste(block, (i * FRAME_W, 0))
    return sheet


def _write_char(tmp_path: Path, monkeypatch, *, animations: list[dict],
                output_subdir: str = "hero") -> Path:
    """Wire up a fake PROJECT_ROOT with sprite defs + output dir; return root."""
    root = tmp_path
    defs_dir = root / "tools" / "sprite_defs" / "characters"
    defs_dir.mkdir(parents=True)
    output_dir = f"assets/sprites/{output_subdir}"
    config = {
        "frame_width": FRAME_W,
        "frame_height": FRAME_H,
        "output_dir": output_dir,
        "animations": animations,
    }
    (defs_dir / "hero.json").write_text(json.dumps(config), encoding="utf-8")
    (root / output_dir).mkdir(parents=True)

    monkeypatch.setattr(mod, "PROJECT_ROOT", root)
    monkeypatch.setattr(mod, "SPRITE_DEFS_DIR", defs_dir)
    return root


# --- slicing (native resolution, no scaling) ------------------------------

def test_slice_frames_count_and_native_dims():
    sheet = _make_sheet(4)
    frames = slice_frames(sheet, FRAME_W, FRAME_H, 4)
    assert len(frames) == 4
    # Native resolution: each frame equals frame_width x frame_height.
    assert all(f.size == (FRAME_W, FRAME_H) for f in frames)


def test_slice_frames_rejects_wrong_width():
    sheet = _make_sheet(3, width=FRAME_W * 4)  # claims 3 frames, 4-wide
    with pytest.raises(ValueError, match="stale or corrupt"):
        slice_frames(sheet, FRAME_W, FRAME_H, 3)


def test_slice_frames_rejects_wrong_height():
    sheet = _make_sheet(3, height=FRAME_H + 5)
    with pytest.raises(ValueError, match="stale or corrupt"):
        slice_frames(sheet, FRAME_W, FRAME_H, 3)


# --- frames_to_gif core ---------------------------------------------------

def test_frames_to_gif_writes_native_resolution(tmp_path):
    frames = slice_frames(_make_sheet(3), FRAME_W, FRAME_H, 3)
    out = frames_to_gif(frames, tmp_path / "a.gif")
    with Image.open(out) as gif:
        assert gif.n_frames == 3  # type: ignore[attr-defined]  # GifImageFile at runtime
        assert gif.size == (FRAME_W, FRAME_H)  # unchanged, no upscale


def test_frames_to_gif_composites_transparent_over_background(tmp_path):
    transparent = [Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))]
    out = frames_to_gif(transparent, tmp_path / "b.gif")
    with Image.open(out) as gif:
        assert gif.convert("RGB").getpixel((0, 0)) == (64, 64, 64)


@pytest.mark.parametrize("bad_fps", [0, -1, -8])
def test_frames_to_gif_rejects_nonpositive_fps(tmp_path, bad_fps):
    frames = slice_frames(_make_sheet(2), FRAME_W, FRAME_H, 2)
    with pytest.raises(ValueError, match="fps must be > 0"):
        frames_to_gif(frames, tmp_path / "c.gif", fps=bad_fps)


def test_frames_to_gif_rejects_empty(tmp_path):
    with pytest.raises(ValueError, match="at least one frame"):
        frames_to_gif([], tmp_path / "d.gif")


# --- animation entry resolution ------------------------------------------

def test_resolve_animation_entry_matches_source():
    config = {"animations": [{"source": "idle.png", "frames": 4}]}
    entry = resolve_animation_entry(config, "idle")
    assert entry["frames"] == 4


def test_resolve_animation_entry_missing_lists_valid_names():
    config = {"animations": [
        {"source": "idle.png", "frames": 4},
        {"source": "walk.png", "frames": 6},
    ]}
    with pytest.raises(ValueError) as exc:
        resolve_animation_entry(config, "run")
    msg = str(exc.value)
    assert "idle" in msg and "walk" in msg


# --- end-to-end export ----------------------------------------------------

def test_export_writes_gif_at_native_resolution(tmp_path, monkeypatch):
    root = _write_char(tmp_path, monkeypatch,
                       animations=[{"source": "idle.png", "frames": 3}])
    _make_sheet(3).save(root / "assets" / "sprites" / "hero" / "idle.png")

    out = export_sprite_gif("hero", "idle", fps=8)

    assert out == root / "assets" / "previews" / "hero" / "idle.gif"
    assert out.exists()
    with Image.open(out) as gif:
        assert gif.n_frames == 3  # type: ignore[attr-defined]  # GifImageFile at runtime
        assert gif.size == (FRAME_W, FRAME_H)


def test_export_resolves_output_alias(tmp_path, monkeypatch):
    """A sling_attack entry whose real file is sling.png must be found."""
    root = _write_char(tmp_path, monkeypatch, animations=[
        {"source": "sling_attack.png", "output": "sling.png", "frames": 2},
    ])
    # Only sling.png exists on disk (the aliased output name).
    _make_sheet(2).save(root / "assets" / "sprites" / "hero" / "sling.png")

    out = export_sprite_gif("hero", "sling_attack")
    # GIF is named after the animation (source stem), not the sheet file.
    assert out.name == "sling_attack.gif"
    assert out.exists()
    with Image.open(out) as gif:
        assert gif.n_frames == 2  # type: ignore[attr-defined]  # GifImageFile at runtime


def test_export_honours_out_override(tmp_path, monkeypatch):
    root = _write_char(tmp_path, monkeypatch,
                       animations=[{"source": "idle.png", "frames": 2}])
    _make_sheet(2).save(root / "assets" / "sprites" / "hero" / "idle.png")
    dest = tmp_path / "custom" / "look.gif"

    out = export_sprite_gif("hero", "idle", out=dest)
    assert out == dest
    assert dest.exists()


# --- error paths ----------------------------------------------------------

def test_export_missing_config_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "SPRITE_DEFS_DIR", tmp_path / "nowhere")
    with pytest.raises(FileNotFoundError, match="ghost"):
        export_sprite_gif("ghost", "idle")


def test_export_missing_sheet_points_to_processor(tmp_path, monkeypatch):
    _write_char(tmp_path, monkeypatch,
                animations=[{"source": "idle.png", "frames": 3}])
    # Sheet file never created on disk.
    with pytest.raises(FileNotFoundError, match="process_character_sprites"):
        export_sprite_gif("hero", "idle")


def test_export_dimension_mismatch_raises(tmp_path, monkeypatch):
    root = _write_char(tmp_path, monkeypatch,
                       animations=[{"source": "idle.png", "frames": 4}])
    # Save a 3-frame sheet where the def claims 4 frames.
    _make_sheet(3).save(root / "assets" / "sprites" / "hero" / "idle.png")
    with pytest.raises(ValueError, match="stale or corrupt"):
        export_sprite_gif("hero", "idle")


@pytest.mark.parametrize("bad_fps", [0, -1, -8])
def test_export_rejects_nonpositive_fps(tmp_path, monkeypatch, bad_fps):
    root = _write_char(tmp_path, monkeypatch,
                       animations=[{"source": "idle.png", "frames": 2}])
    _make_sheet(2).save(root / "assets" / "sprites" / "hero" / "idle.png")
    with pytest.raises(ValueError, match="fps must be > 0"):
        export_sprite_gif("hero", "idle", fps=bad_fps)


# --- CLI ------------------------------------------------------------------

def test_build_parser_defaults_and_help():
    parser = build_parser()
    args = parser.parse_args(["balchar", "idle"])
    assert args.fps == 8
    assert args.out is None
    # --scale was removed; it must not be a recognised option.
    assert not hasattr(args, "scale")
    actions = {a.dest: a for a in parser._actions}
    assert actions["character"].help
    assert actions["animation"].help


def test_preview_gif_path_is_previews_sibling():
    output_dir = Path("/proj/assets/sprites/balchar")
    path = preview_gif_path(output_dir, "idle")
    assert path == Path("/proj/assets/previews/balchar/idle.gif")
