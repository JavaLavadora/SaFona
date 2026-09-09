"""Export a character animation's sprite sheet to an animated GIF.

Standalone dev utility for eyeballing an animation loop without launching
the game. Given a character slug and animation name, it reads the sprite
def JSON (``tools/sprite_defs/characters/<character>.json``), locates the
already-assembled horizontal sprite sheet under the character's
``output_dir``, slices it into frames, composites each over an opaque
background (GIF has no real alpha), and writes a looping GIF at native
resolution.

The GIF-writing core (:func:`frames_to_gif`) is also imported by
``process_character_sprites.py``, which emits a preview GIF for every
animation as part of its normal run. This CLI stays useful for
regenerating a single GIF without reprocessing, or for characters
processed before that integration existed.

Frames are exported at native resolution (e.g. 48x64); zoom in your viewer
if you need a closer look.

Usage:
    python tools/export_sprite_gif.py <character> <animation> [--fps 8]
                                      [--out PATH]

The ``--fps`` is a playback speed for visualisation only; it does NOT match
the engine's per-frame in-game timing (which this tool has no access to).
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPRITE_DEFS_DIR = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"
BACKGROUND_RGBA = (64, 64, 64, 255)
DEFAULT_FPS = 8

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


def frames_to_gif(
    frames: list[Image.Image],
    out_path: Path,
    fps: int = DEFAULT_FPS,
    background: tuple[int, int, int, int] = BACKGROUND_RGBA,
) -> Path:
    """Composite RGBA frames over an opaque background and write a looping GIF.

    Shared core used both by this tool's CLI and by
    ``process_character_sprites.py``. Frames are written at their native
    resolution (no scaling). Each frame is composited onto an opaque
    ``background`` because GIF supports only binary transparency, so naive
    alpha export fringes badly.

    Args:
        frames: Non-empty list of same-sized frames (any mode; converted to
            RGBA for compositing).
        out_path: Destination ``.gif`` path; parent dirs are created.
        fps: Playback frames per second (> 0).
        background: Opaque RGBA fill to composite each frame onto.

    Returns:
        ``out_path``.

    Raises:
        ValueError: If ``fps <= 0`` or ``frames`` is empty.
    """
    if fps <= 0:
        raise ValueError(f"fps must be > 0 (got {fps})")
    if not frames:
        raise ValueError("frames_to_gif requires at least one frame")

    composited: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", frame.size, background)
        canvas.alpha_composite(frame.convert("RGBA"))
        composited.append(canvas.convert("RGB"))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    composited[0].save(
        out_path,
        save_all=True,
        append_images=composited[1:],
        duration=round(1000 / fps),
        loop=0,
    )
    return out_path


def preview_gif_path(output_dir: Path, animation: str) -> Path:
    """Return the preview GIF path for an animation.

    Sibling to ``assets/sprites/`` at
    ``assets/previews/<character>/<animation>.gif``, derived from the
    character's absolute ``output_dir`` (``.../sprites/<character>``).

    Args:
        output_dir: Absolute sprite output dir (e.g.
            ``<root>/assets/sprites/balchar``).
        animation: Animation name without extension.

    Returns:
        Absolute output path for the GIF.
    """
    return output_dir.parent.parent / "previews" / output_dir.name / f"{animation}.gif"


def load_character_config(character: str) -> dict[str, Any]:
    """Load and parse a character's sprite def JSON.

    Args:
        character: Character slug, resolving to
            ``tools/sprite_defs/characters/<character>.json``.

    Returns:
        The parsed config dict.

    Raises:
        FileNotFoundError: If the config JSON does not exist.
    """
    config_path = SPRITE_DEFS_DIR / f"{character}.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"no sprite def for '{character}' at {config_path}; "
            f"expected tools/sprite_defs/characters/<character>.json"
        )
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def resolve_animation_entry(config: dict[str, Any], animation: str) -> dict[str, Any]:
    """Return the animation entry whose ``source`` matches ``<animation>.png``.

    Mirrors process_character_sprites.py: the CLI takes the animation name
    without extension (e.g. ``sling_attack``), matched against each entry's
    ``source`` field. The real sprite filename is ``entry.get("output",
    entry["source"])`` -- so ``sling_attack`` resolves to ``sling.png``.

    Args:
        config: Parsed character config.
        animation: Animation name without the ``.png`` extension.

    Returns:
        The matching animation entry dict.

    Raises:
        ValueError: If no entry's ``source`` matches, listing valid names.
    """
    wanted = f"{animation}.png"
    for entry in config.get("animations", []):
        if entry.get("source") == wanted:
            return entry
    valid = sorted(
        Path(entry["source"]).stem
        for entry in config.get("animations", [])
        if "source" in entry
    )
    raise ValueError(
        f"no animation '{animation}' in sprite def; "
        f"valid animations: {', '.join(valid) or '(none)'}"
    )


def slice_frames(
    sheet: Image.Image, frame_width: int, frame_height: int, frames: int
) -> list[Image.Image]:
    """Slice a horizontal sprite strip into individual frames left-to-right.

    Args:
        sheet: The RGBA sprite sheet.
        frame_width: Width of a single frame in pixels.
        frame_height: Height of a single frame in pixels.
        frames: Number of frames to slice.

    Returns:
        A list of ``frames`` cropped RGBA frames, each
        ``frame_width`` x ``frame_height``.

    Raises:
        ValueError: If ``sheet`` dimensions do not match
            ``frame_width * frames`` by ``frame_height``.
    """
    expected_w = frame_width * frames
    if sheet.width != expected_w or sheet.height != frame_height:
        raise ValueError(
            f"sprite sheet is {sheet.width}x{sheet.height}px but the sprite "
            f"def expects {expected_w}x{frame_height}px "
            f"({frames} frames of {frame_width}x{frame_height}); "
            f"the sheet is stale or corrupt -- re-run process_character_sprites.py"
        )
    return [
        sheet.crop((i * frame_width, 0, (i + 1) * frame_width, frame_height))
        for i in range(frames)
    ]


def export_sprite_gif(
    character: str,
    animation: str,
    fps: int = DEFAULT_FPS,
    out: Path | None = None,
) -> Path:
    """Export a character animation's sprite sheet to an animated GIF.

    Args:
        character: Character slug (resolves the sprite def JSON).
        animation: Animation name without extension (e.g. ``sling_attack``).
        fps: Playback frames per second for the GIF (> 0).
        out: Output path override. Defaults to
            ``assets/previews/<character>/<animation>.gif``.

    Returns:
        The path the GIF was written to.

    Raises:
        ValueError: If ``fps <= 0``, no animation matches, or the sheet
            dimensions disagree with the sprite def.
        FileNotFoundError: If the config JSON or the sprite sheet is missing.
    """
    config = load_character_config(character)
    entry = resolve_animation_entry(config, animation)

    output_dir = PROJECT_ROOT / config["output_dir"]
    sheet_name = entry.get("output", entry["source"])
    sheet_path = output_dir / sheet_name
    if not sheet_path.exists():
        raise FileNotFoundError(
            f"sprite sheet not found at {sheet_path}; "
            f"run process_character_sprites.py to generate it first"
        )

    sheet = Image.open(sheet_path).convert("RGBA")
    frames = slice_frames(
        sheet, config["frame_width"], config["frame_height"], entry["frames"]
    )

    out_path = Path(out) if out is not None else preview_gif_path(output_dir, animation)
    frames_to_gif(frames, out_path, fps=fps)
    log.info("%s %s: %d frames -> %s", character, animation, len(frames), out_path)
    return out_path


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the sprite GIF exporter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "character",
        help="Character slug (e.g. balchar); resolves the sprite def JSON",
    )
    parser.add_argument(
        "animation",
        help="Animation name without .png (e.g. sling_attack)",
    )
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS,
                        help=f"Playback frames per second (default: {DEFAULT_FPS})")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output GIF path (default: assets/previews/"
                             "<character>/<animation>.gif)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    export_sprite_gif(args.character, args.animation, fps=args.fps, out=args.out)


if __name__ == "__main__":
    main()
