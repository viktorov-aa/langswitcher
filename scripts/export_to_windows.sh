#!/usr/bin/env bash
set -euo pipefail

DEST_DIR="/mnt/d/projects/IT/03.LangSwitcher/langswitcher"

if [[ "$DEST_DIR" == "<SET_DESTINATION_DIRECTORY>" ]]; then
  echo "Error: set destination directory in scripts/export_to_windows.sh (DEST_DIR)." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is required. Install it in WSL (e.g. sudo apt install rsync)." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$DEST_DIR"

rsync -a --delete \
  --exclude='.*' \
  "$PROJECT_ROOT"/ "$DEST_DIR"/

echo "Export complete: $PROJECT_ROOT -> $DEST_DIR"
