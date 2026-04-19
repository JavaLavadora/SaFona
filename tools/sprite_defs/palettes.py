"""Color palettes for Sa Fona pixel art sprites.

Each palette maps single characters to RGBA tuples.
'.' is always transparent. Shared across all sprite definitions
so a palette tweak regenerates every sprite that uses it.
"""

# ── Ramon (Player) ────────────────────────────────────────────
# Deeply tanned Balearic foner. White headwrap, open white tunic,
# bright red sash, dark brown pants, leather boots and arm bracers.
# Sling held in hand with dangling cord.
RAMON_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Headwrap (white/cream)
    "w": (235, 228, 215, 255),
    "W": (210, 202, 188, 255),
    # Skin (deep orange-tan)
    "s": (200, 135, 72, 255),
    "S": (175, 112, 58, 255),
    "k": (155, 98, 48, 255),
    # Eyes
    "e": (240, 235, 225, 255),
    "E": (35, 25, 15, 255),
    # Mouth
    "m": (168, 108, 58, 255),
    # Tunic (white)
    "t": (238, 232, 218, 255),
    "T": (252, 248, 238, 255),
    "c": (215, 208, 195, 255),
    "C": (195, 188, 175, 255),
    # Red sash
    "r": (195, 38, 32, 255),
    "R": (225, 55, 45, 255),
    "x": (155, 28, 22, 255),
    # Arm bracers (leather)
    "a": (175, 112, 58, 255),
    "A": (145, 90, 45, 255),
    # Pants (dark brown)
    "p": (82, 58, 38, 255),
    "P": (98, 70, 48, 255),
    "q": (65, 45, 28, 255),
    # Boots
    "b": (142, 92, 48, 255),
    "B": (118, 75, 38, 255),
    "n": (168, 115, 62, 255),
    # Sling cord
    "l": (92, 68, 42, 255),
    "L": (122, 88, 52, 255),
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

# ── Rival Warrior ────────────────────────────────────────────
RIVAL_WARRIOR_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (110, 75, 42, 255),       # skin
    "S": (90, 60, 34, 255),        # skin shadow
    "e": (220, 210, 200, 255),     # eye white
    "E": (35, 25, 15, 255),        # pupil
    "h": (50, 35, 22, 255),        # hair
    "H": (70, 50, 32, 255),        # hair highlight
    "a": (140, 100, 60, 255),      # animal hide armor
    "A": (120, 85, 50, 255),       # armor shadow
    "l": (100, 70, 40, 255),       # leather strap
    "w": (160, 150, 130, 255),     # weapon (stone spear)
    "W": (140, 130, 110, 255),     # weapon shadow
    "g": (100, 68, 38, 255),       # legs
    "G": (85, 56, 30, 255),        # legs shadow
    "f": (80, 55, 32, 255),        # feet
}

# ── Stone Guardian ───────────────────────────────────────────
STONE_GUARDIAN_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (130, 130, 135, 255),     # stone base
    "S": (150, 150, 155, 255),     # stone light
    "d": (100, 100, 105, 255),     # stone dark
    "D": (80, 80, 85, 255),        # stone very dark
    "e": (80, 200, 80, 255),       # eye glow
    "E": (120, 255, 120, 255),     # eye bright
    "m": (70, 100, 55, 255),       # moss
    "M": (90, 120, 70, 255),       # moss light
    "c": (60, 60, 65, 255),        # crack
}

# ── Pickups ──────────────────────────────────────────────────
HEART_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "r": (220, 40, 40, 255),       # heart red
    "R": (255, 80, 80, 255),       # heart light
    "d": (180, 30, 30, 255),       # heart dark
    "w": (255, 180, 180, 255),     # highlight
}

STONE_PICKUP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (160, 155, 140, 255),     # stone base
    "S": (185, 180, 165, 255),     # stone light
    "d": (130, 125, 110, 255),     # stone dark
    "D": (110, 105, 90, 255),      # stone shadow
    "h": (200, 195, 180, 255),     # highlight
}

# ── Breakables ───────────────────────────────────────────────
BREAKABLE_POT_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "p": (180, 120, 60, 255),      # clay body
    "P": (200, 140, 75, 255),      # clay light
    "d": (150, 95, 45, 255),       # clay dark
    "D": (130, 80, 35, 255),       # clay shadow
    "r": (165, 108, 55, 255),      # rim
    "R": (195, 135, 70, 255),      # rim light
}

BREAKABLE_CRATE_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "w": (160, 120, 70, 255),      # wood base
    "W": (180, 140, 85, 255),      # wood light
    "d": (130, 95, 55, 255),       # wood dark
    "D": (110, 80, 45, 255),       # wood shadow
    "n": (100, 70, 38, 255),       # nails/metal
}

# ── World 1 palette (for tilesets, backgrounds) ──────────────
WORLD1_COLORS = {
    "ochre": (200, 160, 100),
    "stone": (128, 128, 128),
    "olive": (107, 142, 80),
    "mediterranean": (74, 144, 200),
}
