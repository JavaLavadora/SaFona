# Balchar Sprite Generation Prompt

Used to generate the AI reference image for all Balchar animations.
Source image: `assets/example_with_sprite_guide.png`
Processing script output: `assets/sprites/balchar/` (idle, walk, jump, wall_slide, wall_jump, sling)

## Prompt

Pixel art sprite sheet of a Balearic slinger warrior character, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced, all the same character at the same scale:

1) Idle standing pose facing right
2) Walk cycle frame — left leg forward, right arm forward, facing right
3) Walk cycle frame — right leg forward, left arm forward, facing right
4) Jump ascending — crouched body, arms raised, facing right
5) Jump descending — body extended, arms out to sides, facing right
6) Wall slide — body pressed against wall on left side, arms reaching up, facing left
7) Sling wind-up — right arm pulled back behind head swinging sling in a circle, body leaning back, facing right
8) Sling release — right arm extended forward after throwing, body lunging forward, sling cord stretched out, facing right

Character design: medium-length dark hair swept backwards held by a cloth headband, deeply tanned olive skin, knee-length white robe/tunic with V-neck showing chest, bright red sash/belt at waist, leather brown arm bracers on forearms, bare tanned legs visible below the robe, leather sandals, holding a sling with dangling cord. Stocky determined warrior. Clean pixel art, no anti-aliasing, no smoothing. Each pose should be clearly separated with green space between them. All poses must be the SAME character with identical colors and proportions.

## Processing Notes (v1)

- Green background removed via chroma key (g - r > 40 and g - b > 40 and g > 80)
- 8 poses detected by finding vertical gaps in alpha channel
- Poses 7 and 8 (sling) split at density valley around column 1270
- All poses scaled uniformly based on idle height (245px -> 30px, factor ~0.1224)
- Placed in 24x32 frames: centered horizontally, bottom-aligned (feet anchored)
- Alpha hard-thresholded: < 100 = transparent, >= 100 = fully opaque
- Idle animation: 4 frames via 1px upper-body shift (breathing bob)
- Walk animation: 6 frames cycling walk_a / idle / walk_b
- Sling frames saved separately for future attack animation integration

## Processing Notes (v2 — tools/process_balchar_sprites.py)

- New AI image (assets/ai_sources/balchar/image.png): 1536x1024, 9 actual poses on green background
- 7 top-level regions detected; rightmost (x=879..1507, w=628) split by density into 3 sling sub-poses
- Poses: idle, 4 walk frames, jump ascending, sling wind-up, sling mid-rotation, sling release
- Jump descending synthesized from jump ascending (1px shift down)
- Wall slide synthesized from idle (horizontal flip + 1px shift up)
- Scale factor: 0.1435 (idle 209px -> 30px target)
- Walk: 4 base frames -> 8-frame cycle [0, 1, 2, 3, 2, 1, 0, 1]
- Sling: 3 frames (wind-up, mid-rotation, release)
- Idle: 4 frames (breathing bob at 62% waist line)
- All sheets: 24x32 frames, RGBA, NEAREST scaling, alpha hard-threshold at 100
