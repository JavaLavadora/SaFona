"""Standalone sprite cleanup CLI — enforce palette compliance on AI-generated PNGs.

Processes an input sprite PNG through three stages:
1. Alpha cleanup: snap semi-transparent pixels to fully opaque or transparent
2. Palette snapping: map every opaque pixel to the nearest palette color (CIELAB)
3. Color count enforcement: merge excess colors into nearest palette neighbors

Palette files are GIMP .gpl text files stored in assets/palettes/.

Usage:
    conda activate safona
    python tools/clean_sprites.py assets/sprites/ramon/idle.png --palette ramon
    python tools/clean_sprites.py idle.png --palette ramon --verbose --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GPL palette parsing
# ---------------------------------------------------------------------------

def parse_gpl(path: Path) -> np.ndarray:
    """Parse a GIMP .gpl palette file into an Nx3 uint8 RGB array.

    GPL format:
        Line 1: "GIMP Palette"
        Lines 2+: optional headers (Name:, Columns:, # comments)
        Color lines: "R G B\\tName"

    Args:
        path: Path to the .gpl file.

    Returns:
        Numpy array of shape (N, 3) with uint8 RGB values.

    Raises:
        FileNotFoundError: If the palette file does not exist.
        ValueError: If no valid color entries are found.
    """
    if not path.exists():
        raise FileNotFoundError(f"Palette file not found: {path}")

    colors = []
    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            # Skip header, metadata, comments, blank lines
            if not line or line.startswith("GIMP Palette"):
                continue
            if line.startswith("Name:") or line.startswith("Columns:"):
                continue
            if line.startswith("#"):
                continue
            # Parse color line: "R G B\tName" or "R G B  Name"
            parts = line.split()
            if len(parts) >= 3:
                try:
                    r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                except ValueError:
                    continue
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValueError(
                        f"RGB values out of 0-255 range at line {line_num} "
                        f"in {path}: ({r}, {g}, {b})"
                    )
                colors.append((r, g, b))

    if not colors:
        raise ValueError(f"No valid color entries found in: {path}")

    return np.array(colors, dtype=np.uint8)


# ---------------------------------------------------------------------------
# RGB <-> CIELAB conversion (vectorized, no scikit-image dependency)
# ---------------------------------------------------------------------------

def _rgb_to_xyz(rgb: np.ndarray) -> np.ndarray:
    """Convert sRGB [0,255] to CIE XYZ (D65 illuminant).

    Args:
        rgb: Array of shape (..., 3) with uint8 values.

    Returns:
        Array of shape (..., 3) with XYZ values.
    """
    # Normalize to [0, 1]
    srgb = rgb.astype(np.float64) / 255.0

    # Inverse sRGB companding
    linear = np.where(
        srgb <= 0.04045,
        srgb / 12.92,
        ((srgb + 0.055) / 1.055) ** 2.4,
    )

    # sRGB to XYZ matrix (D65)
    # fmt: off
    m = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    # fmt: on

    xyz = linear @ m.T
    return xyz


def _xyz_to_lab(xyz: np.ndarray) -> np.ndarray:
    """Convert CIE XYZ to CIELAB (D65 illuminant).

    Args:
        xyz: Array of shape (..., 3) with XYZ values.

    Returns:
        Array of shape (..., 3) with L*a*b* values.
    """
    # D65 reference white
    ref = np.array([0.95047, 1.00000, 1.08883])
    scaled = xyz / ref

    epsilon = 216.0 / 24389.0
    kappa = 24389.0 / 27.0

    f = np.where(
        scaled > epsilon,
        np.cbrt(scaled),
        (kappa * scaled + 16.0) / 116.0,
    )

    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])

    return np.stack([L, a, b], axis=-1)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert sRGB [0,255] to CIELAB.

    Args:
        rgb: Array of shape (..., 3) with uint8 RGB values.

    Returns:
        Array of shape (..., 3) with L*a*b* values.
    """
    return _xyz_to_lab(_rgb_to_xyz(rgb))


# ---------------------------------------------------------------------------
# Pipeline stage 1: Alpha cleanup
# ---------------------------------------------------------------------------

def clean_alpha(rgba: np.ndarray, threshold: int = 128) -> np.ndarray:
    """Snap semi-transparent pixels to fully opaque or fully transparent.

    Pixels with alpha >= threshold become opaque (255).
    Pixels with alpha < threshold become transparent (0).

    Args:
        rgba: RGBA image array of shape (H, W, 4).
        threshold: Alpha cutoff value.

    Returns:
        New RGBA array with binary alpha channel.
    """
    result = rgba.copy()
    result[:, :, 3] = np.where(result[:, :, 3] >= threshold, 255, 0)
    # Zero out RGB on fully transparent pixels to avoid "dirty alpha"
    transparent_mask = result[:, :, 3] == 0
    result[:, :, :3][transparent_mask] = 0
    return result


# ---------------------------------------------------------------------------
# Pipeline stage 2: Palette snapping
# ---------------------------------------------------------------------------

_OUTLINE_LUMINANCE_THRESHOLD = 30.0


def snap_to_palette(
    rgba: np.ndarray,
    palette_rgb: np.ndarray,
) -> np.ndarray:
    """Map every opaque pixel to the nearest palette color in CIELAB space.

    Outline pixels (very dark, L* < threshold) are snapped directly to the
    darkest palette color to avoid CIELAB nonlinearity near black pulling
    dark browns into the outline color.

    Args:
        rgba: RGBA image array of shape (H, W, 4), alpha already cleaned.
        palette_rgb: Palette colors as (N, 3) uint8 array.

    Returns:
        New RGBA array with colors replaced by nearest palette entries.
    """
    result = rgba.copy()

    # Build palette in LAB space
    palette_lab = rgb_to_lab(palette_rgb)

    # Find the darkest palette color (lowest L*)
    darkest_idx = int(np.argmin(palette_lab[:, 0]))
    darkest_rgb = palette_rgb[darkest_idx]

    # Build a KD-tree from all palette entries for nearest-neighbor lookup
    tree = cKDTree(palette_lab)

    # Get opaque pixel mask
    opaque_mask = rgba[:, :, 3] == 255
    if not np.any(opaque_mask):
        return result

    # Extract opaque pixel RGB values
    opaque_rgb = rgba[:, :, :3][opaque_mask]  # (K, 3)

    # Convert all opaque pixels to LAB
    opaque_lab = rgb_to_lab(opaque_rgb)  # (K, 3)

    # Identify outline pixels: very dark (low L*)
    is_outline = opaque_lab[:, 0] < _OUTLINE_LUMINANCE_THRESHOLD

    # Query KD-tree for all pixels
    _, indices = tree.query(opaque_lab)

    # Build result RGB: general pixels get tree result, outlines get darkest
    mapped_rgb = palette_rgb[indices]
    mapped_rgb[is_outline] = darkest_rgb

    # Write back
    result_rgb = result[:, :, :3]
    result_rgb[opaque_mask] = mapped_rgb

    return result


# ---------------------------------------------------------------------------
# Pipeline stage 3: Color count enforcement
# ---------------------------------------------------------------------------

def enforce_color_limit(
    rgba: np.ndarray,
    palette_rgb: np.ndarray,
    max_colors: int = 15,
) -> np.ndarray:
    """Merge least-used colors if unique count exceeds the limit.

    After palette snapping, there should be at most len(palette) colors.
    This is a safety net: if somehow more remain, the least-used ones
    are merged into their nearest palette neighbors.

    Args:
        rgba: RGBA image array (already palette-snapped).
        palette_rgb: Palette colors as (N, 3) uint8 array.
        max_colors: Maximum allowed unique opaque colors.

    Returns:
        New RGBA array with at most max_colors unique opaque colors.
    """
    result = rgba.copy()
    opaque_mask = result[:, :, 3] == 255

    if not np.any(opaque_mask):
        return result

    opaque_rgb = result[:, :, :3][opaque_mask]  # (K, 3)

    # Count unique colors and their frequencies
    unique_colors, inverse, counts = np.unique(
        opaque_rgb, axis=0, return_inverse=True, return_counts=True,
    )

    if len(unique_colors) <= max_colors:
        return result

    log.info("  Color limit exceeded: %d > %d, merging least-used",
             len(unique_colors), max_colors)

    # Convert unique colors to LAB
    unique_lab = rgb_to_lab(unique_colors)
    palette_lab = rgb_to_lab(palette_rgb)
    tree = cKDTree(palette_lab)

    # Sort unique colors by count (ascending) — merge least-used first
    sort_order = np.argsort(counts)

    # Build a mapping: for each unique color, what it should become
    remap = np.arange(len(unique_colors))
    kept = set()

    # First pass: keep colors in descending frequency order up to max_colors
    for idx in reversed(sort_order):
        if len(kept) < max_colors:
            kept.add(idx)

    # Second pass: map unkept colors to their nearest palette color
    # Pre-compute LAB for kept colors for CIELAB distance comparison
    kept_list = sorted(kept)
    kept_lab = unique_lab[kept_list]

    for idx in sort_order:
        if idx not in kept:
            _, nearest = tree.query(unique_lab[idx])
            # Find which kept color is closest to this palette color in CIELAB
            nearest_palette_lab = palette_lab[nearest]
            diffs = kept_lab - nearest_palette_lab
            dists = np.sum(diffs ** 2, axis=1)
            best_kept = kept_list[int(np.argmin(dists))]
            remap[idx] = best_kept

    # Apply remapping
    new_rgb = unique_colors[remap[inverse]]
    result[:, :, :3][opaque_mask] = new_rgb

    return result


# ---------------------------------------------------------------------------
# Stats collection
# ---------------------------------------------------------------------------

def compute_stats(
    original: np.ndarray,
    cleaned: np.ndarray,
    palette_rgb: np.ndarray,
) -> dict:
    """Compute before/after statistics for verbose output.

    Args:
        original: Original RGBA array.
        cleaned: Cleaned RGBA array.
        palette_rgb: Palette RGB array.

    Returns:
        Dict with stats: colors_before, colors_after, pixels_changed,
        total_opaque, semi_transparent_fixed, palette_name_matches.
    """
    orig_opaque = original[:, :, 3] == 255
    clean_opaque = cleaned[:, :, 3] == 255

    # Count semi-transparent pixels that were fixed
    semi_mask = (original[:, :, 3] > 0) & (original[:, :, 3] < 255)
    semi_count = int(np.sum(semi_mask))

    # Unique opaque colors before
    if np.any(orig_opaque):
        orig_colors = np.unique(original[:, :, :3][orig_opaque], axis=0)
        colors_before = len(orig_colors)
    else:
        colors_before = 0

    # Unique opaque colors after
    if np.any(clean_opaque):
        clean_colors = np.unique(cleaned[:, :, :3][clean_opaque], axis=0)
        colors_after = len(clean_colors)
    else:
        clean_colors = np.empty((0, 3), dtype=np.uint8)
        colors_after = 0

    # Pixels whose RGB changed
    total_opaque = int(np.sum(clean_opaque))
    if np.any(clean_opaque):
        orig_rgb = original[:, :, :3][clean_opaque]
        clean_rgb = cleaned[:, :, :3][clean_opaque]
        pixels_changed = int(np.sum(np.any(orig_rgb != clean_rgb, axis=1)))
    else:
        pixels_changed = 0

    # Check how many output colors are in the palette
    palette_set = set(map(tuple, palette_rgb.tolist()))
    on_palette = sum(1 for c in clean_colors if tuple(c) in palette_set)

    return {
        "colors_before": colors_before,
        "colors_after": colors_after,
        "pixels_changed": pixels_changed,
        "total_opaque": total_opaque,
        "semi_transparent_fixed": semi_count,
        "palette_colors_used": on_palette,
        "palette_total": len(palette_rgb),
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def clean_sprite(
    rgba: np.ndarray,
    palette_rgb: np.ndarray,
    alpha_threshold: int = 128,
    max_colors: int = 15,
) -> np.ndarray:
    """Run the full cleanup pipeline on an RGBA sprite array.

    Pipeline order:
    1. Alpha cleanup (snap semi-transparent)
    2. Palette snapping (nearest CIELAB color)
    3. Color count enforcement (merge excess)

    Args:
        rgba: Input RGBA image array of shape (H, W, 4).
        palette_rgb: Palette colors as (N, 3) uint8 array.
        alpha_threshold: Cutoff for alpha snapping.
        max_colors: Maximum allowed unique opaque colors.

    Returns:
        Cleaned RGBA array.
    """
    result = clean_alpha(rgba, threshold=alpha_threshold)
    result = snap_to_palette(result, palette_rgb)
    result = enforce_color_limit(result, palette_rgb, max_colors=max_colors)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Clean up AI-generated sprite PNGs by enforcing palette compliance.",
        epilog="Example: python tools/clean_sprites.py assets/sprites/ramon/idle.png --palette ramon",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input PNG file.",
    )
    parser.add_argument(
        "--palette",
        required=True,
        metavar="NAME",
        help="Palette name — resolves to assets/palettes/{NAME}.gpl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: same dir, {name}_cleaned.png).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed before/after stats.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show stats without writing output file.",
    )
    return parser


def resolve_palette_path(name: str) -> Path:
    """Resolve a palette name to its .gpl file path.

    Args:
        name: Palette name (e.g., "ramon").

    Returns:
        Absolute path to the .gpl file.
    """
    return PROJECT_ROOT / "assets" / "palettes" / f"{name}.gpl"


def resolve_output_path(input_path: Path, output_arg: Path | None) -> Path:
    """Determine the output file path.

    Args:
        input_path: Original input PNG path.
        output_arg: Explicit output path from CLI, or None.

    Returns:
        Resolved output path.
    """
    if output_arg is not None:
        return output_arg
    stem = input_path.stem
    return input_path.parent / f"{stem}_cleaned.png"


def main(argv: list[str] | None = None) -> int:
    """Entry point for the sprite cleanup CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve paths
    input_path = Path(args.input)
    if not input_path.exists():
        log.error("Input file not found: %s", input_path)
        return 1

    palette_path = resolve_palette_path(args.palette)
    try:
        palette_rgb = parse_gpl(palette_path)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        return 1

    output_path = resolve_output_path(input_path, args.output)

    log.info("Input:   %s", input_path)
    log.info("Palette: %s (%d colors)", palette_path.name, len(palette_rgb))
    if not args.dry_run:
        log.info("Output:  %s", output_path)

    # Load image
    img = Image.open(input_path).convert("RGBA")
    original = np.array(img)

    # Run pipeline
    cleaned = clean_sprite(original, palette_rgb)

    # Stats
    stats = compute_stats(original, cleaned, palette_rgb)

    if args.verbose or args.dry_run:
        log.info("--- Stats ---")
        log.info("  Unique colors before:    %d", stats["colors_before"])
        log.info("  Unique colors after:     %d", stats["colors_after"])
        log.info("  Pixels changed:          %d / %d", stats["pixels_changed"], stats["total_opaque"])
        log.info("  Semi-transparent fixed:  %d", stats["semi_transparent_fixed"])
        log.info("  Palette colors used:     %d / %d", stats["palette_colors_used"], stats["palette_total"])

    if args.dry_run:
        log.info("Dry run — no file written.")
        return 0

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(cleaned, "RGBA").save(str(output_path))
    log.info("Saved: %s (%dx%d)", output_path, cleaned.shape[1], cleaned.shape[0])

    return 0


if __name__ == "__main__":
    sys.exit(main())
