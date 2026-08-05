"""Dump frames from the img2vid animation video for visual pruning.

Stage 3 of the img2vid sprite pipeline. Runs ffmpeg to extract every Kth
frame from the single 01_video.mp4 (produced by feeding the master idle to
img2vid with the animation's prompt) into the 02_dumps/ folder. The user
then manually deletes dumps they don't want.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"


def resolve_ffmpeg_exe() -> str:
    """Return the path to an ffmpeg executable to run Stage 3.

    Prefers the static ffmpeg binary shipped by ``imageio-ffmpeg`` (installed
    via the project's ``dev`` extra), which is a modern build supporting
    ``-fps_mode vfr``. Falls back to a system ``ffmpeg`` on PATH when the
    package isn't installed.

    Returns:
        Absolute path to the imageio-ffmpeg binary, or the string ``"ffmpeg"``
        to be resolved against PATH.
    """
    try:
        import imageio_ffmpeg
    except ImportError:
        # imageio-ffmpeg not installed: defer to a system ffmpeg on PATH.
        # dump_video() raises an actionable error if that's missing too.
        return "ffmpeg"
    return imageio_ffmpeg.get_ffmpeg_exe()


def build_ffmpeg_command(
    video: Path, out_dir: Path, k: int, ffmpeg_exe: str = "ffmpeg"
) -> list[str]:
    """Return the ffmpeg argv that extracts every Kth frame.

    Args:
        video: Path to the source MP4 (01_video.mp4).
        out_dir: Destination directory (must exist; caller creates).
        k: Extract every Kth frame.
        ffmpeg_exe: Path to the ffmpeg executable (see resolve_ffmpeg_exe).

    Returns:
        argv list ready for subprocess.run.
    """
    return [
        ffmpeg_exe,
        "-loglevel", "error",
        "-i", str(video),
        "-vf", f"select=not(mod(n\\,{k}))",
        "-fps_mode", "vfr",  # -vsync vfr was deprecated in ffmpeg 5.1
        str(out_dir / "dump_%04d.png"),
    ]


def dump_video(video: Path, out_dir: Path, k: int, reset: bool) -> int:
    """Extract every Kth frame from the single animation video.

    Args:
        video: Source MP4 path (01_video.mp4).
        out_dir: 02_dumps/ folder.
        k: Extract every Kth frame.
        reset: If True, wipe out_dir contents first.

    Returns:
        Number of dump_*.png files in out_dir after extraction.

    Raises:
        FileNotFoundError: If the source video does not exist.
    """
    if not video.exists():
        raise FileNotFoundError(
            f"expected the img2vid output at {video} (01_video.mp4); drop the "
            f"downloaded MP4 there before running Stage 3."
        )
    if reset and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_ffmpeg_command(video, out_dir, k, resolve_ffmpeg_exe())
    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "no ffmpeg available; install the dev extra with "
            "`pip install -e \".[dev]\"` (provides ffmpeg via imageio-ffmpeg), "
            "or install a system ffmpeg >= 5.1 (-fps_mode vfr requires it)."
        ) from exc
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {video}")

    return len(list(out_dir.glob("dump_*.png")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character")
    parser.add_argument("animation")
    parser.add_argument("--k", type=int, default=10,
                        help="Extract every Kth frame (default: 10)")
    parser.add_argument("--reset", action="store_true",
                        help="Wipe the 02_dumps/ folder before extracting")
    args = parser.parse_args()

    work_dir = WORK_ROOT / args.character / args.animation
    video = work_dir / "01_video.mp4"
    dump_dir = work_dir / "02_dumps"

    n = dump_video(video, dump_dir, args.k, args.reset)
    print(f"{video.name}: {n} frames -> {dump_dir}")


if __name__ == "__main__":
    main()
