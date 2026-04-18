# N'Andreu -- D4: Sling Combat & Projectiles

**Date**: 2026-04-17
**Branch**: `feature/d4-sling-combat`
**Issue**: #23
**Tests**: 213 total (54 new), all passing

---

## What Was Built

### SlingSystem (`sa_fona/systems/sling_system.py`)

State machine with four states: `idle -> pressed -> charging -> cooldown`.

- **Tap detection**: If the attack button is pressed and released within 120ms, a short-lived melee hitbox spawns in front of the player. This gives the "whip-crack" feel specified in the GDD.
- **Charge detection**: If held past the tap threshold, transitions to `charging` state. Charge timer accumulates and determines tier:
  - Tier 1: 0.3s (1x damage, 8-tile range)
  - Tier 2: 0.8s (2x damage, 15-tile range)
  - Tier 3: 1.5s (3x damage, 24-tile range)
- **Release**: Spawns a Projectile entity with damage/range based on the active tier. If charge is below Tier 1, falls back to a melee tap.
- **Cooldown**: 150ms lockout after any attack to prevent spam.

The system publishes `sling_tap` and `sling_release` events via EventBus for future audio/visual hooks.

### Projectile (`sa_fona/entities/projectile.py`)

Extends Entity with:

- Horizontal movement at configurable speed (no gravity)
- Distance tracking with automatic deactivation at max range
- `on_hit_tile()` and `on_hit_entity()` hooks -- default behaviour is to deactivate. Subclasses can override for explosive/piercing/freezing rocks.
- `ProjectileType` enum ready for future special ammo types
- Placeholder rendering: warm grey rectangle

### ChargeIndicator (`sa_fona/ui/charge_indicator.py`)

World-space UI element rendered above the player's head:

- Hidden at Tier 0
- Dim yellow bar at Tier 1
- Bright orange (slightly wider) at Tier 2
- Flashing white/red at Tier 3 (~8 Hz pulse)
- 1px darker border for pixel visibility

### Economy Data (`sa_fona/data/economy.json`)

Contains the `sling` section with all charge thresholds, damage multipliers, range values, projectile speed, hitbox dimensions, and tap duration. D5 will extend this file with drops, prices, and consumable data per the roadmap.

### GameplayScene Integration

- SlingSystem reads InputState each frame, returns newly spawned projectiles
- Projectiles are updated and checked against tilemap solid tiles (destroyed on hit)
- Melee hitboxes rendered as translucent white flash rectangles
- Charge indicator renders above the player with camera offset
- Level reset (R key) clears all combat state
- Render order: tilemap background/midground -> melee hitboxes -> projectiles -> player -> charge indicator -> tilemap foreground

---

## Design Decisions

1. **SlingSystem is fully decoupled from Player** -- it reads player position/facing but does not modify player state. Same pattern as PhysicsSystem. The scene orchestrates.

2. **Tap threshold at 120ms** -- slightly above one 60 FPS frame (~16.7ms) to allow for input latency, but short enough that taps feel instant. Configurable as `SlingSystem.TAP_THRESHOLD`.

3. **Melee hitbox as data, not entity** -- the `MeleeHitbox` is a simple dataclass with a rect, damage, and timer. It doesn't extend Entity because it has no velocity, sprite, or movement. The CombatSystem (D6) will check overlap between melee hitboxes and enemy rects.

4. **Projectile has no gravity** -- sling stones travel in a straight horizontal line per the GDD's arcade-style design. Gravity would make aiming frustrating in a fast-paced platformer.

5. **economy.json created incrementally** -- only the `sling` section exists now. D5 adds drops/prices, D6 adds enemy damage tables. This follows the auditor's recommendation (Round 2, Finding #4).

---

## Open Questions

None. All acceptance criteria are met.

---

## What's Next

- **D5 (HUD, Pickups & Economy)**: Extends economy.json, adds EconomySystem, HUD, pickups
- **D6 (Enemies & Combat Integration)**: CombatSystem will resolve melee hitboxes and projectiles against enemies, use the sling_tap/sling_release events
