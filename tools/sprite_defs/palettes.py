"""Color palettes for Sa Fona pixel art sprites.

Each palette maps single characters to RGBA tuples.
'.' is always transparent. Shared across all sprite definitions
so a palette tweak regenerates every sprite that uses it.
"""

# ── Ramon (Player) ────────────────────────────────────────────
# Deeply tanned Balearic foner (slinger) with white/cream robe
# and headband, leather sling straps.
RAMON_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Hair (dark, Mediterranean)
    "h": (35, 22, 12, 255),
    "H": (55, 38, 22, 255),
    # Skin (deeply tanned)
    "s": (166, 110, 64, 255),
    "S": (140, 90, 50, 255),
    "k": (120, 76, 42, 255),
    # Face details
    "e": (230, 225, 215, 255),
    "E": (25, 18, 10, 255),
    "B": (30, 20, 12, 255),
    "m": (130, 80, 45, 255),
    # Robe / tunic (white-cream, Balearic foner style)
    "r": (235, 228, 215, 255),
    "R": (250, 245, 235, 255),
    "c": (200, 192, 178, 255),
    # Headband (white cloth, tied around forehead)
    "w": (245, 240, 230, 255),
    "W": (220, 214, 200, 255),
    # Sling (cream/white leather straps)
    "L": (210, 200, 180, 255),
    "l": (230, 222, 205, 255),
    # Belt / waist wrap (darker leather)
    "b": (120, 85, 50, 255),
    "A": (100, 68, 38, 255),
    # Legs (tanned skin + simple sandal straps)
    "g": (155, 102, 58, 255),
    # Sandals
    "d": (110, 75, 42, 255),
    "D": (90, 60, 34, 255),
    # Outline / accent
    "o": (60, 40, 22, 255),
}

# ── Bep (Myotragus companion) ────────────────────────────────
BEP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Fur
    "f": (160, 130, 90, 255),
    "F": (190, 160, 120, 255),
    "g": (130, 105, 70, 255),
    # Face / details
    "e": (220, 210, 200, 255),
    "E": (35, 25, 15, 255),
    "n": (100, 70, 45, 255),
    # Horns (small, curved)
    "h": (200, 185, 160, 255),
    "H": (170, 155, 130, 255),
    # Hooves
    "b": (80, 55, 35, 255),
}

# ── World 1 enemies ───────────────────────────────────────────
POSSESSED_SHEEP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Wool
    "w": (235, 230, 220, 255),
    "W": (210, 205, 195, 255),
    # Dark wool (shadow)
    "d": (185, 180, 170, 255),
    # Face
    "f": (180, 160, 140, 255),
    # Possessed eyes (glowing red)
    "e": (220, 50, 50, 255),
    "E": (255, 100, 80, 255),
    # Hooves
    "h": (90, 65, 45, 255),
    # Horns
    "H": (180, 165, 140, 255),
}

# ── World 1 palette (for tilesets, backgrounds) ──────────────
WORLD1_COLORS = {
    "ochre": (200, 160, 100),
    "stone": (128, 128, 128),
    "olive": (107, 142, 80),
    "mediterranean": (74, 144, 200),
}
