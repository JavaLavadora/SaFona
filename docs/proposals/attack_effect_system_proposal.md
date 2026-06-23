**En Biel (Game Director):**

# Attack Effect System -- Game Design Proposal

## 1. Design Philosophy

The core problem: enemy body sprites are fixed-size canvases (16x16, 16x24, 24x32) but their attacks have reach that extends well beyond those bounds. The stone guardian's arm sweep covers ~3 tiles (48px) but the 24x32 sprite cannot convey that. The player has no visual feedback for where the danger zone begins and ends.

The solution is borrowed directly from SNES-era design. In Super Metroid, Ridley's tail sweep is a separate sprite overlaid on the body. In Mega Man X, Sigma's beam sword renders independently from his sprite. In Castlevania IV, whip and boss weapon arcs are their own animation layers. The body sprite communicates *who*, the effect sprite communicates *what the attack does*.

**Principle: every attack that extends beyond the enemy body MUST have a visible effect sprite. If the body IS the weapon (sheep, war dog), no separate effect is needed -- but the body animation must clearly sell the attack.**

---

## 2. Visual Language for Attacks

### 2.1 The Three-Phase Visual Contract

Every enemy attack follows a tell-strike-recovery cadence. The player must be able to read each phase at a glance, even when under pressure.

| Phase | Player Reads | Visual Cue | Duration Feel |
|-------|-------------|------------|---------------|
| **Tell (wind-up)** | "Attack incoming, I should move" | Anticipation frames: body coils back, flash/glow on the weapon origin point, 1-2px screen-shake tremor for heavies | 0.5s -- 1.2s depending on enemy weight |
| **Strike (active)** | "This is the danger zone NOW" | Effect sprite appears at full extent, motion trail on fast attacks, brief freeze-frame (1-2 frames) on impact, bright contact flash | 0.3s -- 0.5s |
| **Recovery** | "Safe to punish" | Effect sprite fades/dissipates (2-3 frame fadeout), enemy body slumps or staggers, weapon drops to resting pose | 0.5s -- 0.8s |

### 2.2 Readability Rules

1. **Warm colors = danger.** Attack effects use orange, red, or yellow tones during the strike phase. The player's attacks are blue/white (sling stones). No confusion.
2. **Anticipation flash.** During the tell phase, a small bright pixel cluster (2x2 or 3x3) pulses at the origin point of the attack (hand, spear tip, mouth). This is the universal "attack loading" signal. Color: white with a warm edge (#FFF0D0 -> #FFA040).
3. **Motion trails on fast attacks.** Attacks with speed > 100px/s get 1-2 ghost frames trailing behind the active effect, at 40% opacity. This sells velocity and helps the player track fast sweeps.
4. **Impact freeze.** When the strike phase begins, the effect sprite holds its first fully-extended frame for 2 game frames (~33ms at 60fps) before animating. This is the SNES "hit pause" -- it makes the attack feel weighty and gives the player an extra moment to register danger.
5. **Dust on grounded impacts.** Any attack that hits the ground plane spawns a shared dust effect (already exists in the effects system at `assets/effects/dust.png`). Reuse this.

### 2.3 Size Hierarchy

Attack effects follow a clear size hierarchy that communicates threat level:

- **Small (8x8 to 12x16):** Quick, low-damage attacks. Rival warrior spear thrust, war dog bite.
- **Medium (16x16 to 24x16):** Standard attacks. Legionary gladius stab.
- **Large (32x24 to 48x24):** Heavy attacks. Stone guardian arm sweep.
- **Massive (48x32+):** Boss attacks only.

---

## 3. Per-Enemy Attack Effect Design

### 3.1 Possessed Sheep -- Headbutt Charge

**Visual fantasy:** A wool-covered battering ram, head lowered, barreling forward with reckless abandon. Red-eyed fury.

**Effect decision: NO separate effect sprite needed.** The body IS the weapon. The existing charge animation (lowered head, faster walk cycle) is sufficient. However, the charge needs two enhancements to the existing charge sprite:

- **Tell phase:** Eyes pulse brighter (already in idle frame 1), body lowers by 1-2px (ducking to charge). A small dust puff spawns at the hooves (reuse existing `dust` effect).
- **Strike phase (during charge):** Small speed-line streaks trail behind the sheep. These can be rendered procedurally (2-3 horizontal lines, 4px long, white at 60% opacity, positioned behind the sheep and offset each frame).

**Verdict:** No new sprite sheet needed. Procedural speed lines + existing dust effect. The charge_frames already handle the body animation.

---

### 3.2 Rival Warrior -- Stone Spear Thrust

**Visual fantasy:** A quick, jabbing spear thrust. The warrior lunges forward, extending a rough stone-tipped spear in a straight horizontal line. Think of the Skeleton spear enemies in Castlevania -- compact, fast, and clearly directional.

**Effect sprite dimensions:** 24x16 pixels (1.5 tiles wide x 1 tile tall)
- The attack_hitbox_w is 16px, but the visual should slightly overshoot to feel right.

**Animation frames:** 4 frames

| Frame | Duration | Description |
|-------|----------|-------------|
| 1 -- Anticipation flash | Tell phase (held) | Just the bright anticipation dot (3x3px white/orange glow) at the warrior's hand position. Warrior body handles the pull-back pose. |
| 2 -- Thrust mid-extend | Strike start (1 frame, ~80ms) | Spear at 60% extension. Stone tip visible, wooden shaft trailing. Motion blur line behind the tip. |
| 3 -- Full thrust | Strike active (2 frames, ~160ms) | Spear fully extended. Stone spear tip at the far edge. Slight emphasis glow around the tip (1px bright outline). This is the "danger" frame. |
| 4 -- Retract | Recovery (1 frame, ~80ms) | Spear pulling back, tip fading. Half-opacity version of frame 2. |

**Sprite strip:** 96x16 (4 frames of 24x16)

**Anchor:** Positioned at the warrior's hand height (roughly y_offset = -8 from rect center), extending in facing direction. X offset = 0 (flush with enemy body edge).

**Palette colors:** Stone tip uses the stone_guardian palette greys (#969697, #828285). Shaft uses rival_warrior leather brown (#8C6428). Anticipation glow: #FFF0D0 center, #FFA040 edge.

---

### 3.3 Stone Guardian -- Arm Sweep

**Visual fantasy:** A massive, slow, devastating arc. The stone golem raises one arm (tell), then brings it crashing down and across in a wide horizontal sweep that covers ~3 tiles. Debris and dust fly. Think the Colossus arm sweep from Shadow of the Colossus, but in SNES pixel art. This is the attack that MOST needs a visual -- it is the whole reason this system exists.

**Effect sprite dimensions:** 48x24 pixels (3 tiles wide x 1.5 tiles tall)
- The attack_hitbox_w is 32px, but the visual sweep arc should be 48px wide to properly sell the motion and give the player a generous visual read.

**Animation frames:** 6 frames

| Frame | Duration | Description |
|-------|----------|-------------|
| 1 -- Wind-up glow | Tell phase (held) | Faint green glow emanating from the guardian's fist area (matching the eye glow color #50C850). A 6x6px pulsing cluster. Dust motes begin to rise. |
| 2 -- Arm raise | Tell phase (held) | The stone arm extends upward at ~45 degrees. Rocky forearm and fist visible. Cracks glow faintly green along the arm. |
| 3 -- Sweep start | Strike (1 frame, ~80ms) | Arm begins horizontal sweep. The leading edge has a bright motion trail (white->grey gradient, 3px wide). Small stone chips fly off the fist. |
| 4 -- Sweep mid | Strike active (2 frames, ~160ms) | Full horizontal sweep. The arm is extended across the entire 48px width. Heavy motion blur trail behind it. This is the main danger frame -- the arm and trail fill most of the 48x24 canvas. Impact debris (small grey squares, 2x2px) scatter above and below. |
| 5 -- Sweep end | Strike end (1 frame, ~80ms) | Arm at end of travel, decelerating. Motion trail fades. Larger dust cloud at the terminus. |
| 6 -- Dissipate | Recovery (held) | Just lingering dust particles and small stone debris settling. The arm itself is gone (returned to body). 3-4 small grey pixel clusters at various positions, fading. |

**Sprite strip:** 288x24 (6 frames of 48x24)

**Anchor:** y_offset = -4 from enemy rect.top (the sweep is roughly chest-height). X offset = 0 (flush with body edge, extending outward in facing direction).

**Palette colors:** Arm stone matches the stone_guardian palette (#828285, #505055, #969697). Glow matches eyes (#50C850, #78FF78). Debris uses stone dark (#646469). Motion trail: white (#E0E0E0) fading to mid-grey (#808085).

---

### 3.4 Legionary -- Gladius Stab

**Visual fantasy:** A disciplined, precise forward stab. The legionary drops his shield briefly, steps forward, and thrusts a short gladius (Roman short sword). Quick and clean -- no wild swings, just efficient Roman military technique. The weapon is compact but deadly.

**Effect sprite dimensions:** 16x16 pixels (1 tile square)
- The legionary's attack range is 2.0 tiles from JSON, but the visual gladius stab is short-range. The hitbox extends from the body.

**Animation frames:** 3 frames

| Frame | Duration | Description |
|-------|----------|-------------|
| 1 -- Blade flash | Tell (held) | The gladius blade catches light as it's drawn back. A bright metallic glint (2x2px white highlight) on a small blade shape (3x8px, iron grey). |
| 2 -- Full stab | Strike (2 frames, ~160ms) | Gladius fully extended forward. Clean horizontal blade (4x10px), with a sharp 1px bright edge on the leading tip. Small metallic spark at the tip (1px white). Roman-style straight blade, no curves. |
| 3 -- Retract | Recovery (1 frame, ~80ms) | Blade pulling back, only the tip visible. Half-opacity fade. |

**Sprite strip:** 48x16 (3 frames of 16x16)

**Anchor:** Positioned at the legionary's chest height (y_offset = -4 from center). X offset = 0 from body edge.

**Palette colors:** Blade: iron grey (#C0B8A8) with bright edge (#E0D8C8). Handle: dark leather (#503820). Metallic highlight: white (#F0E8D8).

---

### 3.5 War Dog -- Lunging Bite

**Visual fantasy:** A fast, snapping lunge. The dog leaps forward with jaws open, snapping shut on the target. Quick and vicious. Similar to the wolf enemies in Castlevania -- the threat is the body lunge itself.

**Effect decision: NO separate effect sprite needed.** Like the sheep, the body IS the weapon. The war dog's attack is a lunging bite where the entire body closes distance. However:

- **Tell phase:** The dog crouches lower (body compresses by 1-2px), ears flatten. Snarl visible (mouth opens, showing 2px white teeth pixels). A small dust puff at the paws (reuse `dust` effect).
- **Strike phase:** The body lunges forward with the chase speed. Mouth snaps shut (2-frame snap animation within the body sprite). Speed lines trail behind (same procedural approach as sheep).
- **Optional enhancement:** A tiny bite-snap effect (8x8, 2 frames -- open jaws then closed with a spark). This is low priority because the body lunge already sells it.

**Verdict:** Rely on body animation + procedural speed lines. If we later want extra polish, a tiny 8x8 jaw-snap effect could be added, but it is not necessary for the initial implementation.

---

## 4. Shared / Reusable Effect Components

Several visual elements can be shared across enemies to save asset budget and maintain consistency:

| Shared Effect | Dimensions | Frames | Used By |
|---------------|-----------|--------|---------|
| **Dust puff** | 8x8 | 4 | Already exists (`assets/effects/dust.png`). All grounded impacts. |
| **Impact flash** | 12x12 | 3 | Already exists (`assets/effects/impact.png`). Projectile hits, heavy weapon contacts. |
| **Anticipation glow** | 8x8 | 2 | Rival warrior, stone guardian, legionary. Pulsing warm dot at attack origin during tell. |
| **Stone debris** | 8x8 | 3 | Stone guardian sweep, boss ground_stomp, boss bull_rush (pillar hits). Small grey chunks scattering. |
| **Speed lines** | Procedural | N/A | Sheep charge, war dog lunge. Rendered in code, no sprite needed. |

**New shared sprites to create: 2** (anticipation glow, stone debris). Both are tiny (8x8) and can be on a single sheet.

---

## 5. Effect System Integration Notes

The existing `EffectRenderer` in `sa_fona/rendering/effects.py` already supports:
- Frame strip loading
- Positioned spawning (x, y in world coords)
- Looping and one-shot effects
- Tag-based removal

**What needs to be added for attack effects:**

1. **Anchored effects.** Current effects are spawned at a fixed position. Attack effects need to be anchored to an entity and offset relative to its facing direction. A new spawn method like `spawn_anchored(effect_type, entity, x_offset, y_offset)` that updates position each frame.

2. **Facing-aware flip.** When the enemy faces left, the effect sprite must be horizontally flipped. The existing `EffectRenderer.render` method does not flip sprites.

3. **New effect definitions** in `_EFFECT_DEFS` for each attack effect:
   - `"warrior_spear_thrust"` -- 24x16, 4 frames, 12fps, one-shot
   - `"guardian_arm_sweep"` -- 48x24, 6 frames, 12fps, one-shot
   - `"legionary_gladius_stab"` -- 16x16, 3 frames, 14fps, one-shot
   - `"anticipation_glow"` -- 8x8, 2 frames, 8fps, looping (removed when tell ends)
   - `"stone_debris"` -- 8x8, 3 frames, 10fps, one-shot

4. **Enemy integration.** The `Enemy.render()` method needs to spawn the appropriate attack effect when transitioning to the strike phase, and the effect must be cleaned up on recovery.

---

## 6. Boss Attack Effects

The Bou de Pedra boss has 6 attack patterns across 3 phases. The boss already has a separate rendering pipeline, but the attack effect system should be consistent with the enemy system. Here is how each boss attack maps:

| Boss Attack | Effect Type | Dimensions | Frames | Notes |
|-------------|-------------|-----------|--------|-------|
| **bull_rush** | Body IS weapon (like sheep) | N/A | N/A | Speed lines + screen shake already implemented. Add dust trail behind the boss during rush. |
| **headbutt** | Small impact burst | 16x16 | 3 | Close-range. Reuse `impact` effect, tinted orange. Flash at contact point. |
| **ground_stomp** | Shockwave ring | 48x16 | 5 | Ground-level expanding ring. The `boss_shockwave.png` already exists. Verify it has enough frames. |
| **rock_hurl** | Projectile trail | 8x8 per rock | 2 | Small dust trail per rock. Rocks themselves are sprites (`boss_rock.png` exists). |
| **frenzy_rush** | Same as bull_rush, faster | N/A | N/A | Reuse bull_rush effects with tighter timing. Phase 3 red tint overlay. |
| **core_pulse** | Expanding energy ring | 48x48 | 6 | `boss_pulse.png` exists. Red energy ring expanding from chest core. |

**Key consistency rule:** Boss attack effects follow the exact same tell-strike-recovery visual contract as regular enemies. The boss's tell overlay (pulsing yellow rectangle) should be replaced with proper anticipation effects once the system is in place -- the anticipation glow for the boss would be larger (16x16) and positioned at the attack origin (horns for headbutt, hooves for stomp, etc.).

---

## 7. AI Prompts

Canonical attack-effect prompts now live in [`docs/asset_prompts.md`](../asset_prompts.md) § 13. The earlier prompts in this proposal predate the consolidation and have been superseded — see Issue #123 and PR #124. Do NOT generate effect sprites from copies of this section elsewhere; always start from `asset_prompts.md`.

---

## 8. Implementation Priority

Ordered by gameplay impact (highest first):

| Priority | Item | Justification |
|----------|------|---------------|
| **P0** | Stone guardian arm sweep effect | This is the primary motivation. Players cannot read the 3-tile attack range without it. |
| **P1** | Anchored effect system in EffectRenderer | Required infrastructure for all attack effects. |
| **P1** | Anticipation glow (shared) | Universal tell-phase readability improvement for all weapon-wielding enemies. |
| **P2** | Rival warrior spear thrust effect | Second most important -- the 16px attack extension is invisible without a visual. |
| **P2** | Legionary gladius stab effect | Same reasoning as rival warrior, slightly lower priority since legionary is World 2. |
| **P3** | Stone debris (shared) | Polish layer for the guardian and boss. |
| **P3** | Boss attack effect integration | Boss already has some effect sprites; this is alignment work. |
| **P4** | Speed lines for sheep/dog | Nice to have. Procedural, no art needed. |

---

## 9. Summary Table

| Enemy | Needs Effect Sprite? | Effect File | Dimensions | Frames |
|-------|---------------------|-------------|-----------|--------|
| possessed_sheep | No (body is weapon) | -- | -- | -- |
| rival_warrior | **Yes** | `rival_warrior_spear_thrust.png` | 96x16 | 4 |
| stone_guardian | **Yes** | `stone_guardian_arm_sweep.png` | 288x24 | 6 |
| legionary | **Yes** | `legionary_gladius_stab.png` | 48x16 | 3 |
| war_dog | No (body is weapon) | -- | -- | -- |
| **Shared** | | `anticipation_glow.png` | 16x8 | 2 |
| **Shared** | | `stone_debris.png` | 24x8 | 3 |

**Total new sprites: 5 sheets** (3 enemy-specific, 2 shared).
**Total new frames: 18 frames** across all sheets.

---

*Prepared by En Biel (Game Director), 2026-04-27.*
*References: Super Metroid, Castlevania IV, Mega Man X, Shadow of the Colossus.*
