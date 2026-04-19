# World 1 -- Asset Generation Guide

**Na Margalida (Graphic Designer)**

Instructions for generating all pixel art assets for World 1 (Sa Talaia) of Sa Fona. This document covers every graphic needed: player, companion, enemies, boss, NPCs, pickups, breakables, tilesets, UI elements, dialogue portraits, and effects.

---

## How to Use

1. For each asset below, use the provided prompt with your AI image generator (e.g., Midjourney, DALL-E, Stable Diffusion)
2. Drop the resulting image as `image.png` in the specified folder under `assets/ai_sources/`
3. Check the box when the image has been generated and placed
4. Once all (or a batch) are complete, ask the team to run the processing scripts to extract sprite sheets
5. Processing scripts will handle: green-screen removal, pose detection, scaling, frame extraction, and palette correction

## General Prompt Rules

All prompts share these requirements:
- **Style**: 16-bit pixel art, SNES era aesthetic
- **Background**: Solid bright green (#00FF00) for chroma-key removal
- **No anti-aliasing**: Clean pixel edges, no smoothing, no sub-pixel blending
- **Consistency**: All poses of the same character must have identical colors, proportions, and style
- **Separation**: Each pose/tile must be clearly separated with green space between them
- **Orientation**: Characters face RIGHT by default (left-facing is generated via code flip)

---

## Asset Checklist

### 1. Player -- Ramon

- [ ] **Ramon Movement & Combat Animations** -- `assets/ai_sources/ramon/image.png`

  > Pixel art sprite sheet of a Balearic slinger warrior character, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced, all the same character at the same scale:
  >
  > 1) Idle standing pose facing right
  > 2) Walk cycle -- RIGHT leg forward in a large stride, left arm swinging forward, facing right
  > 3) Walk cycle -- legs passing (both legs close together underneath body, upright), facing right
  > 4) Walk cycle -- LEFT leg forward in a large stride, right arm swinging forward, facing right
  > 5) Walk cycle -- legs passing again (both legs together, slightly different arm position), facing right
  > 6) Jump ascending -- crouched body, arms raised, facing right
  > 7) Jump descending -- body extended, arms out to sides, facing right
  > 8) Wall slide -- body pressed flat as if sliding down a surface, arms reaching up, legs together, facing left. DO NOT draw any wall or surface -- only the character in the sliding pose against empty green background
  > 9) Fona sling wind-up -- right arm raised HIGH above head swinging a long rope sling (fona) in a CIRCLE overhead, body leaning slightly, cord visible making an arc above the head, facing right
  > 10) Fona sling mid-rotation -- arm still overhead, sling cord at a different position in the circular rotation (showing the spinning motion), facing right
  > 11) Fona sling release -- right arm fully extended FORWARD, body lunging, sling cord stretched straight out releasing the stone, facing right
  > 12) Taking damage -- body recoiling backward, arms up defensively, pained expression, facing right
  > 13) Death/defeated -- collapsed on ground, face down, limbs splayed, facing right
  >
  > Character design: medium-length dark hair swept backwards held by a cloth headband, deeply tanned olive skin, knee-length white robe/tunic with V-neck showing chest, bright red sash/belt at waist, leather brown arm bracers on forearms, bare tanned legs visible below the robe, leather sandals, holding a fona (Balearic sling -- a long braided cord with a pouch, NOT a Y-shaped slingshot). Stocky determined warrior. Perpetually unimpressed expression. Clean pixel art, no anti-aliasing, no smoothing. Each pose should be clearly separated with green space between them. All poses must be the SAME character with identical colors and proportions. The LEGS must be clearly different between walk poses -- exaggerate the stride.

  *Will generate sprite sheets*:
  - `idle.png` -- 4 frames (24x32 each) -- breathing bob generated from pose 1
  - `walk.png` -- 6-8 frames (24x32) -- cycling poses 2-5
  - `jump.png` -- 2 frames (24x32) -- ascending (pose 6) and descending (pose 7)
  - `wall_slide.png` -- 2 frames (24x32) -- from pose 8
  - `wall_jump.png` -- 2 frames (24x32) -- derived from jump ascending + directional flip
  - `sling.png` -- 3 frames (24x32) -- wind-up, mid-rotation, release (poses 9-11)
  - `hit.png` -- 1-2 frames (24x32) -- from pose 12
  - `death.png` -- 1-2 frames (24x32) -- from pose 13

  *Frame dimensions*: 24x32 pixels per frame (matching `PLAYER_WIDTH=24`, `PLAYER_HEIGHT=32`)
  *Notes*: This is the v3 prompt, extending v2 with hit and death poses. Existing v2 sprites in `assets/sprites/ramon/` cover poses 1-11 but lack hit/death.

---

### 2. Companion -- Bep (Myotragus)

- [ ] **Bep Animations** -- `assets/ai_sources/bep/image.png`

  > Pixel art sprite sheet of a small prehistoric goat-like creature (myotragus balearicus), 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced, all the same creature at the same scale:
  >
  > 1) Idle standing -- small round body, stubby forward-curving horns, large expressive eyes looking upward happily, short legs, woolly texture, facing right
  > 2) Idle variant -- same pose but head tilted slightly, one ear flicked, curious expression
  > 3) Idle chewing -- mouth open slightly, chewing motion, content expression
  > 4) Idle sleeping -- eyes closed, head drooped, tiny z's optional
  > 5) Walk cycle frame 1 -- right legs forward, body bouncing slightly, facing right
  > 6) Walk cycle frame 2 -- legs passing, body at normal height, facing right
  > 7) Walk cycle frame 3 -- left legs forward, body bouncing slightly, facing right
  > 8) Walk cycle frame 4 -- legs passing again, facing right
  > 9) Jump -- all four legs tucked under body, slight upward arc, startled wide eyes
  > 10) Scared/startled -- body low, ears back, wide frightened eyes, trembling pose
  > 11) Excited -- body bouncing up, ears perked forward, happy wide eyes, mouth open
  > 12) Faint glow aura -- same idle pose but with a subtle magical glow outline around the body (curse effect)
  >
  > Creature design: very small (fits in a 16x16 pixel box), round compact body with short woolly brown-grey fur, two small forward-curving horns on top of head, large dark expressive eyes (the most prominent feature), tiny hooves, short stubby tail. Looks like a sheep-goat hybrid -- cute and round. The creature should look lovable and slightly hapless. Clean pixel art, no anti-aliasing, no smoothing. Each pose clearly separated with green space.

  *Will generate sprite sheets*:
  - `idle.png` -- 4 frames (16x16) -- breathing/ear flick cycle from poses 1-4
  - `walk.png` -- 4 frames (16x16) -- poses 5-8
  - `jump.png` -- 1 frame (16x16) -- pose 9
  - `scared.png` -- 1 frame (16x16) -- pose 10
  - `excited.png` -- 1 frame (16x16) -- pose 11
  - `glow.png` -- 1 frame (16x16) -- pose 12

  *Frame dimensions*: 16x16 pixels per frame (matching `COMPANION_WIDTH=16`, `COMPANION_HEIGHT=16`)
  *Notes*: Currently only `idle.png` exists (4 frames). Walk, jump, and expression variants are needed for full companion behavior.

---

### 3. Enemies

#### 3a. Possessed Sheep

- [ ] **Possessed Sheep Animations** -- `assets/ai_sources/possessed_sheep/image.png`

  > Pixel art sprite sheet of a corrupted demonic sheep, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced:
  >
  > 1) Idle -- standing sheep with glowing red eyes, slightly hunched aggressive stance, dark wool with a faint reddish-purple aura, facing right
  > 2) Idle variant -- same but head lowered slightly, eyes pulsing brighter
  > 3) Walk frame 1 -- right legs forward, aggressive trot, facing right
  > 4) Walk frame 2 -- legs passing, facing right
  > 5) Walk frame 3 -- left legs forward, facing right
  > 6) Walk frame 4 -- legs passing, facing right
  > 7) Charge tell -- body lowered, hooves digging in, eyes blazing, about to charge, facing right
  > 8) Charging -- body lunging forward, legs stretched in full gallop, head lowered like a battering ram, facing right
  > 9) Hit/damaged -- recoiling, eyes flickering, facing right
  > 10) Death -- collapsing sideways, red glow fading, eyes dimming
  >
  > Design: a normal Mediterranean sheep but corrupted by dimoni energy. White-grey wool tinged darker, glowing red eyes (the key visual indicator of possession), slight reddish-purple aura around the body. Small horns. Approximately 16x16 pixels when scaled. Clean pixel art, no anti-aliasing.

  *Will generate sprite sheets*:
  - `possessed_sheep_idle.png` -- 2 frames (16x16) -- poses 1-2
  - `possessed_sheep_walk.png` -- 4 frames (16x16) -- poses 3-6
  - `possessed_sheep_charge_tell.png` -- 1 frame (16x16) -- pose 7
  - `possessed_sheep_charge.png` -- 1 frame (16x16) -- pose 8
  - `possessed_sheep_hit.png` -- 1 frame (16x16) -- pose 9
  - `possessed_sheep_death.png` -- 1 frame (16x16) -- pose 10

  *Frame dimensions*: 16x16 pixels (hitbox w=16, h=16)
  *Notes*: Existing sprites cover idle (2f) and walk (4f). Need charge tell, charge, hit, and death animations.

#### 3b. Rival Tribal Warrior

- [ ] **Rival Warrior Animations** -- `assets/ai_sources/rival_warrior/image.png`

  > Pixel art sprite sheet of a hostile talayotic tribal warrior, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced:
  >
  > 1) Idle -- standing warrior in a combat-ready stance, holding a stone club, wearing a leather tunic and arm wrappings, tanned skin, dark hair, facing right
  > 2) Idle variant -- slight weight shift, club position adjusted
  > 3) Walk frame 1 -- stepping forward aggressively, club at ready, facing right
  > 4) Walk frame 2 -- mid-stride, facing right
  > 5) Walk frame 3 -- stepping with other leg, facing right
  > 6) Walk frame 4 -- completing stride, facing right
  > 7) Attack tell -- club raised high overhead, body coiled to strike, menacing expression
  > 8) Attack swing -- club swung downward in a powerful arc, body extended
  > 9) Blocking -- arms crossed in front with club held horizontally as a shield, defensive crouch
  > 10) Hit/stunned -- recoiling backward, dazed expression, club lowered
  > 11) Death -- falling backward, club dropping, defeated
  >
  > Design: a rival warrior from a competing talayotic tribe. Slightly taller and leaner than Ramon. Leather tunic (darker brown), leather arm wrappings, stone club weapon, messy dark hair, war paint stripes on face. Hostile but clearly human -- not a monster. Approximately 16 wide x 24 tall pixels when scaled. Clean pixel art, no anti-aliasing.

  *Will generate sprite sheets*:
  - `rival_warrior_idle.png` -- 2 frames (16x24) -- poses 1-2
  - `rival_warrior_walk.png` -- 4 frames (16x24) -- poses 3-6
  - `rival_warrior_attack_tell.png` -- 1 frame (16x24) -- pose 7
  - `rival_warrior_attack.png` -- 1 frame (16x24) -- pose 8
  - `rival_warrior_block.png` -- 1 frame (16x24) -- pose 9
  - `rival_warrior_hit.png` -- 1 frame (16x24) -- pose 10
  - `rival_warrior_death.png` -- 1 frame (16x24) -- pose 11

  *Frame dimensions*: 16x24 pixels (hitbox w=16, h=24)
  *Notes*: Existing sprites cover idle (2f) and walk (4f). Need attack, block, hit, and death animations. The block animation is important because this enemy has a 30% block chance.

#### 3c. Stone Guardian

- [ ] **Stone Guardian Animations** -- `assets/ai_sources/stone_guardian/image.png`

  > Pixel art sprite sheet of a large animated stone golem/guardian, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced:
  >
  > 1) Idle -- massive humanoid figure made of rough-hewn dark grey limestone blocks, glowing amber cracks between stone segments, standing imposingly with heavy stone fists, facing right
  > 2) Idle variant -- slight shift, amber glow pulsing
  > 3) Walk frame 1 -- heavy lumbering step, right leg forward, ground impact feel, facing right
  > 4) Walk frame 2 -- mid-stride, both legs close, facing right
  > 5) Walk frame 3 -- left leg forward, heavy step, facing right
  > 6) Attack tell -- right arm raised high, amber cracks blazing brighter, body winding up for a massive overhead strike
  > 7) Attack swing -- arm smashing downward, body lunging, shockwave implied at the strike point
  > 8) Hit/stunned -- cracks flickering, body rocking backward, small stone chips flying off
  > 9) Death/crumbling -- body breaking apart into stone chunks, amber glow fading, collapsing
  >
  > Design: a talayotic stone guardian animated by ancient dimoni energy. Made of stacked rough limestone blocks in a humanoid shape. Dark grey stone body with glowing amber/orange energy visible in the cracks between stone segments. No face -- just a vaguely head-shaped stone block on top. Very heavy and slow-looking. Approximately 24 wide x 32 tall pixels when scaled. Clean pixel art, no anti-aliasing.

  *Will generate sprite sheets*:
  - `stone_guardian_idle.png` -- 2 frames (24x32) -- poses 1-2
  - `stone_guardian_walk.png` -- 3 frames (24x32) -- poses 3-5
  - `stone_guardian_attack_tell.png` -- 1 frame (24x32) -- pose 6
  - `stone_guardian_attack.png` -- 1 frame (24x32) -- pose 7
  - `stone_guardian_hit.png` -- 1 frame (24x32) -- pose 8
  - `stone_guardian_death.png` -- 1 frame (24x32) -- pose 9

  *Frame dimensions*: 24x32 pixels (hitbox w=24, h=32)
  *Notes*: Existing sprites cover idle (2f) and walk (3f). Need attack tell, attack, hit, and death animations. Attack tell is particularly important (1.0s tell time gives the player time to react).

---

### 4. Boss -- Es Bou de Pedra (The Stone Bull)

- [ ] **Bou de Pedra Boss Sprite Sheet** -- `assets/ai_sources/boss_bou_de_pedra/image.png`

  > Pixel art sprite sheet of a massive stone bull boss, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row, evenly spaced:
  >
  > 1) Idle Phase 1 -- massive bull made of dark grey stacked limestone, amber energy cracks glowing between stone segments, standing tall and imposing, hooves planted, facing right. Grey stone color.
  > 2) Idle Phase 2 -- same bull but stone is now orange-tinted, cracks glowing brighter, more agitated stance, small rocks floating near body
  > 3) Idle Phase 3 -- same bull but stone is now red-tinted, visible glowing red core exposed in the chest area, cracks blazing with energy, most aggressive stance
  > 4) Bull Rush tell -- body lowered, front hooves scraping ground, head down with horns forward, energy building, about to charge
  > 5) Bull Rush charging -- body stretched in full gallop, head lowered like a battering ram, dust trail behind, horizontal motion blur feel
  > 6) Headbutt tell -- head pulling back, horns glowing
  > 7) Headbutt strike -- head thrust forward, horns impact
  > 8) Ground Stomp tell -- front hooves raised high
  > 9) Ground Stomp impact -- hooves slamming down, shockwave rings at ground level
  > 10) Rock Hurl -- rearing up on hind legs, tossing rocks from back/horns upward
  > 11) Stunned/punish -- dazed, leaning to one side, stars/swirls around head, amber glow dimmed, briefly vulnerable
  > 12) Phase transition -- body glowing intensely white, stone cracking and reforming, energy surge
  > 13) Defeated -- crumbling apart, amber energy dissipating, stone chunks falling, collapsing
  >
  > Design: Es Bou de Pedra is a giant stone bull inspired by talayotic bronze-age bull worship figurines. Built from rough-hewn Mediterranean limestone blocks in the shape of a charging bull. Massive curved stone horns. Glowing amber/orange energy visible in cracks between stone segments (this is dimoni energy animating it). No organic features -- purely stone and magical energy. The exposed core (Phase 3) is a glowing red weak point in the chest. Approximately 40 wide x 36 tall pixels when scaled. Clean pixel art, no anti-aliasing.

  *Will generate sprite sheets*:
  - `boss_bou_idle_p1.png` -- 2 frames (40x36) -- pose 1 with breathing bob
  - `boss_bou_idle_p2.png` -- 2 frames (40x36) -- pose 2 with more agitated animation
  - `boss_bou_idle_p3.png` -- 2 frames (40x36) -- pose 3 with core pulsing
  - `boss_bou_rush_tell.png` -- 1 frame (40x36) -- pose 4
  - `boss_bou_rush.png` -- 2 frames (40x36) -- pose 5 running cycle
  - `boss_bou_headbutt.png` -- 2 frames (40x36) -- poses 6-7
  - `boss_bou_stomp.png` -- 2 frames (40x36) -- poses 8-9
  - `boss_bou_hurl.png` -- 1 frame (40x36) -- pose 10
  - `boss_bou_stunned.png` -- 2 frames (40x36) -- pose 11
  - `boss_bou_transition.png` -- 1 frame (40x36) -- pose 12
  - `boss_bou_defeated.png` -- 2 frames (40x36) -- pose 13

  *Frame dimensions*: 40x36 pixels (hitbox w=40, h=36)
  *Notes*: Currently rendered as colored placeholder rectangles (grey/orange/red per phase). This is the most complex sprite in W1.

---

### 5. Boss Arena Elements

#### 5a. Destructible Pillars

- [ ] **Arena Pillar** -- `assets/ai_sources/boss_pillar/image.png`

  > Pixel art of a tall stone pillar for a boss arena, 16-bit SNES style, on a solid bright green (#00FF00) background. Show two versions side by side:
  >
  > 1) Intact pillar -- a tall ancient talayotic stone column, rough-hewn Mediterranean limestone, slightly wider at top (capstone), carved with faint bull motifs, approximately 16 wide x 48 tall pixels
  > 2) Destroyed pillar -- same pillar but shattered: broken base stub remaining, stone chunks scattered, dust cloud, rubble on ground
  >
  > Design: ancient talayotic construction, warm grey limestone with subtle ochre undertones, consistent with the World 1 tileset palette. Clean pixel art, no anti-aliasing.

  *Will generate*:
  - `pillar_intact.png` -- 1 frame (16x48)
  - `pillar_destroyed.png` -- 1 frame (16x48) or destruction animation frames

  *Frame dimensions*: 16x48 pixels (1 tile wide x 3 tiles tall, matching `TILE_SIZE * 3`)
  *Notes*: Currently rendered as brown rectangles. Four pillars exist in the boss arena.

#### 5b. Boss Projectiles

- [ ] **Boss Projectile Sprites** -- `assets/ai_sources/boss_projectiles/image.png`

  > Pixel art sprite sheet of boss attack projectiles, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following items in a single horizontal row:
  >
  > 1) Rock projectile -- a small rough stone chunk, grey limestone, tumbling through the air, approximately 8x8 pixels
  > 2) Shockwave -- a horizontal energy wave, amber/yellow, semi-transparent feel, ground-level blast, approximately 16x8 pixels
  > 3) Core pulse -- a circular red energy wave expanding outward, menacing red glow, approximately 24x16 pixels
  > 4) Shadow marker -- a dark elliptical shadow on the ground indicating where a rock will land, approximately 16x6 pixels
  >
  > Clean pixel art, no anti-aliasing. Each item clearly separated.

  *Will generate*:
  - `boss_rock.png` -- 1 frame (8x8)
  - `boss_shockwave.png` -- 1 frame (16x8)
  - `boss_pulse.png` -- 1 frame (24x16)
  - `boss_shadow.png` -- 1 frame (16x6)

  *Notes*: Currently all rendered as basic geometric shapes (circles, rectangles with alpha).

---

### 6. NPCs

#### 6a. Llorencc (Shop NPC)

- [ ] **Llorencc Sprite** -- `assets/ai_sources/npc_llorencc/image.png`

  > Pixel art sprite sheet of a friendly talayotic warrior-scholar NPC, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row:
  >
  > 1) Standing idle -- slightly taller than Ramon, similar bronze-age clothing but with a leather satchel slung across chest full of scrolls and artifacts. Holding a scroll in one hand. Friendly smile. Dark hair, tanned skin, leather tunic, sandals. Facing right.
  > 2) Talking/excited -- same character, hands animated (one gesturing, one holding artifact), mouth open, enthusiastic expression
  > 3) Showing wares -- arms spread, displaying items, shopkeeper pose
  >
  > Character design: Llorencc is a talayotic warrior from Menorca who doubles as a scholar/collector. Slightly taller and leaner than Ramon. Wears a leather tunic (lighter brown than rival warriors), leather satchel/bag always visible, often holding a scroll or artifact. Friendly enthusiastic expression (contrast to Ramon's grumpiness). Clean pixel art, no anti-aliasing. Approximately 20 wide x 36 tall pixels when scaled.

  *Will generate*:
  - `npc_llorencc_idle.png` -- 1 frame (20x36)
  - `npc_llorencc_talk.png` -- 1 frame (20x36)
  - `npc_llorencc_shop.png` -- 1 frame (20x36)

  *Frame dimensions*: 20x36 pixels (matching `_NPC_WIDTH=20`, `_NPC_HEIGHT=36`)
  *Notes*: Currently rendered as a green rectangle with "L" label. Llorencc appears at save points and shop locations. Bruna (his cow companion) is a future nice-to-have.

#### 6b. Dimoni de Sant Joan (Cutscene NPC)

- [ ] **Dimoni de Sant Joan Sprite** -- `assets/ai_sources/npc_dimoni/image.png`

  > Pixel art sprite sheet of a traditional Mallorcan dimoni (demon figure), 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following poses in a single horizontal row:
  >
  > 1) Imposing stance -- tall demonic figure with red skin, curving ram-like horns, sharp features, wearing tattered dark robes, holding a trident/pitchfork, fiery aura around body, dramatic pose, facing right
  > 2) Laughing/mocking -- same figure but head thrown back, mouth open in cruel laughter, more fiery aura
  > 3) Granting mask -- arms extended forward, offering a glowing stone mask, solemn/grudging expression
  > 4) Angry/furious -- body tense, horns seeming to glow, fire flaring, face contorted in rage
  >
  > Design: based on the traditional Mallorcan dimoni de Sant Joan figure from the Correfoc festivals. Red skin, ram-like curved horns, sharp angular features, tattered dark red and black robes or loincloth, carries a traditional trident. Fiery aura. NOT a cute demon -- imposing, theatrical, dramatic. But with a hint of personality (this is the original offended dimoni who cursed Bep). Approximately 24 wide x 40 tall pixels when scaled. Clean pixel art, no anti-aliasing.

  *Will generate*:
  - `dimoni_idle.png` -- 1 frame (24x40)
  - `dimoni_laugh.png` -- 1 frame (24x40)
  - `dimoni_grant.png` -- 1 frame (24x40)
  - `dimoni_angry.png` -- 1 frame (24x40)

  *Notes*: The Dimoni appears in the post-boss cutscene (grants Stone Slam mask) and in narrative foreshadowing. Currently only rendered via dialogue box portrait placeholder.

---

### 7. Pickups

#### 7a. Heart Pickup

- [ ] **Heart Pickup Sprite** -- `assets/ai_sources/pickup_heart/image.png`

  > Pixel art of a glowing heart pickup, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 2 frames side by side:
  >
  > 1) Heart normal -- a classic heart shape, bright red with a lighter red highlight at top-left, slight inner glow, clean edges
  > 2) Heart shimmer -- same heart but with a small white sparkle/glint on the highlight area
  >
  > Approximately 12x12 pixels when scaled. Clean pixel art, no anti-aliasing. Classic video game heart pickup feel.

  *Will generate*:
  - `heart.png` -- 2 frames (12x12) for idle shimmer animation

  *Frame dimensions*: 12x12 pixels (matching `PICKUP_WIDTH=12`, `PICKUP_HEIGHT=12`)
  *Notes*: Currently rendered as a red diamond shape. Real heart shape would be a visual upgrade.

#### 7b. Stone Pickup (Currency)

- [ ] **Stone Pickup Sprite** -- `assets/ai_sources/pickup_stone/image.png`

  > Pixel art of a small sling stone currency pickup, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 2 frames side by side:
  >
  > 1) Stone normal -- a small rough round stone, warm grey limestone color with subtle texture variation, slight shadow underneath
  > 2) Stone shimmer -- same stone with a small white glint
  >
  > Approximately 12x12 pixels when scaled. Clean pixel art. Should look like a natural Mediterranean beach pebble -- smooth but not perfectly round.

  *Will generate*:
  - `stone.png` -- 2 frames (12x12) for idle shimmer animation

  *Frame dimensions*: 12x12 pixels
  *Notes*: Currently rendered as a grey circle. These are the primary currency dropped by enemies and breakables.

#### 7c. Shield Orb Pickup (Future)

- [ ] **Shield Orb Sprite** -- `assets/ai_sources/pickup_shield/image.png`

  > Pixel art of a magical shield orb pickup, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 2 frames side by side:
  >
  > 1) Orb normal -- a glowing translucent blue sphere with a shield icon inside, magical sparkles around it
  > 2) Orb pulse -- same orb but slightly brighter, sparkles in different positions
  >
  > Approximately 12x12 pixels when scaled. Clean pixel art. Should look clearly distinct from heart and stone pickups.

  *Will generate*:
  - `shield.png` -- 2 frames (12x12)

  *Notes*: Referenced in the GDD but not yet implemented in code. Generating the art now for future use.

---

### 8. Breakable Objects

#### 8a. Pot

- [ ] **Breakable Pot Sprite** -- `assets/ai_sources/breakable_pot/image.png`

  > Pixel art of a ceramic pot in two states, 16-bit SNES style, on a solid bright green (#00FF00) background. Show side by side:
  >
  > 1) Intact pot -- a round-bodied Mediterranean ceramic pot/amphora, terracotta orange-brown color with a darker rim, simple geometric pattern painted near the top, sitting on ground
  > 2) Broken pot -- same pot but shattered into 4-5 ceramic shards scattered on the ground with dust particles
  >
  > Approximately 16x16 pixels when scaled. Clean pixel art. Should look like a talayotic-era handmade clay pot.

  *Will generate*:
  - `pot.png` -- 1 frame (16x16) intact state
  - `pot_break.png` -- 1-2 frames (16x16) breaking/broken state

  *Frame dimensions*: 16x16 pixels (matching `BREAKABLE_WIDTH=16`, `BREAKABLE_HEIGHT=16`)
  *Notes*: Currently rendered as a brown rectangle. Drop table: 1-3 stones.

#### 8b. Crate

- [ ] **Breakable Crate Sprite** -- `assets/ai_sources/breakable_crate/image.png`

  > Pixel art of a wooden storage crate in two states, 16-bit SNES style, on a solid bright green (#00FF00) background. Show side by side:
  >
  > 1) Intact crate -- a rough wooden box/crate, dark brown weathered wood planks with visible grain, held together with darker wooden crossbars in an X pattern, metal/leather strap corners
  > 2) Broken crate -- same crate but smashed open, wooden planks scattered, splinters flying
  >
  > Approximately 16x16 pixels when scaled. Clean pixel art. Should look like an ancient storage container.

  *Will generate*:
  - `crate.png` -- 1 frame (16x16) intact state
  - `crate_break.png` -- 1-2 frames (16x16) breaking/broken state

  *Frame dimensions*: 16x16 pixels
  *Notes*: Currently rendered as a dark brown rectangle with X lines. Drop table: 2-4 stones.

---

### 9. Player Projectiles

- [ ] **Sling Stone Projectile** -- `assets/ai_sources/projectile_stone/image.png`

  > Pixel art of sling stone projectiles in three charge tiers, 16-bit SNES style, on a solid bright green (#00FF00) background. Show in a horizontal row:
  >
  > 1) Tier 1 stone -- a small rough grey stone in flight, faint motion trail, warm grey color, 8x8 pixels
  > 2) Tier 2 stone -- same stone but glowing faintly orange, brighter motion trail, slightly more polished look
  > 3) Tier 3 stone -- same stone but blazing with white-red energy, dramatic energy trail, the stone itself seems to glow from within
  >
  > Clean pixel art, no anti-aliasing. Each tier should be visually distinct so the player can see their charge level's effect.

  *Will generate*:
  - `stone_tier1.png` -- 1 frame (8x8)
  - `stone_tier2.png` -- 1 frame (8x8)
  - `stone_tier3.png` -- 1 frame (8x8)

  *Frame dimensions*: 8x8 pixels (matching `projectile_width=8`, `projectile_height=8`)
  *Notes*: Currently rendered as a solid warm-grey rectangle for all tiers. Tier-specific visuals would greatly improve combat feedback.

---

### 10. Tilesets

#### 10a. World 1 Outdoor Tileset (Sa Talaia)

- [ ] **W1 Outdoor Tileset** -- `assets/ai_sources/tileset_world1/image.png`

  > Pixel art tileset for a 2D platformer, 16-bit SNES style, on a solid bright green (#00FF00) background. Show exactly 4 tiles in a single horizontal row, evenly spaced, each tile a separate square block:
  >
  > 1) Top surface tile -- grey Mediterranean limestone with short grass/moss on top edge, light warm grey stone body with subtle mortar line texture, small cracks and color variation
  > 2) Inner stone tile -- solid grey limestone block, no grass, visible mortar lines and subtle stone grain, slightly darker than the surface tile
  > 3) Underground/deep tile -- darker grey stone, more worn and cracked, minimal detail, the deepest layer
  > 4) Wall edge tile -- grey stone with slight weathering on one side, transitional tile between exposed surface and inner stone
  >
  > Style: Balearic island Mediterranean terrain. Warm neutral grey stone (NOT blue-grey), subtle ochre undertones. Clean pixel art, no anti-aliasing, no smoothing. Each tile should be clearly separated with green space between them. Consistent lighting from top-left. Stone should look like ancient talayotic construction -- rough-hewn limestone blocks.

  *Will generate*:
  - `tileset.png` -- 256x16 (16 auto-tile variants from 4 base tiles)

  *Tile size*: 16x16 pixels per tile
  *Notes*: An existing tileset exists at `assets/tilesets/world1/tileset.png`. This prompt is the documented reference for regeneration. Processing script: `tools/process_ai_tiles.py`.

#### 10b. World 1 Cave Tileset (Sa Cova des Foner)

- [ ] **W1 Cave Tileset** -- `assets/ai_sources/tileset_world1_cave/image.png`

  > Pixel art tileset for a cave interior in a 2D platformer, 16-bit SNES style, on a solid bright green (#00FF00) background. Show exactly 4 tiles in a single horizontal row, evenly spaced, each tile a separate square block:
  >
  > 1) Cave ceiling/floor tile -- dark grey-brown limestone with stalactite/stalagmite nubs on one edge, damp texture, slightly wet-looking highlights
  > 2) Cave wall tile -- solid dark grey cave rock, rough texture, small crystal or mineral deposits glinting, deeper darkness
  > 3) Deep cave tile -- very dark stone, almost black with subtle dark purple undertones, barely visible texture, the deepest cavern
  > 4) Cave transition tile -- medium grey stone transitioning between cave interior and the outdoor tileset, some moss growing on the cave side
  >
  > Style: underground Mediterranean cave system. Darker and cooler than the outdoor tileset but still warm-toned (NOT blue). Subtle dampness and mineral deposits. Should feel ancient and mysterious. Clean pixel art, no anti-aliasing. Each tile clearly separated.

  *Will generate*:
  - `tileset.png` -- 256x16 (16 auto-tile variants)

  *Tile size*: 16x16 pixels
  *Notes*: Used in Level 1-2 (Sa Cova des Foner -- the Slinger's Cave). Currently uses the default world1 tileset as a placeholder. Needs distinct cave atmosphere.

#### 10c. World 1 Talayot Interior Tileset (Es Talayot Sagrat)

- [ ] **W1 Talayot Tileset** -- `assets/ai_sources/tileset_world1_talayot/image.png`

  > Pixel art tileset for an ancient stone tower interior in a 2D platformer, 16-bit SNES style, on a solid bright green (#00FF00) background. Show exactly 4 tiles in a single horizontal row, evenly spaced, each tile a separate square block:
  >
  > 1) Talayot wall surface tile -- large precisely cut limestone blocks with tight mortar joints, carved with faint ancient symbols (spirals, bull motifs), warm grey stone, moss growing in crevices
  > 2) Talayot inner wall tile -- solid construction stone, larger blocks than outdoor tileset, very precise rectangular cuts (ancient masonry), slight amber tint from torchlight
  > 3) Talayot deep/foundation tile -- the oldest darkest stone at the base of the tower, rough-hewn megalithic blocks, ancient and weathered, dark grey-brown
  > 4) Talayot edge/platform tile -- a carved stone ledge or step, more ornate than raw stone, suitable for wall-jump surfaces and platforms
  >
  > Style: interior of a sacred talayotic tower (talayot). More refined than natural cave or outdoor terrain. Large precisely-cut stone blocks showing advanced Bronze Age masonry. Faint carved decorative elements. Warm torchlit amber undertones. Should feel ancient, sacred, and impressive. Clean pixel art, no anti-aliasing. Each tile clearly separated.

  *Will generate*:
  - `tileset.png` -- 256x16 (16 auto-tile variants)

  *Tile size*: 16x16 pixels
  *Notes*: Used in Level 1-3 (Es Talayot Sagrat -- the Sacred Tower). Vertical level focused on wall-jumping. Currently uses the default world1 tileset as a placeholder.

---

### 11. Backgrounds

- [ ] **W1 Outdoor Background** -- `assets/ai_sources/bg_world1/image.png`

  > Pixel art parallax background for a Mediterranean island landscape, 16-bit SNES style, on a solid bright green (#00FF00) background only where fully transparent areas are needed. The background itself should be a complete scenic image:
  >
  > A wide panoramic view of a Balearic island landscape at golden hour. Far background: pale blue sky fading to warm gold near the horizon, distant Mediterranean sea on one side. Mid background: rolling green hills dotted with ancient stone structures (talayots), olive trees and carob trees, dry stone walls. Near background: rocky limestone outcrops, wild herbs and grasses, a winding dirt path.
  >
  > Style: 16-bit SNES parallax background. Limited color palette with warm Mediterranean tones. The image should tile horizontally for scrolling. Approximately 384x216 pixels (or 320x180). Clean pixel art, painterly at the distance but crisp in foreground elements.

  *Will generate*:
  - `world1_bg.png` -- background layer for parallax scrolling

  *Notes*: Currently no background implemented (levels render on a flat color). The `asset_manifest.json` has an empty `"backgrounds": {}` section. Multiple parallax layers would be ideal but a single layer is the minimum viable asset.

- [ ] **W1 Cave Background** -- `assets/ai_sources/bg_world1_cave/image.png`

  > Pixel art parallax background for a dark cave interior, 16-bit SNES style. A wide view of a deep Mediterranean cave system. Far background: deep darkness with faint blue-purple bioluminescent glow on distant stalactites. Mid background: massive stalactite formations, underground pool reflections, faint mineral sparkles. Near background: cave wall textures, dripping water effects, moss patches.
  >
  > Dark atmospheric palette. Should tile horizontally. Approximately 384x216 pixels. Clean pixel art.

  *Will generate*:
  - `world1_cave_bg.png` -- cave background layer

- [ ] **W1 Talayot Background** -- `assets/ai_sources/bg_world1_talayot/image.png`

  > Pixel art parallax background for the interior of an ancient stone tower, 16-bit SNES style. A wide view looking up inside a massive cylindrical stone tower. Far background: distant ceiling with a shaft of light coming down from above. Mid background: large stone walls with carved spiral patterns and bull symbols, lit by amber torchlight. Near background: stone archways, wall-mounted torch brackets with flickering flames, ancient pottery on ledges.
  >
  > Warm amber torchlit palette. Should tile horizontally. Approximately 384x216 pixels. Clean pixel art.

  *Will generate*:
  - `world1_talayot_bg.png` -- talayot interior background layer

---

### 12. Dialogue Portraits

The dialogue system uses 44x44 pixel portrait boxes. Currently rendered as colored rectangles with initials. Each character needs portrait variants matching the dialogue data's `"portrait"` field values.

#### 12a. Ramon Portraits

- [ ] **Ramon Dialogue Portraits** -- `assets/ai_sources/portrait_ramon/image.png`

  > Pixel art portrait set of Ramon the Balearic slinger, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following face portraits in a single horizontal row, each a square headshot:
  >
  > 1) ramon_neutral -- straight-faced, slightly bored, deadpan expression, facing slightly left (toward the dialogue text)
  > 2) ramon_annoyed -- furrowed brow, slight frown, exasperated, the default Ramon mood
  > 3) ramon_surprised -- eyebrows raised, mouth slightly open, caught off guard
  > 4) ramon_determined -- narrowed eyes, set jaw, ready for battle
  >
  > Character: medium-length dark hair swept back with cloth headband, deeply tanned olive skin, strong jaw, perpetually unimpressed expression as default. Close-up face and upper shoulders only. Each portrait approximately 44x44 pixels. Clean pixel art, no anti-aliasing. Consistent face proportions across all expressions.

  *Will generate*:
  - `ramon_neutral.png` -- 44x44
  - `ramon_annoyed.png` -- 44x44
  - `ramon_surprised.png` -- 44x44
  - `ramon_determined.png` -- 44x44

  *Notes*: Used in `world1_dialogue.json` with portrait values: `"ramon_annoyed"`, `"ramon_neutral"`. Adding surprised and determined for future dialogue.

#### 12b. Bep Portraits

- [ ] **Bep Dialogue Portraits** -- `assets/ai_sources/portrait_bep/image.png`

  > Pixel art portrait set of Bep the myotragus companion, 16-bit SNES style, on a solid bright green (#00FF00) background. Show the following face portraits in a single horizontal row:
  >
  > 1) bep_neutral -- friendly round face, large dark eyes, small forward-curving horns visible, calm expression, facing slightly left
  > 2) bep_excited -- same face but eyes wide and sparkling, mouth open in a happy bleat, ears perked up
  > 3) bep_scared -- eyes huge with fear, ears flattened back, mouth in a worried "O" shape, trembling
  > 4) bep_sleepy -- half-closed droopy eyes, content sleepy smile
  >
  > Character: round face of a small sheep-goat creature, large expressive dark eyes (the dominant feature), two small forward-curving horns on top, woolly brown-grey fur around the face, small ears. The face should be extremely expressive -- Bep's emotions are always dialed up to 11. Each portrait approximately 44x44 pixels. Clean pixel art.

  *Will generate*:
  - `bep_neutral.png` -- 44x44
  - `bep_excited.png` -- 44x44
  - `bep_scared.png` -- 44x44
  - `bep_sleepy.png` -- 44x44

  *Notes*: Used in `world1_dialogue.json` with portrait values: `"bep_excited"`, `"bep_neutral"`, `"bep_scared"`. Most dialogue in W1 is Bep giving hints.

#### 12c. Dimoni Portrait

- [ ] **Dimoni Dialogue Portrait** -- `assets/ai_sources/portrait_dimoni/image.png`

  > Pixel art portrait of Es Dimoni de Sant Joan, 16-bit SNES style, on a solid bright green (#00FF00) background. Show in a horizontal row:
  >
  > 1) dimoni_imposing -- dramatic close-up of the demon's face, red skin, large curved ram horns framing the face, sharp angular features, glowing yellow eyes, cruel confident smirk, fiery aura at edges of frame
  > 2) dimoni_laughing -- same face but mouth wide open in mocking laughter, eyes narrowed with cruel amusement
  > 3) dimoni_grudging -- same face but slight grimace, begrudging respect, one eyebrow raised
  >
  > Each portrait approximately 44x44 pixels. Clean pixel art. The dimoni should look theatrical and imposing -- based on Mallorcan Correfoc festival demon figures.

  *Will generate*:
  - `dimoni_imposing.png` -- 44x44
  - `dimoni_laughing.png` -- 44x44
  - `dimoni_grudging.png` -- 44x44

  *Notes*: Used in the post-boss cutscene dialogue. Speaker is "Dimoni" in `post_boss_w1.json`.

#### 12d. Llorencc Portrait

- [ ] **Llorencc Dialogue Portrait** -- `assets/ai_sources/portrait_llorencc/image.png`

  > Pixel art portrait of Llorencc the Menorcan scholar-warrior NPC, 16-bit SNES style, on a solid bright green (#00FF00) background. Show in a horizontal row:
  >
  > 1) llorencc_friendly -- warm friendly face, slight smile, scholarly look, dark hair, tanned skin, visible satchel strap over shoulder, facing slightly left
  > 2) llorencc_excited -- same face but eyes lit up with enthusiasm, mouth open explaining something, gesturing with one hand visible
  >
  > Each portrait approximately 44x44 pixels. Clean pixel art.

  *Will generate*:
  - `llorencc_friendly.png` -- 44x44
  - `llorencc_excited.png` -- 44x44

  *Notes*: Used in shop dialogue (`llorencc_shop.json`).

---

### 13. UI Elements

#### 13a. HUD Heart Icon

- [ ] **HUD Heart Icons** -- `assets/ai_sources/ui_hearts/image.png`

  > Pixel art of HUD heart icons in three states, 16-bit SNES style, on a solid bright green (#00FF00) background. Show in a horizontal row:
  >
  > 1) Full heart -- a classic red heart shape, filled solid red with a lighter highlight, clean iconic look
  > 2) Half heart -- left half filled red, right half dark/empty with just an outline
  > 3) Empty heart -- just the heart outline in dark red/maroon, interior is dark/transparent
  >
  > Each heart approximately 12x12 pixels. Clean pixel art. These sit in the top-left corner of the screen. Must be readable at small size.

  *Will generate*:
  - `heart_full.png` -- 12x12
  - `heart_half.png` -- 12x12
  - `heart_empty.png` -- 12x12

  *Notes*: Currently rendered as diamond shapes via code. Real heart icons would match classic platformer HUD conventions.

#### 13b. HUD Stone Counter Icon

- [ ] **HUD Stone Icon** -- `assets/ai_sources/ui_stone_icon/image.png`

  > Pixel art of a small stone icon for the HUD counter, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > 1) A tiny sling stone icon, warm grey, round, with a subtle "x" format indicator space next to it
  >
  > Approximately 10x10 pixels. Clean pixel art. Must be readable at tiny size -- sits next to the stone count number.

  *Will generate*:
  - `stone_icon.png` -- 10x10

  *Notes*: Currently a grey circle drawn via code.

#### 13c. Mask HUD Icon

- [ ] **Stone Slam Mask Icon** -- `assets/ai_sources/ui_mask_stone_slam/image.png`

  > Pixel art of the Stone Slam dimoni mask icon for the HUD, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > 1) Active mask -- a small ancient stone mask with amber glowing eyes, carved from limestone, primitive angular design with horn-like protrusions at top, warm golden glow around it
  > 2) Cooldown mask -- same mask but dimmed, grey-toned, amber eyes dark, semi-transparent overlay effect
  >
  > Each approximately 14x14 pixels. Clean pixel art. This represents the Stone Slam mask power in the HUD top-right corner.

  *Will generate*:
  - `mask_stone_slam_active.png` -- 14x14
  - `mask_stone_slam_cooldown.png` -- 14x14

  *Notes*: Currently rendered as a golden/grey square via code (`_MASK_ICON_SIZE=14`).

#### 13d. Dialogue Box Frame

- [ ] **Dialogue Box UI Frame** -- `assets/ai_sources/ui_dialogue_frame/image.png`

  > Pixel art of a dialogue box frame/border as a 9-slice tileable UI element, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > A rectangular frame with: dark blue-black semi-transparent interior, warm golden/bronze ornate border (2-3 pixels wide), slightly rounded corners with small decorative knots or Mediterranean geometric patterns at corners. The frame should be provided as a 9-slice grid: top-left corner, top edge (tileable), top-right corner, left edge (tileable), center (tileable fill), right edge (tileable), bottom-left corner, bottom edge, bottom-right corner.
  >
  > Overall sample frame approximately 64x32 pixels showing all 9 sections. Clean pixel art. The style should evoke ancient Mediterranean craftsmanship.

  *Will generate*:
  - 9-slice dialogue frame pieces for the dialogue box UI

  *Notes*: Currently the dialogue box is rendered with solid color fills and 1px borders via code. A proper 9-slice frame would significantly improve presentation.

#### 13e. Shop UI Frame

- [ ] **Shop UI Frame** -- `assets/ai_sources/ui_shop_frame/image.png`

  > Pixel art of a shop menu frame, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > A larger rectangular frame for the shop overlay. Dark blue-black semi-transparent background, golden/bronze ornate border (matching dialogue box style), tab indicators at top (two tabs: "Items" and "Masks"), cursor arrow indicator, item slot background. Show the frame with placeholder content layout: header area with tabs, scrollable item list area, footer area with stone count.
  >
  > Overall approximately 200x140 pixels showing the full shop layout. Clean pixel art.

  *Will generate*:
  - Shop frame pieces and UI elements

  *Notes*: Currently rendered entirely with code-drawn rectangles and system fonts. A proper UI skin would match the game's Mediterranean aesthetic.

#### 13f. Boss Health Bar Frame

- [ ] **Boss Health Bar UI** -- `assets/ai_sources/ui_boss_health_bar/image.png`

  > Pixel art of a boss health bar frame, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > 1) Health bar frame -- a long horizontal ornate frame for the boss health bar, dark background with golden/bronze borders matching the dialogue box style, carved stone aesthetic, approximately 300x12 pixels
  > 2) Health fill segment -- a tileable red/green/orange fill texture for inside the bar, 1 pixel wide by 8 pixels tall, with slight texture
  > 3) Phase marker -- a small vertical divider line with a tiny diamond or arrow shape
  >
  > Clean pixel art. The health bar sits at the bottom of the screen during boss fights.

  *Will generate*:
  - Boss health bar frame and fill elements

  *Notes*: Currently drawn with basic rectangles and lines via code.

#### 13g. Charge Indicator

- [ ] **Sling Charge Indicator** -- `assets/ai_sources/ui_charge_indicator/image.png`

  > Pixel art of sling charge tier indicators, 16-bit SNES style, on a solid bright green (#00FF00) background. Show in a horizontal row:
  >
  > 1) Tier 1 glow -- a small faint yellow energy bar/circle above the player's head, dim and understated, 12x4 pixels
  > 2) Tier 2 glow -- a brighter orange energy bar, slightly wider (16x4 pixels), more intense
  > 3) Tier 3 glow -- a blazing white-red energy bar, widest (20x4 pixels), with small spark particles, dramatic
  >
  > Clean pixel art. These float above Ramon's head while charging the sling.

  *Will generate*:
  - `charge_tier1.png` -- 12x4
  - `charge_tier2.png` -- 16x4
  - `charge_tier3.png` -- 20x4

  *Notes*: Currently drawn as colored rectangles via code (`_INDICATOR_WIDTH=12`, `_INDICATOR_HEIGHT=4`).

---

### 14. Main Menu & Screens

- [ ] **Title Screen Logo** -- `assets/ai_sources/ui_title/image.png`

  > Pixel art title logo reading "SA FONA", 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > Large decorative text "SA FONA" in a Mediterranean/ancient stone carved style. Letters appear carved from warm limestone with slight 3D depth/bevel effect. Subtle amber glow behind the text. A small silhouette of a sling (fona) integrated into or below the title. Approximately 200x60 pixels. Clean pixel art. The title should feel ancient, warm, and inviting -- like carved stone lit by firelight.

  *Will generate*:
  - `title_logo.png` -- game title graphic

  *Notes*: Currently "Sa Fona" is rendered with a system font. A proper logo would establish the visual identity.

- [ ] **Game Over Screen Elements** -- `assets/ai_sources/ui_game_over/image.png`

  > Pixel art "GAME OVER" text, 16-bit SNES style, on a solid bright green (#00FF00) background:
  >
  > Large dramatic text "GAME OVER" in dark red stone with cracks, crumbling edges. Below it, a small prompt area for "Press any key to restart" in lighter grey stone. Approximately 200x80 pixels total. Clean pixel art.

  *Will generate*:
  - `game_over.png` -- game over screen graphic

  *Notes*: Currently rendered with system font on a dark red background.

---

### 15. Effects & Particles (Nice-to-Have)

These are lower priority visual polish items. Generate these after all essential assets above are complete.

- [ ] **Dust Particles** -- `assets/ai_sources/fx_dust/image.png`

  > Pixel art of small dust/debris particle sprites, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 4-6 tiny dust puff frames in a row, each approximately 4x4 to 8x8 pixels, showing a small dust cloud expanding and fading. Warm grey/brown tones.

  *Will generate*: Dust particle frames for landing, wall-slide, and breakable destruction effects.

- [ ] **Stone Impact Sparks** -- `assets/ai_sources/fx_impact/image.png`

  > Pixel art of impact spark sprites, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 3-4 frames of stone-on-stone impact sparks: initial bright flash (white-yellow), expanding spark lines, fading ember particles. Each frame approximately 12x12 pixels.

  *Will generate*: Impact spark frames for sling hits on enemies and environment.

- [ ] **Dimoni Energy Aura** -- `assets/ai_sources/fx_dimoni_aura/image.png`

  > Pixel art of a pulsing dimoni energy aura effect, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 4 frames of a reddish-purple magical aura: faint glow, medium glow, bright pulse, fading. Each frame approximately 24x24 pixels. Semi-transparent feel (use color to suggest transparency).

  *Will generate*: Aura overlay frames for possessed enemies, boss energy effects, and the Bep curse glow.

- [ ] **Time Portal Effect** -- `assets/ai_sources/fx_portal/image.png`

  > Pixel art of a swirling time portal, 16-bit SNES style, on a solid bright green (#00FF00) background. Show 4 frames of a circular portal: forming (small swirl), growing (medium with energy tendrils), fully open (large with visible distortion inside showing another era), closing. Each frame approximately 48x48 pixels. Blue-purple energy with white light at center.

  *Will generate*: Portal animation frames for the post-W1 boss time-travel cutscene.

---

## Summary Table

| # | Asset | Folder | Priority | Status |
|---|-------|--------|----------|--------|
| 1 | Ramon (13 poses) | `assets/ai_sources/ramon/` | HIGH | Existing v2 covers 11 poses |
| 2 | Bep (12 poses) | `assets/ai_sources/bep/` | HIGH | Existing covers idle only |
| 3a | Possessed Sheep (10 poses) | `assets/ai_sources/possessed_sheep/` | HIGH | Existing covers idle+walk |
| 3b | Rival Warrior (11 poses) | `assets/ai_sources/rival_warrior/` | HIGH | Existing covers idle+walk |
| 3c | Stone Guardian (9 poses) | `assets/ai_sources/stone_guardian/` | HIGH | Existing covers idle+walk |
| 4 | Bou de Pedra Boss (13 poses) | `assets/ai_sources/boss_bou_de_pedra/` | HIGH | None (placeholder rectangles) |
| 5a | Boss Pillar (2 states) | `assets/ai_sources/boss_pillar/` | MEDIUM | None |
| 5b | Boss Projectiles (4 types) | `assets/ai_sources/boss_projectiles/` | MEDIUM | None |
| 6a | Llorencc NPC (3 poses) | `assets/ai_sources/npc_llorencc/` | MEDIUM | None |
| 6b | Dimoni NPC (4 poses) | `assets/ai_sources/npc_dimoni/` | MEDIUM | None |
| 7a | Heart Pickup (2 frames) | `assets/ai_sources/pickup_heart/` | MEDIUM | Existing basic sprite |
| 7b | Stone Pickup (2 frames) | `assets/ai_sources/pickup_stone/` | MEDIUM | Existing basic sprite |
| 7c | Shield Orb (2 frames) | `assets/ai_sources/pickup_shield/` | LOW | Future use |
| 8a | Breakable Pot (2 states) | `assets/ai_sources/breakable_pot/` | MEDIUM | Existing basic sprite |
| 8b | Breakable Crate (2 states) | `assets/ai_sources/breakable_crate/` | MEDIUM | Existing basic sprite |
| 9 | Sling Projectiles (3 tiers) | `assets/ai_sources/projectile_stone/` | MEDIUM | None |
| 10a | W1 Outdoor Tileset | `assets/ai_sources/tileset_world1/` | HIGH | Existing tileset |
| 10b | W1 Cave Tileset | `assets/ai_sources/tileset_world1_cave/` | HIGH | None (using outdoor as fallback) |
| 10c | W1 Talayot Tileset | `assets/ai_sources/tileset_world1_talayot/` | HIGH | None (using outdoor as fallback) |
| 11a | W1 Outdoor Background | `assets/ai_sources/bg_world1/` | MEDIUM | None |
| 11b | W1 Cave Background | `assets/ai_sources/bg_world1_cave/` | MEDIUM | None |
| 11c | W1 Talayot Background | `assets/ai_sources/bg_world1_talayot/` | MEDIUM | None |
| 12a | Ramon Portraits (4) | `assets/ai_sources/portrait_ramon/` | HIGH | None |
| 12b | Bep Portraits (4) | `assets/ai_sources/portrait_bep/` | HIGH | None |
| 12c | Dimoni Portrait (3) | `assets/ai_sources/portrait_dimoni/` | MEDIUM | None |
| 12d | Llorencc Portrait (2) | `assets/ai_sources/portrait_llorencc/` | MEDIUM | None |
| 13a | HUD Hearts (3 states) | `assets/ai_sources/ui_hearts/` | MEDIUM | None |
| 13b | HUD Stone Icon | `assets/ai_sources/ui_stone_icon/` | LOW | None |
| 13c | Mask Icon (2 states) | `assets/ai_sources/ui_mask_stone_slam/` | LOW | None |
| 13d | Dialogue Frame | `assets/ai_sources/ui_dialogue_frame/` | MEDIUM | None |
| 13e | Shop Frame | `assets/ai_sources/ui_shop_frame/` | LOW | None |
| 13f | Boss Health Bar | `assets/ai_sources/ui_boss_health_bar/` | LOW | None |
| 13g | Charge Indicator (3 tiers) | `assets/ai_sources/ui_charge_indicator/` | LOW | None |
| 14a | Title Logo | `assets/ai_sources/ui_title/` | MEDIUM | None |
| 14b | Game Over Screen | `assets/ai_sources/ui_game_over/` | LOW | None |
| 15a | Dust Particles | `assets/ai_sources/fx_dust/` | LOW | None |
| 15b | Impact Sparks | `assets/ai_sources/fx_impact/` | LOW | None |
| 15c | Dimoni Aura | `assets/ai_sources/fx_dimoni_aura/` | LOW | None |
| 15d | Time Portal | `assets/ai_sources/fx_portal/` | LOW | None |

---

## Processing Pipeline

After generating images:

1. Drop `image.png` in the corresponding `assets/ai_sources/<asset_name>/` folder
2. Run the appropriate processing script:
   - **Character/entity sprites**: `tools/process_ai_sprites.py` (green-screen removal, pose detection, scaling, frame extraction)
   - **Tilesets**: `tools/process_ai_tiles.py` (green-screen removal, color correction, auto-tile generation)
   - **Portraits**: Manual crop or dedicated portrait processing script
   - **UI elements**: Manual extraction or 9-slice processor
3. Output goes to the appropriate `assets/sprites/`, `assets/tilesets/`, `assets/portraits/`, or `assets/ui/` directory
4. The game's sprite loading system automatically picks up files from these paths

## Color Palette Reference (World 1)

To maintain visual consistency across all W1 assets:

- **Stone/limestone**: Warm grey with ochre undertones, RGB range (130,112,82) to (215,195,155)
- **Grass/vegetation**: Mediterranean green, RGB range (72,108,50) to (120,155,85)
- **Dimoni energy**: Amber/orange glow, RGB(255,180,50) to RGB(255,220,80)
- **Possessed enemy aura**: Dark reddish-purple, RGB(120,40,60) to RGB(180,60,80)
- **Bronze-age leather**: Warm brown, RGB(139,90,43) to RGB(180,120,60)
- **Ramon's tunic**: White with warm shadow, RGB(220,215,200) to RGB(255,250,240)
- **Ramon's sash**: Bright red, RGB(200,40,40) to RGB(220,60,60)
- **Boss core energy**: Red glow, RGB(255,80,80) with varying alpha
