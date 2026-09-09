#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
chmod +x install.sh colorize.sh crear_paquete.sh
./install.sh "$@"
echo
read -r -p "Presiona Enter para cerrar..."
