#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="lost_in_space_colorize-portable"
STAGE="$(mktemp -d)"
DESTINATION="${1:-$ROOT/dist}"

cleanup() {
    rm -rf "$STAGE"
}
trap cleanup EXIT

mkdir -p "$STAGE/$PACKAGE_NAME" "$DESTINATION"
rsync -a \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude '.cache/' \
    --exclude '.colorize.lock' \
    --exclude '.env.local' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '*.log' \
    --exclude '.DS_Store' \
    --exclude 'dist/' \
    --exclude 'input/*' \
    --exclude 'output/*' \
    --exclude 'live_previews/*' \
    --exclude 'models/*.pth' \
    --exclude 'models/*.pt' \
    --exclude 'keyframes/' \
    --exclude 'references/' \
    "$ROOT/" "$STAGE/$PACKAGE_NAME/"

mkdir -p "$STAGE/$PACKAGE_NAME/input" "$STAGE/$PACKAGE_NAME/output" \
    "$STAGE/$PACKAGE_NAME/live_previews" "$STAGE/$PACKAGE_NAME/models"

# Los bancos canónicos forman parte de la configuración reproducible.
mkdir -p "$STAGE/$PACKAGE_NAME/references"
for canon_bank in season2_canon season3_canon; do
    if [[ -d "$ROOT/references/$canon_bank" ]]; then
        rsync -a "$ROOT/references/$canon_bank/" \
            "$STAGE/$PACKAGE_NAME/references/$canon_bank/"
    fi
done
for canon_index_file in README.md canon_index.json; do
    if [[ -f "$ROOT/references/$canon_index_file" ]]; then
        cp "$ROOT/references/$canon_index_file" \
            "$STAGE/$PACKAGE_NAME/references/$canon_index_file"
    fi
done

DESTINATION="$(cd "$DESTINATION" && pwd)"
ARCHIVE="$DESTINATION/$PACKAGE_NAME.zip"
if [[ -e "$ARCHIVE" ]]; then
    unlink "$ARCHIVE"
fi
(cd "$STAGE" && /usr/bin/zip -qry "$ARCHIVE" "$PACKAGE_NAME")
echo "Paquete creado: $ARCHIVE"
