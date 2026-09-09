"""Assemble a clean sprite sheet from img2vid dump frames.

Stage 4 of the img2vid sprite pipeline. For each surviving dump frame in
02_dumps/, removes the background, scales the character to the master idle's
body height, palette-quantizes against the character's .gpl palette, and
composites onto a chroma-green canvas the SIZE OF THE MASTER IDLE (i.e. at
source resolution, like the existing AI sources -- not the final game frame
size), anchored at the master idle's baseline. Packs the processed frames
into 03_assembled_raw.png, copies the same sheet into
<source_dir>/<animation>.png, then invokes the canonical
tools/process_character_sprites.py <character>.json as a subprocess for
final cleanup.

Emitting a source-resolution sheet lets process_character_sprites.py own the
single downscale to frame_width x frame_height, exactly as it does for any
other AI source. Scale and anchor come from the character's immutable master
idle still (<source_dir>/idle.png) -- the same seed every img2vid video was
generated from -- NOT from per-animation config. Anchoring every animation to
the one master idle keeps scale and baseline mutually consistent across the
whole character; per-animation vertical placement, scale_pct, and the final
game-frame downscale are all applied downstream by
process_character_sprites.py.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage  # connected-component rescue for --bg-mode both

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

WORK_ROOT = PROJECT_ROOT / "assets" / "ai_sources" / "img2vid"
CHAR_DEF_ROOT = PROJECT_ROOT / "tools" / "sprite_defs" / "characters"
PALETTE_ROOT = PROJECT_ROOT / "assets" / "palettes"

CHROMA_GREEN = (0, 255, 0)
CHROMA_GREEN_RGBA = (0, 255, 0, 255)
ALPHA_THRESHOLD = 128  # postcondition: alpha < 128 -> snap to chroma

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


def chroma_key_mask(img: Image.Image, threshold: int = 40) -> np.ndarray:
    """Return a 0/1 mask where 1 == foreground (non-green).

    Uses the same heuristic as the existing chroma-key pipeline in
    process_character_sprites.py: a pixel is background when
    ``g - r > threshold`` and ``g - b > threshold`` and ``g > 80``.

    Args:
        img: Source image (any mode; converted to RGB internally).
        threshold: Green-dominance cutoff.

    Returns:
        A ``(H, W)`` uint8 array; 1 marks foreground, 0 marks background.
    """
    arr = np.array(img.convert("RGB"))
    r = arr[..., 0].astype(int)
    g = arr[..., 1].astype(int)
    b = arr[..., 2].astype(int)
    bg = (g - r > threshold) & (g - b > threshold) & (g > 80)
    return (~bg).astype(np.uint8)


def rembg_mask(img: Image.Image) -> np.ndarray:
    """Return a 0/1 foreground mask via rembg/U2Net.

    The ``rembg`` import is deferred to call time so unit tests that never
    exercise this path do not load the ~150MB U2Net model.

    Args:
        img: Source image.

    Returns:
        A ``(H, W)`` uint8 array; 1 marks foreground, 0 marks background.
    """
    from rembg import remove

    cut = remove(img)
    if cut.mode != "RGBA":
        cut = cut.convert("RGBA")
    alpha = np.array(cut)[..., 3]
    return (alpha > 16).astype(np.uint8)


def apply_mask(img: Image.Image, mask: np.ndarray) -> Image.Image:
    """Return an RGBA image where ``mask == 0`` pixels are fully transparent.

    Args:
        img: Source image.
        mask: A ``(H, W)`` 0/1 array matching the image dimensions.

    Returns:
        An RGBA image with the mask applied to its alpha channel.
    """
    rgba = np.array(img.convert("RGBA"))
    rgba[..., 3] = mask * 255
    return Image.fromarray(rgba, mode="RGBA")


def remove_background(img: Image.Image, mode: str) -> Image.Image:
    """Remove the background using the requested strategy.

    For ``"both"``, uses rembg as the primary mask and rescues thin chroma-mask
    components (e.g. sling cord, headband ribbon) that are connected to the
    rembg foreground. Chroma components NOT touching the rembg foreground --
    e.g. anti-aliased green-edge halos -- are discarded. This defends thin
    features without amplifying AA edges.

    Args:
        img: Source image.
        mode: One of ``"chroma"``, ``"rembg"``, ``"both"``.

    Returns:
        An RGBA image with the background made transparent.

    Raises:
        ValueError: If ``mode`` is not a recognised strategy.
    """
    if mode == "chroma":
        mask = chroma_key_mask(img)
    elif mode == "rembg":
        mask = rembg_mask(img)
    elif mode == "both":
        rembg = rembg_mask(img)
        chroma = chroma_key_mask(img)
        # Components present in chroma but absent from rembg. Cast to bool
        # explicitly: `~` on a 0/1 uint8 array is bitwise-NOT (255/254), not
        # logical negation, so this must not rely on `chroma`'s 0/1 range to
        # mask it back down.
        missing = chroma.astype(bool) & ~rembg.astype(bool)
        labels, n = ndimage.label(missing, structure=np.ones((3, 3)))
        # Dilate rembg by 1px so "touching" includes diagonal neighbours.
        rembg_neighborhood = ndimage.binary_dilation(rembg.astype(bool))
        keep = np.zeros_like(rembg, dtype=bool)
        for label_id in range(1, n + 1):
            region = labels == label_id
            if (region & rembg_neighborhood).any():
                keep |= region
        mask = (rembg.astype(bool) | keep).astype(np.uint8)
    else:
        raise ValueError(f"unknown bg-mode: {mode}")
    return apply_mask(img, mask)


def tight_crop(img: Image.Image, padding: int = 0) -> Image.Image | None:
    """Crop to the bounding box of non-transparent pixels (+ padding).

    Args:
        img: Source RGBA image.
        padding: Extra pixels to keep around the bounding box.

    Returns:
        The cropped image, or ``None`` if ``img`` is fully transparent (no
        foreground to crop to). Callers MUST treat ``None`` as "skip this
        frame" -- see the caller in ``assemble()``.
    """
    bbox = img.getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)
    return img.crop((left, top, right, bottom))


def compute_source_anchor(
    source_frame: Image.Image, source_path: Path | str = "<unknown>"
) -> tuple[int, int]:
    """From the master idle still, derive ``(bbox_height, anchor_y)``.

    ``bbox_height`` is the height of the character body in the master idle.
    ``anchor_y`` is the y-coordinate of the bbox bottom in the master idle
    canvas, used to place every dump frame at the same baseline.

    Uses the chroma mask (NOT rembg) for the anchor: the master idle is a
    clean, single, immutable still on a solid green background, which is
    exactly where chroma is the reliable signal -- so the anchor never depends
    on loading the U2Net model. The bbox-height sanity clamp below still
    catches a masking failure (e.g. a chroma artifact eating most of the
    character) at the anchor stage.

    Bbox comes from the LARGEST connected foreground component only, not the
    raw mask -- some master idle stills carry small stray artifacts (e.g.
    Balchar's idle.png still has "1"/"2"/"3"/"4" candidate labels baked in
    above the pose), which would otherwise inflate the bbox with disconnected
    pixels unrelated to the character body.

    Args:
        source_frame: The master idle still, RGBA.
        source_path: Path used only for error messages.

    Returns:
        Tuple of ``(bbox_height, anchor_y)``.

    Raises:
        ValueError: If the master idle has no foreground after masking, or
            if the bbox height is below 50% of canvas height (signals the
            chroma key ate most of the character).
    """
    masked = remove_background(source_frame, "chroma")
    mask = np.array(masked)[:, :, 3] > 0
    labeled, n_features = ndimage.label(mask)
    if n_features == 0:
        raise ValueError(
            f"master idle at {source_path} has no foreground after "
            f"chroma-key; manually inspect and re-generate if needed."
        )
    sizes = ndimage.sum(mask, labeled, range(1, n_features + 1))
    largest_id = int(np.argmax(sizes)) + 1
    ys, xs = np.where(labeled == largest_id)
    top, bottom = int(ys.min()), int(ys.max()) + 1
    bbox_h = bottom - top
    if bbox_h < source_frame.height * 0.5:
        raise ValueError(
            f"master idle at {source_path} has no foreground after "
            f"chroma-key; manually inspect and re-generate if needed. "
            f"(bbox height {bbox_h}px is < 50% of canvas height "
            f"{source_frame.height}px -- likely a masking failure.)"
        )
    return (bbox_h, bottom - 1)


def downsample_to_height(img: Image.Image, target_height: int) -> Image.Image:
    """Downsample preserving aspect; bilinear pre-pass then NEAREST snap.

    Args:
        img: Source image.
        target_height: Desired output height in pixels.

    Returns:
        The resized image with width scaled to preserve aspect ratio.
    """
    if img.height == target_height:
        return img
    ratio = target_height / img.height
    target_width = max(1, int(round(img.width * ratio)))
    pre = img.resize((target_width * 2, target_height * 2), Image.BILINEAR)
    return pre.resize((target_width, target_height), Image.NEAREST)


def palette_quantize(img: Image.Image, palette: np.ndarray) -> Image.Image:
    """Snap each opaque pixel to its nearest palette color.

    Args:
        img: Source RGBA image.
        palette: An ``(N, 3)`` array of RGB triplets, matching the shape
            returned by ``tools.clean_sprites.parse_gpl``.

    Returns:
        A new RGBA image with each pixel's RGB replaced by the nearest palette
        color; the alpha channel is preserved.
    """
    rgba = np.array(img.convert("RGBA"))
    rgb = rgba[..., :3].astype(int)
    alpha = rgba[..., 3]

    pal = np.asarray(palette, dtype=int)
    # Distance from every pixel to every palette color
    diffs = rgb[..., None, :] - pal[None, None, :, :]
    dists = (diffs * diffs).sum(axis=-1)
    nearest = np.argmin(dists, axis=-1)
    quantized = pal[nearest]

    out = np.zeros_like(rgba)
    out[..., :3] = quantized
    out[..., 3] = alpha
    return Image.fromarray(out.astype(np.uint8), mode="RGBA")


def composite_onto_canvas(
    char: Image.Image, canvas_w: int, canvas_h: int, anchor_y: int
) -> Image.Image:
    """Paste the character onto a chroma-green canvas with its bottom at anchor_y.

    POSTCONDITION: every output pixel is either exactly ``(0, 255, 0, 255)``
    chroma OR a fully-opaque palette color. No semi-transparent edges, no
    blended green-tinted boundary pixels. The downstream chroma-key in
    process_character_sprites.py only removes pixels where ``(G-R > 40)`` and
    ``(G-B > 40)``, so anti-aliased green edges would bake green-tinted pixels
    into the final asset if this postcondition were relaxed.

    The threshold is applied to the character's OWN alpha BEFORE the paste:
    alpha >= 128 keeps the palette-quantized RGB and pastes at full opacity;
    alpha < 128 drops the pixel, so the chroma canvas shows through.
    Thresholding after the paste would be too late -- a soft edge would have
    already blended its palette RGB with the green canvas into an off-palette
    green-tinted colour that then survives the threshold.

    Args:
        char: The processed character frame, RGBA.
        canvas_w: Canvas width (master idle width).
        canvas_h: Canvas height (master idle height).
        anchor_y: y-coordinate at which to place the character's bottom row.

    Returns:
        The composited RGBA canvas.
    """
    # Harden the character's own alpha to a binary 0/255 mask first, so no
    # soft edge ever blends with the green canvas.
    char = char.convert("RGBA")
    arr = np.array(char)
    arr[..., 3] = np.where(arr[..., 3] >= ALPHA_THRESHOLD, 255, 0).astype(np.uint8)
    hard_char = Image.fromarray(arr, mode="RGBA")

    canvas = Image.new("RGBA", (canvas_w, canvas_h), CHROMA_GREEN_RGBA)
    paste_x = (canvas_w - hard_char.width) // 2
    paste_y = anchor_y - hard_char.height + 1
    # Use the hardened alpha as the paste mask: 255 -> char RGB, 0 -> chroma.
    canvas.paste(hard_char, (paste_x, paste_y), hard_char)
    return canvas


def pack_horizontal(frames: list[Image.Image]) -> Image.Image:
    """Concatenate frames into a single horizontal sheet.

    Args:
        frames: The processed frames, left-to-right.

    Returns:
        A single RGBA sheet.

    Raises:
        ValueError: If ``frames`` is empty.
    """
    if not frames:
        raise ValueError("no frames to pack")
    h = max(f.height for f in frames)
    total_w = sum(f.width for f in frames)
    sheet = Image.new("RGBA", (total_w, h), CHROMA_GREEN_RGBA)
    x = 0
    for f in frames:
        sheet.paste(f, (x, h - f.height), f if f.mode == "RGBA" else None)
        x += f.width
    return sheet


def load_palette_for(character: str) -> np.ndarray:
    """Load the character's palette from ``assets/palettes/<character>.gpl``.

    Uses the same parser as tools/clean_sprites.py so Stage 4 and the final
    cleanup quantize against identical color sets (idempotent).

    Args:
        character: Character slug (e.g. ``balchar``).

    Returns:
        An ``(N, 3)`` np.ndarray of RGB triplets.
    """
    from tools.clean_sprites import parse_gpl  # single source of truth
    palette_path = PALETTE_ROOT / f"{character}.gpl"
    return parse_gpl(palette_path)


def load_character_config(char_json_path: Path) -> dict:
    """Load and parse a character JSON config.

    Args:
        char_json_path: Path to ``tools/sprite_defs/characters/<char>.json``.

    Returns:
        The parsed config dict.
    """
    return json.loads(char_json_path.read_text())


def resolve_master_idle_reference(
    source_dir: Path, config: dict
) -> tuple[Image.Image, Path]:
    """Resolve the single-pose still used as the Stage-4 scale/anchor reference.

    Prefers ``<source_dir>/idle_master.png`` when present: a dedicated,
    tightly-cropped single pose for characters whose production
    ``<source_dir>/idle.png`` isn't shaped like a clean master still (e.g.
    Balchar's is a 4-up candidate-selection sheet with number labels, built
    for the old per-frame pipeline's connected-component cropping -- not a
    canvas-filling still). Lives in ``source_dir`` (tracked in git, unlike
    the img2vid work tree under WORK_ROOT, which is scratch-only) so the
    override travels with the repo. Falls back to ``<source_dir>/idle.png``
    itself, sliced to its first equal-width column when the idle entry
    declares more than one frame (a multi-frame idle breathing loop).

    Args:
        source_dir: The character's AI source directory (has idle.png).
        config: Parsed character JSON (as returned by load_character_config).

    Returns:
        Tuple of ``(reference_image, path_used_for_error_messages)``.
    """
    override_path = source_dir / "idle_master.png"
    if override_path.exists():
        return Image.open(override_path).convert("RGBA"), override_path

    idle_path = source_dir / "idle.png"
    master_idle = Image.open(idle_path).convert("RGBA")
    idle_frames = 1
    for entry in config.get("animations", []):
        if entry.get("source") == "idle.png":
            idle_frames = entry.get("frames", 1)
            break
    if idle_frames <= 1:
        return master_idle, idle_path
    frame_w = master_idle.width // idle_frames
    return master_idle.crop((0, 0, frame_w, master_idle.height)), idle_path


def assemble(
    character: str,
    animation: str,
    bg_mode: str,
    warn_scale_pct: float,
) -> tuple[Path, Path]:
    """Run the full Stage 4 pipeline.

    Emits a source-resolution sheet, not the final game frame size -- see the
    module docstring for the full rationale.

    Args:
        character: Character slug (e.g. ``balchar``).
        animation: Animation name (e.g. ``walk``).
        bg_mode: Background-removal strategy (``rembg``/``chroma``/``both``).
        warn_scale_pct: Drift threshold; a per-frame warning fires when a
            frame's character height, as a fraction of its own frame, differs
            from the master idle's by more than this percentage.

    Returns:
        Tuple ``(raw_checkpoint, source_dir_copy)`` -- the debug checkpoint
        03_assembled_raw.png AND the same sheet copied into
        <source_dir>/<animation>.png (where the canonical processing script
        looks for its input).

    Raises:
        ValueError: If ``animation == "idle"`` -- the idle animation IS the
            master idle seed (<source_dir>/idle.png); it is authored once and
            is not regenerated through img2vid, so Stage 4 must never
            overwrite it.
    """
    if animation == "idle":
        raise ValueError(
            "the 'idle' animation is the immutable master idle seed "
            "(<source_dir>/idle.png); it is not generated through the img2vid "
            "pipeline. Run the pipeline for the other animations only."
        )

    work_dir = WORK_ROOT / character / animation
    dump_dir = work_dir / "02_dumps"
    raw_out = work_dir / "03_assembled_raw.png"

    char_json = CHAR_DEF_ROOT / f"{character}.json"
    config = load_character_config(char_json)
    source_dir = (PROJECT_ROOT / config["source_dir"]).resolve()
    palette = load_palette_for(character)

    # Scale/anchor reference: the character's immutable master idle still.
    # Computed once and applied to every dump frame so the whole animation
    # shares one baseline and scale. The idle's own dimensions are also the
    # Stage-4 canvas size -- source-resolution rationale in the module
    # docstring.
    master_idle, master_idle_path = resolve_master_idle_reference(
        source_dir, config
    )
    canvas_w, canvas_h = master_idle.width, master_idle.height
    source_bbox_h, source_anchor_y = compute_source_anchor(
        master_idle, master_idle_path
    )

    all_processed: list[Image.Image] = []
    for dump_path in sorted(dump_dir.glob("dump_*.png")):
        raw = Image.open(dump_path).convert("RGBA")
        no_bg = remove_background(raw, bg_mode)
        cropped = tight_crop(no_bg, padding=1)
        if cropped is None:
            log.warning(
                "%s has no foreground after background removal, skipping",
                dump_path,
            )
            continue

        # Drift check: compare the character's height as a FRACTION of its
        # own frame in each pixel space (video-native dump vs idle.png-native)
        # before diffing, so the warning reflects genuine zoom/pan drift and
        # not a resolution difference between the clip and the master idle.
        frame_frac = cropped.height / max(raw.height, 1)
        idle_frac = source_bbox_h / max(canvas_h, 1)
        drift_pct = 100.0 * (frame_frac / max(idle_frac, 1e-6) - 1.0)
        if abs(drift_pct) > warn_scale_pct:
            log.warning(
                "%s character height differs from the master idle by %+.1f%% "
                "(each as a fraction of its own frame)",
                dump_path.name, drift_pct,
            )

        scaled = downsample_to_height(cropped, source_bbox_h)
        quantized = palette_quantize(scaled, palette)
        composed = composite_onto_canvas(
            quantized, canvas_w, canvas_h, source_anchor_y
        )
        all_processed.append(composed)

    sheet = pack_horizontal(all_processed)
    sheet.save(raw_out)
    log.info("Wrote %s (%d frames)", raw_out, len(all_processed))

    # Copy into the character's source_dir where the canonical processing
    # script looks for its input (it expects <animation>.png there).
    source_dir.mkdir(parents=True, exist_ok=True)
    source_copy = source_dir / f"{animation}.png"
    sheet.save(source_copy)
    log.info("Copied -> %s (canonical script input)", source_copy)
    return raw_out, source_copy


def resolve_output_filename(config: dict, animation: str) -> str:
    """Resolve the output filename the same way process_character_sprites.py does.

    process_character_sprites.py resolves each animation's output as
    ``entry.get("output", entry["source"])`` -- most entries omit ``output``
    and fall back to ``source``, but some (e.g. balchar.json's ``sling_attack``
    entry, which sets ``"output": "sling.png"``) rename the shipped asset.
    Assuming the output is always ``f"{animation}.png"`` is wrong whenever an
    entry sets an explicit ``output``, so this helper mirrors the same lookup
    instead of re-deriving the filename from ``animation`` alone.

    Args:
        config: Parsed character JSON (as returned by load_character_config).
        animation: Animation name (matches ``source`` field minus ``.png``).

    Returns:
        The output filename (e.g. ``"sling.png"``), including the ``.png``
        suffix.

    Raises:
        KeyError: If no animation entry matches.
    """
    target = f"{animation}.png"
    for entry in config.get("animations", []):
        if entry.get("source") == target:
            return entry.get("output", entry["source"])
    raise KeyError(f"unknown animation '{animation}' in character config")


def chain_process_script(character: str, animation: str) -> Path:
    """Invoke the canonical tools/process_character_sprites.py and verify output.

    The canonical script is always required. If it's missing, the repo is
    broken -- raise loudly rather than silently skipping (which would cause
    every non-Balchar character to ship with no final asset).

    process_character_sprites.py walks EVERY animation entry in the JSON and
    exits 1 if any source PNG is missing. On a partially-generated character
    (only idle.png plus the one animation we just assembled), that non-zero
    exit is expected and does NOT mean our target failed -- so this must NOT
    use check=True. Success is defined as "the animation's resolved output
    file exists under <output_dir> after the run"; that check (below) is the
    authority, and it raises if the target is missing.

    Args:
        character: Character slug (e.g. ``balchar``).
        animation: Animation name (e.g. ``walk``).

    Returns:
        The resolved path to the final game asset.

    Raises:
        FileNotFoundError: If the canonical script is missing, or if it ran
            but the resolved output file did not appear.
    """
    script = PROJECT_ROOT / "tools" / "process_character_sprites.py"
    if not script.exists():
        raise FileNotFoundError(
            f"canonical processing script not found at {script}; the repo is "
            f"broken. (Stage 4 expects this script to always exist; do not "
            f"add silent-skip fallbacks here.)"
        )
    char_json = CHAR_DEF_ROOT / f"{character}.json"
    # check=False on purpose -- see docstring above.
    # --only limits what gets *saved* to the one animation we just assembled;
    # the script still loads every source (missing ones just log + continue),
    # so the shared base scale is unaffected.
    subprocess.run(
        [sys.executable, str(script), str(char_json), "--only", animation],
        check=False,
    )

    # Resolve the expected output filename -- see resolve_output_filename().
    config = load_character_config(char_json)
    output_dir = (PROJECT_ROOT / config["output_dir"]).resolve()
    expected_output = output_dir / resolve_output_filename(config, animation)
    if not expected_output.exists():
        raise FileNotFoundError(
            f"canonical script returned but expected output "
            f"{expected_output} is missing. Inspect the script's logs and the "
            f"character JSON's animation entry for `{animation}.png` "
            f"(check its `output` field)."
        )
    return expected_output


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the Stage 4 sprite-sheet assembler."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "character",
        help="Character slug (e.g. balchar); names the img2vid work subfolder "
             "and resolves the palette and character JSON.",
    )
    parser.add_argument(
        "animation",
        help="Animation name (e.g. walk); names the img2vid work subfolder. "
             "'idle' is rejected -- it is the immutable master idle seed.",
    )
    parser.add_argument(
        "--bg-mode",
        choices=["rembg", "chroma", "both"],
        default="both",
        help="Background-removal strategy (default: both).",
    )
    parser.add_argument(
        "--warn-scale-pct",
        type=float,
        default=15.0,
        help="Warn when a frame's character height (as a fraction of its own "
             "frame) drifts from the master idle by more than this percent "
             "(default: 15).",
    )
    parser.add_argument(
        "--no-chain",
        action="store_true",
        help="Skip the canonical process_character_sprites.py chain.",
    )
    return parser


def main() -> None:
    """Entry point for the Stage 4 sprite-sheet assembler."""
    args = build_parser().parse_args()

    _raw, _source_copy = assemble(
        args.character, args.animation, args.bg_mode, args.warn_scale_pct
    )
    if not args.no_chain:
        final = chain_process_script(args.character, args.animation)
        log.info("Final asset -> %s", final)


if __name__ == "__main__":
    main()
