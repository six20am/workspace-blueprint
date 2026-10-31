#!/usr/bin/env python3
"""Corpus-wide coverage pass over every transcript.

Usage: python mine.py <work dir> [--topics "term1,term2,..."] [--show warn|money|pct]

Sampling videos misses anything said once in a video you never opened. This reads
every transcript on disk and surfaces the sentence-level claims worth checking:
money, measured numbers, and warning-shaped language.

Treat the output as POINTERS, NOT FINDINGS. Every creator has verbal tics the
warning regex will catch by the hundred (one channel said "let me break that down"
in almost every video). Filter, expect noise, and use the hits to decide which
videos to open. Never quote from this pass without reading the source in context.

Writes <work>/mined.json.
"""
import io
import json
import os
import re
import sys
from collections import Counter

STAMP = re.compile(r"\[\d{2}:\d{2}\]")

WARN = re.compile(
    r"\b("
    r"biggest mistake|most people (don't|dont|do not)|a lot of people (don't|dont)|"
    r"make sure (you )?(don't|dont|do not)|never do|do not do|don't ever|"
    r"the (only|one) (way|thing)|here's the (trick|secret|thing)|"
    r"nobody (talks about|tells you)|the problem with|"
    r"(will|can|could) get (banned|rejected|denied|declined)|gets? (rejected|denied)|"
    r"will (crash|break|not work)|won't work|doesn't work|does not work|"
    r"you (have to|must|cannot|can't)\b|not allowed|"
    r"be careful|warning|pro tip|cheat code|loophole|workaround"
    r")\b", re.I)

# Drop the creator's own funnel language; it is never a finding.
PROMO = re.compile(
    r"link in the description|affiliate|subscribe|my course|free course|"
    r"bonus|comment below|join (the|our)|community|peace out|like and sub", re.I)

MONEY = re.compile(r"\$\s?[\d,]+(?:\.\d{1,2})?")
PCT = re.compile(r"\b\d{1,3}(?:\.\d+)?\s?%")


def sentences(text):
    text = re.sub(r"\s+", " ", STAMP.sub(" ", text))
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text)
            if 25 < len(s.strip()) < 420]


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())[:80]


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else "."
    topics = None
    if "--topics" in sys.argv:
        topics = [t.strip() for t in sys.argv[sys.argv.index("--topics") + 1].split(",") if t.strip()]
    show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None

    txt_dir = os.path.join(work, "txt")
    files = [f for f in os.listdir(txt_dir) if f.endswith(".txt")]
    feat = Counter()
    buckets = {"money": [], "pct": [], "warn": []}
    seen = {k: set() for k in buckets}

    for fn in files:
        raw = io.open(os.path.join(txt_dir, fn), encoding="utf-8", errors="replace").read()
        lines = raw.split("\n")
        title = lines[0].replace("TITLE: ", "") if lines else fn
        body = "\n".join(lines[4:])
        if topics:
            low = body.lower()
            for t in topics:
                c = low.count(t.lower())
                if c:
                    feat[t] += c
        for s in sentences(body):
            if PROMO.search(s):
                continue
            for key, rx in (("money", MONEY), ("pct", PCT), ("warn", WARN)):
                if rx.search(s):
                    k = norm(s)
                    if k not in seen[key]:
                        seen[key].add(k)
                        buckets[key].append({"id": fn[:-4], "title": title, "text": s})

    with io.open(os.path.join(work, "mined.json"), "w", encoding="utf-8") as f:
        json.dump({"files": len(files), "topics": feat.most_common(), **buckets}, f, indent=1)

    print("transcripts scanned: %d" % len(files))
    print("money: %d | percentages: %d | warning-shaped: %d"
          % (len(buckets["money"]), len(buckets["pct"]), len(buckets["warn"])))
    if feat:
        print("\n--- topic mentions across the corpus ---")
        for k, v in feat.most_common():
            print("  %-22s %5d" % (k, v))
        print("\nCompare this against the channel's own titles. What it talks about")
        print("most is often not what it advertises.")
    if show in buckets:
        print("\n--- %s (deduped, promo filtered) ---" % show)
        for h in buckets[show][:80]:
            print("- [%s]\n    %s\n" % (h["title"][:52], h["text"][:260]))
    else:
        print("\nRe-run with --show warn (or money, pct) to print the hits.")
    print("full output: %s" % os.path.join(work, "mined.json"))


if __name__ == "__main__":
    main()
