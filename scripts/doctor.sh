#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: $PYTHON_BIN is required but was not found." >&2
  exit 1
fi

"$PYTHON_BIN" checks/standards_check.py
"$PYTHON_BIN" checks/surface_activation_check.py
"$PYTHON_BIN" checks/repository_index_check.py
