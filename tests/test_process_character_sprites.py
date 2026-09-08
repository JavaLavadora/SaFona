"""Tests for tools/process_character_sprites.py.

Focused on the preview-GIF integration (every run emits a GIF per
animation by default; --no-preview-gif suppresses it). The chroma-key /
cropping / scaling internals are exercised elsewhere.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import tools.process_character_sprites as mod
from tools.process_character_sprites import build_parser, main, process_character

FRAME_W = 8
FRAME_H = 10


def _make_source(path: Path, frames: int, block_h: int = 12) -> None:
    """Write a green-screen source strip: `frames` red blocks on green."""
    path.parent.mkdir(parents=True, exist_ok=True)
    strip_w = 20
    img = Image.new("RGBA", (strip_w * frames, 24), (0, 255, 0, 255))
    for i in range(frames):
        # Distinct colour/position per frame so the GIF has real motion.
        block = Image.new("RGBA", (12, block_h), (200, 40 + i * 30, 50, 255))
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


def _write_multi_config(root: Path) -> Path:
    """Two animations with deliberately different crop heights.

    ``walk`` is the tallest (drives the shared global max height); ``idle``
    is shorter. Restricting a run to ``idle`` must still measure ``walk``.
    """
    config = {
        "frame_width": FRAME_W,
        "frame_height": FRAME_H,
        "source_dir": "assets/ai_sources/hero",
        "output_dir": "assets/sprites/hero",
        "split_mode": "equal",
        "animations": [
            {"source": "walk.png", "frames": 2, "scale_pct": 100},
            {"source": "idle.png", "frames": 2, "scale_pct": 100},
        ],
    }
    config_path = root / "hero.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    _make_source(root / "assets" / "ai_sources" / "hero" / "walk.png", 2, block_h=20)
    _make_source(root / "assets" / "ai_sources" / "hero" / "idle.png", 2, block_h=8)
    return config_path


def _base_scale_from_log(caplog) -> tuple[float, int]:
    """Extract (base_scale, global_max_h) from the 'Base scale:' log line."""
    for record in caplog.records:
        m = re.search(
            r"Base scale: ([\d.]+) \(global max_h=(\d+)", record.getMessage()
        )
        if m:
            return float(m.group(1)), int(m.group(2))
    raise AssertionError("no 'Base scale:' line was logged")


def test_only_preserves_global_base_scale(tmp_path, monkeypatch, caplog):
    """The scale-consistency invariant: --only must NOT change base_scale.

    Steps 1-2 measure EVERY animation's crop height regardless of --only, so
    the shared base scale computed from the global max height is identical to
    a full run. If --only skipped loading the other animations, base_scale
    would be computed from a smaller sample and drift -- this guards that.
    """
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    config_path = _write_multi_config(tmp_path)

    with caplog.at_level("INFO"):
        process_character(config_path, emit_preview=False)
        full_scale, full_max_h = _base_scale_from_log(caplog)

    caplog.clear()

    with caplog.at_level("INFO"):
        process_character(config_path, emit_preview=False, only="idle")
        only_scale, only_max_h = _base_scale_from_log(caplog)

    assert only_max_h == full_max_h
    assert only_scale == full_scale


def test_only_writes_single_animation(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    config_path = _write_multi_config(tmp_path)

    successes, failures = process_character(config_path, only="walk")

    assert (successes, failures) == (1, 0)
    sprites = tmp_path / "assets" / "sprites" / "hero"
    previews = tmp_path / "assets" / "previews" / "hero"
    assert (sprites / "walk.png").exists()
    assert (previews / "walk.gif").exists()
    # The other animation is neither saved nor previewed.
    assert not (sprites / "idle.png").exists()
    assert not (previews / "idle.gif").exists()


def test_only_unknown_animation_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    config_path = _write_multi_config(tmp_path)

    with pytest.raises(ValueError, match="valid animations: idle, walk"):
        process_character(config_path, only="run")


def test_only_with_multiple_configs_errors(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "a.json", "b.json", "--only", "walk"])
    with pytest.raises(SystemExit):
        main()
    assert "cannot" in capsys.readouterr().err
