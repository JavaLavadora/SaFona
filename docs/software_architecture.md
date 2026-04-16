# Sa Fona -- Software Architecture Document

> **Version**: 1.0
> **Author**: En Miquel (Software Architect)
> **Based on**: GDD v3.0 (Production -- Mask Acquisition Restructure)
> **Engine**: Pygame (Python)
> **Date**: 2026-04-16

---

## Table of Contents

1. [Technical Constraints](#1-technical-constraints)
2. [Project Structure](#2-project-structure)
3. [System Interfaces](#3-system-interfaces)
4. [Data Formats](#4-data-formats)
5. [Dependency Diagram](#5-dependency-diagram)
6. [Extension Points](#6-extension-points)

---

## 1. Technical Constraints

| Constraint | Value |
|---|---|
| Framework | Pygame (Python 3.10+) |
| Base resolution | 384x216 (pixel-perfect, integer-scaled to display) |
| Tile size | 16x16 pixels |
| FPS target | 60 |
| Collision model | AABB (axis-aligned bounding boxes) |
| Input | Keyboard + gamepad (remappable) |
| Art style | 16-bit pixel art (SNES era), hard pixel edges, no anti-aliasing |
| Audio formats | .ogg, .mp3, .wav |
| Save format | JSON, single local file, single slot (decided, Issue #13; extensible to multiple slots) |
| Docstrings | Google style |
| Tests | Small, concise tests for all implementations |
| Assets | Placeholder shapes during development; hot-swappable with real assets |

**Resolution rationale**: 384x216 is chosen over 320x180 because it provides a wider canvas for the larger boss sprites (up to 96x96) while keeping perfect 16:9 aspect ratio. Both are exact multiples of the 16x16 tile grid. The final choice is a constant in `config/settings.py` and can be switched without code changes.

---

## 2. Project Structure

```
sa_fona/
|-- main.py                      # Entry point: init Pygame, create Game, run loop
|-- config/
|   |-- settings.py              # Global constants: resolution, FPS, colors, paths
|   |-- controls.py              # Default key/gamepad bindings (remappable at runtime)
|
|-- core/
|   |-- game.py                  # Main game loop: input -> update -> render
|   |-- scene_manager.py         # Scene stack (push/pop state machine)
|   |-- input_handler.py         # Keyboard + gamepad abstraction, remapping
|   |-- camera.py                # Follow target, screen shake, clamping to level bounds
|   |-- event_bus.py             # Publish/subscribe event system for decoupled communication
|
|-- scenes/
|   |-- base_scene.py            # Abstract base: on_enter, on_exit, update, render, handle_input
|   |-- main_menu.py             # Title screen, start/continue, settings, credits
|   |-- level_select.py          # Per-level replay grid, completion indicators
|   |-- gameplay.py              # Active level: physics, entities, combat, HUD
|   |-- dialogue.py              # Dialogue overlay (pushable on top of gameplay)
|   |-- shop.py                  # Llorencc's shop: masks tab, items tab
|   |-- pause.py                 # Pause overlay with resume/items/controls/quit
|   |-- cutscene.py              # Scripted sequences: boss intros, mask grants, portals
|   |-- boss.py                  # Boss arena (extends gameplay with boss-specific logic)
|   |-- game_over.py             # Death / restart screen
|   |-- settings_menu.py         # Volume, controls remapping, display options
|   |-- credits.py               # Scrolling credits
|
|-- entities/
|   |-- entity.py                # Base entity: position, velocity, rect, sprite, update/render
|   |-- player.py                # Ramon: moveset, sling, mask activation, state machine
|   |-- companion.py             # Bep: follow AI, idle animations, dialogue triggers
|   |-- enemy.py                 # Base enemy + EnemyFactory (JSON-driven)
|   |-- enemy_behaviors.py       # Behavior components: patrol, chase, flee, shield, swoop
|   |-- boss_entity.py           # Base boss entity: phases, health bar, patterns
|   |-- npc.py                   # Llorencc, dimonis, generic NPCs
|   |-- projectile.py            # Sling stones (basic + special), enemy projectiles, bombs
|   |-- pickup.py                # Heart pickups, stone pickups, consumable drops
|
|-- systems/
|   |-- physics.py               # AABB collision, gravity, movement resolution, one-way platforms
|   |-- combat.py                # Damage calculation, hit detection, invincibility frames
|   |-- sling_system.py          # Tap/hold detection, charge tiers, projectile spawning
|   |-- mask_system.py           # Mask inventory, equip/swap, cooldowns, quick-swap
|   |-- economy.py               # Stone currency, drop tables, spending, reads economy.json
|   |-- save_system.py           # JSON save/load, per-level completion, death rollback
|   |-- audio_manager.py         # Named-slot music/SFX playback, fallback to silence
|   |-- special_ammo.py          # Ammo types, recharge timer, kill-acceleration
|   |-- consumable_system.py     # Buff timers, heal effects, refund on death
|
|-- level/
|   |-- tilemap.py               # Tile loading, rendering, collision layer extraction
|   |-- level_loader.py          # Load level JSON, spawn entities, configure triggers
|   |-- parallax.py              # Background parallax layers (2-3 per world)
|   |-- trigger.py               # Level triggers: dialogue, cutscene, boss gate, save point
|
|-- ui/
|   |-- hud.py                   # Hearts, mask icon + cooldown radial, stone count, ammo
|   |-- dialogue_box.py          # Text box, portrait, letter-by-letter, skip on press
|   |-- shop_ui.py               # Tabs (masks/items), selection, price display, feedback
|   |-- menu_ui.py               # Reusable menu widgets: buttons, sliders, selection lists
|   |-- level_select_ui.py       # World grid, per-level cards, completion badges
|   |-- charge_indicator.py      # In-world charge meter near Ramon (Tier 1/2/3)
|   |-- boss_health_bar.py       # Top-of-screen boss HP bar with phase markers
|   |-- transition.py            # Screen fade, wipe, and world-transition vignettes
|
|-- rendering/
|   |-- sprite_renderer.py       # Sprite sheet slicing, frame caching, animation playback
|   |-- animation.py             # Animation definitions: frames, durations, state transitions
|   |-- renderer.py              # Main render pipeline: clear, layers, entities, UI, scale
|   |-- effects.py               # Screen shake, flash, invincibility blink, particle spawner
|   |-- pixel_scaler.py          # Integer upscale from base resolution to display window
|
|-- data/
|   |-- economy.json             # ALL economy values (prices, drops, costs, effects)
|   |-- audio_config.json        # Named slots -> file paths for music and SFX
|   |-- asset_manifest.json      # Asset ID -> file path (sprites, tilesets, backgrounds)
|   |-- masks.json               # Mask definitions (powers, cooldowns, parameters)
|   |-- controls_default.json    # Default control bindings (keyboard + gamepad)
|   |-- levels/
|   |   |-- world1/
|   |   |   |-- level_1_1.json
|   |   |   |-- level_1_2.json
|   |   |   |-- level_1_3.json
|   |   |   |-- level_1_4.json
|   |   |   |-- boss_1.json
|   |   |-- world2/
|   |   |   |-- ...
|   |   |-- world3/
|   |   |-- world4/
|   |   |-- world5/
|   |   |-- world5_5/
|   |-- enemies/
|   |   |-- world1_enemies.json
|   |   |-- world2_enemies.json
|   |   |-- ...
|   |-- dialogue/
|   |   |-- world1_dialogue.json
|   |   |-- world2_dialogue.json
|   |   |-- bep_hints.json
|   |   |-- llorencc_shop.json
|   |   |-- boss_intros.json
|   |   |-- ...
|   |-- shop/
|   |   |-- shop_inventory.json  # Full shop inventory with unlock-world thresholds
|   |-- bosses/
|   |   |-- boss_bou_de_pedra.json
|   |   |-- boss_metellus.json
|   |   |-- boss_comte_mal.json
|   |   |-- boss_dragut.json
|   |   |-- boss_magnat_p1.json
|   |   |-- boss_magnat_p2.json
|
|-- assets/
|   |-- sprites/
|   |   |-- ramon/
|   |   |-- bep/
|   |   |-- enemies/
|   |   |-- bosses/
|   |   |-- npcs/
|   |   |-- projectiles/
|   |   |-- pickups/
|   |-- tilesets/
|   |   |-- world1/
|   |   |-- world2/
|   |   |-- ...
|   |-- ui/
|   |   |-- hud/
|   |   |-- dialogue/
|   |   |-- shop/
|   |   |-- menus/
|   |-- backgrounds/
|   |   |-- world1/
|   |   |-- world2/
|   |   |-- ...
|   |-- audio/
|       |-- music/
|       |-- sfx/
|
|-- tests/
    |-- test_physics.py
    |-- test_combat.py
    |-- test_sling_system.py
    |-- test_mask_system.py
    |-- test_economy.py
    |-- test_save_system.py
    |-- test_special_ammo.py
    |-- test_consumable_system.py
    |-- test_level_loader.py
    |-- test_input_handler.py
    |-- test_scene_manager.py
    |-- test_audio_manager.py
    |-- ...
```

### Design Principles

1. **Data-driven**: Every game value that a designer/playtester might want to adjust lives in a JSON file under `data/`. No economy values, enemy stats, mask parameters, dialogue, or level layouts are hardcoded.

2. **One system, one module**: Each major system (physics, combat, masks, economy, audio, save) is a single module with a clear public API. Systems communicate through the event bus or explicit method calls, never through shared mutable state.

3. **Scene stack**: The scene manager uses a push/pop stack. Dialogue, pause, and shop overlay the gameplay scene without destroying it. This preserves gameplay state during overlays.

4. **Entity-component style**: Entities share a common base with position/velocity/rect/sprite. Behavior is composed through components (e.g., `enemy_behaviors.py`) rather than deep inheritance. The enemy factory instantiates from JSON definitions.

5. **Placeholder-first**: All rendering and audio use placeholder shapes/silence during development. The asset manifest and audio config make swapping real assets a file-path change.

---

## 3. System Interfaces

### 3.1 SceneManager

```python
class SceneManager:
    """Push/pop scene stack. Manages scene lifecycle and transitions.

    The active scene is the top of the stack. Pushed scenes (pause, dialogue,
    shop) overlay without destroying the scene below. Pop returns to the
    previous scene.
    """

    def push(self, scene: BaseScene) -> None:
        """Push a scene onto the stack. Calls on_enter on the new scene."""
        ...

    def pop(self) -> None:
        """Pop the top scene. Calls on_exit, then on_resume on the new top."""
        ...

    def replace(self, scene: BaseScene) -> None:
        """Replace the top scene. Calls on_exit on old, on_enter on new."""
        ...

    def update(self, dt: float) -> None:
        """Update the active (top) scene."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Render the active scene. Overlay scenes may render the scene below."""
        ...

    @property
    def active_scene(self) -> BaseScene:
        """The scene currently on top of the stack."""
        ...
```

**Data owned**: Scene stack (list of BaseScene instances).
**Dependencies**: None (scenes are passed in by Game).

### 3.2 BaseScene

```python
class BaseScene(ABC):
    """Abstract base class for all game scenes.

    Every scene implements the same lifecycle: on_enter, on_exit,
    handle_input, update, render. Overlay scenes (pause, dialogue)
    can optionally render the scene below them for transparency.
    """

    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def on_resume(self) -> None: ...
    def handle_input(self, input_state: InputState) -> None: ...
    def update(self, dt: float) -> None: ...
    def render(self, surface: pygame.Surface) -> None: ...

    @property
    def is_overlay(self) -> bool:
        """If True, the scene below is also rendered (dimmed)."""
        ...
```

### 3.3 InputHandler

```python
class InputHandler:
    """Abstracts keyboard and gamepad input into logical actions.

    Reads raw Pygame events and produces an InputState with action flags.
    Bindings are loaded from controls_default.json and are remappable
    at runtime. Supports both keyboard and gamepad simultaneously.
    """

    def __init__(self, bindings_path: str) -> None: ...

    def process_events(self, events: list[pygame.event.Event]) -> InputState:
        """Process raw Pygame events into an InputState for the current frame."""
        ...

    def remap(self, action: str, key: int) -> None:
        """Remap an action to a different key/button."""
        ...

    def save_bindings(self, path: str) -> None:
        """Persist current bindings to JSON."""
        ...


@dataclass
class InputState:
    """Snapshot of all logical input actions for one frame.

    Fields are True on the frame the action occurs (pressed),
    or True every frame (held). Released flags are True on release frame.
    """
    move_left: bool = False
    move_right: bool = False
    jump_pressed: bool = False
    jump_held: bool = False
    jump_released: bool = False
    attack_pressed: bool = False
    attack_held: bool = False
    attack_released: bool = False
    mask_power_pressed: bool = False
    mask_cycle_left: bool = False
    mask_cycle_right: bool = False
    special_ammo_toggle: bool = False
    pause_pressed: bool = False
    interact_pressed: bool = False
    # Analog stick values for smooth movement
    move_x: float = 0.0  # -1.0 to 1.0
```

**Data owned**: Current bindings map, connected gamepad references.
**Dependencies**: Pygame event system.

### 3.4 Camera

```python
class Camera:
    """Follows a target entity with smooth interpolation and screen shake.

    Clamps to level bounds so the camera never shows outside the map.
    Screen shake is driven by events (boss attacks, Stone Slam, etc.)
    via the event bus.
    """

    def __init__(self, level_width: int, level_height: int) -> None: ...

    def follow(self, target_rect: pygame.Rect, dt: float) -> None:
        """Smoothly move the camera toward the target."""
        ...

    def shake(self, intensity: float, duration: float) -> None:
        """Start a screen shake effect."""
        ...

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Offset a world-space rect to screen space."""
        ...

    def update(self, dt: float) -> None:
        """Update shake decay."""
        ...

    @property
    def offset(self) -> tuple[int, int]:
        """Current camera offset (x, y) in world coordinates."""
        ...
```

**Data owned**: Camera position, shake state, level bounds.
**Dependencies**: None.

### 3.5 EventBus

```python
class EventBus:
    """Publish/subscribe event system for decoupled inter-system communication.

    Systems publish game events (enemy_killed, mask_acquired, stone_collected,
    boss_phase_changed, etc.) without knowing who listens. Other systems
    subscribe to events they care about.

    This is the primary mechanism for cross-system communication without
    creating circular dependencies. For example, the economy system subscribes
    to 'enemy_killed' to handle stone drops, while the audio manager subscribes
    to the same event to play a sound effect.
    """

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type."""
        ...

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Remove a callback registration."""
        ...

    def publish(self, event_type: str, **data) -> None:
        """Publish an event, invoking all registered callbacks."""
        ...
```

**Data owned**: Callback registry (dict of event_type -> list of callables).
**Dependencies**: None.

**Event types used across the codebase**:

| Event | Published by | Consumed by |
|---|---|---|
| `enemy_killed` | Combat | Economy (stone drops), AudioManager (SFX), SpecialAmmo (recharge acceleration) |
| `stone_collected` | Pickup | Economy (update count), AudioManager (SFX), HUD (refresh) |
| `heart_collected` | Pickup | Player (heal), AudioManager (SFX), HUD (refresh) |
| `damage_dealt` | Combat | AudioManager (SFX), HUD (refresh), Effects (flash) |
| `damage_taken` | Combat | Player (reduce HP), AudioManager (SFX), HUD (refresh), Effects (screen flash) |
| `player_died` | Player | GameplayScene (trigger death sequence), SaveSystem (rollback) |
| `mask_acquired` | CutsceneScene | MaskSystem (unlock), SaveSystem (persist), AudioManager (jingle) |
| `mask_swapped` | MaskSystem | HUD (update icon), AudioManager (SFX) |
| `mask_power_used` | MaskSystem | AudioManager (SFX), Effects (visual), Camera (shake for Stone Slam) |
| `mask_cooldown_ready` | MaskSystem | HUD (update icon), AudioManager (SFX) |
| `boss_phase_changed` | BossEntity | AudioManager (SFX), Effects (screen shake), HUD (boss bar) |
| `boss_defeated` | BossEntity | GameplayScene (trigger post-boss sequence), AudioManager (jingle) |
| `level_completed` | GameplayScene | SaveSystem (mark level, save), AudioManager (jingle) |
| `shop_purchase` | ShopUI | Economy (deduct stones), Consumable/SpecialAmmo (add item), AudioManager (SFX) |
| `consumable_used` | ConsumableSystem | Player (apply effect), AudioManager (SFX), HUD (refresh) |
| `dialogue_started` | Trigger | SceneManager (push dialogue), AudioManager (optional SFX) |
| `screen_shake` | Various | Camera (apply shake) |
| `quick_swap_unlocked` | CutsceneScene | MaskSystem (enable cycling), HUD (show arrows) |

### 3.6 Physics

```python
class PhysicsSystem:
    """AABB collision detection and resolution for all entities.

    Handles gravity, movement resolution, one-way platforms, breakable tiles,
    and phase-through tiles (Smoke Vanish). Collision layers separate terrain,
    enemies, projectiles, and triggers.

    The physics system does NOT own entity positions -- it reads them, computes
    collisions, and writes back resolved positions. This keeps entity ownership
    clear.
    """

    def __init__(self, tilemap: TileMap) -> None: ...

    def update(self, entities: list[Entity], dt: float) -> None:
        """Apply gravity, move entities, resolve collisions for one frame."""
        ...

    def check_collision(self, rect: pygame.Rect, layer: str = "solid") -> list[pygame.Rect]:
        """Return all tile rects in the specified layer that overlap rect."""
        ...

    def raycast(self, origin: tuple, direction: tuple, max_dist: float,
                layer: str = "solid") -> tuple | None:
        """Cast a ray and return the first collision point, or None."""
        ...

    def set_phase_through(self, enabled: bool) -> None:
        """Enable/disable phase-through for thin walls (Smoke Vanish)."""
        ...

    @property
    def gravity(self) -> float:
        """Current gravity value (can be modified for special zones)."""
        ...
```

**Data owned**: Reference to active TileMap, gravity constant, phase-through state.
**Dependencies**: TileMap (for collision geometry).

### 3.7 CombatSystem

```python
class CombatSystem:
    """Manages damage dealing, hit detection, and invincibility frames.

    All damage values are read from economy.json (enemy damage tables) and
    entity definitions. The combat system resolves entity-vs-entity AABB
    overlaps, applies damage, handles invincibility frames after being hit,
    and publishes events for audio/visual feedback.
    """

    def __init__(self, event_bus: EventBus, economy_data: dict) -> None: ...

    def update(self, player: Player, enemies: list[Enemy],
               projectiles: list[Projectile], dt: float) -> None:
        """Check all combat interactions for one frame."""
        ...

    def deal_damage(self, target: Entity, amount: float, source: Entity) -> None:
        """Apply damage to a target, respecting invincibility frames."""
        ...

    def is_invincible(self, entity: Entity) -> bool:
        """Check if an entity is currently in invincibility frames."""
        ...
```

**Data owned**: Invincibility frame timers per entity.
**Dependencies**: EventBus, economy data (damage values).

### 3.8 SlingSystem

```python
class SlingSystem:
    """Handles Ramon's sling tap/hold/charge/release mechanics.

    Detects tap vs. hold from InputState. On tap, spawns a melee hitbox.
    On hold, tracks charge time across 3 tiers with visual/audio feedback.
    On release, spawns a projectile with damage and range based on the
    charge tier. Special ammo modifies the projectile type.

    Charge tier thresholds are defined in economy.json for easy tuning.
    """

    def __init__(self, event_bus: EventBus, economy_data: dict) -> None: ...

    def update(self, input_state: InputState, player: Player, dt: float) -> None:
        """Process sling input: detect tap, update charge, handle release."""
        ...

    def get_charge_tier(self) -> int:
        """Return current charge tier (0=none, 1/2/3=charging)."""
        ...

    @property
    def is_charging(self) -> bool:
        """Whether the player is currently holding the attack button."""
        ...
```

**Data owned**: Charge timer, current charge tier, tap detection state.
**Dependencies**: EventBus, economy data (charge thresholds, damage per tier).

### 3.9 MaskSystem

```python
class MaskSystem:
    """Manages the dimoni mask inventory, equipping, cooldowns, and quick-swap.

    Masks are unlocked via mask_acquired events (post-boss). Only one mask
    is active at a time. The active mask determines the effect of the mask
    power button. Each mask has a cooldown after use.

    Quick-swap (cycling with L1/R1 or Q/E) is unlocked at W5.5 start via
    the quick_swap_unlocked event. Before that, masks are swapped only
    at Llorencc's shop.

    Mask definitions (power type, cooldown, parameters) are loaded from
    data/masks.json.
    """

    def __init__(self, event_bus: EventBus, masks_data: dict) -> None: ...

    def unlock_mask(self, mask_id: str) -> None:
        """Add a mask to the player's inventory. Called on mask_acquired event."""
        ...

    def equip_mask(self, mask_id: str) -> None:
        """Set the active mask. Publishes mask_swapped event."""
        ...

    def activate_power(self, player: Player) -> bool:
        """Activate the current mask's power if off cooldown. Returns success."""
        ...

    def cycle_mask(self, direction: int) -> None:
        """Cycle to the next/previous mask. Only works if quick-swap is unlocked.

        Args:
            direction: +1 for next, -1 for previous. Wraps around.
        """
        ...

    def enable_quick_swap(self) -> None:
        """Enable real-time mask cycling (W5.5 unlock)."""
        ...

    def update(self, dt: float) -> None:
        """Update cooldown timers."""
        ...

    @property
    def active_mask(self) -> str | None:
        """ID of the currently equipped mask, or None."""
        ...

    @property
    def unlocked_masks(self) -> list[str]:
        """List of all unlocked mask IDs in acquisition order."""
        ...

    @property
    def cooldown_remaining(self) -> float:
        """Seconds remaining on the active mask's cooldown."""
        ...

    @property
    def cooldown_fraction(self) -> float:
        """0.0 (ready) to 1.0 (full cooldown) for HUD radial display."""
        ...

    @property
    def quick_swap_enabled(self) -> bool:
        """Whether the player can cycle masks in real time."""
        ...
```

**Data owned**: Unlocked mask list, active mask ID, cooldown timers, quick-swap state, swap cooldown timer (0.3s).
**Dependencies**: EventBus, masks.json data.

### 3.10 EconomySystem

```python
class EconomySystem:
    """Manages sling stone currency: collection, spending, drop tables.

    ALL economy values are loaded from data/economy.json at initialization.
    No economy value is hardcoded. This file is the single source of truth
    for: stone prices, heart upgrade costs, consumable prices, consumable
    effects, special ammo costs, enemy drop rates, breakable yields,
    secret rewards, tax collector steal amounts, and shop unlock thresholds.

    The project owner can edit economy.json during playtesting to adjust
    any balance value without touching Python code.
    """

    def __init__(self, event_bus: EventBus, economy_path: str) -> None:
        """Load all economy data from the JSON file."""
        ...

    def add_stones(self, amount: int) -> None:
        """Add stones to the player's wallet."""
        ...

    def spend_stones(self, amount: int) -> bool:
        """Attempt to spend stones. Returns False if insufficient."""
        ...

    def get_enemy_drop(self, enemy_type: str) -> int:
        """Return the stone drop amount for a killed enemy type."""
        ...

    def get_breakable_yield(self, breakable_type: str) -> int:
        """Return the stone yield for a broken object type."""
        ...

    def get_price(self, item_id: str) -> int:
        """Return the price of a shop item."""
        ...

    def get_heart_upgrade_cost(self, upgrade_index: int) -> int:
        """Return the cost of the Nth heart upgrade (0-indexed)."""
        ...

    def get_consumable_effect(self, item_id: str) -> dict:
        """Return the effect parameters for a consumable item."""
        ...

    def get_shop_inventory(self, current_world: int) -> list[dict]:
        """Return items available for purchase given the current world."""
        ...

    def snapshot(self) -> dict:
        """Return a snapshot of the player's economy state for save/rollback."""
        ...

    def restore(self, snapshot: dict) -> None:
        """Restore economy state from a snapshot (death rollback)."""
        ...

    @property
    def stone_count(self) -> int:
        """Current sling stone count."""
        ...

    def reload_config(self) -> None:
        """Reload economy.json from disk (hot-reload for playtesting)."""
        ...
```

**Data owned**: Stone count, full economy configuration (loaded from JSON).
**Dependencies**: EventBus (subscribes to stone_collected, enemy_killed, shop_purchase).

> **Decided** (Issue #11): Hot-reload scope is limited to `economy.json` and `audio_config.json` only. For other data files (levels, enemies, masks, dialogue), restart the level or game. This avoids the complexity of file watchers and state inconsistencies during development.

### 3.11 SaveSystem

> **Decided** (Issue #13): Single save slot for now. The SaveSystem takes `save_path` as a constructor parameter, so adding multiple slots later is a UI-only change (slot selection screen passes a different path). No multi-slot infrastructure is built upfront.

```python
class SaveSystem:
    """JSON-based save/load with per-level completion tracking.

    Uses a single save slot (decided, Issue #13). The save_path parameter
    makes multi-slot extension trivial: pass a different path per slot.

    Save is triggered automatically at the end of each level and after
    post-boss mask acquisition. Save data is a single JSON file.

    On death, the player state is rolled back to the pre-level snapshot
    (stones, hearts, consumables are restored to level-entry values).
    Consumables used during a failed attempt are refunded.

    The save file tracks individual level completion and secret-found flags,
    driving the Level Select screen.
    """

    def __init__(self, save_path: str) -> None: ...

    def save(self, game_state: GameState) -> None:
        """Write the current game state to disk."""
        ...

    def load(self) -> GameState | None:
        """Load game state from disk. Returns None if no save exists."""
        ...

    def exists(self) -> bool:
        """Check if a save file exists."""
        ...

    def delete(self) -> None:
        """Delete the save file (new game)."""
        ...

    def snapshot_level_entry(self, game_state: GameState) -> dict:
        """Capture state at level entry for death rollback."""
        ...

    def rollback_to_snapshot(self, snapshot: dict, game_state: GameState) -> None:
        """Restore player state from the level-entry snapshot."""
        ...

    def mark_level_complete(self, world: int, level: int,
                            game_state: GameState) -> None:
        """Mark a level as completed and save."""
        ...

    def mark_secret_found(self, world: int, level: int, secret_id: str,
                          game_state: GameState) -> None:
        """Mark a secret as found in a level and save."""
        ...

    def mark_mask_acquired(self, mask_id: str, game_state: GameState) -> None:
        """Persist a newly acquired mask to the save file."""
        ...


@dataclass
class GameState:
    """Complete game state for saving/loading.

    This is the single authoritative representation of all persistent
    player data. Systems read from and write to this object.
    """
    current_world: int = 1
    current_level: int = 1
    stone_count: int = 0
    max_hearts: int = 3
    current_hearts: float = 3.0
    unlocked_masks: list[str] = field(default_factory=list)
    active_mask: str | None = None
    quick_swap_unlocked: bool = False
    purchased_upgrades: list[str] = field(default_factory=list)
    consumable_inventory: dict[str, int] = field(default_factory=dict)
    special_ammo: dict[str, int] = field(default_factory=dict)
    level_completion: dict[str, dict] = field(default_factory=dict)
    # level_completion format: {"w1_l1": {"completed": True, "secrets": ["secret_a"]}, ...}
    play_time: float = 0.0
```

**Data owned**: Save file path, level-entry snapshots.
**Dependencies**: None (reads/writes GameState, file I/O only).

### 3.12 AudioManager

```python
class AudioManager:
    """Centralized audio playback with named slots.

    Reads data/audio_config.json mapping slot names to file paths.
    Graceful fallback: missing files log a warning and play silence.
    Never crashes due to missing audio. Placeholder sounds are generated
    programmatically (simple beeps/tones) when no file is configured.

    Subscribes to EventBus events for automatic SFX playback (e.g.,
    stone_collected -> play stone_pickup SFX).
    """

    def __init__(self, event_bus: EventBus, config_path: str) -> None: ...

    def play_music(self, slot: str, loop: bool = True, fade_ms: int = 0) -> None:
        """Play a music track by slot name. Crossfades if fade_ms > 0."""
        ...

    def stop_music(self, fade_ms: int = 0) -> None:
        """Stop the current music, optionally fading out."""
        ...

    def play_sfx(self, slot: str) -> None:
        """Play a sound effect by slot name. Fires and forgets."""
        ...

    def set_volume(self, music: float = None, sfx: float = None) -> None:
        """Set volume levels (0.0 to 1.0)."""
        ...

    def reload_config(self) -> None:
        """Reload audio_config.json from disk (hot-reload for development)."""
        ...
```

**Data owned**: Audio slot -> file path mapping, loaded Sound/Music objects, volume levels.
**Dependencies**: EventBus (subscribes for automatic SFX), Pygame mixer.

### 3.13 SpecialAmmoSystem

```python
class SpecialAmmoSystem:
    """Manages special ammo types, inventory, and the hybrid recharge system.

    Special ammo recharges on a passive timer (base ~15-20 seconds per unit).
    Each enemy kill reduces the remaining recharge time by 30% multiplicatively.
    All values are from economy.json.
    """

    def __init__(self, event_bus: EventBus, economy_data: dict) -> None: ...

    def equip_ammo(self, ammo_type: str) -> None:
        """Set the active special ammo type."""
        ...

    def consume_ammo(self) -> bool:
        """Use one unit of equipped ammo. Returns False if empty."""
        ...

    def update(self, dt: float) -> None:
        """Tick the passive recharge timer."""
        ...

    def on_enemy_killed(self) -> None:
        """Accelerate recharge by 30% of remaining time."""
        ...

    @property
    def current_ammo_type(self) -> str | None: ...

    @property
    def ammo_count(self) -> int: ...

    @property
    def recharge_fraction(self) -> float:
        """0.0 (empty) to 1.0 (full) for HUD display."""
        ...
```

**Data owned**: Equipped ammo type, ammo counts per type, recharge timer.
**Dependencies**: EventBus (subscribes to enemy_killed), economy data.

### 3.14 ConsumableSystem

> **Decided** (Issue #12): Consumables are used exclusively via the pause menu. There is no quick-use keybind. This keeps the tension loop intact and prevents consumable spam during combat. The `use_item` interface is keybind-agnostic -- if a quick-use keybind is needed later, it can call `use_item` directly from the gameplay scene without refactoring the ConsumableSystem.

```python
class ConsumableSystem:
    """Manages consumable items: inventory, usage, active buffs, and refunds.

    Consumables are used from the pause menu only (decided, Issue #12).
    The use_item method is input-agnostic: it can be called from any context
    (pause menu scene, or a future quick-use keybind) without changes.

    On death, all consumables used during the failed attempt are refunded
    (restored to the level-entry state). Active buff timers are tracked here.
    All consumable effects come from economy.json.
    """

    def __init__(self, event_bus: EventBus, economy_data: dict) -> None: ...

    def use_item(self, item_id: str, player: Player) -> bool:
        """Use a consumable. Returns False if none in inventory.

        This method is input-agnostic. Currently called from the PauseScene
        items menu. Can be called from a quick-use keybind handler in
        GameplayScene if that feature is added later.
        """
        ...

    def update(self, dt: float) -> None:
        """Tick active buff timers."""
        ...

    def get_damage_multiplier(self) -> float:
        """Return current damage multiplier from active buffs (default 1.0)."""
        ...

    def get_defense_multiplier(self) -> float:
        """Return current defense multiplier from active buffs (default 1.0)."""
        ...

    def is_invincible(self) -> bool:
        """Whether an invincibility consumable (Aigua de Font) is active."""
        ...

    def snapshot(self) -> dict:
        """Snapshot for death rollback."""
        ...

    def restore(self, snapshot: dict) -> None:
        """Restore consumable state from snapshot."""
        ...
```

**Data owned**: Consumable inventory counts, active buff timers and effects.
**Dependencies**: EventBus, economy data.

### 3.15 LevelLoader

```python
class LevelLoader:
    """Loads a level from its JSON data file into runtime objects.

    Parses the tile grid, collision layers, entity spawn points, triggers,
    parallax background configuration, and level metadata. Returns a
    populated TileMap and a list of entities/triggers ready for the
    gameplay scene.
    """

    def __init__(self, asset_manifest: dict, enemy_definitions: dict,
                 economy_data: dict) -> None: ...

    def load(self, level_path: str) -> LevelData:
        """Load a level JSON and return a LevelData container.

        Returns:
            LevelData with tilemap, entities, triggers, parallax config,
            and level metadata.
        """
        ...


@dataclass
class LevelData:
    """Container for all runtime data produced by loading a level."""
    tilemap: TileMap
    entities: list[Entity]
    triggers: list[Trigger]
    parallax_layers: list[dict]
    metadata: dict  # level name, world, music slot, etc.
    player_spawn: tuple[int, int]
    companion_spawn: tuple[int, int]
```

**Data owned**: None persistent (produces LevelData from files).
**Dependencies**: Asset manifest, enemy definitions, economy data.

### 3.16 TileMap

```python
class TileMap:
    """Tile-based level geometry: rendering and collision data.

    Manages multiple layers: background, midground (collision), foreground
    (decoration), and special tile types (breakable, one-way, phase-through,
    wooden).

    Tiles are 16x16 pixels. The tilemap is loaded by LevelLoader and
    referenced by the physics system for collision checks.
    """

    def __init__(self, tile_data: dict, tileset_surface: pygame.Surface) -> None: ...

    def get_collision_rects(self, layer: str = "solid") -> list[pygame.Rect]:
        """Return all collision rects for the specified layer."""
        ...

    def get_tile_at(self, x: int, y: int, layer: str) -> int:
        """Return the tile ID at grid position (x, y) in the given layer."""
        ...

    def set_tile_at(self, x: int, y: int, layer: str, tile_id: int) -> None:
        """Change a tile at runtime (e.g., breaking a breakable tile)."""
        ...

    def render_layer(self, surface: pygame.Surface, layer: str,
                     camera_offset: tuple[int, int]) -> None:
        """Render a single tile layer with camera offset."""
        ...

    @property
    def width_pixels(self) -> int: ...

    @property
    def height_pixels(self) -> int: ...

    @property
    def width_tiles(self) -> int: ...

    @property
    def height_tiles(self) -> int: ...
```

**Data owned**: Tile grid data (per layer), tileset surface.
**Dependencies**: None (receives data from LevelLoader).

### 3.17 SpriteRenderer

```python
class SpriteRenderer:
    """Loads sprite sheets, slices into frames, and plays animations.

    Sprite sheets are defined in the asset manifest. Animation sequences
    are defined per entity type. The renderer caches sliced frames to
    avoid re-slicing every frame.
    """

    def __init__(self, asset_manifest: dict) -> None: ...

    def load_sprite_sheet(self, asset_id: str) -> None:
        """Load and slice a sprite sheet by asset ID."""
        ...

    def get_frame(self, asset_id: str, frame_index: int) -> pygame.Surface:
        """Return a specific frame from a loaded sprite sheet."""
        ...

    def create_animation(self, asset_id: str,
                         frame_indices: list[int],
                         frame_durations: list[float],
                         loop: bool = True) -> Animation:
        """Create an Animation object from frame indices and durations."""
        ...


class Animation:
    """Plays a sequence of frames with per-frame durations.

    Driven by update(dt). Returns the current frame surface.
    """

    def update(self, dt: float) -> None: ...
    def reset(self) -> None: ...

    @property
    def current_frame(self) -> pygame.Surface: ...

    @property
    def finished(self) -> bool:
        """True if a non-looping animation has completed."""
        ...
```

**Data owned**: Frame cache (dict of asset_id -> list of Surfaces).
**Dependencies**: Asset manifest (file paths).

### 3.18 HUD

```python
class HUD:
    """Renders the in-game heads-up display.

    Top-left: hearts (current/max, half-heart granularity).
    Top-right: mask icon with cooldown radial fill, stone count,
    special ammo count with recharge indicator.
    Quick-swap arrows when enabled.
    No-mask placeholder in World 1.

    Subscribes to EventBus for real-time updates.
    """

    def __init__(self, event_bus: EventBus) -> None: ...

    def update(self, game_state: GameState, mask_system: MaskSystem,
               special_ammo: SpecialAmmoSystem) -> None:
        """Refresh HUD data from current game state."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Draw all HUD elements."""
        ...
```

**Data owned**: Cached display values, mask icon surfaces, heart sprites.
**Dependencies**: EventBus (subscribes for refresh triggers).

### 3.19 DialogueBox

```python
class DialogueBox:
    """Renders the bottom-screen dialogue text box with character portrait.

    Dialogue data is loaded from JSON files in data/dialogue/.
    Text appears letter-by-letter. Pressing interact advances or skips.
    A dialogue sequence is a list of lines, each with a speaker, portrait,
    text, and optional SFX trigger.
    """

    def __init__(self, event_bus: EventBus) -> None: ...

    def start(self, dialogue_sequence: list[dict]) -> None:
        """Begin a dialogue sequence."""
        ...

    def advance(self) -> bool:
        """Advance to next line or finish revealing current line.

        Returns True if the dialogue sequence is complete.
        """
        ...

    def update(self, dt: float) -> None:
        """Update letter-by-letter text reveal."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Draw the dialogue box, portrait, and text."""
        ...

    @property
    def is_active(self) -> bool: ...
```

**Data owned**: Current dialogue sequence, current line index, text reveal timer.
**Dependencies**: EventBus (publishes dialogue_started/ended).

### 3.20 ShopUI

```python
class ShopUI:
    """Llorencc's shop interface with Masks and Items tabs.

    Inventory is driven by data/shop/shop_inventory.json filtered by
    the current world (unlock thresholds). Mask tab shows all unlocked
    masks for equipping. Items tab shows purchasable consumables,
    upgrades, and special ammo.

    After quick-swap unlock, the Masks tab shows a note about L1/R1 cycling.
    """

    def __init__(self, event_bus: EventBus, economy: EconomySystem,
                 mask_system: MaskSystem) -> None: ...

    def open(self, current_world: int) -> None:
        """Open the shop with inventory filtered for the current world."""
        ...

    def handle_input(self, input_state: InputState) -> None:
        """Navigate tabs, select items, confirm purchases."""
        ...

    def update(self, dt: float) -> None: ...

    def render(self, surface: pygame.Surface) -> None: ...
```

**Data owned**: Current tab, selected item index, shop inventory for current world.
**Dependencies**: EventBus, EconomySystem (prices, spending), MaskSystem (equip).

### 3.21 EnemyFactory

```python
class EnemyFactory:
    """Creates enemy instances from JSON definitions.

    Enemy types are defined in data/enemies/worldN_enemies.json.
    Each definition specifies: type ID, health, damage, behavior,
    sprite reference, drop table, and movement parameters.

    The factory instantiates an Enemy with the appropriate behavior
    components attached (patrol, chase, flee, shield, swoop, etc.).
    """

    def __init__(self, enemy_definitions: dict, economy_data: dict,
                 sprite_renderer: SpriteRenderer) -> None: ...

    def create(self, enemy_type: str, position: tuple[int, int]) -> Enemy:
        """Create an enemy of the given type at the given position."""
        ...

    def register_type(self, type_id: str, definition: dict) -> None:
        """Register a new enemy type (for runtime extension)."""
        ...
```

**Data owned**: Enemy type registry (loaded from JSON).
**Dependencies**: Enemy definitions (JSON), economy data (drop tables), SpriteRenderer.

### 3.22 Game (Main Loop)

```python
class Game:
    """Top-level game object. Owns the main loop and all shared systems.

    Initializes Pygame, creates all systems, wires dependencies, and
    runs the main loop: process events -> update -> render at 60 FPS.

    Systems are created once and shared across scenes. Scenes are
    created/destroyed as needed by the SceneManager.
    """

    def __init__(self) -> None: ...

    def run(self) -> None:
        """Start the main game loop. Blocks until quit."""
        ...

    # Shared systems accessible by scenes:
    event_bus: EventBus
    input_handler: InputHandler
    scene_manager: SceneManager
    audio_manager: AudioManager
    save_system: SaveSystem
    economy: EconomySystem
    mask_system: MaskSystem
    sprite_renderer: SpriteRenderer
    # Scene-local systems (created per gameplay scene):
    # physics, combat, sling, special_ammo, consumable
```

---

## 4. Data Formats

All data files live under `sa_fona/data/`. JSON is the universal format for human-editable game data.

### 4.1 Level Format (`data/levels/worldN/level_X_Y.json`)

> **Decided** (Issue #10): Custom JSON is the level file format. No runtime TMX parsing. If a visual map editor (e.g., Tiled) is needed later, a Tiled-to-JSON converter script can be added without changing the engine.

```json
{
  "metadata": {
    "world": 1,
    "level": 1,
    "name": "Es Primer Pas",
    "name_en": "The First Step",
    "music_slot": "world_1_theme",
    "difficulty": 1,
    "tileset": "world1",
    "background": "world1_bg"
  },
  "dimensions": {
    "width": 120,
    "height": 15
  },
  "layers": {
    "background": [
      [0, 0, 0, 1, 1, "...array of tile IDs, width x height..."]
    ],
    "midground": [
      ["...collision layer tile IDs..."]
    ],
    "foreground": [
      ["...decoration layer tile IDs..."]
    ]
  },
  "collision_types": {
    "solid": [1, 2, 3, 4, 5],
    "one_way": [10, 11],
    "breakable_slam": [20, 21],
    "breakable_fire": [22, 23],
    "phase_through": [30, 31],
    "hazard": [40, 41]
  },
  "player_spawn": { "x": 2, "y": 12 },
  "companion_spawn": { "x": 3, "y": 12 },
  "entities": [
    {
      "type": "possessed_sheep",
      "x": 45,
      "y": 12,
      "properties": {
        "patrol_range": 5,
        "facing": "left"
      }
    },
    {
      "type": "heart_pickup",
      "x": 80,
      "y": 10
    }
  ],
  "triggers": [
    {
      "type": "dialogue",
      "rect": { "x": 5, "y": 10, "w": 3, "h": 3 },
      "dialogue_id": "w1_l1_bep_intro",
      "once": true
    },
    {
      "type": "save_point",
      "rect": { "x": 115, "y": 12, "w": 2, "h": 3 },
      "shop_available": false
    },
    {
      "type": "level_end",
      "rect": { "x": 118, "y": 12, "w": 2, "h": 3 }
    }
  ],
  "secrets": [
    {
      "id": "w1_l1_secret_a",
      "requires_mask": null,
      "description": "Hidden alcove behind breakable rocks",
      "reward": { "stones": 3 }
    }
  ],
  "parallax": [
    {
      "layer": "far",
      "asset": "world1_bg_sky",
      "scroll_factor": 0.1
    },
    {
      "layer": "mid",
      "asset": "world1_bg_mountains",
      "scroll_factor": 0.3
    },
    {
      "layer": "near",
      "asset": "world1_bg_trees",
      "scroll_factor": 0.6
    }
  ]
}
```

**Notes**:
- Tile layers are 2D arrays of tile IDs. Tile ID 0 = empty.
- `collision_types` maps semantic collision categories to tile IDs. The physics system uses these to determine tile behavior.
- `entities` defines spawn points. Each entity references an enemy type (defined in the enemy JSON) or a pickup type.
- `triggers` define interaction zones (dialogue, save points, level boundaries, boss gates).
- `secrets` track discoverable secrets per level. The `requires_mask` field indicates which mask is needed (null = no mask needed). This drives the Level Select secret-found indicators.
- `parallax` defines background scrolling layers with different scroll factors.
- All coordinates are in tile units (multiply by 16 for pixels).

### 4.2 Enemy Definitions (`data/enemies/worldN_enemies.json`)

```json
{
  "possessed_sheep": {
    "display_name": "Possessed Sheep",
    "health": 2,
    "contact_damage": 0.5,
    "behavior": "patrol",
    "behavior_params": {
      "patrol_range": 5,
      "speed": 40,
      "charge_speed": 80,
      "charge_tell_time": 0.8,
      "charge_distance": 4
    },
    "sprite": "enemy_possessed_sheep",
    "hitbox": { "w": 16, "h": 16 },
    "drops": {
      "stones": { "min": 1, "max": 2 },
      "heart_chance": 0.1
    },
    "vulnerabilities": {
      "slam_stun_duration": 1.5,
      "fire_dash_kills": false
    }
  },
  "rival_warrior": {
    "display_name": "Rival Tribal Warrior",
    "health": 3,
    "contact_damage": 1.0,
    "behavior": "chase",
    "behavior_params": {
      "chase_range": 6,
      "speed": 50,
      "attack_range": 1.5,
      "attack_cooldown": 1.0,
      "block_chance": 0.3,
      "block_duration": 0.5
    },
    "sprite": "enemy_rival_warrior",
    "hitbox": { "w": 16, "h": 24 },
    "drops": {
      "stones": { "min": 1, "max": 3 },
      "heart_chance": 0.15
    },
    "vulnerabilities": {
      "slam_stun_duration": 2.0,
      "fire_dash_kills": false
    }
  },
  "stone_guardian": {
    "display_name": "Stone Guardian",
    "health": 6,
    "contact_damage": 1.5,
    "behavior": "patrol",
    "behavior_params": {
      "patrol_range": 3,
      "speed": 20,
      "attack_range": 2.0,
      "attack_cooldown": 2.0,
      "attack_tell_time": 1.0
    },
    "sprite": "enemy_stone_guardian",
    "hitbox": { "w": 24, "h": 32 },
    "drops": {
      "stones": { "min": 2, "max": 4 },
      "heart_chance": 0.2
    },
    "vulnerabilities": {
      "slam_stun_duration": 2.5,
      "fire_dash_kills": false
    }
  }
}
```

**Notes**:
- One JSON file per world keeps enemy definitions organized.
- `behavior` references a behavior component: `patrol`, `chase`, `flee`, `shield`, `swoop`, `sniper`, `bomber`, `swarm`, `steal`.
- `behavior_params` are specific to the behavior type. The enemy factory passes these to the behavior component constructor.
- `drops` reference economy values. The `stones` range is the base; the actual drop is a random integer in [min, max]. Drop rates can be overridden in `economy.json` for global tuning.
- `vulnerabilities` define how the enemy reacts to mask powers (stun durations, instant kills, etc.).

### 4.3 Boss Definitions (`data/bosses/boss_*.json`)

```json
{
  "boss_id": "bou_de_pedra",
  "display_name": "Es Bou de Pedra",
  "world": 1,
  "health": 30,
  "sprite": "boss_bou_de_pedra",
  "music_slot": "boss_1_theme",
  "intro_dialogue_id": "boss_1_intro",
  "arena": {
    "width": 25,
    "height": 10,
    "destructible_pillars": 4
  },
  "phases": [
    {
      "phase": 1,
      "name": "The Charge",
      "hp_range": [0.66, 1.0],
      "patterns": [
        {
          "id": "bull_rush",
          "tell_time": 1.0,
          "damage": 1.5,
          "punish_window": 2.5,
          "params": {
            "speed": 200,
            "stun_on_wall_hit": true,
            "destroys_pillars": true
          }
        },
        {
          "id": "headbutt",
          "tell_time": 0.5,
          "damage": 1.0,
          "punish_window": 1.5,
          "params": {
            "range": 2.0
          }
        }
      ],
      "transition_effect": "roar_screen_shake"
    },
    {
      "phase": 2,
      "name": "The Stomp",
      "hp_range": [0.33, 0.66],
      "patterns": [
        {
          "id": "bull_rush",
          "tell_time": 0.8,
          "damage": 1.5,
          "punish_window": 2.5,
          "params": { "speed": 250 }
        },
        {
          "id": "ground_stomp",
          "tell_time": 1.2,
          "damage": 1.0,
          "punish_window": 2.0,
          "params": {
            "shockwave_range": 6,
            "direct_damage": 1.5
          }
        },
        {
          "id": "rock_hurl",
          "tell_time": 0.8,
          "damage": 1.0,
          "punish_window": 1.5,
          "params": {
            "rock_count": 3
          }
        }
      ],
      "transition_effect": "core_reveal"
    },
    {
      "phase": 3,
      "name": "The Core",
      "hp_range": [0.0, 0.33],
      "patterns": [
        {
          "id": "frenzy_rush",
          "tell_time": 0.6,
          "damage": 1.5,
          "punish_window": 2.5,
          "params": {
            "bounces": 3
          }
        },
        {
          "id": "core_pulse",
          "tell_time": 1.0,
          "damage": 1.0,
          "punish_window": 2.0,
          "params": {
            "radius": 8
          }
        }
      ],
      "weak_point": {
        "location": "chest",
        "charge_multiplier": 2.0,
        "tier3_multiplier": 3.0
      }
    }
  ],
  "post_defeat": {
    "mask_granted": "stone_slam",
    "dialogue_id": "dimoni_sant_joan_grant",
    "cutscene": "w1_post_boss"
  }
}
```

**Notes**:
- Boss definitions are highly structured to support the 3-phase design pattern.
- Each pattern has explicit `tell_time` and `punish_window` values (enforcing the GDD's non-negotiable rules).
- `post_defeat` drives the mask acquisition flow: which mask is granted, the dimoni dialogue, and the cutscene ID.
- Pattern `id` values map to boss behavior implementations in code. The JSON provides the tuning parameters; the code provides the behavior logic.

### 4.4 Mask Definitions (`data/masks.json`)

```json
{
  "stone_slam": {
    "display_name": "Mask of Sant Joan",
    "power_name": "Stone Slam",
    "description": "Ground pound shockwave. Breaks floors, stuns enemies.",
    "earned_after_world": 1,
    "cooldown": 2.0,
    "icon": "mask_icon_stone_slam",
    "params": {
      "shockwave_range_tiles": 3,
      "shockwave_damage": 2.0,
      "stun_duration": 1.5,
      "breaks_tiles": ["breakable_slam"],
      "creates_platform": true,
      "screen_shake_intensity": 0.5,
      "screen_shake_duration": 0.3
    }
  },
  "double_jump": {
    "display_name": "Mask of Manacor",
    "power_name": "Double Jump",
    "description": "Second midair jump. Resets on landing.",
    "earned_after_world": 2,
    "cooldown": 0.5,
    "icon": "mask_icon_double_jump",
    "params": {
      "jump_force_multiplier": 0.9,
      "resets_on_landing": true,
      "max_air_jumps": 1
    }
  },
  "fire_dash": {
    "display_name": "Mask of Fire",
    "power_name": "Fire Dash",
    "description": "Horizontal dash. Burns barricades, damages enemies in path.",
    "earned_after_world": 3,
    "cooldown": 3.0,
    "icon": "mask_icon_fire_dash",
    "params": {
      "dash_distance_tiles": 5,
      "dash_speed": 400,
      "invulnerability_duration": 0.3,
      "damage": 2.0,
      "breaks_tiles": ["breakable_fire"],
      "fire_trail_duration": 0.5
    }
  },
  "smoke_vanish": {
    "display_name": "Mask of Pollenca",
    "power_name": "Smoke Vanish",
    "description": "Brief invisibility. Phase through thin walls and enemies.",
    "earned_after_world": 4,
    "cooldown": 4.0,
    "icon": "mask_icon_smoke_vanish",
    "params": {
      "duration": 1.5,
      "phases_through_thin_walls": true,
      "phases_through_enemies": true,
      "phases_through_projectiles": true
    }
  },
  "tourist_rage": {
    "display_name": "Mask of Sa Pobla",
    "power_name": "Tourist Rage",
    "description": "AoE shockwave. Pushes back and stuns all nearby enemies.",
    "earned_after_world": 5,
    "cooldown": 5.0,
    "icon": "mask_icon_tourist_rage",
    "params": {
      "push_distance_tiles": 4,
      "stun_duration": 2.0,
      "damage": 1.0,
      "radius_tiles": 4,
      "breaks_destructible_env": true,
      "screen_shake_intensity": 0.3,
      "screen_shake_duration": 0.2
    }
  }
}
```

### 4.5 Economy Configuration (`data/economy.json`)

This is the **single source of truth** for all economy values. The project owner edits this file to tune balance during playtesting.

```json
{
  "version": "1.0",
  "sling": {
    "charge_thresholds": {
      "tier_1": { "min_hold": 0.3, "max_hold": 0.8, "damage_multiplier": 1.0, "range_tiles": 8 },
      "tier_2": { "min_hold": 0.8, "max_hold": 1.5, "damage_multiplier": 2.0, "range_tiles": 15 },
      "tier_3": { "min_hold": 1.5, "damage_multiplier": 3.0, "range_tiles": 24 }
    },
    "tap_damage": 1.0,
    "tap_range_tiles": 1.5
  },
  "special_ammo": {
    "recharge_base_seconds": 17.5,
    "kill_recharge_reduction": 0.3,
    "types": {
      "explosive_rock": {
        "display_name": "Explosive Rock",
        "effect": "aoe_damage",
        "aoe_radius_tiles": 2,
        "damage_multiplier": 2.0,
        "breaks_walls": true,
        "unlock_world": 2,
        "pack_size": 3,
        "pack_price": 30
      },
      "piercing_rock": {
        "display_name": "Piercing Rock",
        "effect": "pierce",
        "max_targets": 3,
        "ignores_shields": true,
        "damage_multiplier": 1.5,
        "unlock_world": 3,
        "pack_size": 3,
        "pack_price": 40
      },
      "frozen_rock": {
        "display_name": "Frozen Rock",
        "effect": "freeze",
        "freeze_duration": 3.0,
        "damage_multiplier": 1.0,
        "unlock_world": 4,
        "pack_size": 3,
        "pack_price": 50
      }
    }
  },
  "health": {
    "starting_hearts": 3,
    "max_hearts_cap": 8,
    "heart_upgrade_costs": [40, 75, 120, 175, 240],
    "half_heart_value": 0.5
  },
  "damage_table": {
    "weak_enemy_contact": 0.5,
    "standard_enemy_attack": 1.0,
    "heavy_enemy_attack": 1.5,
    "environmental_hazard": 1.0,
    "boss_normal_attack": 1.0,
    "boss_heavy_attack": 1.5,
    "boss_heavy_attack_max": 2.0,
    "tax_collector_contact": 0
  },
  "tax_collector": {
    "steal_min": 5,
    "steal_max": 15
  },
  "consumables": {
    "ensaimada": {
      "display_name": "Ensaimada",
      "effect": "heal",
      "heal_amount": 2.0,
      "price": 10,
      "unlock_world": 1
    },
    "sobrassada_pot": {
      "display_name": "Sobrassada Pot",
      "effect": "heal_full",
      "price": 25,
      "unlock_world": 2
    },
    "herbes_liqueur": {
      "display_name": "Herbes Liqueur",
      "effect": "damage_buff",
      "damage_multiplier": 1.5,
      "duration_seconds": 60,
      "price": 30,
      "unlock_world": 3
    },
    "oli_doliva": {
      "display_name": "Oli d'Oliva",
      "effect": "defense_buff",
      "defense_multiplier": 0.5,
      "duration_seconds": 60,
      "price": 30,
      "unlock_world": 3
    },
    "aigua_de_font": {
      "display_name": "Aigua de Font",
      "effect": "invincibility",
      "duration_seconds": 5,
      "price": 40,
      "unlock_world": 4
    }
  },
  "stone_drops": {
    "breakable_pot": { "min": 1, "max": 3 },
    "breakable_crate": { "min": 2, "max": 4 },
    "grass_tuft": { "min": 0, "max": 2 },
    "furniture": { "min": 1, "max": 3 }
  },
  "level_income_targets": {
    "explorer_per_level_min": 28,
    "explorer_per_level_max": 52,
    "rusher_per_level_min": 12,
    "rusher_per_level_max": 20
  }
}
```

### 4.6 Dialogue Format (`data/dialogue/*.json`)

```json
{
  "w1_l1_bep_intro": {
    "trigger": "area",
    "skippable": true,
    "lines": [
      {
        "speaker": "bep",
        "portrait": "bep_excited",
        "text": "Ramon! Move! The sheep are acting strange!",
        "sfx": "bep_bleat",
        "auto_advance_ms": null
      },
      {
        "speaker": "ramon",
        "portrait": "ramon_annoyed",
        "text": "...They're always strange.",
        "sfx": null,
        "auto_advance_ms": null
      }
    ]
  },
  "boss_1_intro": {
    "trigger": "boss_gate",
    "skippable_on_retry": true,
    "skippable": false,
    "lines": [
      {
        "speaker": "narrator",
        "portrait": null,
        "text": "The ground shakes. Ancient stone begins to move.",
        "sfx": "boss_intro",
        "auto_advance_ms": 3000
      }
    ]
  }
}
```

**Notes**:
- `skippable` controls whether the player can skip the dialogue entirely (first encounter).
- `skippable_on_retry` allows skipping on subsequent encounters (boss intros).
- `auto_advance_ms` makes a line advance automatically after a delay (for narrator/cutscene lines).
- `portrait` references an asset ID from the asset manifest.

### 4.7 Shop Inventory (`data/shop/shop_inventory.json`)

```json
{
  "masks_tab": {
    "description": "Swap your active dimoni mask. (Once quick-swap is unlocked, use L1/R1 to cycle masks anytime.)",
    "items": "dynamic: populated from MaskSystem.unlocked_masks at runtime"
  },
  "items_tab": [
    {
      "id": "ensaimada",
      "category": "consumable",
      "unlock_world": 1,
      "max_stock": 5
    },
    {
      "id": "sobrassada_pot",
      "category": "consumable",
      "unlock_world": 2,
      "max_stock": 3
    },
    {
      "id": "herbes_liqueur",
      "category": "consumable",
      "unlock_world": 3,
      "max_stock": 3
    },
    {
      "id": "oli_doliva",
      "category": "consumable",
      "unlock_world": 3,
      "max_stock": 3
    },
    {
      "id": "aigua_de_font",
      "category": "consumable",
      "unlock_world": 4,
      "max_stock": 2
    },
    {
      "id": "explosive_rock_pack",
      "category": "special_ammo",
      "ammo_type": "explosive_rock",
      "unlock_world": 2,
      "max_stock": null
    },
    {
      "id": "piercing_rock_pack",
      "category": "special_ammo",
      "ammo_type": "piercing_rock",
      "unlock_world": 3,
      "max_stock": null
    },
    {
      "id": "frozen_rock_pack",
      "category": "special_ammo",
      "ammo_type": "frozen_rock",
      "unlock_world": 4,
      "max_stock": null
    },
    {
      "id": "heart_upgrade_1",
      "category": "permanent",
      "unlock_world": 1,
      "max_stock": 1
    },
    {
      "id": "heart_upgrade_2",
      "category": "permanent",
      "unlock_world": 2,
      "max_stock": 1
    },
    {
      "id": "heart_upgrade_3",
      "category": "permanent",
      "unlock_world": 3,
      "max_stock": 1
    },
    {
      "id": "heart_upgrade_4",
      "category": "permanent",
      "unlock_world": 4,
      "max_stock": 1
    },
    {
      "id": "heart_upgrade_5",
      "category": "permanent",
      "unlock_world": 5,
      "max_stock": 1
    }
  ]
}
```

**Notes**:
- The Masks tab is dynamically populated from the MaskSystem -- it shows whatever masks the player has unlocked.
- Prices and effects are not duplicated here; they reference `economy.json` by item ID.
- `unlock_world` determines when an item appears in the shop.
- `max_stock` limits how many can be held at once (null = unlimited purchases, e.g., ammo packs).

### 4.8 Save Format (`saves/save_slot_1.json`)

```json
{
  "version": "1.0",
  "timestamp": "2026-04-16T14:30:00Z",
  "play_time_seconds": 3600,
  "current_world": 2,
  "current_level": 3,
  "story_position": {
    "world": 2,
    "level": 3,
    "in_replay": false
  },
  "player": {
    "max_hearts": 4,
    "current_hearts": 3.5,
    "stone_count": 85
  },
  "masks": {
    "unlocked": ["stone_slam"],
    "active": "stone_slam",
    "quick_swap_unlocked": false
  },
  "purchases": {
    "heart_upgrades": 1,
    "items_bought": ["heart_upgrade_1"]
  },
  "consumable_inventory": {
    "ensaimada": 2,
    "sobrassada_pot": 0,
    "herbes_liqueur": 1
  },
  "special_ammo": {
    "explosive_rock": 3,
    "piercing_rock": 0,
    "frozen_rock": 0,
    "equipped": "explosive_rock"
  },
  "level_completion": {
    "w1_l1": { "completed": true, "secrets_found": [] },
    "w1_l2": { "completed": true, "secrets_found": ["w1_l2_secret_a"] },
    "w1_l3": { "completed": true, "secrets_found": [] },
    "w1_l4": { "completed": true, "secrets_found": ["w1_l4_secret_a"] },
    "w1_boss": { "completed": true, "secrets_found": [] },
    "w2_l1": { "completed": true, "secrets_found": ["w2_l1_secret_a"] },
    "w2_l2": { "completed": true, "secrets_found": [] }
  }
}
```

**Notes**:
- `story_position` tracks the player's current story progression separately from replay state. Replaying earlier levels does not change `current_world`/`current_level`.
- `level_completion` drives the Level Select screen. Only levels with `"completed": true` appear as selectable. `secrets_found` is a list of secret IDs matching the level definition's secret list.
- `masks.active` can be null (World 1 before any mask is earned).

### 4.9 Audio Configuration (`data/audio_config.json`)

```json
{
  "music": {
    "menu_theme": { "path": "assets/audio/music/menu_theme.ogg", "volume": 0.8 },
    "world_1_theme": { "path": null, "volume": 0.7 },
    "world_2_theme": { "path": null, "volume": 0.7 },
    "world_3_theme": { "path": null, "volume": 0.7 },
    "world_4_theme": { "path": null, "volume": 0.7 },
    "world_5_theme": { "path": null, "volume": 0.7 },
    "world_5_5_theme": { "path": null, "volume": 0.7 },
    "boss_1_theme": { "path": null, "volume": 0.8 },
    "boss_2_theme": { "path": null, "volume": 0.8 },
    "boss_3_theme": { "path": null, "volume": 0.8 },
    "boss_4_theme": { "path": null, "volume": 0.8 },
    "boss_5_theme": { "path": null, "volume": 0.8 },
    "boss_5_5_theme": { "path": null, "volume": 0.8 },
    "shop_theme": { "path": null, "volume": 0.6 },
    "cutscene_theme": { "path": null, "volume": 0.7 },
    "victory_jingle": { "path": null, "volume": 0.9 },
    "death_jingle": { "path": null, "volume": 0.7 },
    "game_over_theme": { "path": null, "volume": 0.7 },
    "credits_theme": { "path": null, "volume": 0.8 }
  },
  "sfx": {
    "sling_tap": { "path": null, "volume": 0.8 },
    "sling_charge_1": { "path": null, "volume": 0.5 },
    "sling_charge_2": { "path": null, "volume": 0.6 },
    "sling_charge_3": { "path": null, "volume": 0.7 },
    "sling_release": { "path": null, "volume": 0.8 },
    "stone_hit": { "path": null, "volume": 0.7 },
    "jump": { "path": null, "volume": 0.5 },
    "double_jump": { "path": null, "volume": 0.5 },
    "wall_jump": { "path": null, "volume": 0.5 },
    "land": { "path": null, "volume": 0.4 },
    "damage_taken": { "path": null, "volume": 0.8 },
    "heart_pickup": { "path": null, "volume": 0.6 },
    "stone_pickup": { "path": null, "volume": 0.5 },
    "mask_equip": { "path": null, "volume": 0.7 },
    "mask_cooldown_ready": { "path": null, "volume": 0.5 },
    "power_stone_slam": { "path": null, "volume": 0.9 },
    "power_fire_dash": { "path": null, "volume": 0.8 },
    "power_smoke_vanish": { "path": null, "volume": 0.6 },
    "power_tourist_rage": { "path": null, "volume": 0.9 },
    "bep_bleat": { "path": null, "volume": 0.5 },
    "bep_sneeze": { "path": null, "volume": 0.7 },
    "portal_open": { "path": null, "volume": 0.8 },
    "boss_intro": { "path": null, "volume": 0.8 },
    "boss_hit": { "path": null, "volume": 0.7 },
    "boss_phase_change": { "path": null, "volume": 0.9 },
    "boss_death": { "path": null, "volume": 0.9 },
    "menu_select": { "path": null, "volume": 0.5 },
    "menu_confirm": { "path": null, "volume": 0.6 },
    "shop_buy": { "path": null, "volume": 0.6 },
    "shop_insufficient": { "path": null, "volume": 0.5 }
  }
}
```

**Notes**:
- `path: null` means no audio file is provided yet. The AudioManager generates a simple placeholder tone or plays silence.
- To add real audio: drop the file in the appropriate `assets/audio/` subfolder and update the `path` here.
- Per-slot volume allows mixing before a real audio pipeline is needed.

### 4.10 Asset Manifest (`data/asset_manifest.json`)

```json
{
  "sprites": {
    "ramon_idle": { "path": "assets/sprites/ramon/idle.png", "frame_width": 24, "frame_height": 32, "frame_count": 4 },
    "ramon_walk": { "path": "assets/sprites/ramon/walk.png", "frame_width": 24, "frame_height": 32, "frame_count": 6 },
    "ramon_jump": { "path": "assets/sprites/ramon/jump.png", "frame_width": 24, "frame_height": 32, "frame_count": 2 },
    "ramon_attack_tap": { "path": "assets/sprites/ramon/attack_tap.png", "frame_width": 32, "frame_height": 32, "frame_count": 3 },
    "ramon_attack_charge": { "path": "assets/sprites/ramon/attack_charge.png", "frame_width": 24, "frame_height": 32, "frame_count": 4 },
    "ramon_wall_slide": { "path": "assets/sprites/ramon/wall_slide.png", "frame_width": 24, "frame_height": 32, "frame_count": 2 },
    "ramon_damage": { "path": "assets/sprites/ramon/damage.png", "frame_width": 24, "frame_height": 32, "frame_count": 2 },
    "ramon_death": { "path": "assets/sprites/ramon/death.png", "frame_width": 24, "frame_height": 32, "frame_count": 4 },
    "bep_idle": { "path": "assets/sprites/bep/idle.png", "frame_width": 16, "frame_height": 16, "frame_count": 4 },
    "bep_follow": { "path": "assets/sprites/bep/follow.png", "frame_width": 16, "frame_height": 16, "frame_count": 4 },
    "enemy_possessed_sheep": { "path": "assets/sprites/enemies/possessed_sheep.png", "frame_width": 16, "frame_height": 16, "frame_count": 4 },
    "enemy_rival_warrior": { "path": "assets/sprites/enemies/rival_warrior.png", "frame_width": 16, "frame_height": 24, "frame_count": 4 },
    "enemy_stone_guardian": { "path": "assets/sprites/enemies/stone_guardian.png", "frame_width": 24, "frame_height": 32, "frame_count": 4 }
  },
  "tilesets": {
    "world1": { "path": "assets/tilesets/world1/tileset.png", "tile_size": 16 },
    "world2": { "path": "assets/tilesets/world2/tileset.png", "tile_size": 16 }
  },
  "backgrounds": {
    "world1_bg_sky": { "path": "assets/backgrounds/world1/sky.png" },
    "world1_bg_mountains": { "path": "assets/backgrounds/world1/mountains.png" },
    "world1_bg_trees": { "path": "assets/backgrounds/world1/trees.png" }
  },
  "ui": {
    "heart_full": { "path": "assets/ui/hud/heart_full.png" },
    "heart_half": { "path": "assets/ui/hud/heart_half.png" },
    "heart_empty": { "path": "assets/ui/hud/heart_empty.png" },
    "mask_icon_stone_slam": { "path": "assets/ui/hud/mask_stone_slam.png" },
    "mask_icon_double_jump": { "path": "assets/ui/hud/mask_double_jump.png" },
    "mask_icon_fire_dash": { "path": "assets/ui/hud/mask_fire_dash.png" },
    "mask_icon_smoke_vanish": { "path": "assets/ui/hud/mask_smoke_vanish.png" },
    "mask_icon_tourist_rage": { "path": "assets/ui/hud/mask_tourist_rage.png" },
    "mask_icon_empty": { "path": "assets/ui/hud/mask_empty.png" }
  }
}
```

**Notes**:
- Every asset is referenced by an ID, never by a hardcoded file path in game code.
- During development, placeholder assets are simple colored rectangles. When real art is provided by Na Margalida, the file path is updated here and the game picks up the change with no code modification.
- `frame_width`, `frame_height`, `frame_count` enable the SpriteRenderer to slice the sheet automatically.

### 4.11 Controls Configuration (`data/controls_default.json`)

```json
{
  "keyboard": {
    "move_left": ["a", "left"],
    "move_right": ["d", "right"],
    "jump": ["space"],
    "attack": ["j", "z"],
    "mask_power": ["k", "x"],
    "mask_cycle_left": ["q"],
    "mask_cycle_right": ["e"],
    "special_ammo_toggle": ["l", "c"],
    "pause": ["escape"],
    "interact": ["return"]
  },
  "gamepad": {
    "move": "left_stick_or_dpad",
    "jump": "button_a",
    "attack": "button_x",
    "mask_power": "button_y",
    "mask_cycle_left": "left_bumper",
    "mask_cycle_right": "right_bumper",
    "special_ammo_toggle": "button_b",
    "pause": "start",
    "interact": "button_a"
  }
}
```

---

## 5. Dependency Diagram

The diagram below shows which modules depend on which. Arrows point from dependent to dependency. There are **no circular dependencies**.

```
main.py
  |
  v
core/game.py
  |-- core/scene_manager.py
  |-- core/input_handler.py
  |-- core/event_bus.py
  |-- systems/audio_manager.py        (event_bus)
  |-- systems/save_system.py
  |-- systems/economy.py              (event_bus)
  |-- systems/mask_system.py           (event_bus)
  |-- rendering/sprite_renderer.py
  |-- rendering/pixel_scaler.py
  |
  v (scenes created by Game, passed shared systems)

scenes/main_menu.py
  |-- ui/menu_ui.py
  |-- systems/save_system.py           (check if save exists)
  |-- systems/audio_manager.py         (menu music)

scenes/level_select.py
  |-- ui/level_select_ui.py
  |-- systems/save_system.py           (level completion data)

scenes/gameplay.py
  |-- core/camera.py
  |-- systems/physics.py               (tilemap)
  |-- systems/combat.py                (event_bus, economy_data)
  |-- systems/sling_system.py          (event_bus, economy_data)
  |-- systems/special_ammo.py          (event_bus, economy_data)
  |-- systems/consumable_system.py     (event_bus, economy_data)
  |-- entities/player.py
  |-- entities/companion.py
  |-- entities/enemy.py + factory
  |-- entities/projectile.py
  |-- entities/pickup.py
  |-- level/level_loader.py            (asset_manifest, enemy_defs, economy)
  |-- level/tilemap.py
  |-- level/parallax.py
  |-- level/trigger.py
  |-- ui/hud.py                        (event_bus)
  |-- ui/charge_indicator.py
  |-- rendering/renderer.py
  |-- rendering/effects.py

scenes/boss.py (extends gameplay.py)
  |-- entities/boss_entity.py
  |-- ui/boss_health_bar.py

scenes/dialogue.py (overlay)
  |-- ui/dialogue_box.py               (event_bus)

scenes/shop.py
  |-- ui/shop_ui.py                    (event_bus, economy, mask_system)
  |-- systems/economy.py
  |-- systems/mask_system.py

scenes/pause.py (overlay, consumable usage entry point -- Issue #12)
  |-- ui/menu_ui.py
  |-- systems/consumable_system.py

scenes/cutscene.py
  |-- ui/dialogue_box.py
  |-- ui/transition.py
  |-- rendering/effects.py

scenes/game_over.py
  |-- ui/menu_ui.py
  |-- systems/save_system.py

scenes/settings_menu.py
  |-- ui/menu_ui.py
  |-- core/input_handler.py            (remapping)
  |-- systems/audio_manager.py         (volume)

scenes/credits.py
  |-- ui/menu_ui.py
```

### Dependency Rules

1. **core/** modules have no dependencies on scenes/, entities/, systems/, or level/. They are infrastructure.
2. **systems/** modules depend only on core/event_bus and data (JSON configs). They never import scenes/ or entities/ directly; they receive entity references through method parameters.
3. **entities/** modules depend on nothing outside their own package (and base data types). Entity behavior is driven by the systems that operate on them.
4. **scenes/** are the integration layer. They wire systems, entities, and UI together. Scenes may depend on anything except other scenes.
5. **ui/** modules depend only on core/event_bus for refresh events. They render data passed to them; they do not reach into systems.
6. **level/** modules depend on data files and the asset manifest. They produce runtime objects (TileMap, entities) consumed by scenes.
7. **rendering/** modules depend on nothing except Pygame surfaces. They are pure rendering utilities.

### Communication Flow

Inter-system communication follows these rules:

1. **Direct method calls** for tightly coupled operations (e.g., CombatSystem calls `deal_damage` on an Entity).
2. **EventBus** for loosely coupled notifications (e.g., `enemy_killed` triggers stone drops in Economy AND a sound in AudioManager AND recharge acceleration in SpecialAmmo -- none of these systems need to know about each other).
3. **No global state**. All shared state flows through Game -> scenes -> systems via explicit parameter passing.

---

## 6. Extension Points

Each extension point describes how to add new content without modifying existing Python code (data-only changes) or with minimal code changes (new behavior implementations).

### 6.1 Adding a New World

**Data-only steps (no code changes)**:

1. Create level files: `data/levels/worldN/level_N_1.json` through `level_N_4.json` + `boss_N.json`
2. Create enemy definitions: `data/enemies/worldN_enemies.json`
3. Create dialogue: `data/dialogue/worldN_dialogue.json`
4. Add boss definition: `data/bosses/boss_<name>.json`
5. Add tileset: `assets/tilesets/worldN/tileset.png`
6. Add background layers: `assets/backgrounds/worldN/`
7. Add audio slots to `data/audio_config.json`: `world_N_theme`, `boss_N_theme`
8. Update `data/asset_manifest.json` with new sprites, tilesets, backgrounds
9. Add world-specific shop items to `data/shop/shop_inventory.json` (update `unlock_world`)
10. Update `data/economy.json` with new enemy drop rates if the new enemies use new types

**Code changes needed**:

- If the new world introduces a new enemy behavior type (e.g., a behavior not in `enemy_behaviors.py`), implement it as a new behavior class and register it in the EnemyFactory.
- If the new world introduces a new boss with unique attack patterns, implement the pattern handlers in a new boss behavior module.

### 6.2 Adding a New Enemy Type

**Data-only steps**:

1. Add the enemy definition to the appropriate `data/enemies/worldN_enemies.json`
2. Add the sprite sheet to `assets/sprites/enemies/` and register in `data/asset_manifest.json`
3. Add drop rates to `data/economy.json` if using a new drop profile
4. Place the enemy in level files by adding entries to the `entities` array

**Code change needed only if**: The enemy uses a behavior not yet implemented in `enemy_behaviors.py`.

### 6.3 Adding a New Mask Power

**Data-only steps**:

1. Add the mask definition to `data/masks.json`
2. Add the mask icon to `assets/ui/hud/` and register in `data/asset_manifest.json`
3. Set `earned_after_world` to the appropriate world number
4. Update the boss definition's `post_defeat.mask_granted` for the granting boss

**Code change needed**: Implement the power's effect as a new method in `mask_system.py` (or a dedicated power module) and register it in the mask power dispatcher. The mask's parameters (cooldown, range, damage, etc.) come from the JSON; only the behavior logic is in code.

### 6.4 Adding a New Shop Item

**Data-only steps**:

1. Add the item definition to `data/economy.json` (under `consumables` or `special_ammo.types`)
2. Add the item to `data/shop/shop_inventory.json` with `unlock_world`
3. If it has a new sprite, add to `assets/` and `data/asset_manifest.json`

**Code change needed only if**: The item has a new effect type not already supported by ConsumableSystem (heal, heal_full, damage_buff, defense_buff, invincibility) or SpecialAmmoSystem.

### 6.5 Adding New Audio

**Data-only steps (no code changes)**:

1. Place the audio file in `assets/audio/music/` or `assets/audio/sfx/`
2. Update the corresponding slot's `path` in `data/audio_config.json`
3. The AudioManager picks it up on next load (or on `reload_config()` during development)

### 6.6 Adding New Dialogue

**Data-only steps (no code changes)**:

1. Add dialogue sequences to the appropriate `data/dialogue/*.json` file
2. Reference the dialogue ID in a level trigger (`triggers` array in the level JSON) or in a boss/cutscene definition

### 6.7 Tuning Economy Balance

**Data-only steps (no code changes)**:

1. Edit `data/economy.json` directly
2. Adjust any value: prices, drop rates, heal amounts, buff durations, charge thresholds, etc.
3. The EconomySystem's `reload_config()` method can hot-reload changes during a play session (development mode)

### 6.8 Adding a New Level to an Existing World

**Data-only steps (no code changes)**:

1. Create `data/levels/worldN/level_N_X.json` following the level format schema
2. The level loader will pick it up
3. Update the world's level sequence metadata (stored in the level files themselves or in a world metadata file)

### 6.9 Modifying Level Layouts

**Data-only steps (no code changes)**:

1. Edit the tile arrays in `data/levels/worldN/level_N_X.json`
2. Move/add/remove entity spawn points and triggers
3. All changes take effect on next level load

### 6.10 Adding a Quick-Use Keybind for Consumables (Future)

> Currently consumables are pause-menu only (Issue #12). This extension point documents how to add quick-use without refactoring.

**Steps (minimal code changes)**:

1. Add a `consumable_use_pressed` action to `InputState` in `core/input_handler.py`
2. Add the keybind to `data/controls_default.json`
3. In `scenes/gameplay.py`, when `input_state.consumable_use_pressed` is True, call `consumable_system.use_item(selected_consumable, player)` directly
4. Optionally add a consumable selection cycling keybind (similar to mask cycling)
5. No changes needed to `ConsumableSystem` itself -- `use_item()` is already input-agnostic

### 6.11 Adding Multiple Save Slots (Future)

> Currently a single save slot (Issue #13). This extension point documents how to add multi-slot support.

**Steps (minimal code changes)**:

1. Create a `SlotSelectScene` in `scenes/` that presents slot choices (e.g., 3 slots)
2. Each slot maps to a different `save_path` (e.g., `saves/save_slot_1.json`, `saves/save_slot_2.json`)
3. Pass the selected slot's path to `SaveSystem.__init__(save_path)`
4. The `MainMenuScene` pushes `SlotSelectScene` before loading or starting a game
5. No changes needed to `SaveSystem` itself -- it already takes `save_path` as a parameter

---

## Appendix A: Game State Machine (Full)

```
                              +---> CREDITS
                              |
MAIN_MENU ---+---> LEVEL_SELECT ---+---> GAMEPLAY ---+---> DIALOGUE (overlay)
     |        |                     |        |         |
     |        +---> SETTINGS_MENU   |        |         +---> SHOP
     |                              |        |         |
     +------------------------------+        |         +---> PAUSE (overlay)
                                             |                   |
                                             |                   +---> SETTINGS_MENU
                                             |
                                             +---> CUTSCENE (post-boss mask grant,
                                             |               portal transition,
                                             |               world arrival)
                                             |
                                             +---> BOSS (extends GAMEPLAY)
                                             |        |
                                             |        +---> CUTSCENE (boss intro)
                                             |
                                             +---> GAME_OVER
                                                      |
                                                      +---> GAMEPLAY (restart level)
                                                      +---> MAIN_MENU
```

Overlay scenes (DIALOGUE, PAUSE) are pushed on top of GAMEPLAY without destroying it. Popping them returns to the active gameplay state.

## Appendix B: Mask Acquisition Data Flow

This traces the data flow when a mask is acquired post-boss:

```
1. BossEntity HP reaches 0
   -> publishes 'boss_defeated' event

2. GameplayScene receives 'boss_defeated'
   -> reads boss definition: post_defeat.mask_granted = "stone_slam"
   -> reads boss definition: post_defeat.cutscene = "w1_post_boss"
   -> pushes CutsceneScene

3. CutsceneScene plays the dimoni dialogue + mask grant animation
   -> at the grant moment, publishes 'mask_acquired' with mask_id="stone_slam"

4. MaskSystem receives 'mask_acquired'
   -> calls unlock_mask("stone_slam")
   -> adds to unlocked_masks list
   -> (does NOT auto-equip; player equips at shop in next world)

5. SaveSystem receives 'mask_acquired'
   -> calls mark_mask_acquired("stone_slam", game_state)
   -> writes save file immediately (mask persists even if player quits during portal)

6. AudioManager receives 'mask_acquired'
   -> plays victory_jingle

7. CutsceneScene continues with portal animation
   -> on complete, transitions to next world's first level
```

## Appendix C: Death Rollback Data Flow

```
1. Level starts
   -> SaveSystem.snapshot_level_entry(game_state) captures:
      {stone_count, current_hearts, consumable_inventory, special_ammo}

2. Player plays the level
   -> collects stones (economy.add_stones)
   -> uses consumables (consumable_system.use_item)
   -> takes damage

3. Player dies (current_hearts reaches 0)
   -> Player publishes 'player_died'

4. GameplayScene receives 'player_died'
   -> calls SaveSystem.rollback_to_snapshot(snapshot, game_state)
      - stone_count restored to level-entry value
      - current_hearts restored to level-entry value
      - consumable_inventory restored (used consumables refunded)
      - special_ammo restored
   -> pushes GameOverScene

5. GameOverScene offers: Retry (reload same level) or Quit to Menu
   -> Retry: replaces with new GameplayScene for the same level
   -> Quit: replaces with MainMenuScene
```

## Appendix D: Level Replay Data Flow

```
1. Player opens Level Select from Main Menu
   -> LevelSelectScene reads game_state.level_completion
   -> displays all levels where completed=true, organized by world
   -> shows secret badges per level

2. Player selects a completed level (e.g., W1-L3)
   -> game_state.story_position is preserved (player is still at W3-L2 in the story)
   -> game_state is marked: in_replay = true
   -> GameplayScene loads the selected level
   -> player has all currently unlocked masks available
   -> if quick_swap_unlocked, quick-swap is active

3. Player completes the replay level
   -> stones collected during replay are KEPT (added to game_state)
   -> any new secrets found are marked in level_completion
   -> save is written with updated stones and secret flags
   -> story_position is NOT changed
   -> player returns to Level Select (or Main Menu)

4. Player dies during replay
   -> normal death rollback (stones/consumables restored to replay-entry state)
   -> returns to Level Select on quit
```
