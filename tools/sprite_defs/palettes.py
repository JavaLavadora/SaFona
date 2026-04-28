"""Color palettes for Sa Fona pixel art sprites.

Each palette maps single characters to RGBA tuples.
'.' is always transparent. Shared across all sprite definitions
so a palette tweak regenerates every sprite that uses it.

All palettes are SNES 15-bit compliant:
    - Every RGB channel value is a multiple of 8 (0-248).
    - Each palette has at most 15 unique non-transparent colors.
"""

# ── Ramon (Player) ────────────────────────────────────────────
# Deeply tanned Balearic foner. White headwrap, open white tunic,
# bright red sash, dark brown pants, leather boots and arm bracers.
# Sling held in hand with dangling cord.
#
# Consolidated from 24 to 15 unique colors. Multiple keys may share
# the same RGBA value so that existing sprite art is not broken.
RAMON_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Tunic brightest / highlight
    "T": (248, 248, 240, 255),
    # Headwrap light / eye white / tunic base (merged e, w, t)
    "w": (240, 232, 216, 255),
    "e": (240, 232, 216, 255),
    "t": (240, 232, 216, 255),
    # Headwrap shadow / tunic mid-shadow (merged W, c)
    "W": (208, 200, 192, 255),
    "c": (208, 200, 192, 255),
    # Tunic deep crease
    "C": (192, 192, 176, 255),
    # Skin base (bright)
    "s": (200, 136, 72, 255),
    # Skin shadow / arm bracers / mouth / boot highlight (merged S, a, m, n)
    "S": (176, 112, 56, 255),
    "a": (176, 112, 56, 255),
    "m": (176, 112, 56, 255),
    "n": (176, 112, 56, 255),
    # Skin dark / boot mid (merged k, b)
    "k": (152, 96, 48, 255),
    "b": (152, 96, 48, 255),
    # Pupil / dark outline
    "E": (32, 24, 16, 255),
    # Red sash bright
    "R": (224, 56, 48, 255),
    # Red sash base
    "r": (192, 40, 32, 255),
    # Red sash dark
    "x": (152, 32, 24, 255),
    # Leather dark / sling cord light (merged A, L)
    "A": (136, 88, 48, 255),
    "L": (136, 88, 48, 255),
    # Pants mid / boot dark (merged P, B)
    "P": (96, 72, 48, 255),
    "B": (96, 72, 48, 255),
    # Pants base / sling cord (merged p, l)
    "p": (88, 64, 40, 255),
    "l": (88, 64, 40, 255),
    # Pants / boots darkest
    "q": (64, 48, 32, 255),
}

# ── Bep (Myotragus companion) ────────────────────────────────
BEP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Fur
    "f": (160, 128, 88, 255),
    "F": (192, 160, 120, 255),
    "g": (128, 104, 72, 255),
    # Face / details
    "e": (224, 208, 200, 255),
    "E": (32, 24, 16, 255),
    "n": (104, 72, 48, 255),
    # Horns (small, curved)
    "h": (200, 184, 160, 255),
    "H": (168, 152, 128, 255),
    # Hooves
    "b": (80, 56, 32, 255),
}

# ── World 1 enemies ───────────────────────────────────────────
POSSESSED_SHEEP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "w": (232, 232, 224, 255),
    "W": (208, 208, 192, 255),
    "d": (184, 184, 168, 255),
    "f": (184, 160, 144, 255),
    "e": (224, 48, 48, 255),
    "E": (248, 96, 80, 255),
    "h": (88, 64, 48, 255),
    "H": (184, 168, 144, 255),
}

# ── Rival Warrior ────────────────────────────────────────────
RIVAL_WARRIOR_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (112, 72, 40, 255),       # skin
    "S": (88, 56, 32, 255),        # skin shadow
    "e": (224, 208, 200, 255),     # eye white
    "E": (32, 24, 16, 255),        # pupil
    "h": (48, 32, 24, 255),        # hair
    "H": (72, 48, 32, 255),        # hair highlight
    "a": (144, 96, 56, 255),       # animal hide armor
    "A": (120, 88, 48, 255),       # armor shadow
    "l": (96, 72, 40, 255),        # leather strap
    "w": (160, 152, 128, 255),     # weapon (stone spear)
    "W": (136, 128, 112, 255),     # weapon shadow
    "g": (96, 72, 40, 255),        # legs
    "G": (88, 56, 32, 255),        # legs shadow
    "f": (80, 56, 32, 255),        # feet
}

# ── Stone Guardian ───────────────────────────────────────────
STONE_GUARDIAN_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (128, 128, 136, 255),     # stone base
    "S": (152, 152, 152, 255),     # stone light
    "d": (96, 96, 104, 255),       # stone dark
    "D": (80, 80, 88, 255),        # stone very dark
    "e": (80, 200, 80, 255),       # eye glow
    "E": (120, 248, 120, 255),     # eye bright
    "m": (72, 96, 56, 255),        # moss
    "M": (88, 120, 72, 255),       # moss light
    "c": (56, 56, 64, 255),        # crack
}

# ── Pickups ──────────────────────────────────────────────────
HEART_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "r": (224, 40, 40, 255),       # heart red
    "R": (248, 80, 80, 255),       # heart light
    "d": (176, 32, 32, 255),       # heart dark
    "w": (248, 184, 184, 255),     # highlight
}

STONE_PICKUP_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (160, 152, 144, 255),     # stone base
    "S": (184, 184, 168, 255),     # stone light
    "d": (128, 128, 112, 255),     # stone dark
    "D": (112, 104, 88, 255),      # stone shadow
    "h": (200, 192, 184, 255),     # highlight
}

# ── Breakables ───────────────────────────────────────────────
BREAKABLE_POT_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "p": (184, 120, 56, 255),      # clay body
    "P": (200, 144, 72, 255),      # clay light
    "d": (152, 96, 48, 255),       # clay dark
    "D": (128, 80, 32, 255),       # clay shadow
    "r": (168, 112, 56, 255),      # rim
    "R": (192, 136, 72, 255),      # rim light
}

BREAKABLE_CRATE_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "w": (160, 120, 72, 255),      # wood base
    "W": (184, 144, 88, 255),      # wood light
    "d": (128, 96, 56, 255),       # wood dark
    "D": (112, 80, 48, 255),       # wood shadow
    "n": (96, 72, 40, 255),        # nails/metal
}

# ── Llorencc (NPC shopkeeper) ────────────────────────────────
# Mediterranean merchant: warm earth tones, colorful apron/vest,
# friendly face. Balearic market trader aesthetic.
LLORENCC_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (192, 136, 80, 255),      # skin base
    "S": (168, 112, 64, 255),      # skin shadow
    "h": (64, 40, 24, 255),        # hair / beard
    "e": (32, 24, 16, 255),        # eyes
    "t": (240, 232, 208, 255),     # shirt (cream linen)
    "T": (216, 208, 184, 255),     # shirt shadow
    "v": (56, 104, 72, 255),       # vest (olive green)
    "V": (40, 80, 56, 255),        # vest shadow
    "a": (184, 56, 40, 255),       # apron (terracotta)
    "A": (152, 40, 32, 255),       # apron shadow
    "p": (88, 64, 40, 255),        # pants (brown)
    "b": (112, 80, 48, 255),       # boots
}

# ── Dimoni (NPC trickster demon) ─────────────────────────────
# Supernatural trickster from Mallorcan folklore. Dark purples,
# fiery reds/oranges, glowing yellow eyes.
DIMONI_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "d": (72, 24, 56, 255),        # dark body base
    "D": (48, 16, 40, 255),        # body shadow
    "r": (200, 48, 32, 255),       # fiery red accent
    "R": (240, 96, 40, 255),       # orange fire glow
    "y": (248, 232, 56, 255),      # glowing eyes
    "Y": (248, 200, 32, 255),      # eye outer glow
    "p": (104, 40, 88, 255),       # purple mid
    "P": (136, 56, 112, 255),      # purple highlight
    "h": (56, 16, 32, 255),        # horns dark
    "H": (88, 32, 48, 255),        # horns light
    "c": (32, 8, 24, 255),         # cloak darkest
    "f": (232, 128, 40, 255),      # flame tips
}

# ── Legionary (W2 Roman soldier) ─────────────────────────────
# Imperial Roman soldier: iron/steel armor, red tunic/cape,
# leather accents. Military discipline in palette.
LEGIONARY_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "a": (168, 168, 176, 255),     # armor steel base
    "A": (136, 136, 144, 255),     # armor shadow
    "h": (200, 200, 208, 255),     # armor highlight
    "r": (176, 32, 24, 255),       # red tunic/cape
    "R": (216, 48, 40, 255),       # red highlight
    "x": (136, 24, 16, 255),       # red dark shadow
    "s": (168, 128, 80, 255),      # skin
    "S": (144, 104, 64, 255),      # skin shadow
    "l": (104, 72, 40, 255),       # leather straps
    "L": (80, 56, 32, 255),        # leather dark
    "g": (192, 168, 72, 255),      # gold trim
    "e": (32, 24, 16, 255),        # eyes / dark
    "b": (72, 56, 40, 255),        # boots
}

# ── War Dog (W2 Roman war dog) ───────────────────────────────
# Fierce Roman war dog: dark brown/grey fur, leather collar,
# red eyes. Menacing beast.
WAR_DOG_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "f": (96, 80, 64, 255),        # fur base (dark brown-grey)
    "F": (120, 104, 80, 255),      # fur highlight
    "d": (64, 48, 40, 255),        # fur dark
    "D": (40, 32, 24, 255),        # fur darkest / outline
    "e": (200, 40, 32, 255),       # eyes red
    "E": (248, 80, 56, 255),       # eye glow
    "n": (56, 40, 32, 255),        # nose / muzzle
    "c": (136, 56, 32, 255),       # leather collar
    "C": (104, 40, 24, 255),       # collar shadow
    "m": (160, 160, 168, 255),     # metal studs on collar
    "t": (248, 240, 224, 255),     # teeth / claws
}

# ── Boss: Bou de Pedra (Stone Bull) ──────────────────────────
# Massive stone bull with glowing runes. Phase colors from
# boss_bou_de_pedra.json: P1=(140,140,140), P2=(220,140,40),
# P3=(220,40,40). Rounded to SNES grid.
BOSS_BOU_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "s": (144, 144, 144, 255),     # stone base (phase 1 color)
    "S": (176, 176, 176, 255),     # stone highlight
    "d": (104, 104, 112, 255),     # stone dark
    "D": (72, 72, 80, 255),        # stone darkest
    "c": (56, 56, 64, 255),        # crack lines
    "e": (224, 200, 56, 255),      # rune glow (neutral)
    "E": (248, 240, 120, 255),     # rune glow bright
    "1": (144, 144, 144, 255),     # phase 1 accent (grey stone)
    "2": (224, 144, 40, 255),      # phase 2 accent (fiery orange)
    "3": (224, 40, 40, 255),       # phase 3 accent (enraged red)
    "h": (120, 112, 96, 255),      # horn base
    "H": (88, 80, 72, 255),        # horn dark
    "m": (64, 88, 48, 255),        # moss accent
}

# ── Projectile (sling stones) ───────────────────────────────
# Three tiers: grey base, blue-glow upgraded, gold-glow mastered.
PROJECTILE_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Tier 1: plain stone
    "s": (160, 160, 152, 255),     # stone base
    "S": (128, 128, 120, 255),     # stone shadow
    "h": (192, 192, 184, 255),     # stone highlight
    # Tier 2: blue glow
    "b": (80, 144, 224, 255),      # blue glow
    "B": (120, 184, 248, 255),     # blue bright
    # Tier 3: gold glow
    "g": (216, 184, 56, 255),      # gold glow
    "G": (248, 224, 96, 255),      # gold bright
    # Common
    "d": (96, 96, 88, 255),        # dark outline
}

# ── UI Palette (HUD elements) ───────────────────────────────
# Clean, readable colors for health bar, ammo counter, coins,
# and other HUD elements. High contrast for visibility.
UI_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    "r": (224, 40, 40, 255),       # health red
    "R": (248, 96, 80, 255),       # health bright
    "g": (64, 184, 64, 255),       # health green (full)
    "y": (248, 216, 48, 255),      # coin / gold
    "Y": (200, 168, 32, 255),      # coin shadow
    "b": (80, 144, 224, 255),      # ammo / mana blue
    "w": (248, 248, 240, 255),     # text white
    "W": (200, 200, 192, 255),     # text shadow
    "d": (32, 32, 40, 255),        # dark background
    "D": (56, 56, 64, 255),        # panel border
    "o": (200, 152, 64, 255),      # orange (warning)
}

# ── Effects Palette (particles, dust, portal, aura) ─────────
# Visual effects: white/grey dust, yellow impact flash,
# purple portal glow, green dimoni aura.
EFFECTS_PALETTE: dict[str, tuple[int, int, int, int]] = {
    ".": (0, 0, 0, 0),
    # Dust / debris
    "w": (240, 240, 232, 255),     # dust white
    "W": (200, 200, 192, 255),     # dust grey
    "d": (160, 152, 144, 255),     # dust dark
    # Impact flash
    "y": (248, 240, 120, 255),     # flash yellow
    "Y": (248, 208, 56, 255),      # flash orange-yellow
    # Portal glow
    "p": (152, 72, 200, 255),      # portal purple
    "P": (192, 112, 240, 255),     # portal bright
    "v": (104, 40, 152, 255),      # portal deep
    # Dimoni aura
    "g": (72, 200, 80, 255),       # aura green
    "G": (120, 240, 120, 255),     # aura bright
    "a": (48, 144, 56, 255),       # aura dark
    # Common
    "o": (248, 152, 48, 255),      # orange spark
}

# ── World 1 palette (for tilesets, backgrounds) ──────────────
WORLD1_COLORS = {
    "ochre": (200, 160, 96),
    "stone": (128, 128, 128),
    "olive": (104, 144, 80),
    "mediterranean": (72, 144, 200),
}
