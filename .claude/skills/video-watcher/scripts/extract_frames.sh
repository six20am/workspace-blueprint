#!/usr/bin/env bash
# extract_frames.sh <video> <framedir> <interval_seconds>
# Samples 1 frame every <interval> seconds, downscaled to <=768px wide to save tokens.
# frame_00001.jpg ~ t=0, frame_00002.jpg ~ t=interval, ... => timestamp ~ (index-1)*interval.
# Prints the number of frames written on stdout.
set -euo pipefail

VIDEO="${1:?usage: extract_frames.sh <video> <framedir> <interval_seconds>}"
FRAMEDIR="${2:?missing framedir}"
INTERVAL="${3:-2}"
mkdir -p "$FRAMEDIR"

# fps = 1/interval frames per second
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" \
  -vf "fps=1/${INTERVAL},scale='min(768,iw)':-2" -q:v 4 \
  "$FRAMEDIR/frame_%05d.jpg"

ls "$FRAMEDIR"/frame_*.jpg 2>/dev/null | wc -l
