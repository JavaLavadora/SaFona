"""Tests for tools/assemble_sprite_sheet.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.assemble_sprite_sheet import (
    assemble,
    chain_process_script,
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
    # 100/200 = 0.5 -> width should be 20
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


def test_compute_source_anchor_rejects_masking_failure():
    """A near-empty idle (tiny body) must raise, not return a bogus anchor."""
    img = Image.new("RGBA", (32, 48), (0, 255, 0, 255))
    for y in range(46, 48):  # 2-px body -> well under 50% of height
        for x in range(10, 22):
            img.putpixel((x, y), (200, 100, 50, 255))

    with pytest.raises(ValueError, match="masking failure"):
        compute_source_anchor(img)


def test_composite_onto_canvas_anchors_at_y():
    canvas_w, canvas_h = 32, 48
    char = Image.new("RGBA", (12, 30), (200, 100, 50, 255))

    out = composite_onto_canvas(char, canvas_w, canvas_h, anchor_y=47)
    # Bottom row should contain the character color
    assert out.getpixel((canvas_w // 2, 47))[:3] == (200, 100, 50)
    # Top row should still be chroma green
    assert out.getpixel((canvas_w // 2, 0))[:3] == (0, 255, 0)


def test_pack_horizontal_concatenates_in_order():
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
    chroma or exact palette colors -- no semi-transparent edges, no blended
    pixels. Downstream chroma-key in process_character_sprites.py relies on
    this invariant (it only removes pixels where G-R > 40 and G-B > 40, so
    anti-aliased green edges would bake green-tinted pixels into the asset).
    """
    palette = [(200, 100, 50), (100, 50, 25)]
    char = Image.new("RGBA", (4, 6), (200, 100, 50, 255))
    # Introduce a semi-transparent edge to force the threshold path:
    for y in range(6):
        char.putpixel((0, y), (200, 100, 50, 64))  # alpha 64 < 128 -> chroma

    out = composite_onto_canvas(char, 8, 8, anchor_y=7)
    arr = np.array(out)
    allowed = {(0, 255, 0, 255)} | {(*c, 255) for c in palette}
    seen = {tuple(p) for p in arr.reshape(-1, 4)}
    assert seen.issubset(allowed), (
        f"composite leaked non-allowed colors: {seen - allowed}"
    )


def test_resolve_output_filename_uses_output_field_when_present():
    """balchar.json's sling_attack entry sets "output": "sling.png" -- the
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


def test_assemble_rejects_idle_animation():
    """idle IS the immutable master seed -- Stage 4 must never assemble it."""
    with pytest.raises(ValueError, match="immutable master idle seed"):
        assemble("balchar", "idle", bg_mode="chroma", warn_scale_pct=15.0)


def test_chain_treats_output_exists_as_success(tmp_path: Path):
    """chain_process_script must NOT rely on the subprocess return code:
    process_character_sprites.py exits non-zero when any OTHER animation's
    source is absent (normal mid-generation). Success is defined solely as
    'the resolved output file exists after the run'.
    """
    char = "toy"
    output_dir = tmp_path / "sprites" / char
    output_dir.mkdir(parents=True)
    config_text = (
        '{"source_dir": "src/toy", "output_dir": "%s",'
        ' "animations": [{"source": "walk.png", "frames": 2}]}'
        % output_dir.as_posix()
    )
    char_json = tmp_path / f"{char}.json"
    char_json.write_text(config_text)
    script = tmp_path / "tools" / "process_character_sprites.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("")  # existence is all chain_process_script checks

    def fake_run(cmd, check):
        # Simulate the canonical script producing the output despite a
        # non-zero exit for other missing animations.
        (output_dir / "walk.png").write_bytes(b"png")
        class R:  # noqa: D401 - trivial return stub
            returncode = 1
        return R()

    with patch("tools.assemble_sprite_sheet.PROJECT_ROOT", tmp_path), \
         patch("tools.assemble_sprite_sheet.CHAR_DEF_ROOT", tmp_path), \
         patch("tools.assemble_sprite_sheet.subprocess.run", side_effect=fake_run):
        result = chain_process_script(char, "walk")

    assert result == output_dir / "walk.png"
    assert result.exists()


def test_chain_raises_when_output_missing(tmp_path: Path):
    """If the resolved output never appears, chain must raise even on exit 0."""
    char = "toy"
    output_dir = tmp_path / "sprites" / char
    output_dir.mkdir(parents=True)
    config_text = (
        '{"source_dir": "src/toy", "output_dir": "%s",'
        ' "animations": [{"source": "walk.png", "frames": 2}]}'
        % output_dir.as_posix()
    )
    char_json = tmp_path / f"{char}.json"
    char_json.write_text(config_text)
    script = tmp_path / "tools" / "process_character_sprites.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("")

    def fake_run(cmd, check):
        class R:
            returncode = 0
        return R()

    with patch("tools.assemble_sprite_sheet.PROJECT_ROOT", tmp_path), \
         patch("tools.assemble_sprite_sheet.CHAR_DEF_ROOT", tmp_path), \
         patch("tools.assemble_sprite_sheet.subprocess.run", side_effect=fake_run):
        with pytest.raises(FileNotFoundError, match="expected output"):
            chain_process_script(char, "walk")


def test_source_resolution_canvas_matches_master_idle(tmp_path: Path, monkeypatch):
    """The assembled canvas must be sized to the MASTER IDLE's native
    dimensions (source resolution), NOT the game frame_width/frame_height.
    process_character_sprites.py owns the sole downscale.
    """
    char = "toy"
    idle_w, idle_h = 120, 200  # deliberately not 48x64
    source_dir = tmp_path / "src" / char
    source_dir.mkdir(parents=True)
    dump_dir = tmp_path / "img2vid" / char / "walk" / "02_dumps"
    dump_dir.mkdir(parents=True)

    # Master idle: green canvas with a tall body occupying most of the height.
    idle = Image.new("RGBA", (idle_w, idle_h), (0, 255, 0, 255))
    for y in range(20, idle_h):
        for x in range(40, 80):
            idle.putpixel((x, y), (200, 100, 50, 255))
    idle.save(source_dir / "idle.png")

    # A dump frame with a body on green.
    dump = Image.new("RGBA", (64, 96), (0, 255, 0, 255))
    for y in range(30, 96):
        for x in range(20, 44):
            dump.putpixel((x, y), (200, 100, 50, 255))
    dump.save(dump_dir / "dump_0000.png")

    config = {
        "source_dir": (source_dir.relative_to(tmp_path)).as_posix(),
        "output_dir": "out/toy",
        "animations": [{"source": "walk.png", "frames": 1}],
    }
    char_json = tmp_path / f"{char}.json"
    char_json.write_text(__import__("json").dumps(config))

    monkeypatch.setattr("tools.assemble_sprite_sheet.PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("tools.assemble_sprite_sheet.CHAR_DEF_ROOT", tmp_path)
    monkeypatch.setattr("tools.assemble_sprite_sheet.WORK_ROOT",
                        tmp_path / "img2vid")
    monkeypatch.setattr(
        "tools.assemble_sprite_sheet.load_palette_for",
        lambda _c: np.array([(200, 100, 50), (100, 50, 25)]),
    )

    raw_out, source_copy = assemble(char, "walk", bg_mode="chroma",
                                    warn_scale_pct=100.0)
    sheet = Image.open(raw_out)
    # One frame -> sheet width == canvas width == master idle width.
    assert sheet.size == (idle_w, idle_h)
    assert source_copy == source_dir / "walk.png"
    # Postcondition still holds on the real assembled sheet.
    allowed = {(0, 255, 0, 255), (200, 100, 50, 255), (100, 50, 25, 255)}
    seen = {tuple(p) for p in np.array(sheet).reshape(-1, 4)}
    assert seen.issubset(allowed), f"leaked: {seen - allowed}"
