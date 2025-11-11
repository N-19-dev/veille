#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND="$ROOT_DIR/backend"
FRONTEND="$ROOT_DIR/frontend"

cd "$BACKEND"

: "${WEEK_OFFSET:=0}"
echo "[run_all] WEEK_OFFSET=${WEEK_OFFSET}"
python3 main.py

# Copier les exports vers le front
mkdir -p "$FRONTEND/public"
rm -rf "$FRONTEND/public/export"
cp -R "$BACKEND/export" "$FRONTEND/public/"

echo "[run_all] Exports copiés vers frontend/public/export"

if [[ "${START_DEV:-0}" == "1" ]]; then
  cd "$FRONTEND"
  npm install
  npm run dev
fi