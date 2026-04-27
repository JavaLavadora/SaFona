#!/usr/bin/env bash
# Sa Fona — Quick launch / restart script
# Usage:
#   ./run.sh                     # Launch from current branch (master)
#   ./run.sh --level world1/level_1_2   # Start at a specific level
#   ./run.sh --branch fix/my-feature    # Checkout branch first, then launch
#   ./run.sh --worktree agent-abc123    # Run from a worktree
#
# The script kills any running instance, force-compiles all levels,
# then launches the game. Port 6080 for VNC.

set -e

REPO_DIR="/home/jovyan/projects/SaFona"

# ── Pre-flight: check display packages ──────────────────────────
MISSING_CMDS=()
command -v Xvfb >/dev/null 2>&1 || MISSING_CMDS+=(Xvfb)
command -v x11vnc >/dev/null 2>&1 || MISSING_CMDS+=(x11vnc)
[[ -d /usr/share/novnc ]] || MISSING_CMDS+=(novnc)

if [[ ${#MISSING_CMDS[@]} -gt 0 ]]; then
    echo "Error: Missing display packages: ${MISSING_CMDS[*]}"
    echo "Run ./setup_display.sh first (VM was likely reset)."
    exit 1
fi
LEVEL=""
BRANCH=""
WORKTREE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --level|-l)   LEVEL="$2"; shift 2 ;;
        --branch|-b)  BRANCH="$2"; shift 2 ;;
        --worktree|-w) WORKTREE="$2"; shift 2 ;;
        -h|--help)
            head -8 "$0" | tail -7 | sed 's/^# //'
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Determine working directory
if [[ -n "$WORKTREE" ]]; then
    WORK_DIR="$REPO_DIR/.claude/worktrees/$WORKTREE"
    if [[ ! -d "$WORK_DIR" ]]; then
        echo "Error: worktree '$WORKTREE' not found at $WORK_DIR"
        exit 1
    fi
    echo "Using worktree: $WORKTREE"
else
    WORK_DIR="$REPO_DIR"
fi

cd "$WORK_DIR"

# Switch branch if requested
if [[ -n "$BRANCH" ]]; then
    echo "Switching to branch: $BRANCH"
    git checkout "$BRANCH" 2>&1
fi

echo "Working directory: $(pwd)"
echo "Branch: $(git branch --show-current)"

# Kill any running game instance
pkill -f "python -m sa_fona.main" 2>/dev/null && echo "Killed previous instance" || true
sleep 1

# Ensure display services are running
pgrep -f Xvfb > /dev/null 2>&1 || (Xvfb :99 -screen 0 1152x648x24 & sleep 0.5)
pgrep -f x11vnc > /dev/null 2>&1 || (x11vnc -display :99 -nopw -forever -shared -rfbport 5900 & sleep 0.5)
pgrep -f websockify > /dev/null 2>&1 || (websockify --web /usr/share/novnc 6080 localhost:5900 &)

# Force-compile all levels
echo "Compiling levels..."
conda run -n safona python -c "
from sa_fona.level.map_compiler import compile_all_maps
compile_all_maps()
" 2>&1 | grep -v "^$" || true

# Also force-compile any map that has a newer yaml/map than json
for mapfile in sa_fona/data/levels/world*/level_*.map; do
    dir=$(dirname "$mapfile")
    base=$(basename "$mapfile" .map)
    yaml="$dir/${base}.yaml"
    json="$dir/${base}.json"
    if [[ -f "$yaml" ]]; then
        conda run -n safona python tools/map_to_json.py "$mapfile" "$yaml" -o "$json" 2>&1 | grep -v "^$" || true
    fi
done
echo "Compilation done."

# Build launch command
CMD="python -m sa_fona.main"
if [[ -n "$LEVEL" ]]; then
    CMD="$CMD --level $LEVEL"
fi

# Launch
echo "Launching game..."
echo "Connect: http://localhost:6080/vnc.html (port 6080)"
DISPLAY=:99 conda run -n safona $CMD &
echo "Game PID: $!"
echo "Ready."
