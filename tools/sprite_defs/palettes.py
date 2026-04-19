"""Color palettes for Sa Fona pixel art sprites.

Each palette maps single characters to RGBA tuples.
'.' is always transparent. Shared across all sprite definitions
so a palette tweak regenerates every sprite that uses it.
"""

# ── Ramon (Player) ────────────────────────────────────────────
# Deeply tanned Balearic foner. Knee-length white robe, long dark
# hair held by a sling-headband, second sling worn as belt. Both
# slings have loose knotted ends that overflow for volume.
RAMON_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Hair (long, dark Mediterranean)
    "h": (38, 25, 14, 255),
    "H": (58, 40, 24, 255),
    # Skin (deeply tanned)
    "s": (170, 114, 66, 255),
    "S": (145, 95, 55, 255),
    "k": (125, 80, 45, 255),
    # Eyes (simple: white + dark pupil)
    "e": (240, 235, 225, 255),
    "E": (35, 25, 15, 255),
    # Mouth
    "m": (140, 92, 52, 255),
    # Robe (white-cream, knee length)
    "r": (235, 228, 215, 255),
    "R": (250, 245, 235, 255),
    "c": (205, 198, 182, 255),
    # Sling straps (cream leather — headband + belt, with dangling ends)
    "L": (215, 205, 182, 255),
    "l": (235, 225, 205, 255),
    "p": (195, 185, 162, 255),
    # Belt area (sling-as-belt wrap)
    "b": (200, 190, 168, 255),
    "B": (185, 175, 155, 255),
    # Legs (tanned skin, visible below knee)
    "g": (160, 106, 60, 255),
    "G": (140, 90, 50, 255),
    # Sandals
    "d": (110, 75, 42, 255),
    "D": (90, 60, 34, 255),
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
    "w": (235, 230, 220, 255),
    "W": (210, 205, 195, 255),
    "d": (185, 180, 170, 255),
    "f": (180, 160, 140, 255),
    "e": (220, 50, 50, 255),
    "E": (255, 100, 80, 255),
    "h": (90, 65, 45, 255),
    "H": (180, 165, 140, 255),
}

# ── World 1 palette (for tilesets, backgrounds) ──────────────
WORLD1_COLORS = {
    "ochre": (200, 160, 100),
    "stone": (128, 128, 128),
    "olive": (107, 142, 80),
    "mediterranean": (74, 144, 200),
}
