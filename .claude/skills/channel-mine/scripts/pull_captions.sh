#!/usr/bin/env bash
# Pull auto-captions for every video in <work>/videos.txt.
#
# Usage: bash pull_captions.sh "<work dir>" [reverse]
#
# Idempotent: skips ids already on disk. Run it twice in the background, once
# plain and once with "reverse", and the two workers walk the list from opposite
# ends, meet in the middle and roughly halve wall-clock. Do NOT add a third:
# YouTube rate limiting is real and a throttled run costs more than it saves.
set -u

WORK="${1:?usage: pull_captions.sh <work dir> [reverse]}"
DIR="${2:-forward}"
cd "$WORK" || exit 1
mkdir -p vtt logs

if [ "$DIR" = "reverse" ]; then
  LIST="videos_rev.txt"
  TAG="rev"
  tac videos.txt > "$LIST"
else
  LIST="videos.txt"
  TAG="fwd"
fi

TOTAL=$(wc -l < videos.txt)
N=0; OK=0; FAIL=0

while IFS='|' read -r vid dur views title; do
  N=$((N + 1))
  [ -z "$vid" ] && continue
  if [ -s "vtt/${vid}.en.vtt" ]; then           # already have it (or the other worker did)
    OK=$((OK + 1)); continue
  fi
  # --sub-langs "en" not "en.*": the latter also grabs en-orig, doubling the bytes
  # for an identical file.
  yt-dlp --quiet --no-warnings --no-progress --skip-download \
    --write-auto-subs --write-subs --sub-langs "en" --sub-format vtt \
    --sleep-requests 1 \
    -o "vtt/%(id)s.%(ext)s" "https://www.youtube.com/watch?v=$vid" \
    >>"logs/pull-${TAG}.log" 2>&1
  if [ -s "vtt/${vid}.en.vtt" ]; then
    OK=$((OK + 1))
  else
    FAIL=$((FAIL + 1))
    echo "$vid|$title" >> "logs/failed-${TAG}.txt"   # no captions; normal, keep going
  fi
  [ $((N % 25)) -eq 0 ] && echo "progress: $N/$TOTAL ok=$OK fail=$FAIL" >> "logs/progress-${TAG}.txt"
done < "$LIST"

echo "DONE ${TAG}: seen=$N ok=$OK fail=$FAIL" >> "logs/progress-${TAG}.txt"
