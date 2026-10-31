#!/usr/bin/env python3
"""Writes a one-page brief of the week in this workspace.

    python tools/weekly-brief/brief.py                      # the last 7 days, ending today
    python tools/weekly-brief/brief.py --days 14 --out x.md
    python tools/weekly-brief/brief.py --today 2026-10-31   # end the week on that date

Five sections: files that came in (changed in the window), files that went out (the ones inside
a delivery or sent folder), dates coming up in the next 14 days (from paperwork/dates.md), gaps
logged (setup/gap-log.md) and sign-ins still needed (setup/setup-report.md). It reads only file
dates, plus those three files and the router file. It saves weekly-brief-YYYY-MM-DD.md in the
notes folder the router names, else the workspace folder, and prints the path. Standard library only.
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROUTER = "CONTEXT.md"   # the Claude Code name; setup/adapter.json "router" overrides it
SKIP_TOP = {"setup", "tools", "_reference"}
SKIP_ANY = {".git", "node_modules", "__pycache__"}
DELIVERY = {"delivery", "delivered", "sent", "out", "3-delivery", "6-comms"}
BRIEF_NAME = re.compile(r"^weekly-brief-\d{4}-\d{2}-\d{2}\.md$")
DATED = re.compile(r"^(?:[-*]\s+)?(\d{4}-\d{2}-\d{2})\s*\|")
CAP = 40
DUE_DAYS = 14


def read_adapter(root):
    """setup/adapter.json as a dict; missing or unreadable means the defaults."""
    try:
        with open(os.path.join(root, "setup", "adapter.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _dated_lines(path, first, last):
    """Lines that start with a date between first and last (inclusive), sorted."""
    out = []
    for line in _read(path).splitlines():
        line = line.strip()
        m = DATED.match(line)
        if not m:
            continue
        try:
            day = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if first <= day <= last:
            out.append(re.sub(r"^[-*]\s+", "", line))
    return sorted(out)


def _sign_ins(path):
    """Bullets under '## Sign in yourself', bold markers dropped."""
    out, inside = [], False
    for line in _read(path).splitlines():
        if line.startswith("## "):
            inside = line[3:].strip() == "Sign in yourself"
        elif inside and line.startswith("- "):
            out.append(line[2:].strip().replace("**", ""))
    return out


def _day_start(day):
    return datetime.datetime(day.year, day.month, day.day).timestamp()


def collect(root, today, days):
    start = today - datetime.timedelta(days=max(days, 1) - 1)
    lo, hi = _day_start(start), _day_start(today + datetime.timedelta(days=1))
    skills_dir = str(read_adapter(root).get("skills_dir") or "skills").replace("\\", "/").strip("/")
    found = []
    for dirpath, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        rel_dir = "" if rel_dir == "." else rel_dir
        keep = []
        for d in dirs:
            rel = (rel_dir + "/" + d).lstrip("/")
            if d.startswith(".") or d in SKIP_ANY or rel in SKIP_TOP or rel in (skills_dir, "skills"):
                continue
            keep.append(d)
        dirs[:] = keep
        for f in files:
            if f.startswith(".") or BRIEF_NAME.match(f):
                continue
            try:
                mtime = os.path.getmtime(os.path.join(dirpath, f))
            except OSError:
                continue
            if lo <= mtime < hi:
                found.append((mtime, (rel_dir + "/" + f).lstrip("/")))
    found.sort(key=lambda t: (-t[0], t[1]))
    came_in = [rel for _, rel in found]
    went_out = [rel for rel in came_in if any(p.lower() in DELIVERY for p in rel.split("/")[:-1])]
    return {
        "came_in": came_in,
        "went_out": went_out,
        "dates_due": _dated_lines(os.path.join(root, "paperwork", "dates.md"), today, today + datetime.timedelta(days=DUE_DAYS)),
        "gaps": _dated_lines(os.path.join(root, "setup", "gap-log.md"), start, today),
        "sign_ins": _sign_ins(os.path.join(root, "setup", "setup-report.md")),
        "window": (start, today),
    }


def _section(title, items, cap=None):
    lines = ["## " + title, ""]
    if not items:
        lines.append("Nothing.")
    else:
        lines += ["- " + i for i in (items[:cap] if cap else items)]
        if cap and len(items) > cap:
            lines.append("- and %d more" % (len(items) - cap))
    return lines + [""]


def render(data):
    start, end = data["window"]
    lines = ["# Week of %s to %s" % (start.isoformat(), end.isoformat()), ""]
    lines += _section("Came in", data["came_in"], CAP)
    lines += _section("Went out", data["went_out"], CAP)
    lines += _section("Dates coming up", data["dates_due"])
    lines += _section("Gaps logged", data["gaps"])
    lines += _section("Sign-ins needed", data["sign_ins"])
    return "\n".join(lines).rstrip("\n") + "\n"


def notes_folder(root):
    """The folder the router names for notes: the first line with the word 'notes' followed by a
    backticked path. A backticked file name (one with an extension) is not a folder and is skipped."""
    router = str(read_adapter(root).get("router") or DEFAULT_ROUTER)
    for line in _read(os.path.join(root, router)).splitlines():
        m = re.search(r"\bnotes\b", line, re.I)
        if not m:
            continue
        for path in re.findall(r"`([^`]+)`", line[m.end():]):
            path = path.strip().replace("\\", "/").strip("/")
            if path and not os.path.splitext(path)[1] and not os.path.isabs(path) and ".." not in path.split("/"):
                return path
    return None


def output_path(root, today, out):
    if out:
        return out
    name = "weekly-brief-%s.md" % today.isoformat()
    folder = notes_folder(root)
    return os.path.join(root, *folder.split("/"), name) if folder else os.path.join(root, name)


def main(argv=None):
    p = argparse.ArgumentParser(description="Writes a one-page brief of the week in this workspace.")
    p.add_argument("--days", type=int, default=7, help="how many days back, today included (default 7)")
    p.add_argument("--out", help="where to save the brief")
    p.add_argument("--today", help="the date the week ends on, YYYY-MM-DD (default today)")
    args = p.parse_args(argv)
    try:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    except ValueError:
        print("--today must be YYYY-MM-DD")
        return 2
    path = output_path(ROOT, today, args.out)
    text = render(collect(ROOT, today, args.days))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
