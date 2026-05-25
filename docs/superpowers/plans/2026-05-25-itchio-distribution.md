# itch.io Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package Sa Fona into standalone executables for Windows and Linux using PyInstaller, with a build script and documentation, ready for itch.io upload.

**Architecture:** PyInstaller bundles the Python runtime, Pygame, source code, and game assets into a self-contained directory. Two code files (`settings.py`, `asset_loader.py`) get a small frozen-mode path detection block so assets resolve correctly inside the bundle. A `build.sh` script automates the build-and-zip process.

**Tech Stack:** PyInstaller, Pygame 2.6, Python 3.11, bash, butler (itch.io CLI)

**Spec:** `docs/superpowers/specs/2026-05-25-itchio-distribution-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `sa_fona/config/settings.py` | Modify | Frozen-mode path detection for `PACKAGE_DIR`, `ASSETS_DIR`, `SAVES_DIR` |
| `sa_fona/rendering/asset_loader.py` | Modify | Frozen-mode `_PROJECT_ROOT` detection |
| `tests/test_settings.py` | Modify | Add tests for frozen-mode path logic |
| `tests/test_asset_loader_paths.py` | Create | Test `_PROJECT_ROOT` resolves correctly in both modes |
| `safona.spec` | Create | PyInstaller build specification |
| `build.sh` | Create | Build script: run PyInstaller, zip output |
| `dist_assets/README.txt.template` | Create | Player-facing README template bundled in zip |
| `pyproject.toml` | Modify | Add `pyinstaller` to dev dependencies |
| `.gitignore` | Modify | Add `*.spec.bak` |
| `docs/distribution.md` | Create | Developer guide for building and publishing |
| `README.md` | Modify | Add Download and Building for Distribution sections |

---

### Task 1: Frozen-mode path detection in settings.py

**Files:**
- Modify: `sa_fona/config/settings.py:1-74`
- Modify: `tests/test_settings.py`

- [ ] **Step 1: Write failing tests for frozen-mode paths**

Add a new test class to `tests/test_settings.py`:

```python
import sys
from pathlib import Path
from unittest.mock import patch


class TestFrozenModePaths:
    """Verify path resolution adapts to PyInstaller frozen mode."""

    def test_normal_mode_package_dir_is_pathlib(self) -> None:
        from sa_fona.config import settings
        assert isinstance(settings.PACKAGE_DIR, Path)

    def test_normal_mode_data_dir_under_package(self) -> None:
        from sa_fona.config import settings
        assert settings.DATA_DIR == settings.PACKAGE_DIR / "data"

    def test_normal_mode_assets_dir_exists(self) -> None:
        from sa_fona.config import settings
        assert settings.ASSETS_DIR.is_dir()

    def test_frozen_mode_uses_meipass(self, tmp_path) -> None:
        fake_meipass = tmp_path / "meipass_fake"
        fake_meipass.mkdir()
        (fake_meipass / "sa_fona").mkdir()
        (fake_meipass / "assets").mkdir()

        with patch.dict(sys.__dict__, {"frozen": True, "_MEIPASS": str(fake_meipass)}):
            # Force re-evaluation of the module-level paths.
            from sa_fona.config import settings
            import importlib
            importlib.reload(settings)

            assert settings.PACKAGE_DIR == fake_meipass / "sa_fona"
            assert settings.ASSETS_DIR == fake_meipass / "assets"
            assert ".safona" in str(settings.SAVES_DIR)

        # Restore normal paths.
        importlib.reload(settings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda run -n safona python -m pytest tests/test_settings.py::TestFrozenModePaths -v`
Expected: `test_frozen_mode_uses_meipass` FAILS because `settings.py` does not check `sys.frozen`.

- [ ] **Step 3: Implement frozen-mode path detection**

Replace the filesystem paths section at the bottom of `sa_fona/config/settings.py` (lines 69-74). The full file ending becomes:

```python
import sys

# ── Filesystem Paths ────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BUNDLE_DIR: Path = Path(sys._MEIPASS)
    PACKAGE_DIR: Path = _BUNDLE_DIR / "sa_fona"
    ASSETS_DIR: Path = _BUNDLE_DIR / "assets"
    SAVES_DIR: Path = Path.home() / ".safona" / "saves"
else:
    PACKAGE_DIR: Path = Path(__file__).resolve().parent.parent
    ASSETS_DIR: Path = PACKAGE_DIR.parent / "assets"
    SAVES_DIR: Path = PACKAGE_DIR.parent / "saves"

DATA_DIR: Path = PACKAGE_DIR / "data"
```

Note: `sys` is already imported at the top of the file (it's used transitively by `pathlib`), but add `import sys` after `from pathlib import Path` if not present.

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda run -n safona python -m pytest tests/test_settings.py -v`
Expected: ALL tests pass, including the new `TestFrozenModePaths` class and the existing `TestPaths` class.

- [ ] **Step 5: Commit**

```bash
git add sa_fona/config/settings.py tests/test_settings.py
git commit -m "feat: add PyInstaller frozen-mode path detection in settings"
```

---

### Task 2: Frozen-mode path detection in asset_loader.py

**Files:**
- Modify: `sa_fona/rendering/asset_loader.py:1-25`
- Create: `tests/test_asset_loader_paths.py`

- [ ] **Step 1: Write failing test for asset loader frozen-mode**

Create `tests/test_asset_loader_paths.py`:

```python
"""Tests for asset_loader._PROJECT_ROOT in normal and frozen modes."""

import importlib
import os
import sys
from unittest.mock import patch


class TestProjectRoot:
    """Verify _PROJECT_ROOT resolves correctly."""

    def test_normal_mode_project_root_is_string(self) -> None:
        from sa_fona.rendering import asset_loader
        assert isinstance(asset_loader._PROJECT_ROOT, str)

    def test_normal_mode_project_root_contains_sa_fona(self) -> None:
        from sa_fona.rendering import asset_loader
        assert os.path.isdir(
            os.path.join(asset_loader._PROJECT_ROOT, "sa_fona")
        )

    def test_frozen_mode_uses_meipass(self, tmp_path) -> None:
        fake_meipass = str(tmp_path / "meipass_fake")
        os.makedirs(fake_meipass, exist_ok=True)

        with patch.dict(sys.__dict__, {"frozen": True, "_MEIPASS": fake_meipass}):
            from sa_fona.rendering import asset_loader
            importlib.reload(asset_loader)

            assert asset_loader._PROJECT_ROOT == fake_meipass

        # Restore.
        importlib.reload(asset_loader)

    def test_manifest_path_under_project_root(self) -> None:
        from sa_fona.rendering import asset_loader
        assert asset_loader._MANIFEST_PATH.startswith(asset_loader._PROJECT_ROOT)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `conda run -n safona python -m pytest tests/test_asset_loader_paths.py -v`
Expected: `test_frozen_mode_uses_meipass` FAILS.

- [ ] **Step 3: Implement frozen-mode detection in asset_loader.py**

Replace lines 11-25 of `sa_fona/rendering/asset_loader.py` with:

```python
import json
import os
import sys
from typing import Any

import pygame

if getattr(sys, 'frozen', False):
    _PROJECT_ROOT = sys._MEIPASS
else:
    _PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )

_MANIFEST_PATH = os.path.join(
    _PROJECT_ROOT, "sa_fona", "data", "asset_manifest.json"
)
```

Note: `sys` import is added alongside the existing `os` import.

- [ ] **Step 4: Run tests to verify they pass**

Run: `conda run -n safona python -m pytest tests/test_asset_loader_paths.py tests/test_settings.py -v`
Expected: ALL pass.

- [ ] **Step 5: Commit**

```bash
git add sa_fona/rendering/asset_loader.py tests/test_asset_loader_paths.py
git commit -m "feat: add frozen-mode _PROJECT_ROOT detection in asset_loader"
```

---

### Task 3: PyInstaller spec file

**Files:**
- Create: `safona.spec`

- [ ] **Step 1: Create the PyInstaller spec file**

Create `safona.spec` at the project root:

```python
# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Sa Fona.

Build with:
    pyinstaller safona.spec

Output lands in dist/SaFona/
"""

import os
import platform

block_cipher = None

_ROOT = os.path.abspath(".")

datas = [
    (os.path.join(_ROOT, "sa_fona", "data"), os.path.join("sa_fona", "data")),
    (os.path.join(_ROOT, "assets", "sprites"), os.path.join("assets", "sprites")),
    (os.path.join(_ROOT, "assets", "tilesets"), os.path.join("assets", "tilesets")),
    (os.path.join(_ROOT, "assets", "backgrounds"), os.path.join("assets", "backgrounds")),
    (os.path.join(_ROOT, "assets", "ui"), os.path.join("assets", "ui")),
    (os.path.join(_ROOT, "assets", "effects"), os.path.join("assets", "effects")),
    (os.path.join(_ROOT, "assets", "portraits"), os.path.join("assets", "portraits")),
    (os.path.join(_ROOT, "assets", "palettes"), os.path.join("assets", "palettes")),
]

# Filter out data dirs that don't exist yet (e.g. palettes may be empty).
datas = [(src, dst) for src, dst in datas if os.path.isdir(src)]

a = Analysis(
    [os.path.join(_ROOT, "sa_fona", "main.py")],
    pathex=[_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=["pygame"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "email", "xml", "pydoc"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SaFona",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=platform.system() != "Windows",
    icon=os.path.join(_ROOT, "assets", "ui", "icon.ico")
    if os.path.isfile(os.path.join(_ROOT, "assets", "ui", "icon.ico"))
    else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SaFona",
)
```

- [ ] **Step 2: Verify the spec file is valid Python**

Run: `conda run -n safona python -c "compile(open('safona.spec').read(), 'safona.spec', 'exec'); print('OK')"` from project root.
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add safona.spec
git commit -m "feat: add PyInstaller spec file for distribution builds"
```

---

### Task 4: Player-facing README template

**Files:**
- Create: `dist_assets/README.txt.template`

- [ ] **Step 1: Create the dist_assets directory and template**

Create `dist_assets/README.txt.template`:

```
SA FONA v{{VERSION}}
====================

A 2D retro side-scrolling platformer set across the Balearic Islands.

You play as Balchar, a grumpy talayotic slinger cursed into time-traveling
alongside Bep, his myotragus companion.


SYSTEM REQUIREMENTS
-------------------
- OS: Windows 10+ / Linux (x86_64)
- RAM: 512 MB
- Disk: 100 MB


HOW TO PLAY
-----------
- Windows: Double-click SaFona.exe
- Linux:   Run ./SaFona from a terminal


CONTROLS
--------
  Move        Arrow keys / A, D
  Jump        Space
  Attack      X
  Interact    Enter
  Mask Power  Z
  Pause       Escape


UPDATES & SUPPORT
-----------------
Visit the itch.io page for the latest version:
  https://TODO-SET-ITCHIO-URL.itch.io/sa-fona


LICENSE
-------
This game is released under the GPL-3.0 License.
See the project repository for full license text:
  https://github.com/JavaLavadora/SaFona
```

- [ ] **Step 2: Commit**

```bash
git add dist_assets/README.txt.template
git commit -m "feat: add player-facing README template for distribution zip"
```

---

### Task 5: Build script

**Files:**
- Create: `build.sh`

- [ ] **Step 1: Create the build script**

Create `build.sh` at the project root:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VERSION=$(python3 -c "
import re
text = open('pyproject.toml').read()
m = re.search(r'version\s*=\s*\"([^\"]+)\"', text)
print(m.group(1) if m else '0.0.0')
")

TARGET="${1:-linux}"

echo "=== Sa Fona build (v${VERSION}, target: ${TARGET}) ==="

# Clean previous build artifacts.
rm -rf build/ dist/

# Ensure PyInstaller is available.
if ! python3 -m PyInstaller --version &>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

echo "Running PyInstaller..."
python3 -m PyInstaller safona.spec --noconfirm

if [ ! -d "dist/SaFona" ]; then
    echo "ERROR: PyInstaller output not found at dist/SaFona/"
    exit 1
fi

# Generate player-facing README from template.
if [ -f "dist_assets/README.txt.template" ]; then
    sed "s/{{VERSION}}/${VERSION}/g" dist_assets/README.txt.template \
        > dist/SaFona/README.txt
    echo "Generated README.txt (v${VERSION})"
fi

# Create zip archive.
PLATFORM_SUFFIX="${TARGET}"
ZIP_NAME="SaFona-${PLATFORM_SUFFIX}.zip"
cd dist
zip -r "${ZIP_NAME}" SaFona/
cd ..

FINAL_SIZE=$(du -sh "dist/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Build complete ==="
echo "  Output: dist/${ZIP_NAME} (${FINAL_SIZE})"
echo ""
echo "To upload with butler:"
echo "  butler push dist/${ZIP_NAME} <username>/sa-fona:${PLATFORM_SUFFIX}"
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x build.sh`

- [ ] **Step 3: Verify script syntax**

Run: `bash -n build.sh`
Expected: No output (no syntax errors).

- [ ] **Step 4: Commit**

```bash
git add build.sh
git commit -m "feat: add build script for PyInstaller distribution"
```

---

### Task 6: Update pyproject.toml and .gitignore

**Files:**
- Modify: `pyproject.toml`
- Modify: `.gitignore`

- [ ] **Step 1: Add pyinstaller to dev dependencies**

In `pyproject.toml`, change:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0",
]
```

to:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0",
    "pyinstaller>=6.0",
]
```

- [ ] **Step 2: Add spec.bak to .gitignore**

Append to `.gitignore`:

```
# PyInstaller
*.spec.bak
```

Note: `build/` and `dist/` are already in `.gitignore`.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml .gitignore
git commit -m "chore: add pyinstaller dev dep, gitignore spec.bak"
```

---

### Task 7: Test the build (Linux)

**Files:** None (verification only)

- [ ] **Step 1: Install PyInstaller in the conda env**

Run: `conda run -n safona pip install pyinstaller`

- [ ] **Step 2: Run the build script**

Run: `conda run -n safona bash build.sh linux` from project root.
Expected: Script completes with `=== Build complete ===` and reports the zip size.

- [ ] **Step 3: Verify the zip contents**

Run: `unzip -l dist/SaFona-linux.zip | head -30`
Expected: Contains `SaFona/SaFona` (executable), `SaFona/README.txt`, `SaFona/assets/` dirs, `SaFona/sa_fona/data/` dirs.

- [ ] **Step 4: Verify the executable starts**

Run:
```bash
Xvfb :98 -screen 0 1152x648x24 &
DISPLAY=:98 dist/SaFona/SaFona &
sleep 3
# Take a screenshot to confirm it renders.
DISPLAY=:98 import -window root /tmp/safona_dist_test.png
kill %2 2>/dev/null; kill %1 2>/dev/null
```
Expected: `/tmp/safona_dist_test.png` shows the game's main menu (or at minimum a pygame window).

- [ ] **Step 5: Check zip size is reasonable**

Run: `du -sh dist/SaFona-linux.zip`
Expected: Between 30 MB and 100 MB. If over 100 MB, investigate what got bundled that shouldn't have.

---

### Task 8: Developer distribution guide

**Files:**
- Create: `docs/distribution.md`

- [ ] **Step 1: Write the distribution guide**

Create `docs/distribution.md`:

```markdown
# Sa Fona — Building & Publishing

Guide for building standalone executables and uploading to itch.io.

## Prerequisites

- Python 3.11+ (conda `safona` environment)
- PyInstaller 6.0+ (`pip install pyinstaller` or `pip install -e ".[dev]"`)
- butler CLI (for itch.io uploads): https://itch.io/docs/butler/

## Building Locally

Run the build script from the project root:

```bash
conda activate safona
./build.sh linux        # Linux build (default)
./build.sh windows      # Windows build (run on Windows)
```

Output:
- `dist/SaFona/` — the standalone game directory
- `dist/SaFona-linux.zip` (or `-windows.zip`) — ready for upload

The script:
1. Reads the version from `pyproject.toml`
2. Runs PyInstaller with `safona.spec`
3. Generates `README.txt` from `dist_assets/README.txt.template`
4. Zips the output

## Testing a Build

Before uploading, verify the build works:

```bash
# Linux
cd dist/SaFona
./SaFona

# Windows
cd dist\SaFona
SaFona.exe
```

Check that:
- The game window opens and shows the main menu
- You can start a level and play
- Sprites and backgrounds load (not just placeholders)
- Saves work (save, quit, relaunch, continue)

## Uploading to itch.io

### First-time setup

1. Install butler: https://itch.io/docs/butler/installing.html
2. Authenticate: `butler login`
3. Create the project on itch.io (web interface):
   - Kind: Downloadable
   - Classification: Game
   - Pricing: Pay what you want, $0 minimum
   - Tags: pixel-art, platformer, retro, pygame, 2d, action, balearic-islands, indie

### Upload

```bash
butler push dist/SaFona-linux.zip <username>/sa-fona:linux
butler push dist/SaFona-windows.zip <username>/sa-fona:windows
```

Butler handles delta compression — subsequent uploads only push changed bytes.

### Versioning

butler auto-increments build numbers. To tag a specific version:

```bash
butler push dist/SaFona-linux.zip <username>/sa-fona:linux --userversion 0.1.0
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Missing assets in build | Check `safona.spec` datas list includes the directory |
| `ModuleNotFoundError` at runtime | Add the module to `hiddenimports` in `safona.spec` |
| DLL/SO not found (Windows/Linux) | PyInstaller may miss SDL deps — add to `binaries` in spec |
| Game crashes silently on Windows | Run from cmd to see console output, or set `console=True` in spec |
| Saves not persisting | Check `~/.safona/saves/` exists and is writable |
| Build over 100 MB | Check for accidental `ai_sources` inclusion; review `datas` |

## Windows Builds

Windows builds must be created on a Windows machine — PyInstaller cannot cross-compile.

1. Install Python 3.11 + conda
2. Clone the repo and `pip install pygame pyinstaller`
3. Run `build.sh windows` (or `python -m PyInstaller safona.spec`)
4. Upload `dist/SaFona-windows.zip` with butler
```

- [ ] **Step 2: Commit**

```bash
git add docs/distribution.md
git commit -m "docs: add build and publish guide for itch.io distribution"
```

---

### Task 9: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add Download section after the intro**

After the `---` on line 16 and the intro paragraph (line 18), before the `<p align="center">` gameplay screenshot (line 20), insert:

```markdown
## Download

**[Play Sa Fona on itch.io](https://TODO-SET-ITCHIO-URL.itch.io/sa-fona)** — standalone builds for Windows and Linux, no Python required.
```

- [ ] **Step 2: Add Building for Distribution section after Development**

After the Development section (after line 113, before `## License`), insert:

```markdown
## Building for Distribution

Sa Fona can be packaged as a standalone executable using PyInstaller. See [docs/distribution.md](docs/distribution.md) for the full build and upload guide.

```bash
conda activate safona
pip install pyinstaller
./build.sh linux    # produces dist/SaFona-linux.zip
```
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add download link and build-for-distribution section to README"
```

---

### Task 10: Run full test suite

**Files:** None (verification only)

- [ ] **Step 1: Run all tests**

Run: `conda run -n safona python -m pytest tests/ -x -q`
Expected: All tests pass. No regressions from the path detection changes.

- [ ] **Step 2: Verify the game still runs normally (non-frozen mode)**

Run:
```bash
Xvfb :98 -screen 0 1152x648x24 &
DISPLAY=:98 conda run -n safona python -m sa_fona.main &
sleep 3
DISPLAY=:98 import -window root /tmp/safona_normal_test.png
kill %2 2>/dev/null; kill %1 2>/dev/null
```
Expected: `/tmp/safona_normal_test.png` shows the main menu — confirms the path changes didn't break dev mode.
