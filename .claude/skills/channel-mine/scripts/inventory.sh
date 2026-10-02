#!/usr/bin/env bash
# Inventory every video on a channel or playlist. Writes <work>/videos.txt as
# id|duration|views|title and prints the totals you need to scope the job.
#
# Usage: bash inventory.sh "<channel or playlist URL>" "<work dir>"
set -u

URL="${1:?usage: inventory.sh <url> <work dir>}"
WORK="${2:?usage: inventory.sh <url> <work dir>}"
mkdir -p "$WORK/logs"

# /videos gets long-form uploads. Pass the URL with an explicit tab to override.
case "$URL" in
  *"/videos"|*"/streams"|*"/shorts"|*"list="*) TARGET="$URL" ;;
  *) TARGET="${URL%/}/videos" ;;
esac

echo "inventorying: $TARGET"

# --quiet --no-warnings --no-progress is mandatory: the workspace hook rejects
# default verbosity and the banner buys nothing.
yt-dlp --quiet --no-warnings --no-progress --flat-playlist \
  --print "%(id)s|%(duration)s|%(view_count)s|%(title)s" \
  "$TARGET" > "$WORK/videos.txt" 2>"$WORK/logs/inventory-err.txt"

if [ ! -s "$WORK/videos.txt" ]; then
  echo "FAILED: no videos returned. See $WORK/logs/inventory-err.txt"
  head -5 "$WORK/logs/inventory-err.txt" 2>/dev/null
  exit 1
fi

"$(command -v python3 || command -v python)" - "$WORK" <<'PY'
import sys, os
work = sys.argv[1]
raw = open(os.path.join(work, "videos.txt"), "rb").read()
for enc in ("utf-8", "cp1252", "latin-1"):      # yt-dlp writes cp1252 on Windows
    try:
        text = raw.decode(enc)
        break
    except Exception:
        continue

rows = []
for line in text.splitlines():
    p = line.split("|", 3)
    if len(p) < 4:
        continue
    try:
        d = float(p[1])
    except Exception:
        d = 0.0
    try:
        v = int(p[2])
    except Exception:
        v = 0
    rows.append((p[0], d, v, p[3]))

if not rows:
    print("no parseable rows")
    raise SystemExit(1)

hours = sum(r[1] for r in rows) / 3600
print("videos:      %d" % len(rows))
print("total hours: %.1f" % hours)
print("total views: {:,}".format(sum(r[2] for r in rows)))
print("median mins: %.1f" % (sorted(r[1] for r in rows)[len(rows) // 2] / 60))

if len(rows) < 20:
    rec = "small: pull captions and read them all"
elif len(rows) <= 80:
    rec = "medium: cluster, read the top half, coverage pass over the rest"
else:
    rec = "large: cluster, sample canonically, lean on the coverage pass"
print("scope:       %s" % rec)
print("est. pull:   ~%d min single worker, ~%d min with two"
      % (len(rows) / 3.5, len(rows) / 7))

print("\n--- top 15 by views ---")
for vid, d, v, t in sorted(rows, key=lambda r: -r[2])[:15]:
    print("  %9s  %4.0fm  %s" % ("{:,}".format(v), d / 60, t[:72]))

print("\n--- 10 most recent (channel order) ---")
for vid, d, v, t in rows[:10]:
    print("  %9s  %4.0fm  %s" % ("{:,}".format(v), d / 60, t[:72]))
print("\nCompare the two lists. If they look like different channels, the corpus")
print("has two eras and the recent one is usually where our knowledge is thinnest.")
PY
