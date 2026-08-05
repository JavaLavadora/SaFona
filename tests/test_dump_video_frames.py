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
    dump_video,
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


def test_dump_video_invokes_ffmpeg_and_resets(tmp_path: Path):
    video = tmp_path / "01_video.mp4"
    video.write_bytes(b"")
    out_dir = tmp_path / "02_dumps"
    out_dir.mkdir(parents=True)
    (out_dir / "stale.png").write_bytes(b"")  # leftover from previous run

    with patch("tools.dump_video_frames.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        dump_video(video, out_dir, k=10, reset=True)

    assert not (out_dir / "stale.png").exists()
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"


def test_dump_video_errors_when_video_missing(tmp_path: Path):
    video = tmp_path / "01_video.mp4"  # does not exist
    out_dir = tmp_path / "02_dumps"

    with pytest.raises(FileNotFoundError, match="01_video.mp4"):
        dump_video(video, out_dir, k=10, reset=False)
