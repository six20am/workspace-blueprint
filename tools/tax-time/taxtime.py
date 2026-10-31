"""Gathers one year's tax papers from what is already filed in the workspace into taxes/<year>/, by category,
with a cover sheet and a zip for the accountant. Copies only; nothing is moved, renamed or made up.

    python tools/tax-time/taxtime.py --year 2026 --dry-run        # show the plan, change nothing
    python tools/tax-time/taxtime.py --year 2026                  # copy, write COVER.md, zip
    python tools/tax-time/taxtime.py --year 2026 --also receipts-box --also "S1-admin/old invoices"

A file belongs to the year when its name starts with that year, or, with no date in the name, when it was last
changed in that year. Its category comes from words in its name (see CATEGORIES); the money-log summaries in
money/<year>/ are "Bank summaries". A file already copied (same name and size) is skipped on a second run.

Standard library only. Reads file names and sizes; opens nothing but the files it copies.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKIP_TOP = {"setup", "tools", "_reference", "skills", "taxes"}
SKIP_ANY = {".git", "node_modules", "__pycache__"}
SENT = {"delivery", "delivered", "sent", "out", "3-delivery", "04-delivery", "6-comms", "s6-comms", "invoices-sent", "sent-invoices"}
YEAR_PREFIX = re.compile(r"^(\d{4})(?:-\d{2})?(?:-\d{2})?\b")
# (category, words in the file name); the first match wins, so the specific lines sit above "invoice"
CATEGORIES = [
    ("Tax forms", r"\b1099\b|\bw-?2\b|\b1098\b|\b1095\b|\bk-?1\b|\btax\b|estimated payment"),
    ("Donations", r"donation|charity|charitable|contribution"),
    ("Medical", r"medical|dental|pharmacy|prescription"),
    ("Mileage and travel", r"mileage|travel|hotel|flight|airfare|parking"),
    ("Home and property", r"mortgage|property tax|\brent\b|\bhoa\b"),
    ("Income", r"\bsales\b|payout|\bincome\b"),
    ("Receipts and expenses", r"receipt|expense|purchase"),
]
INVOICE = re.compile(r"invoice", re.I)
SUMMARY = re.compile(r"^\d{4}-\d{2}-summary\.md$")
ORDER = ["Income", "Receipts and expenses", "Tax forms", "Donations", "Medical", "Mileage and travel",
         "Home and property", "Bank summaries"]
COVER = "COVER.md"


def file_year(name, path):
    m = YEAR_PREFIX.match(name)
    if m:
        return int(m.group(1))
    try:
        return dt.date.fromtimestamp(os.path.getmtime(path)).year
    except OSError:
        return None


def categorize(rel, year):
    """The category for a workspace-relative path in the year, or None when the name says nothing."""
    parts = rel.replace("\\", "/").split("/")
    name, folders = parts[-1], [p.lower() for p in parts[:-1]]
    low = name.lower()
    if folders[:1] == ["money"] and SUMMARY.match(name) and name.startswith(str(year)):
        return "Bank summaries"
    for cat, words in CATEGORIES:
        if re.search(words, low):
            return cat
    if INVOICE.search(low):
        return "Income" if any(f in SENT for f in folders) else "Receipts and expenses"
    return None


def plan(root, year, also=(), out=None):
    """(found, not_gathered): found is [(category, rel, size)], not_gathered is [rel] for the year's files
    whose names say nothing. Walks the workspace minus setup, tools, skills, _reference and taxes/."""
    out = os.path.abspath(out or os.path.join(root, "taxes", str(year)))
    found, skipped = [], []
    roots = [root] + [os.path.join(root, a) for a in also if os.path.isdir(os.path.join(root, a))]
    seen = set()
    for base in roots:
        extra = base != root
        for dirpath, dirs, files in os.walk(base):
            if os.path.abspath(dirpath).startswith(out):
                dirs[:] = []
                continue
            rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
            rel_dir = "" if rel_dir == "." else rel_dir
            keep = []
            for d in dirs:
                rel = (rel_dir + "/" + d).lstrip("/")
                if d.startswith(".") or d in SKIP_ANY or (not extra and rel in SKIP_TOP):
                    continue
                keep.append(d)
            dirs[:] = keep
            for f in files:
                if f.startswith(".") or f == COVER or f.endswith(".zip"):
                    continue
                p = os.path.join(dirpath, f)
                rel = (rel_dir + "/" + f).lstrip("/")
                if rel in seen:
                    continue
                seen.add(rel)
                if file_year(f, p) != year:
                    continue
                if rel.startswith("money/") and not SUMMARY.match(f):
                    continue  # the ledger, rules and dashboards stay home; the summaries carry the totals
                cat = categorize(rel, year)
                try:
                    size = os.path.getsize(p)
                except OSError:
                    continue
                (found if cat else skipped).append((cat, rel, size) if cat else rel)
    found.sort(key=lambda t: (ORDER.index(t[0]), t[1]))
    return found, sorted(skipped)


def target_name(folder, name, size):
    """The path to copy to: skip (None) when the same file is already there, ' (2)' when a different one is."""
    p = os.path.join(folder, name)
    if not os.path.exists(p):
        return p
    if os.path.getsize(p) == size:
        return None
    stem, ext = os.path.splitext(name)
    n = 2
    while True:
        q = os.path.join(folder, "%s (%d)%s" % (stem, n, ext))
        if not os.path.exists(q):
            return q
        if os.path.getsize(q) == size:
            return None
        n += 1


def gather(root, year, found, out):
    """Copies found files into out/<Category>/. Returns [(category, rel, copied_as or None)]."""
    done = []
    for cat, rel, size in found:
        folder = os.path.join(out, cat)
        os.makedirs(folder, exist_ok=True)
        dest = target_name(folder, os.path.basename(rel), size)
        if dest:
            shutil.copy2(os.path.join(root, *rel.split("/")), dest)
        done.append((cat, rel, os.path.relpath(dest, out).replace(os.sep, "/") if dest else None))
    return done


def cover(year, found, skipped, today=None):
    today = today or dt.date.today()
    counts = {}
    for cat, _, _ in found:
        counts[cat] = counts.get(cat, 0) + 1
    out = ["# Tax papers for %d" % year, "", "Gathered %s from what was already filed in the workspace. Copies; every original is where it was. "
           "Nothing here was added up, made or changed." % today.isoformat(), ""]
    out += ["## What is here", ""] + ["- %s: %d file%s" % (c, n, "" if n == 1 else "s") for c, n in sorted(counts.items(), key=lambda t: ORDER.index(t[0]))]
    out += ["", "## Where each file came from", ""]
    last = None
    for cat, rel, size in found:
        if cat != last:
            out += ["", "### " + cat, ""]
            last = cat
        out.append("- %s (from %s, %s)" % (os.path.basename(rel), rel, human(size)))
    empty = [c for c in ORDER if c not in counts]
    out += ["", "## Nothing found for", ""] + (["- " + c for c in empty] or ["Every category has something."])
    out += ["", "## Not gathered (the name says nothing about what it is)", ""] + (["- " + r for r in skipped] or ["Nothing."])
    out += ["", "An invoice in a sent or delivery folder counts as income; anywhere else, as an expense. Move one if that is wrong.", ""]
    return "\n".join(out)


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%d %s" % (n, unit) if unit == "B" else "%.1f %s" % (n, unit)
        n /= 1024.0


def make_zip(out, year):
    path = os.path.join(out, "taxes-%d-for-accountant.zip" % year)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirs, files in os.walk(out):
            dirs.sort()
            for f in sorted(files):
                if f.endswith(".zip"):
                    continue
                p = os.path.join(dirpath, f)
                z.write(p, os.path.relpath(p, out).replace(os.sep, "/"))
    return path


def render_plan(year, found, skipped, out):
    lines = ["# Plan for %d (dry run, nothing changed)" % year, ""]
    for cat, rel, size in found:
        lines.append("- %s  <- %s (%s)" % (cat, rel, human(size)))
    if not found:
        lines.append("Nothing found for %d." % year)
    lines += ["", "Would copy %d file%s into %s, write %s and a zip." % (len(found), "" if len(found) == 1 else "s", out, COVER)]
    if skipped:
        lines += ["", "Not gathered (the name says nothing):"] + ["- " + r for r in skipped]
    return "\n".join(lines)


def main(argv, root=None):
    root = root or ROOT
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=dt.date.today().year - 1)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--also", action="append", default=[], help="another folder to look in, inside or outside the workspace (repeatable)")
    p.add_argument("--out", help="where to gather (default taxes/<year>)")
    args = p.parse_args(argv)
    out = os.path.abspath(args.out or os.path.join(root, "taxes", str(args.year)))
    found, skipped = plan(root, args.year, args.also, out)
    if args.dry_run:
        print(render_plan(args.year, found, skipped, out))
        return 0
    if not found:
        print("Nothing found for %d. Check the year, or name a folder with --also." % args.year)
        return 1
    os.makedirs(out, exist_ok=True)
    done = gather(root, args.year, found, out)
    with open(os.path.join(out, COVER), "w", encoding="utf-8") as fh:
        fh.write(cover(args.year, found, skipped))
    z = make_zip(out, args.year)
    copied = sum(1 for _, _, c in done if c)
    print("%d file%s in %s (%d copied now, %d already there). Cover sheet: %s. Zip: %s" % (
        len(done), "" if len(done) == 1 else "s", out, copied, len(done) - copied, os.path.join(out, COVER), z))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
