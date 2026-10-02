#!/usr/bin/env python3
"""Convert YouTube auto-caption VTT files to deduped, timestamped plain text.

Usage: python vtt_to_text.py <work dir>

Why this is not optional: YouTube auto-captions are rolling. Every cue repeats the
previous line, so a raw VTT is roughly three times the real text and unreadable.
We keep the first appearance of each line in order and stamp a timecode every
minute, so any quote stays traceable to a point in the video.

Writes <work>/txt/<id>.txt (with a title header) and <work>/index.json.
"""
import io
import json
import os
import re
import sys

TAG = re.compile(r"<[^>]+>")
TS = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.\d{3}\s+-->")
SKIP = ("WEBVTT", "Kind:", "Language:", "NOTE")


def decode(path):
    """yt-dlp writes cp1252 on Windows. Assuming UTF-8 throws on the first smart quote."""
    raw = open(path, "rb").read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", "replace")


def vtt_to_text(path, stamp_every=60):
    out, seen = [], set()
    cur_t, last_block = 0, -1
    for line in decode(path).splitlines():
        line = line.strip()
        if not line:
            continue
        m = TS.match(line)
        if m:
            h, mi, s = (int(g) for g in m.groups())
            cur_t = h * 3600 + mi * 60 + s
            continue
        if line.startswith(SKIP) or line.isdigit():
            continue
        clean = TAG.sub("", line).strip()
        for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&#39;", "'"), ("&quot;", '"')):
            clean = clean.replace(a, b)
        clean = re.sub(r"\s+", " ", clean)
        if not clean or clean in seen:      # the rolling-caption dedupe
            continue
        seen.add(clean)
        block = cur_t // stamp_every
        if block != last_block:
            out.append("\n[%02d:%02d] " % divmod(cur_t, 60))
            last_block = block
        out.append(clean + " ")
    return "".join(out).strip()


def load_meta(work):
    meta = {}
    p = os.path.join(work, "videos.txt")
    if not os.path.exists(p):
        return meta
    raw = open(p, "rb").read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue
    for line in text.splitlines():
        p2 = line.split("|", 3)
        if len(p2) == 4:
            meta[p2[0]] = {"dur": p2[1], "views": p2[2], "title": p2[3]}
    return meta


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else "."
    vtt_dir, txt_dir = os.path.join(work, "vtt"), os.path.join(work, "txt")
    os.makedirs(txt_dir, exist_ok=True)
    meta = load_meta(work)

    n, total, index = 0, 0, []
    for fn in sorted(os.listdir(vtt_dir)):
        if not fn.endswith(".en.vtt"):
            continue
        vid = fn[: -len(".en.vtt")]
        body = vtt_to_text(os.path.join(vtt_dir, fn))
        m = meta.get(vid, {})
        try:
            mins = "%.0f" % (float(m.get("dur", 0)) / 60)
        except Exception:
            mins = "?"
        header = ("TITLE: %s\nVIDEO: https://www.youtube.com/watch?v=%s\n"
                  "LENGTH: %s min | VIEWS: %s\n%s\n\n"
                  % (m.get("title", "(unknown)"), vid, mins, m.get("views", "?"), "-" * 60))
        with io.open(os.path.join(txt_dir, vid + ".txt"), "w", encoding="utf-8") as f:
            f.write(header + body + "\n")
        n += 1
        total += len(body)
        index.append({"id": vid, "title": m.get("title", "(unknown)"),
                      "minutes": mins, "views": m.get("views", "?"), "chars": len(body)})

    with io.open(os.path.join(work, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)

    print("converted:   %d transcripts" % n)
    print("total chars: {:,}".format(total))
    print("est. words:  {:,}".format(total // 6))


if __name__ == "__main__":
    main()
