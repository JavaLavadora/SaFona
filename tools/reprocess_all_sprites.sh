#!/usr/bin/env bash
# Reprocess all AI source images through the updated sprite pipeline.
# Usage: conda activate safona && bash tools/reprocess_all_sprites.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 1: Process Ramon sprites (directory mode) ==="
python tools/process_ramon_ai_sprites.py \
    --source-dir assets/ai_sources/ramon \
    --output-dir assets/sprites/ramon \
    --frame-width 48 --frame-height 64

echo ""
echo "=== Phase 2: Process characters with per-animation sources (directory mode) ==="

echo "--- stone_guardian ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/stone_guardian assets/sprites/enemies \
    --frame-width 48 --frame-height 64 \
    --mapping stone_guardian_idle:2 stone_guardian_walk:3 \
              stone_guardian_attack:2 stone_guardian_hit:1 \
              stone_guardian_death:1

echo "--- rival_warrior ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/rival_warrior assets/sprites/enemies \
    --frame-width 32 --frame-height 48 \
    --mapping rival_warrior_idle:2 rival_warrior_walk:4 \
              rival_warrior_attack:2 rival_warrior_block:1 \
              rival_warrior_hit:1 rival_warrior_death:2

echo "--- possessed_sheep ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/possessed_sheep assets/sprites/enemies \
    --frame-width 32 --frame-height 32 \
    --mapping "sheep_idle>possessed_sheep_idle:2" \
              "sheep_walk>possessed_sheep_walk:4" \
              "sheep_charge>possessed_sheep_charge:2" \
              "sheep_hit>possessed_sheep_hit:1" \
              "sheep_death>possessed_sheep_death:1"

echo "--- boss_bou_de_pedra ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/boss_bou_de_pedra assets/sprites/boss \
    --frame-width 80 --frame-height 72 \
    --mapping "es_bou_de_pedra_idle_1_image>bou_idle_p1:4" \
              "es_bou_de_pedra_idle_2_image>bou_idle_p2:4" \
              "es_bou_de_pedra_idle_3_image>bou_idle_p3:4" \
              "es_bou_de_pedra_rush_attack_image>bou_rush:2" \
              "es_bou_de_pedra_headbutt_image>bou_headbutt:2" \
              "es_bou_de_pedra_stomp_image>bou_stomp:2" \
              "es_bou_de_pedra_hurl_image>bou_hurl:1" \
              "es_bou_de_pedra_stunned_image>bou_stunned:1" \
              "es_bou_de_pedra_transition_image>bou_transition:1" \
              "es_bou_de_pedra_death_image>bou_death:2"

echo "--- npc_dimoni (idle only, other poses via config) ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/npc_dimoni assets/sprites/npcs \
    --frame-width 48 --frame-height 80 \
    --mapping dimoni_idle:1

echo "--- npc_llorencc ---"
python tools/process_ai_sprites.py \
    assets/ai_sources/npc_llorencc assets/sprites/npcs \
    --frame-width 40 --frame-height 72 \
    --mapping "llorenc_idle>llorencc_idle:4" \
              "llorenc_talk>llorencc_talk:4" \
              "llorenc_shop>llorencc_shop:2"

echo ""
echo "=== Phase 3: Process remaining sprites (config mode) ==="
python tools/process_ai_sprites.py tools/process_all_sprites_config.json

echo ""
echo "=== Phase 4: Clean character sprites (with outline) ==="
for sprite in assets/sprites/ramon/*.png assets/sprites/enemies/*.png assets/sprites/boss/*.png assets/sprites/npcs/*.png; do
    if [ -f "$sprite" ]; then
        palette="ramon"
        if [[ "$sprite" == *"boss/"* ]]; then
            palette="boss"
        elif [[ "$sprite" == *"enemies/"* ]]; then
            palette="enemies"
        elif [[ "$sprite" == *"npcs/"* ]]; then
            palette="npcs"
        fi
        if [ ! -f "assets/palettes/${palette}.gpl" ]; then
            palette="ramon"
        fi
        if [ -f "assets/palettes/${palette}.gpl" ]; then
            echo "  Cleaning (outline ON): $sprite [palette: $palette]"
            python tools/clean_sprites.py "$sprite" --palette "$palette" --output "$sprite" || true
        else
            echo "  SKIP (no palette): $sprite"
        fi
    fi
done

echo ""
echo "=== Phase 5: Clean environment sprites (no outline) ==="
for sprite in assets/sprites/breakables/*.png assets/sprites/pickups/*.png assets/sprites/projectiles/*.png; do
    if [ -f "$sprite" ]; then
        palette="world1"
        if [ ! -f "assets/palettes/${palette}.gpl" ]; then
            palette="ramon"
        fi
        if [ -f "assets/palettes/${palette}.gpl" ]; then
            echo "  Cleaning (outline OFF): $sprite [palette: $palette]"
            python tools/clean_sprites.py "$sprite" --palette "$palette" --no-outline --output "$sprite" || true
        else
            echo "  SKIP (no palette): $sprite"
        fi
    fi
done

echo ""
echo "=== Done! ==="
echo "Review the output sprites in assets/sprites/ and assets/portraits/"
