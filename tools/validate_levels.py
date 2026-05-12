#!/usr/bin/env python3
"""Level validator: physics-accurate reachability + structural checks.

Uses BFS over a discretized state space that models the player's actual
movement capabilities (walk, jump, fall, wall jump, wall slide) to prove
every level is completable from spawn to level_end trigger.

CRITICAL: All movement checks verify the ENTIRE path is clear — the
player cannot teleport through walls. Every horizontal or vertical
movement traces through each intermediate tile position.

Usage:
    python tools/validate_levels.py                    # validate all world1 levels
    python tools/validate_levels.py world1/level_1_2   # validate one level
"""

from __future__ import annotations

import json
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TILE_SIZE = 24

# Player physics (must match sa_fona/config/settings.py).
PLAYER_TILES_W = 1  # ceil(20/24)
PLAYER_TILES_H = 2  # ceil(42/24)

JUMP_FORCE = 495.0
GRAVITY = 1200.0
MAX_JUMP_HEIGHT_PX = (JUMP_FORCE ** 2) / (2 * GRAVITY)  # ~102 px
MAX_JUMP_HEIGHT_TILES = int(MAX_JUMP_HEIGHT_PX / TILE_SIZE)  # 4

WALL_JUMP_FORCE_Y = 465.0
MAX_WJ_HEIGHT_TILES = int((WALL_JUMP_FORCE_Y ** 2) / (2 * GRAVITY) / TILE_SIZE)  # 3

WALL_JUMP_FORCE_X = 240.0
WALL_JUMP_LOCKOUT = 0.40
MAX_WJ_HORIZ_TILES = int(WALL_JUMP_FORCE_X * WALL_JUMP_LOCKOUT / TILE_SIZE)  # 4

MOVE_SPEED = 180.0
JUMP_AIR_TIME = 2 * JUMP_FORCE / GRAVITY
MAX_JUMP_HORIZ_TILES = int(MOVE_SPEED * JUMP_AIR_TIME / TILE_SIZE)  # 6


@dataclass
class ValidationError:
    level: str
    category: str
    message: str
    tile_x: int = -1
    tile_y: int = -1

    def __str__(self) -> str:
        loc = f" at ({self.tile_x}, {self.tile_y})" if self.tile_x >= 0 else ""
        return f"[{self.category}]{loc}: {self.message}"


@dataclass
class ValidationResult:
    level_name: str
    level_path: str
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reachable_positions: int = 0
    total_standable: int = 0
    path_found: bool = False

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


class LevelValidator:

    def __init__(self, level_data: dict, level_path: str) -> None:
        self._data = level_data
        self._path = level_path
        meta = level_data.get("metadata", {})
        dims = level_data.get("dimensions", {})
        self._name = meta.get("name", level_data.get("name", "Unknown"))
        self._width = dims.get("width", level_data.get("width", 0))
        self._height = dims.get("height", level_data.get("height", 0))

        ct = level_data.get("collision_types", {})
        self._solid_ids: set[int] = set()
        self._solid_ids.update(ct.get("solid", []))

        layers = level_data.get("layers", {})
        self._midground: list[list[int]] = layers.get("midground", [])

        self._errors: list[ValidationError] = []
        self._warnings: list[str] = []

    def _err(self, cat: str, msg: str, tx: int = -1, ty: int = -1) -> None:
        self._errors.append(ValidationError(self._name, cat, msg, tx, ty))

    def _warn(self, msg: str) -> None:
        self._warnings.append(msg)

    # ── Tile queries ──────────────────────────────────────────────

    def is_solid(self, tx: int, ty: int) -> bool:
        if tx < 0 or tx >= self._width or ty < 0 or ty >= self._height:
            return False
        row = self._midground[ty] if ty < len(self._midground) else []
        tid = row[tx] if tx < len(row) else 0
        return tid in self._solid_ids

    def is_empty(self, tx: int, ty: int) -> bool:
        if tx < 0 or tx >= self._width:
            return False
        if ty < 0 or ty >= self._height:
            return True
        return not self.is_solid(tx, ty)

    def player_fits(self, tx: int, ty: int) -> bool:
        """Player (2 wide, 2 tall) with bottom-left at (tx, ty)."""
        for dx in range(PLAYER_TILES_W):
            for dy in range(PLAYER_TILES_H):
                if not self.is_empty(tx + dx, ty - dy):
                    return False
        return True

    def can_stand(self, tx: int, ty: int) -> bool:
        if not self.player_fits(tx, ty):
            return False
        return self.is_solid(tx, ty + 1) or self.is_solid(tx + 1, ty + 1)

    def has_wall_left(self, tx: int, ty: int) -> bool:
        return self.is_solid(tx - 1, ty) or self.is_solid(tx - 1, ty - 1)

    def has_wall_right(self, tx: int, ty: int) -> bool:
        rx = tx + PLAYER_TILES_W
        return self.is_solid(rx, ty) or self.is_solid(rx, ty - 1)

    # ── Path-clear checks (the critical fix) ──────────────────────

    def _horiz_path_clear(self, from_x: int, to_x: int, at_y: int) -> bool:
        """Check player fits at every column from from_x to to_x at height at_y."""
        step = 1 if to_x >= from_x else -1
        cx = from_x
        while True:
            if not self.player_fits(cx, at_y):
                return False
            if cx == to_x:
                break
            cx += step
        return True

    def _vert_path_clear(self, at_x: int, from_y: int, to_y: int) -> bool:
        """Check player fits at every row from from_y to to_y at column at_x."""
        step = 1 if to_y >= from_y else -1
        cy = from_y
        while True:
            if not self.player_fits(at_x, cy):
                return False
            if cy == to_y:
                break
            cy += step
        return True

    def _jump_arc_reachable(self, from_x: int, from_y: int,
                            to_x: int, peak_y: int) -> bool:
        """Check a jump arc: go up to peak_y at from_x, move horizontally
        to to_x at peak_y. Conservative: checks vertical then horizontal."""
        if not self._vert_path_clear(from_x, from_y, peak_y):
            return False
        if not self._horiz_path_clear(from_x, to_x, peak_y):
            return False
        return True

    # ── Structural checks ─────────────────────────────────────────

    def check_dimensions(self) -> None:
        if len(self._midground) != self._height:
            self._err("STRUCTURE", f"Midground has {len(self._midground)} rows, expected {self._height}")
        for i, row in enumerate(self._midground):
            if len(row) != self._width:
                self._err("STRUCTURE", f"Row {i} has {len(row)} tiles, expected {self._width}", ty=i)

    def check_player_spawn(self) -> None:
        spawn = self._data.get("player_spawn", {})
        sx, sy = spawn.get("x", 0), spawn.get("y", 0)
        if not self.player_fits(sx, sy):
            self._err("SPAWN", f"Player doesn't fit at spawn ({sx}, {sy})", sx, sy)
        has_ground = False
        for dy in range(1, self._height - sy):
            if self.is_solid(sx, sy + dy) or self.is_solid(sx + 1, sy + dy):
                has_ground = True
                break
        if not has_ground:
            self._err("SPAWN", f"No ground below spawn ({sx}, {sy})", sx, sy)

    def check_enemy_spawns(self) -> None:
        for ent in self._data.get("entities", []):
            if ent.get("type") != "enemy":
                continue
            ex, ey = ent.get("x", 0), ent.get("y", 0)
            etype = ent.get("enemy_type", "unknown")
            if self.is_solid(ex, ey):
                self._err("ENEMY", f"{etype} spawns inside solid tile", ex, ey)
            if not self.is_solid(ex, ey + 1):
                self._err("ENEMY", f"{etype} has no ground below spawn", ex, ey)

    def _get_trigger_rect(self, t: dict) -> tuple[int, int, int, int]:
        rect = t.get("rect", {})
        x = rect.get("x", t.get("x", 0))
        y = rect.get("y", t.get("y", 0))
        w = rect.get("w", t.get("width", 1))
        h = rect.get("h", t.get("height", 1))
        return x, y, w, h

    def check_level_end_exists(self) -> None:
        if not any(t.get("type") == "level_end" for t in self._data.get("triggers", [])):
            self._err("TRIGGER", "No level_end trigger found")

    # ── Reachability BFS ──────────────────────────────────────────

    def find_reachable(self) -> tuple[set[tuple[int, int]], bool]:
        """BFS with collision-aware movement. No teleporting through walls."""
        spawn = self._data.get("player_spawn", {})
        start = (spawn.get("x", 0), spawn.get("y", 0))

        end_rects: list[tuple[int, int, int, int]] = []
        for t in self._data.get("triggers", []):
            if t.get("type") == "level_end":
                x, y, w, h = self._get_trigger_rect(t)
                end_rects.append((x, y, x + w, y + h))

        visited: set[tuple[int, int]] = set()
        queue: deque[tuple[int, int]] = deque()

        def enqueue(nx: int, ny: int) -> None:
            if (nx, ny) not in visited and 0 <= nx < self._width and 0 <= ny < self._height:
                if self.player_fits(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # Seed: spawn position + fall to landing.
        sx, sy = start
        if self.player_fits(sx, sy):
            enqueue(sx, sy)
            if not self.can_stand(sx, sy):
                for dy in range(1, self._height - sy):
                    land_y = sy + dy
                    if not self.player_fits(sx, land_y):
                        break
                    if self.can_stand(sx, land_y):
                        enqueue(sx, land_y)
                        break

        reached_end = False

        while queue:
            tx, ty = queue.popleft()

            for ex1, ey1, ex2, ey2 in end_rects:
                if tx + 1 >= ex1 and tx < ex2 and ty >= ey1 and ty < ey2:
                    reached_end = True

            on_ground = self.can_stand(tx, ty)
            in_air = self.player_fits(tx, ty) and not on_ground
            wl = self.has_wall_left(tx, ty)
            wr = self.has_wall_right(tx, ty)

            # ── 1. WALK (on ground, one tile at a time) ──
            if on_ground:
                if self.player_fits(tx - 1, ty):
                    enqueue(tx - 1, ty)
                if self.player_fits(tx + 1, ty):
                    enqueue(tx + 1, ty)
                # Step up 1-tile ledge.
                for dx in (-1, 1):
                    ntx = tx + dx
                    if not self.player_fits(ntx, ty) and self.player_fits(ntx, ty - 1):
                        if self.can_stand(ntx, ty - 1):
                            enqueue(ntx, ty - 1)

            # ── 2. FALL (straight down or 1-column drift per row) ──
            prev_x_set = {tx}
            for fall_dy in range(1, self._height):
                ny = ty + fall_dy
                if ny >= self._height:
                    break
                next_x_set: set[int] = set()
                for cx in prev_x_set:
                    if not self.player_fits(cx, ny):
                        continue
                    next_x_set.add(cx)
                    if self.can_stand(cx, ny):
                        enqueue(cx, ny)
                    # Drift left/right by 1 tile while falling.
                    for drift in (-1, 1):
                        dx = cx + drift
                        if self.player_fits(dx, ny):
                            next_x_set.add(dx)
                            if self.can_stand(dx, ny):
                                enqueue(dx, ny)
                if not next_x_set:
                    break
                prev_x_set = next_x_set

            # ── 3. GROUND JUMP (arc: rise then fall) ──
            if on_ground:
                # Rise phase: go up column by column, checking clearance.
                for peak_dy in range(1, MAX_JUMP_HEIGHT_TILES + 1):
                    peak_y = ty - peak_dy
                    if peak_y < 0:
                        break
                    if not self._vert_path_clear(tx, ty - 1, peak_y):
                        break
                    # At peak height, move horizontally checking each column.
                    for direction in (-1, 1):
                        cx = tx
                        for _ in range(MAX_JUMP_HORIZ_TILES):
                            nx = cx + direction
                            if nx < 0 or nx >= self._width:
                                break
                            if not self.player_fits(nx, peak_y):
                                break
                            cx = nx
                            enqueue(cx, peak_y)
                            # From this horizontal position, fall down.
                            for land_dy in range(1, self._height):
                                land_y = peak_y + land_dy
                                if land_y >= self._height:
                                    break
                                if not self.player_fits(cx, land_y):
                                    break
                                if self.can_stand(cx, land_y):
                                    enqueue(cx, land_y)
                                    break
                    # Also just jump straight up and land at same x.
                    enqueue(tx, peak_y)

            # ── 4. WALL JUMP (must be in air touching a wall) ──
            if in_air and (wl or wr):
                if wl:
                    # Jump right + up from left wall.
                    for up_dy in range(0, MAX_WJ_HEIGHT_TILES + 1):
                        ny = ty - up_dy
                        if ny < 0:
                            break
                        if not self._vert_path_clear(tx, ty, ny):
                            break
                        cx = tx
                        for _ in range(MAX_WJ_HORIZ_TILES):
                            nx = cx + 1
                            if nx >= self._width:
                                break
                            if not self.player_fits(nx, ny):
                                break
                            cx = nx
                            enqueue(cx, ny)
                if wr:
                    # Jump left + up from right wall.
                    for up_dy in range(0, MAX_WJ_HEIGHT_TILES + 1):
                        ny = ty - up_dy
                        if ny < 0:
                            break
                        if not self._vert_path_clear(tx, ty, ny):
                            break
                        cx = tx
                        for _ in range(MAX_WJ_HORIZ_TILES):
                            nx = cx - 1
                            if nx < 0:
                                break
                            if not self.player_fits(nx, ny):
                                break
                            cx = nx
                            enqueue(cx, ny)

            # ── 5. WALL SLIDE (slide down along a wall) ──
            if self.player_fits(tx, ty) and (wl or wr):
                for slide_dy in range(1, self._height):
                    ny = ty + slide_dy
                    if ny >= self._height:
                        break
                    if not self.player_fits(tx, ny):
                        break
                    enqueue(tx, ny)
                    if self.can_stand(tx, ny):
                        break

        return visited, reached_end

    # ── Main validation ───────────────────────────────────────────

    def validate(self) -> ValidationResult:
        result = ValidationResult(self._name, self._path)

        self.check_dimensions()
        self.check_player_spawn()
        self.check_enemy_spawns()
        self.check_level_end_exists()

        reachable, path_found = self.find_reachable()
        result.reachable_positions = len(reachable)
        result.path_found = path_found

        standable = sum(
            1 for ty in range(self._height) for tx in range(self._width)
            if self.can_stand(tx, ty)
        )
        result.total_standable = standable

        if not path_found:
            self._err("REACHABILITY", "No path from spawn to level_end trigger!")

        for ent in self._data.get("entities", []):
            if ent.get("type") != "enemy":
                continue
            ex, ey = ent.get("x", 0), ent.get("y", 0)
            etype = ent.get("enemy_type", "unknown")
            near = any(
                (ex + dx, ey + dy) in reachable
                for dx in range(-3, 4) for dy in range(-3, 4)
            )
            if not near:
                self._warn(f"Enemy {etype} at ({ex}, {ey}) may be unreachable")

        for t in self._data.get("triggers", []):
            ttype = t.get("type", "")
            trx, try_, trw, trh = self._get_trigger_rect(t)
            near = any(
                (trx + dx, try_ + dy) in reachable
                for dx in range(-1, trw + 1) for dy in range(-1, trh + 1)
            )
            if not near:
                self._warn(f"Trigger '{ttype}' at ({trx}, {try_}) may be unreachable")

        result.errors = self._errors
        result.warnings = self._warnings
        return result


def load_level(level_id: str) -> tuple[dict, str]:
    data_dir = PROJECT_ROOT / "sa_fona" / "data" / "levels"
    path = data_dir / f"{level_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), str(path)


def validate_level(level_id: str) -> ValidationResult:
    data, path = load_level(level_id)
    return LevelValidator(data, path).validate()


def main() -> None:
    level_ids = sys.argv[1:] or [
        "world1/level_1_1", "world1/level_1_2",
        "world1/level_1_3", "world1/level_1_4",
    ]

    all_passed = True
    for lid in level_ids:
        print(f"\n{'='*60}")
        print(f"Validating: {lid}")
        print(f"{'='*60}")

        try:
            result = validate_level(lid)
        except Exception as e:
            print(f"  FAILED TO LOAD: {e}")
            all_passed = False
            continue

        status = "PASS" if result.passed else "FAIL"
        print(f"  Level: {result.level_name}")
        print(f"  Status: {status}")
        print(f"  Path to exit: {'FOUND' if result.path_found else 'NOT FOUND'}")
        print(f"  Reachable: {result.reachable_positions}/{result.total_standable} standable")

        if result.errors:
            print(f"\n  ERRORS ({len(result.errors)}):")
            for err in result.errors:
                print(f"    X {err}")
            all_passed = False

        if result.warnings:
            print(f"\n  WARNINGS ({len(result.warnings)}):")
            for w in result.warnings:
                print(f"    ! {w}")

    print(f"\n{'='*60}")
    print(f"Overall: {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}")
    print(f"{'='*60}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
