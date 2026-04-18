# D5: HUD, Pickups & Economy -- Handoff Report

**Author**: N'Andreu (Engine Programmer)
**Date**: 2026-04-17
**Issue**: #26
**Branch**: `feature/d5-hud-pickups-economy`

---

## Summary

Implemented the heads-up display (HUD), pickup entities (heart and stone), breakable objects, and the economy system. The player can now see their health and stone count on screen, collect pickups by walking over them, and break objects with the sling melee attack to earn stones.

## What Was Built

### EconomySystem (`sa_fona/systems/economy.py`)
- Loads all economy values from `data/economy.json`
- Tracks stone count with `add_stones()` / `spend_stones()`
- Provides `snapshot()` / `restore()` for death rollback
- Drop tables for enemies and breakable objects (randomized within configured ranges)
- Price lookups, consumable effects, heart upgrade costs
- Subscribes to `stone_collected` and `enemy_killed` EventBus events
- Hot-reload via `reload_config()` for playtesting

### HUD (`sa_fona/ui/hud.py`)
- Renders hearts in the top-left corner with half-heart granularity
- Hearts are diamond-shaped placeholders: full (red), half (pink), empty (dark red)
- Stone count with grey circle icon and text displayed in top-right corner
- Updates via EventBus subscriptions: `heart_collected`, `stone_collected`, `damage_taken`
- Renders in screen space on top of all other elements

### Pickup Entity (`sa_fona/entities/pickup.py`)
- Two types: HEART (red diamond) and STONE (grey circle)
- Spawned from level JSON entity definitions
- Static entities, no physics -- just sit at their position
- `collect()` method returns the event type and data for the EventBus
- GameplayScene checks player rect overlap each frame and publishes collection events

### Breakable Entity (`sa_fona/entities/breakable.py`)
- Two types: `breakable_pot` (brown rectangle) and `breakable_crate` (brown with X)
- Spawned from level JSON entity definitions
- Destroyed when overlapping with sling melee hitbox
- Drops stone pickups based on economy.json `stone_drops` table
- Dropped pickups spawn at slightly randomized positions around the breakable

### economy.json Extension
- Added `health` section (starting hearts, max cap, upgrade costs)
- Added `consumables` section (ensaimada)
- Added `stone_drops` section (breakable pot, crate, grass, furniture)
- Added `enemy_drops` section (default drop rates)
- Added `prices` section (shop item prices)
- Added `pickup_values` section (heart and stone pickup amounts)
- Preserved existing `sling` section from D4

### Test Level Updates
- Added 9 stone pickups placed along the ground and on platforms
- Added 3 heart pickups at various positions
- Added 2 breakable objects (1 pot, 1 crate)
- Pickups are visible and collectible during testing

### GameplayScene Integration
- Spawns pickups and breakables from level entity definitions on load
- Checks player-pickup overlap each frame, publishes events on collection
- Checks melee hitbox-breakable overlap each frame, spawns drop pickups
- HUD renders on top of everything after camera-relative rendering
- Level reset (R key) respawns pickups and breakables, resets HUD

## Test Coverage

74 new tests added (287 total, all passing):
- **test_economy.py**: Stone management (add/spend), snapshot/restore roundtrip, drop tables, prices, EventBus integration, hot-reload, missing file fallback
- **test_hud.py**: Initialization, data updates via events, half-heart handling, damage clamping, render smoke tests, cleanup
- **test_pickup.py**: Pickup entity creation/collection, breakable entity creation/destruction, GameplayScene integration (collection updates economy and HUD)

## Design Decisions

1. **EconomySystem subscribes to EventBus rather than being called directly**: This keeps the economy decoupled from specific pickup/combat code. When a stone is collected, the event flows: Pickup -> EventBus -> EconomySystem + HUD.

2. **HUD uses EventBus for updates, not direct references**: The HUD does not reference the Player or EconomySystem. It subscribes to `heart_collected`, `stone_collected`, and `damage_taken` events. This means any system can update the HUD by publishing the right event.

3. **Breakable drops are immediate**: When a breakable is hit, it immediately spawns Pickup entities rather than using a deferred drop system. This keeps the implementation simple while still allowing the pickups to be collected normally.

4. **Pickup positions in level JSON use tile coordinates**: Consistent with player_spawn format. Converted to pixel coordinates during spawning.

## Open Questions

- Should pickups have a small bob/float animation to make them more visible? (Currently static.)
- Should there be a brief invulnerability period after collecting a heart, or is instant healing fine?
- Should breakables respawn on level reset? (Currently yes, they respawn when R is pressed.)

## Testing Instructions

```bash
# Run tests
SDL_VIDEODRIVER=dummy conda run -n safona python -m pytest tests/ -v --tb=short

# Run the game
DISPLAY=:99 conda run -n safona python -m sa_fona.main
# Forward port 6080 -> http://localhost:6080/vnc.html
```

Walk right to see stone pickups (grey circles) and heart pickups (red diamonds). Break the pot at tile x=30 and crate at tile x=48 using the sling tap attack (J/Z key). Watch the HUD update in the top corners.
