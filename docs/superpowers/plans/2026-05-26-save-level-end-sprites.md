# Save Point & Level End Sprites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace placeholder rectangles for save points and level-end markers with sprite-based visuals (bonfire and taula gate).

**Architecture:** Create placeholder sprite assets, add them to the asset manifest, then replace the rectangle-drawing code in `GameplayScene` with sprite blitting. Save points track activation state to swap between unlit/lit bonfire frames. AI prompt files and processing configs are added for the future asset pipeline.

**Tech Stack:** Python, Pygame, existing `asset_loader` and `process_ai_sprites.py` pipeline.

---

### Task 1: Create Placeholder Sprite Assets

**Files:**
- Create: `assets/environment/bonfire.png` (2-frame sprite sheet, 48x32 — two 24x32 frames side by side)
- Create: `assets/environment/taula_gate.png` (single 32x48 sprite)

- [ ] **Step 1: Create the `assets/environment/` directory**

```bash
mkdir -p assets/environment
```

- [ ] **Step 2: Generate placeholder bonfire sprite sheet**

Create a simple 48x32 PNG with two 24x32 frames side by side. Frame 0 (left): brown/grey stacked shapes for unlit logs. Frame 1 (right): same base with orange/yellow triangle for flame.

```python
import pygame
pygame.init()
surf = pygame.Surface((48, 32), pygame.SRCALPHA)

# Frame 0: unlit bonfire (left half, 24x32)
# Stone base
pygame.draw.rect(surf, (120, 100, 80), (6, 24, 12, 8))
# Logs
pygame.draw.rect(surf, (100, 70, 40), (4, 20, 16, 6))
pygame.draw.rect(surf, (90, 60, 35), (7, 16, 10, 6))

# Frame 1: lit bonfire (right half, offset by 24px)
# Same stone base
pygame.draw.rect(surf, (120, 100, 80), (30, 24, 12, 8))
# Same logs
pygame.draw.rect(surf, (100, 70, 40), (28, 20, 16, 6))
pygame.draw.rect(surf, (90, 60, 35), (31, 16, 10, 6))
# Flame
pygame.draw.polygon(surf, (255, 160, 30), [(36, 15), (32, 6), (34, 2), (38, 7), (40, 15)])
pygame.draw.polygon(surf, (255, 220, 50), [(36, 15), (34, 8), (36, 5), (38, 9), (38, 15)])

pygame.image.save(surf, "assets/environment/bonfire.png")
print("Saved bonfire.png (48x32, 2 frames of 24x32)")
```

Run: `cd /home/jovyan/projects/SaFona && python -c "<above code>"`

- [ ] **Step 3: Generate placeholder taula gate sprite**

Create a simple 32x48 PNG: grey vertical pillar with horizontal capstone forming a T/doorway shape.

```python
import pygame
pygame.init()
surf = pygame.Surface((32, 48), pygame.SRCALPHA)

# Vertical pillar (center)
pygame.draw.rect(surf, (140, 135, 125), (12, 8, 8, 40))
# Horizontal capstone on top
pygame.draw.rect(surf, (160, 155, 145), (4, 2, 24, 8))
# Subtle moss on capstone
pygame.draw.rect(surf, (80, 110, 60), (6, 2, 6, 2))
pygame.draw.rect(surf, (70, 100, 55), (20, 3, 4, 2))
# Stone texture lines
pygame.draw.line(surf, (120, 115, 105), (13, 20), (19, 20), 1)
pygame.draw.line(surf, (120, 115, 105), (13, 32), (19, 32), 1)

pygame.image.save(surf, "assets/environment/taula_gate.png")
print("Saved taula_gate.png (32x48)")
```

Run: `cd /home/jovyan/projects/SaFona && python -c "<above code>"`

- [ ] **Step 4: Commit placeholder assets**

```bash
git add assets/environment/bonfire.png assets/environment/taula_gate.png
git commit -m "feat: add placeholder bonfire and taula gate sprites"
```

---

### Task 2: Add Asset Manifest Entries

**Files:**
- Modify: `sa_fona/data/asset_manifest.json`

- [ ] **Step 1: Write the failing test**

Create test that verifies the manifest has the new entries.

File: `tests/test_env_sprites_manifest.py`

```python
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
```

Run: `pytest tests/test_env_sprites_manifest.py -v`
Expected: FAIL with `KeyError: 'env_bonfire'`

- [ ] **Step 2: Add manifest entries**

Add two entries to the `"sprites"` section of `sa_fona/data/asset_manifest.json`, just before the closing `}` of the `"sprites"` object. Find the last sprite entry and add after it:

```json
    "env_bonfire": {
      "path": "assets/environment/bonfire.png",
      "frame_width": 24,
      "frame_height": 32,
      "frame_count": 2
    },
    "env_taula_gate": {
      "path": "assets/environment/taula_gate.png",
      "frame_width": 32,
      "frame_height": 48,
      "frame_count": 1
    }
```

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/test_env_sprites_manifest.py -v`
Expected: PASS (both tests)

- [ ] **Step 4: Commit**

```bash
git add sa_fona/data/asset_manifest.json tests/test_env_sprites_manifest.py
git commit -m "feat: add bonfire and taula gate to asset manifest"
```

---

### Task 3: Replace Save Point Rendering with Bonfire Sprite

**Files:**
- Modify: `sa_fona/scenes/gameplay.py:82-220` (add `_activated_save_points` to `__init__`)
- Modify: `sa_fona/scenes/gameplay.py:697-729` (rewrite `_render_save_point_cues`)
- Modify: `sa_fona/scenes/gameplay.py:1317-1378` (add trigger tracking in `_on_trigger_save_point`)
- Test: `tests/test_env_sprite_rendering.py`

- [ ] **Step 1: Write the failing test for save point sprite rendering**

File: `tests/test_env_sprite_rendering.py`

```python
"""Tests for environment sprite rendering (bonfire + taula gate)."""

import pygame
import pytest

from sa_fona.core.event_bus import EventBus
from sa_fona.level.trigger import Trigger, TriggerType


@pytest.fixture(autouse=True)
def _init_pygame():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    yield
    pygame.quit()


class TestSavePointRendering:
    """Tests for bonfire sprite rendering at save points."""

    def test_activated_save_points_initialized(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        assert hasattr(scene, "_activated_save_points")
        assert isinstance(scene._activated_save_points, set)
        assert len(scene._activated_save_points) == 0

    def test_save_point_activation_tracks_trigger(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        trigger = Trigger(
            pygame.Rect(480, 192, 32, 48),
            TriggerType.SAVE_POINT,
            once=False,
            properties={"shop_available": False},
        )
        scene._on_trigger_save_point(trigger=trigger)
        assert id(trigger) in scene._activated_save_points

    def test_render_save_point_cues_does_not_crash(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        surface = pygame.Surface((384, 216))
        scene._render_save_point_cues(surface, (0, 0))
```

Run: `pytest tests/test_env_sprite_rendering.py::TestSavePointRendering -v`
Expected: FAIL — `_activated_save_points` does not exist yet

- [ ] **Step 2: Add `_activated_save_points` set to `__init__`**

In `sa_fona/scenes/gameplay.py`, after line 182 (`self._checkpoint_pos: tuple[float, float] | None = None`), add:

```python
        self._activated_save_points: set[int] = set()
```

- [ ] **Step 3: Rewrite `_render_save_point_cues` to use bonfire sprite**

Replace the entire method body at lines 697-729 of `sa_fona/scenes/gameplay.py`:

```python
    def _render_save_point_cues(
        self, surface: pygame.Surface, cam_offset: tuple[int, int],
    ) -> None:
        """Draw bonfire sprite at save_point trigger locations."""
        from sa_fona.level.trigger import TriggerType as _TT
        from sa_fona.rendering.asset_loader import load_frame_strip

        frames = load_frame_strip("assets/environment/bonfire.png", 24, 32)
        for trigger in self._trigger_system.triggers:
            if trigger.trigger_type != _TT.SAVE_POINT:
                continue
            sx = trigger.rect.x - cam_offset[0]
            sy = trigger.rect.y - cam_offset[1]
            w = trigger.rect.width
            h = trigger.rect.height

            if frames:
                frame_idx = 1 if id(trigger) in self._activated_save_points else 0
                frame = frames[frame_idx]
                fx = sx + (w - frame.get_width()) // 2
                fy = sy + h - frame.get_height()
                surface.blit(frame, (fx, fy))
            else:
                beacon_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                beacon_surf.fill((80, 200, 255, 40))
                surface.blit(beacon_surf, (sx, sy))
                pygame.draw.rect(surface, (80, 200, 255), (sx, sy, w, h), 1)
```

The fallback block keeps the old rectangle if the sprite file is missing (e.g. during tests without assets).

- [ ] **Step 4: Track activation in `_on_trigger_save_point`**

In `sa_fona/scenes/gameplay.py`, at the start of `_on_trigger_save_point` (after the docstring, around line 1328), add the tracking line before the existing `shop_available = False`:

```python
        if trigger is not None:
            self._activated_save_points.add(id(trigger))
```

This goes right before the existing `if trigger is not None:` block at line 1329. Since both check `trigger is not None`, merge them — add `self._activated_save_points.add(id(trigger))` as the first line inside the existing `if trigger is not None:` block at line 1329, before `self._checkpoint_pos = (...)`.

- [ ] **Step 5: Run tests to verify**

Run: `pytest tests/test_env_sprite_rendering.py::TestSavePointRendering -v`
Expected: PASS (all 3 tests)

- [ ] **Step 6: Commit**

```bash
git add sa_fona/scenes/gameplay.py tests/test_env_sprite_rendering.py
git commit -m "feat: render bonfire sprite at save points"
```

---

### Task 4: Replace Level End Rendering with Taula Gate Sprite

**Files:**
- Modify: `sa_fona/scenes/gameplay.py:731-765` (rewrite `_render_level_end_cues`)
- Modify: `tests/test_env_sprite_rendering.py` (add level end test class)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_env_sprite_rendering.py`:

```python
class TestLevelEndRendering:
    """Tests for taula gate sprite rendering at level end markers."""

    def test_render_level_end_cues_does_not_crash(self):
        from sa_fona.scenes.gameplay import GameplayScene
        scene = GameplayScene()
        surface = pygame.Surface((384, 216))
        scene._render_level_end_cues(surface, (0, 0))
```

Run: `pytest tests/test_env_sprite_rendering.py::TestLevelEndRendering -v`
Expected: PASS (this should pass even before changes since the old code works, but verifies the method exists)

- [ ] **Step 2: Rewrite `_render_level_end_cues` to use taula sprite**

Replace the entire method body at lines 731-765 of `sa_fona/scenes/gameplay.py`:

```python
    def _render_level_end_cues(
        self, surface: pygame.Surface, cam_offset: tuple[int, int],
    ) -> None:
        """Draw taula gate sprite at level_end trigger locations."""
        from sa_fona.rendering.asset_loader import load_image

        taula = load_image("assets/environment/taula_gate.png")
        for trigger in self._trigger_system.triggers:
            if trigger.trigger_type != TriggerType.LEVEL_END:
                continue
            sx = trigger.rect.x - cam_offset[0]
            sy = trigger.rect.y - cam_offset[1]
            w = trigger.rect.width
            h = trigger.rect.height

            if taula:
                fx = sx + (w - taula.get_width()) // 2
                fy = sy + h - taula.get_height()
                surface.blit(taula, (fx, fy))
            else:
                gate_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                gate_surf.fill((255, 220, 80, 50))
                surface.blit(gate_surf, (sx, sy))
                pygame.draw.rect(surface, (255, 200, 50), (sx, sy, w, h), 2)
```

- [ ] **Step 3: Run tests to verify**

Run: `pytest tests/test_env_sprite_rendering.py -v`
Expected: PASS (all 4 tests)

- [ ] **Step 4: Run full test suite**

Run: `pytest tests/ -v`
Expected: All existing tests still pass.

- [ ] **Step 5: Commit**

```bash
git add sa_fona/scenes/gameplay.py tests/test_env_sprite_rendering.py
git commit -m "feat: render taula gate sprite at level end markers"
```

---

### Task 5: Add AI Prompt Files

**Files:**
- Create: `tools/sprite_defs/bonfire_ai_prompt.md`
- Create: `tools/sprite_defs/taula_gate_ai_prompt.md`

- [ ] **Step 1: Create bonfire AI prompt**

File: `tools/sprite_defs/bonfire_ai_prompt.md`

```markdown
# Bonfire Sprite Generation Prompt

Used to generate the AI reference image for save point bonfire sprites.
Source image: `assets/ai_sources/bonfire/bonfire.png`
Processing config: `tools/sprite_defs/characters/bonfire.json`
Output: `assets/environment/bonfire.png` (48x32, 2 frames of 24x32)

## Prompt

Pixel art of two bonfire sprites, 16-bit SNES style, on a solid bright green (#00FF00) background. Show both sprites in a single horizontal row, evenly spaced, at the same scale:

1) Unlit bonfire — a small pile of stacked rough-hewn limestone rocks with dry scrubland wood and kindling arranged on top, no flame, no glow, cold and dormant. The wood is sun-bleached Mediterranean driftwood and dry brush.

2) Lit bonfire — the exact same rock and wood arrangement as sprite 1, but now burning with a warm orange-yellow flame rising from the wood. The flame should be simple and stylized (3-4 colors: dark orange base, bright orange middle, yellow tips). Small ember dots above the flame.

Style: Balearic island Mediterranean feel. Warm grey limestone rocks (NOT blue-grey), dry earth tones for wood. The bonfire should be small — roughly knee-height for a warrior character (about 16-20 pixels tall). Clean pixel art, no anti-aliasing, no smoothing. Both sprites must have identical base rocks and wood — only difference is the flame on sprite 2. Clearly separated with green space between them.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- 2 sprite regions detected via connected components on non-green mask
- Both frames scaled uniformly to fit 24x32 frame, bottom-aligned
- Output: single horizontal sprite sheet (48x32), frame 0 = unlit, frame 1 = lit
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/bonfire.json`
```

- [ ] **Step 2: Create taula gate AI prompt**

File: `tools/sprite_defs/taula_gate_ai_prompt.md`

```markdown
# Taula Gate Sprite Generation Prompt

Used to generate the AI reference image for level-end taula gate sprite.
Source image: `assets/ai_sources/taula_gate/taula_gate.png`
Processing config: `tools/sprite_defs/characters/taula_gate.json`
Output: `assets/environment/taula_gate.png` (32x48, single frame)

## Prompt

Pixel art of a taula monument viewed from the side, 16-bit SNES style, on a solid bright green (#00FF00) background. Single sprite:

A T-shaped megalithic stone monument (taula) seen from the side, forming a doorway or gate. One thick vertical limestone pillar supports a wide horizontal capstone across the top. The proportions should form a clear doorway opening — tall enough for a warrior character to walk through (about 48 pixels tall). The pillar is roughly one-third the width of the capstone.

The stone is weathered ancient grey limestone with subtle warm undertones — NOT blue-grey. Small patches of green-brown moss or lichen on the capstone and upper pillar. Fine cracks and mortar-line texture in the stone. The monument should look ancient and monumental but not ruined — solid, heavy, enduring.

Style: Based on real taula monuments from Menorca (Torralba d'en Salort, Torre d'en Galmés). Balearic talayotic architecture. Clean pixel art, no anti-aliasing, no smoothing. Solid bright green (#00FF00) background for chroma-key removal.

## Processing Notes

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- Single sprite region detected
- Scaled to fit 32x48 frame, bottom-aligned
- Output: single image (32x48)
- Process with: `python tools/process_ai_sprites.py tools/sprite_defs/characters/taula_gate.json`
```

- [ ] **Step 3: Commit**

```bash
git add tools/sprite_defs/bonfire_ai_prompt.md tools/sprite_defs/taula_gate_ai_prompt.md
git commit -m "docs: add AI generation prompts for bonfire and taula gate"
```

---

### Task 6: Add Processing Configs

**Files:**
- Create: `tools/sprite_defs/characters/bonfire.json`
- Create: `tools/sprite_defs/characters/taula_gate.json`

- [ ] **Step 1: Create bonfire processing config**

File: `tools/sprite_defs/characters/bonfire.json`

```json
{
  "frame_width": 24,
  "frame_height": 32,
  "source_dir": "assets/ai_sources/bonfire",
  "output_dir": "assets/environment",
  "animations": [
    {
      "source": "bonfire.png",
      "frames": 2,
      "scale_pct": 100,
      "vertical_snap": "bottom"
    }
  ]
}
```

- [ ] **Step 2: Create taula gate processing config**

File: `tools/sprite_defs/characters/taula_gate.json`

```json
{
  "frame_width": 32,
  "frame_height": 48,
  "source_dir": "assets/ai_sources/taula_gate",
  "output_dir": "assets/environment",
  "animations": [
    {
      "source": "taula_gate.png",
      "frames": 1,
      "scale_pct": 100,
      "vertical_snap": "bottom"
    }
  ]
}
```

- [ ] **Step 3: Create AI source directories**

```bash
mkdir -p assets/ai_sources/bonfire
mkdir -p assets/ai_sources/taula_gate
```

- [ ] **Step 4: Commit**

```bash
git add tools/sprite_defs/characters/bonfire.json tools/sprite_defs/characters/taula_gate.json
git commit -m "feat: add processing configs for bonfire and taula gate sprites"
```

---

### Task 7: Final Verification

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass, including the new ones.

- [ ] **Step 2: Verify assets exist**

```bash
ls -la assets/environment/bonfire.png assets/environment/taula_gate.png
```

Expected: Both files exist and have non-zero size.

- [ ] **Step 3: Run the game and visually verify**

```bash
conda activate safona
Xvfb :99 -screen 0 1152x648x24 &
x11vnc -display :99 -nopw -forever -shared -rfbport 5900 &
websockify --web /usr/share/novnc 6080 localhost:5900 &
DISPLAY=:99 python -m sa_fona.main
```

User forwards port 6080 and opens `http://localhost:6080/vnc.html`.

Verify:
- Bonfire appears at save point (unlit by default)
- Walking into save point lights the bonfire (frame swap)
- Taula gate appears at level end
- No visual glitches or crashes
