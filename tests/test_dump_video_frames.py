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
    build_parser,
    dump_video,
    resolve_ffmpeg_exe,
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


def test_dump_video_invokes_ffmpeg(tmp_path: Path):
    video = tmp_path / "01_video.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "02_dumps"

    with patch("tools.dump_video_frames.subprocess.run") as mock_run, patch(
        "tools.dump_video_frames.resolve_ffmpeg_exe", return_value="ffmpeg"
    ):
        mock_run.return_value.returncode = 0
        dump_video(video, out_dir, k=10)

    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"


def test_dump_video_leaves_no_stale_dumps_on_rerun(tmp_path: Path):
    """A re-run on a shorter video must not leave higher-numbered stale
    frames from a prior longer run (E2)."""
    video = tmp_path / "01_video.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "02_dumps"
    # Simulate a prior, longer run: dump_0001..dump_0005 already on disk.
    out_dir.mkdir(parents=True)
    for i in range(1, 6):
        (out_dir / f"dump_{i:04d}.png").write_bytes(b"")

    # The re-run's ffmpeg only emits two frames (a shorter video).
    def fake_run(cmd, *args, **kwargs):
        for i in range(1, 3):
            (out_dir / f"dump_{i:04d}.png").write_bytes(b"")
        return type("R", (), {"returncode": 0})()

    with patch("tools.dump_video_frames.subprocess.run", side_effect=fake_run), patch(
        "tools.dump_video_frames.resolve_ffmpeg_exe", return_value="ffmpeg"
    ):
        n = dump_video(video, out_dir, k=10)

    dumps = sorted(p.name for p in out_dir.glob("dump_*.png"))
    assert dumps == ["dump_0001.png", "dump_0002.png"]
    assert n == 2  # returned count reflects only the current run


def test_dump_video_errors_when_video_missing(tmp_path: Path):
    video = tmp_path / "01_video.mp4"  # does not exist
    out_dir = tmp_path / "02_dumps"

    with pytest.raises(FileNotFoundError, match="01_video.mp4"):
        dump_video(video, out_dir, k=10)


@pytest.mark.parametrize("bad_k", [0, -1, -10])
def test_dump_video_rejects_nonpositive_k(tmp_path: Path, bad_k: int):
    """--k < 1 must fail fast with a clear message, before touching ffmpeg."""
    video = tmp_path / "01_video.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "02_dumps"

    with patch("tools.dump_video_frames.subprocess.run") as mock_run:
        with pytest.raises(ValueError, match=rf"--k must be >= 1 \(got {bad_k}\)"):
            dump_video(video, out_dir, k=bad_k)

    assert not mock_run.called


def test_build_parser_has_help_on_positionals():
    """character/animation positionals must carry help text (A2)."""
    parser = build_parser()
    actions = {a.dest: a for a in parser._actions}
    assert actions["character"].help
    assert actions["animation"].help


def test_resolve_ffmpeg_prefers_imageio_binary():
    """The static imageio-ffmpeg binary wins over a bare PATH lookup."""
    fake = type(sys)("imageio_ffmpeg")
    fake.get_ffmpeg_exe = lambda: "/opt/imageio/ffmpeg"  # type: ignore[attr-defined]

    with patch.dict(sys.modules, {"imageio_ffmpeg": fake}):
        assert resolve_ffmpeg_exe() == "/opt/imageio/ffmpeg"


def test_resolve_ffmpeg_falls_back_to_path_ffmpeg():
    """Without imageio-ffmpeg installed, fall back to a system ffmpeg."""
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "imageio_ffmpeg":
            raise ImportError("no imageio-ffmpeg")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        assert resolve_ffmpeg_exe() == "ffmpeg"
