#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

start_generator() {
  python3 "${ROOT_DIR}/backend/scripts/generate_dependency_chart.py" --serve
}

start_ui() {
  python3 -m http.server 8000
}

cleanup() {
  if [[ -n "${GEN_PID:-}" ]]; then
    kill "${GEN_PID}" 2>/dev/null || true
  fi
  if [[ -n "${UI_PID:-}" ]]; then
    kill "${UI_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT

start_generator &
GEN_PID=$!

start_ui &
UI_PID=$!

echo "Generator server: http://127.0.0.1:8765"
echo "UI server: http://localhost:8000/ui/"
echo "Press Ctrl+C to stop both."

wait
