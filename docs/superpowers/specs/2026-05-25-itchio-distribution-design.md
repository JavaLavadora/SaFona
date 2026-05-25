# Sa Fona — itch.io Distribution Design

## Goal

Package Sa Fona as standalone executables for Windows and Linux and distribute via itch.io with "pay what you want" pricing.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bundler | PyInstaller | Most mature for Pygame, large community, proven on itch.io |
| Bundle mode | `--onedir` | Faster startup than `--onefile`, easier to debug |
| Platforms | Windows + Linux | Covers most itch.io users; Mac deferred |
| Build method | Manual script | Simple `build.sh`; CI/CD can be added later |
| Pricing | Pay what you want | Free download with optional donation |
| Upload tool | butler (itch.io CLI) | Delta-patched uploads, versioning |

## 1. Build Configuration — PyInstaller `.spec` File

A `safona.spec` file at the project root configures the PyInstaller build.

**Entry point**: `sa_fona/main.py`

**Bundled data directories** (added via `datas` in the spec):

| Source | Destination in bundle | Notes |
|--------|-----------------------|-------|
| `sa_fona/data/` | `sa_fona/data/` | Levels, dialogue, manifests, enemy defs, etc. |
| `assets/sprites/` | `assets/sprites/` | All sprite sheets |
| `assets/tilesets/` | `assets/tilesets/` | Tileset images |
| `assets/backgrounds/` | `assets/backgrounds/` | Background layers |
| `assets/ui/` | `assets/ui/` | UI elements |
| `assets/effects/` | `assets/effects/` | Visual effects |
| `assets/portraits/` | `assets/portraits/` | Character portraits |
| `assets/palettes/` | `assets/palettes/` | Color palettes |

**Excluded from bundle**:
- `assets/ai_sources/` — raw AI generation outputs, ~112 MB, not needed at runtime
- `assets/screenshots/` — development screenshots
- `saves/` — created at runtime in user directory
- `tools/`, `tests/`, `docs/` — development-only

**Executable name**: `SaFona.exe` (Windows) / `SaFona` (Linux)

**Console**: Hidden on Windows (`--noconsole`), visible on Linux (helps debugging for now).

**Icon**: Requires a `.ico` file for Windows. Use a placeholder initially; Na Margalida can create a proper icon later.

## 2. Path Resolution for Frozen Builds

PyInstaller sets `sys.frozen = True` and extracts bundled files to `sys._MEIPASS`. The game's path resolution in `sa_fona/config/settings.py` must handle both modes.

**Current paths** (in `settings.py`):
```python
PACKAGE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_DIR / "data"
ASSETS_DIR = PACKAGE_DIR.parent / "assets"
SAVES_DIR = PACKAGE_DIR.parent / "saves"
```

**Changed to**:
```python
import sys

if getattr(sys, 'frozen', False):
    _BUNDLE_DIR = Path(sys._MEIPASS)
    PACKAGE_DIR = _BUNDLE_DIR / "sa_fona"
    ASSETS_DIR = _BUNDLE_DIR / "assets"
    SAVES_DIR = Path.home() / ".safona" / "saves"
else:
    PACKAGE_DIR = Path(__file__).resolve().parent.parent
    ASSETS_DIR = PACKAGE_DIR.parent / "assets"
    SAVES_DIR = PACKAGE_DIR.parent / "saves"

DATA_DIR = PACKAGE_DIR / "data"
```

**Save directory**: In frozen mode, saves go to `~/.safona/saves/` (Linux) or `%USERPROFILE%/.safona/saves/` (Windows). This ensures saves persist across game updates and aren't inside the read-only bundle. The `save_system.py` already uses `SAVES_DIR` from settings, so no other changes needed — just ensure `SAVES_DIR` is created on first write if it doesn't exist.

**Asset loader**: `sa_fona/rendering/asset_loader.py` uses `_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))`. This needs the same frozen-mode detection:
```python
if getattr(sys, 'frozen', False):
    _PROJECT_ROOT = sys._MEIPASS
else:
    _PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
```

## 3. Build Script

A `build.sh` script at the project root:

```
Usage: ./build.sh [linux|windows|all]
Default: linux
```

**Steps for Linux build**:
1. Activate conda `safona` environment
2. Install PyInstaller if not present (`pip install pyinstaller`)
3. Run `pyinstaller safona.spec`
4. Output lands in `dist/SaFona/`
5. Create `dist/SaFona-linux.zip` archive

**Windows build**:
- Must be run on a Windows machine or VM
- Same spec file works on both platforms
- Creates `dist/SaFona-windows.zip`

The script cleans `build/` and `dist/` before each run for reproducibility.

**`.gitignore` additions**:
```
build/
dist/
*.spec.bak
```

## 4. itch.io Page Setup

Done manually by the user (Toni) in the itch.io web interface.

**Project settings**:
- Kind: Downloadable
- Classification: Game
- Pricing: $0 minimum, pay what you want
- Suggested tags: `pixel-art`, `platformer`, `retro`, `pygame`, `2d`, `action`, `balearic-islands`, `indie`

**Uploads**:
- `SaFona-linux.zip` — marked as Linux
- `SaFona-windows.zip` — marked as Windows

**Butler upload commands** (for subsequent updates):
```bash
butler push dist/SaFona-linux.zip <username>/sa-fona:linux
butler push dist/SaFona-windows.zip <username>/sa-fona:windows
```

Butler handles delta compression — only changed bytes are uploaded on updates.

## 5. Documentation

Three documentation deliverables that integrate with the existing doc structure.

### 5a. `docs/distribution.md` — Developer Build & Publish Guide

Audience: the dev team (same as `software_architecture.md` and `implementation_roadmap.md`).

Contents:
- **Prerequisites**: Python 3.11, conda `safona` env, PyInstaller, butler CLI
- **Building locally**: How to run `build.sh`, what it produces, where output lands
- **Testing a build**: How to run the bundled executable locally before uploading
- **Uploading to itch.io**: butler install, authentication, push commands, channel naming
- **Updating the game**: How versioning works with butler, how to push a patch
- **Troubleshooting**: Common PyInstaller issues (missing assets, DLL errors, path problems)

### 5b. Update `README.md` — Download & Build Sections

Add to the existing README (which already has Installation, Running, Controls, etc.):

- **"Download" section** near the top (after the intro, before Installation): link to the itch.io page so GitHub visitors know where to get the playable game
- **"Building for Distribution" section** (after Development): one-paragraph summary pointing to `docs/distribution.md` for full instructions

### 5c. `dist/README.txt` — Player-Facing README (Bundled in Zip)

A short plain-text file included in the distributable zip. Generated by `build.sh` from a template so it stays in sync with the game version.

Contents:
- Game title and one-line description
- System requirements (OS, minimum specs)
- How to launch (run `SaFona.exe` / `./SaFona`)
- Controls table
- Known issues (if any)
- Link to itch.io page for updates and support
- License notice (GPL-3.0)

Template lives at `dist_assets/README.txt.template` — the build script substitutes the version from `pyproject.toml`.

## 6. Files Created / Modified

| File | Action | Description |
|------|--------|-------------|
| `safona.spec` | **New** | PyInstaller build specification |
| `build.sh` | **New** | Build script for producing distributable archives |
| `sa_fona/config/settings.py` | **Modified** | Add frozen-mode path detection (~8 lines) |
| `sa_fona/rendering/asset_loader.py` | **Modified** | Add frozen-mode root path detection (~5 lines) |
| `sa_fona/systems/save_system.py` | **No change** | Already creates saves directory with `mkdir(parents=True)` |
| `.gitignore` | **Modified** | Add `build/`, `dist/` |
| `pyproject.toml` | **Modified** | Add `pyinstaller` to optional dev dependencies |
| `docs/distribution.md` | **New** | Developer guide: building, testing, and publishing to itch.io |
| `README.md` | **Modified** | Add Download link and Building for Distribution section |
| `dist_assets/README.txt.template` | **New** | Player-facing README template, bundled into zip by build script |

## 7. Out of Scope

- Mac builds — can be added later when a Mac environment is available
- CI/CD automation — manual builds for now
- Auto-updater — itch.io desktop app handles updates natively
- Splash screen or loading screen changes
- DRM or license verification
- Game content changes (this is packaging only)

## 8. Estimated Build Size

| Component | Size |
|-----------|------|
| Python 3.11 runtime | ~15 MB |
| Pygame + SDL libraries | ~15-20 MB |
| Sa Fona source code | ~2 MB |
| Game data (JSON) | ~0.5 MB |
| Game assets (images) | ~14 MB |
| **Total per platform** | **~50-70 MB** |

Well within itch.io's 1 GB limit.
