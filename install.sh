#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_BASE="https://huggingface.co/piddnad/DDColor-models/resolve/main"
MODEL_SIZE="large"

if [[ "${1:-}" == "--tiny-only" ]]; then
    MODEL_SIZE="tiny"
elif [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: ./install.sh [--tiny-only]"
    exit 0
elif [[ $# -gt 0 ]]; then
    echo "Usage: ./install.sh [--tiny-only]"
    exit 2
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This installer is designed for macOS."
    exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install it from https://brew.sh and run this installer again."
    exit 1
fi

echo "[1/6] Checking Python, FFmpeg, Git, and curl..."
brew install python@3.12 ffmpeg git curl

PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Python 3.12 was not found after installation."
    exit 1
fi

echo "[2/6] Creating the local virtual environment..."
"$PYTHON_BIN" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --upgrade pip setuptools wheel

echo "[3/6] Installing Python dependencies..."
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/requirements-runtime.txt"

echo "[4/6] Checking DDColor..."
if [[ ! -f "$ROOT/DDColor/ddcolor/model.py" ]]; then
    git clone --depth 1 https://github.com/piddnad/DDColor.git "$ROOT/DDColor"
fi

mkdir -p "$ROOT/models" "$ROOT/input" "$ROOT/output" \
    "$ROOT/live_previews" "$ROOT/.cache"

download_model() {
    local filename="$1"
    local destination="$ROOT/models/$filename"
    if [[ -s "$destination" ]]; then
        echo "Model already present: $filename"
        return
    fi
    echo "Downloading $filename..."
    curl -fL --retry 4 --retry-delay 3 \
        "$MODEL_BASE/$filename" -o "$destination.part"
    mv "$destination.part" "$destination"
}

echo "[5/6] Downloading the DDColor model..."
if [[ "$MODEL_SIZE" == "tiny" ]]; then
    download_model "ddcolor_paper_tiny.pth"
else
    download_model "ddcolor_modelscope.pth"
fi

if [[ ! -f "$ROOT/.env.local" ]]; then
    cat > "$ROOT/.env.local" <<EOF
LIS_INPUT_DIR="$ROOT/input"
LIS_OUTPUT_DIR="$ROOT/output"
EOF
fi

chmod +x "$ROOT/colorize.sh" "$ROOT/install.sh" "$ROOT/crear_paquete.sh" \
    "$ROOT/Instalar.command" 2>/dev/null || true

echo "[6/6] Running diagnostics..."
"$ROOT/.venv/bin/python" - <<'PY'
import cv2
import numpy
import torch
from pathlib import Path

root = Path.cwd()
print(f"Python/Torch: {torch.__version__}")
print(f"OpenCV: {cv2.__version__}; NumPy: {numpy.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")
PY
ffmpeg -version | head -n 1

echo
echo "Installation complete."
echo "1. Place MKV files in: $ROOT/input"
echo "2. Run: $ROOT/colorize.sh -all --mode balanced --sample-step 6"
