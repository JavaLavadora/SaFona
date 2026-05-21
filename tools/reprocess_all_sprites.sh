#!/usr/bin/env bash
# Reprocess all AI source images through the updated sprite pipeline.
# Usage: conda activate safona && bash tools/reprocess_all_sprites.sh
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 1: Process all characters ==="
for config in tools/sprite_defs/characters/*.json; do
    echo "--- $(basename $config .json) ---"
    python tools/process_character_sprites.py "$config"
done

echo ""
echo "=== Phase 2: Process remaining sprites (config mode) ==="
python tools/process_ai_sprites.py tools/process_all_sprites_config.json

echo ""
echo "=== Phase 3: Clean character sprites (with outline) ==="
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
echo "=== Phase 4: Clean environment sprites (no outline) ==="
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
