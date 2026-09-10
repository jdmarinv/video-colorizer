#!/usr/bin/env bash
# Lost in Space - Local Batch Video Colorizer
# Zero LLM token usage. Runs 100% locally on Apple Silicon Metal GPU.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$DIR/.venv/bin/python"

if [ -f "$DIR/.env.local" ]; then
    # Installation-specific directory configuration.
    set -a
    source "$DIR/.env.local"
    set +a
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: the virtual environment was not found at $DIR/.venv"
    exit 1
fi

exec "$VENV_PYTHON" "$DIR/colorize_episode.py" "$@"
