#!/bin/bash
# Grok Bot installer. Walks setup/tools.json's linux column. Safe to run again; doctor re-runs it.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
  if [ "$(id -u)" = "0" ]; then apt-get install -y python3; else sudo -n apt-get install -y python3; fi
fi
command -v python3 >/dev/null 2>&1 || { echo "python3 is missing and did not install"; exit 4; }
python3 setup/runner.py --platform linux "$@"
