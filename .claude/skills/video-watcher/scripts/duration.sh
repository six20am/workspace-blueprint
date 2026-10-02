#!/usr/bin/env bash
# duration.sh <media>  -> prints duration in whole seconds (for the Mode B length guard)
set -euo pipefail
IN="${1:?usage: duration.sh <media>}"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN" | awk '{printf "%d\n", $1}'
