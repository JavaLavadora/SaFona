# D2: Tilemap, Physics & Camera -- Handoff Report

**Author:** N'Andreu (Engine Programmer)
**Date:** 2026-04-17
**GitHub Issue:** #19
**Depends on:** D1 (merged to master)

## Summary

Implemented the tilemap system, AABB physics with collision resolution, and a smooth-follow camera with screen shake. All systems are data-driven and load from JSON level files.

## What Was Built

### New Modules

| Module | Purpose |
|--------|---------|
| `sa_fona/level/__init__.py` | Package init for level subsystem |
| `sa_fona/level/tilemap.py` | `TileMap` class: multi-layer tile grid, collision queries, viewport-culled rendering |
| `sa_fona/level/level_loader.py` | `LevelLoader` + `LevelData` dataclass: loads JSON, produces runtime data |
| `sa_fona/systems/__init__.py` | Package init for game systems |
| `sa_fona/systems/physics.py` | `PhysicsSystem`: gravity, AABB collision, one-way platforms |
| `sa_fona/core/camera.py` | `Camera`: lerp follow, level-bound clamping, screen shake |
| `sa_fona/scenes/demo_tilemap_scene.py` | `DemoTilemapScene`: playable demo with all D2 systems |
| `sa_fona/data/levels/test/test_level.json` | 60x15 test level with platforms, hazards, gaps |

### Modified Modules

| Module | Change |
|--------|--------|
| `sa_fona/core/game.py` | Swapped `TestScene` for `DemoTilemapScene` as initial scene; generalized quit check |

### Tests

| Test File | Count | Coverage |
|-----------|-------|----------|
| `tests/test_tilemap.py` | 16 | Load, collision rects, tile accessors, dimensions |
| `tests/test_physics.py` | 10 | Gravity, ground landing, one-way pass-through, wall collision |
| `tests/test_camera.py` | 7 | Follow, clamp, apply offset, shake |
| `tests/test_level_loader.py` | 12 | Load, spawn points, dimensions, entities, metadata |
| **Total new** | **45** | |
| **Total suite** | **118** | All passing (70 D1 + 48 D2) |

## Design Decisions

1. **Ground-contact probe:** When an entity is `on_ground`, the physics system probes 1px downward each frame to re-detect ground contact. This prevents the entity from flickering between grounded and airborne states caused by sub-pixel gravity accumulation rounding to zero displacement.

2. **Collision layers are data-driven:** Collision categories (`solid`, `one_way`, `hazard`, `breakable_slam`) and their tile IDs come from the level JSON. No hardcoded tile IDs in the physics code.

3. **Viewport culling in TileMap:** `render_layer` only iterates tiles visible within the camera viewport, skipping off-screen tiles entirely.

4. **Camera smoothing via lerp:** `camera_pos += (target_pos - camera_pos) * smoothing * dt` with smoothing=5.0 gives responsive but not jarring follow. Screen shake uses linear decay.

5. **Tileset surface parameter:** `TileMap.__init__` accepts an optional `tileset_surface` parameter for future real-asset rendering. Currently unused (placeholder colored rects).

## Test Level Layout (60x15)

- **Row 14 (bottom):** Solid ground with two gaps (cols 14-16 and cols 40-42) and two hazard tiles (cols 22-23)
- **Row 5:** High solid platform (cols 47-50)
- **Row 7:** One-way platforms (cols 11-13, cols 35-38)
- **Row 8:** Solid platform (cols 23-27)
- **Row 9:** One-way platform (cols 42-44)
- **Row 10:** Solid platforms (cols 6-9, cols 51-54)
- **Row 11:** One-way platform (cols 17-19)
- **Player spawn:** tile (2, 12) -- above ground
- **Companion spawn:** tile (3, 12)

## Open Questions

1. **Hazard tile behavior:** Currently hazard tiles have collision rects but no damage logic. This will be needed in D5 (Player Entity) or D6 (Enemy/Combat).

2. **Breakable tiles:** `breakable_slam` is defined in the collision type system but has no destruction logic yet. Will need an event-driven approach (EventBus publish on slam attack).

## How to Run the Demo

```bash
conda activate safona
Xvfb :99 -screen 0 1152x648x24 &
x11vnc -display :99 -nopw -forever -shared -rfbport 5900 &
websockify --web /usr/share/novnc 6080 localhost:5900 &
DISPLAY=:99 python -m sa_fona.main
```

Forward port **6080** and open `http://localhost:6080/vnc.html`.

**Controls:** Arrow keys/WASD to move, Space/W/Up to jump, Enter for screen shake, ESC to quit.
