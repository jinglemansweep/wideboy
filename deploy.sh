#!/usr/bin/env bash
set -euo pipefail

PI_HOST="${1:-}"
PI_DIR="${2:-~/wideboy}"

if [ -z "$PI_HOST" ]; then
    echo "Usage: $0 <pi-host> [remote-dir]"
    echo "  e.g. $0 pi@192.168.1.100"
    echo "       $0 pi@192.168.1.100 /opt/wideboy"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

rsync -avz --delete \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='.ruff_cache/' \
    --exclude='.mypy_cache/' \
    --exclude='wideboy.egg-info/' \
    --exclude='.git/' \
    --exclude='.direnv/' \
    --exclude='.envrc' \
    --exclude='shell.nix' \
    --exclude='secrets.yml' \
    --exclude='settings.local.yml' \
    --exclude='plans/' \
    "$SCRIPT_DIR/" \
    "$PI_HOST:$PI_DIR/"

echo "Synced to $PI_HOST:$PI_DIR"
