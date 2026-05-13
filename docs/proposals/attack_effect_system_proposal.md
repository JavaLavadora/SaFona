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

## 7. AI Sprite Generation Prompts

The following prompts are ready to paste into an AI image generator. Each follows the format established in `tools/sprite_defs/ramon_ai_prompt.md`.

---

### 7.1 Rival Warrior Spear Thrust Effect

**File:** `assets/sprites/effects/rival_warrior_spear_thrust.png`
**Dimensions:** 96x16 (4 frames, each 24x16)

```
Pixel art sprite sheet of a stone spear thrust attack effect for a 2D platformer,
16-bit SNES style, on a solid bright green (#00FF00) background.

Show exactly 4 frames in a single horizontal row, each frame 24x16 pixels, evenly
spaced with green gaps between them. All frames show the same spear weapon from the
same angle, at different stages of a thrust attack, pointing RIGHT.

Frame 1 — ANTICIPATION: A small bright warm glow (3x3 pixels, white center #FFF0D0,
orange edge #FFA040) at the left side of the frame. This represents the energy
gathering before the strike. Rest of frame is empty/transparent.

Frame 2 — MID-THRUST: A stone-tipped spear at 60% extension pointing right. The
spear tip is a rough stone point (4x3 pixels, grey #969697 with dark edge #646469).
The wooden shaft trails behind it (brown #8C6428, 2px wide). A 2-pixel motion blur
line trails behind the tip in light grey (#C0C0C0).

Frame 3 — FULL THRUST: The spear fully extended across the frame pointing right.
Stone tip at the far right edge with a 1-pixel bright highlight (#E0D8C8) on the
leading point. Full wooden shaft visible. Small bright spark (1px white) at the
very tip. This is the main attack frame — the spear should look sharp and dangerous.

Frame 4 — RETRACT: The spear pulling back to the left, only the tip and partial
shaft visible, rendered at roughly 50% opacity/faded. Tip near center of frame.

Style: Clean pixel art, no anti-aliasing, no smoothing. Stone tip should look rough
and chipped like hand-knapped flint. Wooden shaft is simple and straight. Consistent
with 16-bit SNES era (think Castlevania IV skeleton spear). Each frame must be clearly
separated with bright green (#00FF00) space between them.

Color palette:
- Stone tip: #969697 (base), #646469 (dark edge), #B0B0B5 (highlight)
- Wood shaft: #8C6428 (base), #6E4E1E (shadow)
- Anticipation glow: #FFF0D0 (center), #FFA040 (edge)
- Motion blur: #C0C0C0 at 60% opacity
- Spark: #FFFFFF
```

---

### 7.2 Stone Guardian Arm Sweep Effect

**File:** `assets/sprites/effects/stone_guardian_arm_sweep.png`
**Dimensions:** 288x24 (6 frames, each 48x24)

```
Pixel art sprite sheet of a heavy stone arm sweep attack effect for a 2D platformer,
16-bit SNES style, on a solid bright green (#00FF00) background.

Show exactly 6 frames in a single horizontal row, each frame 48x24 pixels, evenly
spaced with green gaps between them. All frames show stages of a massive stone golem
arm sweeping horizontally from left to right.

Frame 1 — WIND-UP GLOW: A faint green glow cluster (6x6 pixels) on the left side
of the frame, pulsing energy color (#50C850 base, #78FF78 bright center). Small dust
motes (1-pixel grey dots) scattered around it. Rest of frame empty. This represents
magical energy gathering in the golem's fist.

Frame 2 — ARM RAISE: A stone arm and fist extending upward-right at ~45 degrees from
the left side. The arm is made of rough grey stone blocks (forearm ~6x14 pixels, fist
~8x8 pixels). Stone colors: dark grey #505055 base, mid grey #828285 highlights,
light grey #969697 for top surfaces. Faint green cracks along the arm (#50C850, 1px
lines). Small stone chips (2x2 pixels, grey) beginning to fly off.

Frame 3 — SWEEP START: The arm now horizontal, starting its sweep from left. Leading
edge of the fist has a bright white-to-grey motion trail (3 pixels wide gradient,
#E0E0E0 to #808085). Stone chips (2x2 grey pixels) flying upward from the fist.
The arm extends about 60% across the frame.

Frame 4 — FULL SWEEP: The massive arm sweeps across the ENTIRE 48-pixel width of the
frame. This is the main danger frame. The stone arm and heavy fist fill the middle
band. A thick motion blur trail behind it (6px wide, white #E0E0E0 fading to grey
#808085). Impact debris — small grey squares (2x2 pixels, #646469) — scatter above
and below the sweep line. The fist should look heavy and crushing.

Frame 5 — SWEEP END: The arm at the far right, decelerating. Motion trail fading
(thinner, more transparent). A dust cloud (cluster of 4-5 light grey pixels #B0B0B0)
at the terminus on the right side. The arm is losing momentum.

Frame 6 — DISSIPATE: No arm visible. Only lingering effects: 3-4 small grey pixel
clusters (2x2, #828285) at various positions representing settling debris and dust.
A few single-pixel dust motes. Frame is mostly empty — the attack is over.

Style: Clean pixel art, no anti-aliasing, no smoothing. The stone arm should look
like it is made of ancient rough-hewn limestone blocks, consistent with a talayotic
stone golem. Heavy, weighty feel — think SNES boss arm attacks (Castlevania IV stone
golem, Mega Man X Sting Chameleon tongue). Each frame clearly separated with bright
green (#00FF00) gaps.

Color palette:
- Stone base: #505055 (dark), #828285 (mid), #969697 (light)
- Green glow (magical): #50C850 (base), #78FF78 (bright)
- Motion trail: #E0E0E0 (bright) fading to #808085 (mid)
- Debris: #646469 (dark grey chunks)
- Dust: #B0B0B0 (light grey particles)
- Moss patches on arm: #465537 (dark green), #5A7846 (green)
```

---

### 7.3 Legionary Gladius Stab Effect

**File:** `assets/sprites/effects/legionary_gladius_stab.png`
**Dimensions:** 48x16 (3 frames, each 16x16)

```
Pixel art sprite sheet of a Roman gladius sword stab attack effect for a 2D
platformer, 16-bit SNES style, on a solid bright green (#00FF00) background.

Show exactly 3 frames in a single horizontal row, each frame 16x16 pixels, evenly
spaced with green gaps between them. All frames show a Roman short sword (gladius)
during a forward stab attack, pointing RIGHT.

Frame 1 — BLADE FLASH: The gladius blade drawn back, catching light. A bright
metallic glint (2x2 pixels, white #F0E8D8) on a small straight blade shape (3x8
pixels, iron grey #C0B8A8 with darker edge #908880). The blade points slightly
upward-right. A warm leather handle visible at the left (dark brown #503820, 2x3
pixels). This is the wind-up moment.

Frame 2 — FULL STAB: The gladius fully extended forward to the right. Clean
horizontal straight blade (4x10 pixels), iron grey #C0B8A8 body with a sharp 1-pixel
bright edge (#E0D8C8) along the top and a 1-pixel leading tip highlight (white
#F0E8D8). The blade should look disciplined and efficient — a straight Roman military
weapon, not a curved fantasy sword. Small metallic spark (1 pixel, white) at the
very tip. Leather-wrapped handle at the far left.

Frame 3 — RETRACT: The blade pulling back to the left, only the tip and partial
blade visible at roughly 50% visual presence (fainter, fewer detail pixels). Tip
near the center of the frame. The stab is ending.

Style: Clean pixel art, no anti-aliasing, no smoothing. The gladius should be
historically inspired — short, straight, double-edged, with a simple cross-guard.
Think Roman legionary equipment rendered in 16-bit SNES style. Each frame clearly
separated with bright green (#00FF00) gaps.

Color palette:
- Blade: #C0B8A8 (iron grey body), #E0D8C8 (bright edge), #908880 (shadow edge)
- Handle: #503820 (dark leather), #6B4E30 (leather highlight)
- Cross-guard: #A09080 (bronze-tinted grey)
- Metallic highlight/spark: #F0E8D8 to #FFFFFF
```

---

### 7.4 Anticipation Glow (Shared)

**File:** `assets/effects/anticipation_glow.png`
**Dimensions:** 16x8 (2 frames, each 8x8)

```
Pixel art sprite sheet of a small energy glow anticipation effect for a 2D
platformer, 16-bit SNES style, on a solid bright green (#00FF00) background.

Show exactly 2 frames in a single horizontal row, each frame 8x8 pixels, evenly
spaced with green gaps between them. This is a tiny pulsing glow that appears before
an enemy attack — a universal "about to strike" warning signal.

Frame 1 — GLOW DIM: A small warm glow dot in the center of the frame. Inner 2x2
pixels are warm white (#FFF0D0). Surrounding ring of 1-pixel orange (#FFA040) on
the 4 cardinal directions. Subtle — this is the "charging" state.

Frame 2 — GLOW BRIGHT: Same glow dot, brighter and slightly larger. Inner 2x2
pixels are bright white (#FFFFFF). Surrounding 8 pixels (cardinal + diagonal) are
bright orange (#FFB850). One additional ring of 1-pixel dim orange (#CC8030) on the
outer cardinals. This is the "about to fire" pulse.

Style: Clean pixel art, no anti-aliasing, no smoothing. Should read as a small
magical/energy charge point. Warm color temperature (orange/gold family). Each frame
clearly separated with bright green (#00FF00) gaps.
```

---

### 7.5 Stone Debris (Shared)

**File:** `assets/effects/stone_debris.png`
**Dimensions:** 24x8 (3 frames, each 8x8)

```
Pixel art sprite sheet of small stone debris particles for a 2D platformer,
16-bit SNES style, on a solid bright green (#00FF00) background.

Show exactly 3 frames in a single horizontal row, each frame 8x8 pixels, evenly
spaced with green gaps between them. This shows stone chunks scattering after a
heavy impact — used for stone golem attacks and boss arena destruction.

Frame 1 — BURST: 4-5 small stone chunks (each 2x2 pixels) clustered near center,
just beginning to scatter outward. Colors: dark grey #646469, mid grey #828285.
One chunk slightly lighter #969697 for variety. Chunks are angular, not round.

Frame 2 — SCATTER: The same chunks now spread further apart, moving outward from
center. 2-3 chunks near the edges of the frame. 1-2 single-pixel dust motes
(light grey #B0B0B0) appearing between chunks.

Frame 3 — SETTLE: Only 1-2 chunks remain visible near the bottom of the frame,
"landing." 2-3 single-pixel dust motes scattered. Most of the energy is gone.
Nearly empty frame — the debris has dispersed.

Style: Clean pixel art, no anti-aliasing, no smoothing. Stone chunks should look
like rough limestone fragments — angular, not smooth. Consistent with Mediterranean
ancient stone construction. Each frame clearly separated with bright green (#00FF00)
gaps.

Color palette:
- Stone chunks: #646469 (dark), #828285 (mid), #969697 (light)
- Dust motes: #B0B0B0 (single pixels)
```

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
