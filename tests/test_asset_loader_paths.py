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
