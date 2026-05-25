"""Save system: JSON save/load with death rollback.

Manages a single save slot as a JSON file. Tracks the player's current
level, stone count, hearts, masks, and consumables. Provides level-entry
snapshots for death rollback so the player restarts a failed level with
the state they had when they entered it.

ALL persistent state flows through this system. Scenes call ``save()``
at level transitions and ``rollback_to_snapshot()`` on death.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sa_fona.config.settings import SAVES_DIR
from sa_fona.core.event_bus import EventBus


class SaveSystem:
    """JSON-based save/load with death rollback.

    Uses a single save slot (decided, Issue #13). The ``save_path``
    parameter makes multi-slot extension trivial: pass a different
    path per slot.

    Args:
        event_bus: Shared event bus for subscribing to game events.
        save_path: Filesystem path to the save file. Defaults to
            ``saves/save_slot_1.json``.
    """

    # Default save format version.
    _VERSION = "1.0"

    def __init__(
        self,
        event_bus: EventBus,
        save_path: str | None = None,
    ) -> None:
        self._event_bus = event_bus

        if save_path is None:
            save_path = str(SAVES_DIR / "save_slot_1.json")
        self._save_path = save_path

        # In-memory game state (populated on load or new game).
        self._state: dict[str, Any] = self._default_state()

        # Level-entry snapshot for death rollback.
        self._level_entry_snapshot: dict[str, Any] | None = None

        # Subscribe to game events.
        self._event_bus.subscribe("level_complete", self._on_level_complete)

    # ── Default state ─────────────────────────────────────────────

    @staticmethod
    def _default_state() -> dict[str, Any]:
        """Return the default new-game state.

        Returns:
            A dict with all save fields at their starting values.
        """
        return {
            "version": SaveSystem._VERSION,
            "timestamp": "",
            "current_level": "",
            "stone_count": 0,
            "current_hearts": 3.0,
            "max_hearts": 3,
            "masks_unlocked": [],
            "masks_equipped": [],
            "consumables": {},
            "level_completion": {},
        }

    # ── Public API ────────────────────────────────────────────────

    @property
    def state(self) -> dict[str, Any]:
        """Current in-memory game state (read-only access)."""
        return self._state

    def save(self) -> None:
        """Write the current state to disk.

        Creates the parent directory if it does not exist. Stamps the
        save with the current UTC timestamp.
        """
        self._state["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._state["version"] = self._VERSION

        save_dir = Path(self._save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=str(save_dir), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._state, fh, indent=2)
            # On Windows, os.replace can fail with PermissionError if
            # antivirus or another process has the target file locked.
            # Retry a few times before falling back to direct write.
            import time
            for attempt in range(3):
                try:
                    os.replace(tmp_path, self._save_path)
                    return
                except PermissionError:
                    if attempt < 2:
                        time.sleep(0.1)
            # Fallback: write directly if atomic replace keeps failing.
            with open(self._save_path, "w", encoding="utf-8") as fh:
                json.dump(self._state, fh, indent=2)
        except BaseException:
            pass
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def load(self) -> dict[str, Any] | None:
        """Load game state from disk.

        Returns:
            The loaded state dict, or ``None`` if no save file exists
            or the file is unreadable.
        """
        try:
            with open(self._save_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            merged = self._default_state()
            merged.update(data)
            self._state = merged
            return merged
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def exists(self) -> bool:
        """Check whether a save file exists on disk.

        Returns:
            True if the save file is present.
        """
        return Path(self._save_path).is_file()

    def delete(self) -> None:
        """Delete the save file and reset to default state."""
        path = Path(self._save_path)
        if path.is_file():
            path.unlink()
        self._state = self._default_state()
        self._level_entry_snapshot = None

    # ── State mutation helpers ────────────────────────────────────

    def set_level(self, level_path: str) -> None:
        """Set the current level path in the state.

        Args:
            level_path: Filesystem path to the level JSON file.
        """
        self._state["current_level"] = level_path

    def set_player_state(
        self,
        stone_count: int,
        current_hearts: float,
        max_hearts: int,
    ) -> None:
        """Update the player-related fields in the state.

        Args:
            stone_count: Current sling stone count.
            current_hearts: Current heart count (may be fractional).
            max_hearts: Maximum heart capacity.
        """
        self._state["stone_count"] = stone_count
        self._state["current_hearts"] = current_hearts
        self._state["max_hearts"] = max_hearts

    # ── Snapshot / rollback (death) ───────────────────────────────

    def snapshot_level_entry(
        self,
        stone_count: int,
        current_hearts: float,
        max_hearts: int,
        consumables: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Capture state at level entry for death rollback.

        Call this at the start of each level. The returned snapshot is
        also stored internally for ``rollback_to_snapshot()``.

        Args:
            stone_count: Player's stone count at level entry.
            current_hearts: Player's heart count at level entry.
            max_hearts: Player's maximum hearts at level entry.
            consumables: Consumable inventory dict (copied).

        Returns:
            A snapshot dict capturing the level-entry state.
        """
        snapshot = {
            "stone_count": stone_count,
            "current_hearts": current_hearts,
            "max_hearts": max_hearts,
            "consumables": dict(consumables) if consumables else {},
        }
        self._level_entry_snapshot = snapshot
        return snapshot

    def rollback_to_snapshot(self) -> dict[str, Any] | None:
        """Restore state from the level-entry snapshot.

        Applies the snapshot to the internal state and returns it so
        the caller can propagate values to subsystems.

        Returns:
            The snapshot dict, or ``None`` if no snapshot was taken.
        """
        if self._level_entry_snapshot is None:
            return None

        snap = self._level_entry_snapshot
        self._state["stone_count"] = snap["stone_count"]
        self._state["current_hearts"] = snap["current_hearts"]
        self._state["max_hearts"] = snap["max_hearts"]
        self._state["consumables"] = dict(snap.get("consumables", {}))
        return snap

    @property
    def level_entry_snapshot(self) -> dict[str, Any] | None:
        """The most recent level-entry snapshot (read-only)."""
        return self._level_entry_snapshot

    # ── Event handlers ────────────────────────────────────────────

    def _on_level_complete(self, **kwargs: Any) -> None:
        """Handle level_complete events by auto-saving.

        The caller (GameplayScene) should update state fields
        (level path, player state) before publishing this event.
        """
        self.save()

    # ── Cleanup ───────────────────────────────────────────────────

    def cleanup(self) -> None:
        """Unsubscribe from EventBus events."""
        try:
            self._event_bus.unsubscribe("level_complete", self._on_level_complete)
        except ValueError:
            pass
