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
    (os.path.join(_ROOT, "assets", "environment"), os.path.join("assets", "environment")),
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
