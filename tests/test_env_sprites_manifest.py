"""Tests for environment sprite manifest entries."""

import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent.parent / "sa_fona" / "data" / "asset_manifest.json"


def test_manifest_has_bonfire_entry():
    manifest = json.loads(MANIFEST_PATH.read_text())
    entry = manifest["sprites"]["env_bonfire"]
    assert entry["path"] == "assets/environment/bonfire.png"
    assert entry["frame_width"] == 24
    assert entry["frame_height"] == 32
    assert entry["frame_count"] == 2


def test_manifest_has_taula_gate_entry():
    manifest = json.loads(MANIFEST_PATH.read_text())
    entry = manifest["sprites"]["env_taula_gate"]
    assert entry["path"] == "assets/environment/taula_gate.png"
    assert entry["frame_width"] == 32
    assert entry["frame_height"] == 48
    assert entry["frame_count"] == 1
