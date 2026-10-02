#!/usr/bin/env bash
# try_captions.sh <url> <outdir>
# Attempts to pull existing (human or auto) English captions via yt-dlp WITHOUT downloading video.
# Prints a .vtt path on stdout if captions were found; prints nothing (exit 0) if none exist.
set -euo pipefail

URL="${1:?usage: try_captions.sh <url> <outdir>}"
OUTDIR="${2:?missing outdir}"
mkdir -p "$OUTDIR"

command -v yt-dlp >/dev/null || { echo "yt-dlp not installed" >&2; exit 0; }

yt-dlp --quiet --no-warnings --no-progress --write-subs --write-auto-subs \
       --sub-langs "en.*,en" --sub-format vtt \
       --skip-download \
       -o "$OUTDIR/caps.%(ext)s" "$URL" >&2 2>&1 || true

ls "$OUTDIR"/caps*.vtt 2>/dev/null | head -1
