"""Shared test fixtures for the Sa Fona test suite."""

from __future__ import annotations

import pytest

from sa_fona.rendering.asset_loader import clear_caches


@pytest.fixture(autouse=True)
def _clear_asset_caches():
    """Reset the centralised asset caches between every test.

    Without this, surfaces loaded during one test (which may have a
    ``pygame.display`` initialised) leak into later tests that do not
    set up a display, causing unexpected sprite-vs-placeholder
    behaviour.
    """
    yield
    clear_caches()
