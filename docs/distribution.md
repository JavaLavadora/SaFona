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
