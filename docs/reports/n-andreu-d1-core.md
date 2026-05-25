# D1: Core Engine Bootstrap -- Handoff Report

**Author:** N'Andreu (A + B)
**Date:** 2026-04-17
**Issue:** #17
**Branch:** `feature/d1-systems`

## What Was Implemented

### Core Foundation (N'Andreu-A)
- `sa_fona/config/settings.py` -- Global constants: 384x216 base resolution, 3x window scale, 60 FPS, color palette, filesystem paths
- `sa_fona/config/controls.py` -- JSON control-binding loader with key-name-to-pygame-constant resolution
- `sa_fona/data/controls_default.json` -- Default keyboard and gamepad bindings
- `sa_fona/data/asset_manifest.json` -- Sprite, tileset, background, and UI asset definitions
- `sa_fona/rendering/pixel_scaler.py` -- Pixel-perfect integer scaling from 384x216 to display window
- `sa_fona/core/game.py` -- Main Game class with window creation and 60 FPS delta-time loop
- `sa_fona/main.py` -- Entry point (`python -m sa_fona.main`)

### Systems (N'Andreu-B)
- `sa_fona/core/event_bus.py` -- Publish/subscribe event system with dict[str, list[Callable]] storage
- `sa_fona/core/input_handler.py` -- Keyboard abstraction with JSON bindings, pressed/held/released tri-state tracking, multiple keys per action, remap and save support
- `sa_fona/core/scene_manager.py` -- Push/pop/replace scene stack with on_enter/on_exit/on_resume lifecycle, overlay rendering
- `sa_fona/scenes/base_scene.py` -- Abstract base class for all game scenes
- `sa_fona/rendering/sprite_renderer.py` -- Placeholder colored-rectangle generator with caching and Animation class
- `sa_fona/scenes/test_scene.py` -- Proof-of-life scene: movable blue rectangle (Balchar), title text, ESC quit

### Integration
- `game.py` wires up real InputHandler, EventBus, SceneManager, SpriteRenderer
- TestScene pushed as initial scene
- Main loop: events -> InputHandler.process_events -> scene.handle_input -> scene.update -> scene.render -> PixelScaler.present

## Key Technical Decisions

1. **InputState dataclass** -- Single immutable snapshot per frame instead of callback soup. Clean separation between raw events and game logic.
2. **Tri-state input tracking** -- Actions like jump/attack have `_pressed`, `_held`, `_released` variants for responsive controls. Movement uses `_held` only.
3. **JSON-driven bindings** -- InputHandler reads from `controls_default.json`; supports runtime remap and save. The key-name-to-constant map covers full alphabet, arrows, modifiers, and F-keys.
4. **Scene stack with overlay support** -- SceneManager renders scene below if top scene's `is_overlay` is True (with dimming layer), enabling pause menu overlays.
5. **SpriteRenderer color mapping** -- Asset IDs containing "balchar" are blue, "bep" green, "enemy" red, others white. Cached on first load.
6. **Animation with per-frame durations** -- Supports both looping and one-shot animations with reset capability.

## Test Results

```
70 passed, 2 warnings in 4.81s

tests/test_event_bus.py       -- 7 passed
tests/test_input_handler.py   -- 13 passed
tests/test_scene_manager.py   -- 14 passed
tests/test_sprite_renderer.py -- 18 passed
tests/test_pixel_scaler.py    -- 7 passed
tests/test_settings.py        -- 11 passed
```

Run tests: `SDL_VIDEODRIVER=dummy python -m pytest tests/ -v --tb=short`

## How to Run

```bash
python -m sa_fona.main
```

- Blue 24x32 rectangle (Balchar) at center of 384x216 screen, scaled 3x
- Move with WASD or arrow keys (150 px/sec)
- Jump/up with Space, W, or Up arrow
- ESC to quit
- "Sa Fona - Test Scene" title text displayed

## File Structure

```
sa_fona/
  __init__.py
  main.py
  config/
    __init__.py
    settings.py
    controls.py
  core/
    __init__.py
    game.py
    event_bus.py
    input_handler.py
    scene_manager.py
  data/
    controls_default.json
    asset_manifest.json
  rendering/
    __init__.py
    pixel_scaler.py
    sprite_renderer.py
  scenes/
    __init__.py
    base_scene.py
    test_scene.py
tests/
  __init__.py
  test_event_bus.py
  test_input_handler.py
  test_scene_manager.py
  test_sprite_renderer.py
  test_pixel_scaler.py
  test_settings.py
```
