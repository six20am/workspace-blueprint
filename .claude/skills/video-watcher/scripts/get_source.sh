#!/usr/bin/env bash
# get_source.sh <input> <outdir> <need:audio|video>
# Local path -> echoes it back unchanged.
# URL -> downloads via yt-dlp. need=audio grabs mp3; need=video grabs <=720p mp4.
# Prints the resulting local media path on stdout; all yt-dlp noise goes to stderr.
set -euo pipefail

INPUT="${1:?usage: get_source.sh <input> <outdir> <audio|video>}"
OUTDIR="${2:?missing outdir}"
NEED="${3:-audio}"
mkdir -p "$OUTDIR"

if [[ "$INPUT" =~ ^https?:// ]]; then
  command -v yt-dlp >/dev/null || { echo "ERROR: yt-dlp not installed; cannot fetch URL" >&2; exit 1; }
  if [[ "$NEED" == "video" ]]; then
    yt-dlp --quiet --no-warnings --no-progress -f "bv*[height<=720]+ba/b[height<=720]/b" \
           --merge-output-format mp4 \
           -o "$OUTDIR/source.%(ext)s" "$INPUT" >&2
    ls "$OUTDIR"/source.* 2>/dev/null | grep -viE '\.(vtt|srt)$' | head -1
  else
    yt-dlp --quiet --no-warnings --no-progress -x --audio-format mp3 \
           -o "$OUTDIR/source.%(ext)s" "$INPUT" >&2
    ls "$OUTDIR"/source.mp3 2>/dev/null | head -1
  fi
else
  [[ -f "$INPUT" ]] || { echo "ERROR: file not found: $INPUT" >&2; exit 1; }
  echo "$INPUT"
fi
