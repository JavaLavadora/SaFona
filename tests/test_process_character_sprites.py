"""Tests for tools/process_character_sprites.py.

Focused on the preview-GIF integration (every run emits a GIF per
animation by default; --no-preview-gif suppresses it). The chroma-key /
cropping / scaling internals are exercised elsewhere.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import tools.process_character_sprites as mod
from tools.process_character_sprites import build_parser, process_character

FRAME_W = 8
FRAME_H = 10


def _make_source(path: Path, frames: int) -> None:
    """Write a green-screen source strip: `frames` red blocks on green."""
    path.parent.mkdir(parents=True, exist_ok=True)
    strip_w = 20
    img = Image.new("RGBA", (strip_w * frames, 16), (0, 255, 0, 255))
    for i in range(frames):
        # Distinct colour/position per frame so the GIF has real motion.
        block = Image.new("RGBA", (12, 12), (200, 40 + i * 30, 50, 255))
        img.paste(block, (i * strip_w + 2 + i, 2))
    img.save(path)


def _write_config(root: Path, *, frames: int = 2) -> Path:
    """Create sprite def + source; return the config path."""
    config = {
        "frame_width": FRAME_W,
        "frame_height": FRAME_H,
        "source_dir": "assets/ai_sources/hero",
        "output_dir": "assets/sprites/hero",
        "split_mode": "equal",
        "animations": [{"source": "idle.png", "frames": frames, "scale_pct": 100}],
    }
    config_path = root / "hero.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    _make_source(root / "assets" / "ai_sources" / "hero" / "idle.png", frames)
    return config_path


def test_process_character_emits_preview_gif_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    config_path = _write_config(tmp_path, frames=2)

    successes, failures = process_character(config_path)

    assert (successes, failures) == (1, 0)
    sheet = tmp_path / "assets" / "sprites" / "hero" / "idle.png"
    gif = tmp_path / "assets" / "previews" / "hero" / "idle.gif"
    assert sheet.exists()
    assert gif.exists()
    with Image.open(gif) as g:
        assert g.n_frames == 2  # type: ignore[attr-defined]  # GifImageFile at runtime
        assert g.size == (FRAME_W, FRAME_H)  # native resolution, no upscale


def test_process_character_no_preview_gif_suppresses(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    config_path = _write_config(tmp_path, frames=2)

    process_character(config_path, emit_preview=False)

    # The sheet is still written; only the GIF is skipped.
    assert (tmp_path / "assets" / "sprites" / "hero" / "idle.png").exists()
    assert not (tmp_path / "assets" / "previews" / "hero" / "idle.gif").exists()
    assert not (tmp_path / "assets" / "previews").exists()


def test_no_preview_gif_flag_defaults_off():
    parser = build_parser()
    assert parser.parse_args(["cfg.json"]).no_preview_gif is False
    assert parser.parse_args(["cfg.json", "--no-preview-gif"]).no_preview_gif is True
