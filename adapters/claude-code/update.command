#!/bin/bash
cd "$(dirname "$0")"
PY="$(command -v python3.12 || command -v python3 || true)"
if [ -z "$PY" ]; then
  echo "Python is not installed yet. Run setup.command first."
  read -r -p "Press Return to close."
  exit 1
fi
"$PY" tools/update/update.py
echo
read -r -p "Press Return to close."
