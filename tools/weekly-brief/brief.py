#!/usr/bin/env python3
"""Writes a one-page brief of the week in this workspace.

    python tools/weekly-brief/brief.py                      # the last 7 days, ending today
    python tools/weekly-brief/brief.py --days 14 --out x.md
    python tools/weekly-brief/brief.py --today 2026-10-31   # end the week on that date

Nine sections: files that came in (changed in the window), files that went out (the ones inside
a delivery or sent folder), dates coming up in the next 14 days (from paperwork/dates.md), renewals
due within 30 days or past (renewals.md, read with tools/renewals/renewals.py), things
waited on past their time (waiting-on.md, read with tools/waiting-on/waiting.py), decisions
logged this week (decisions.md), gaps logged (setup/gap-log.md), jobs that keep coming back
(undo-history summaries from the last 90 days that repeat three or more times) and sign-ins still
needed (setup/setup-report.md). It reads only file dates, those six files, the router file and the
undo history's summaries. It saves weekly-brief-YYYY-MM-DD.md in the
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


def _sibling_tool(folder, module):
    """Load tools/<folder>/<module>.py from beside this script; None when the tool is not installed."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", folder, module + ".py")
    if not os.path.isfile(path):
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location(module, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _waiting_on(root, today):
    """Overdue lines from waiting-on.md, as the waiting-on tool prints them. Empty without the file or the tool."""
    waiting = _sibling_tool("waiting-on", "waiting")
    text = _read(os.path.join(root, "waiting-on.md"))
    if waiting is None or not text:
        return []
    overdue, _ = waiting.sort_items(waiting.parse(text), today)
    return [waiting.line_for(it) for it in overdue]


def _renewals(root, today):
    """Lines from renewals.md past or due within 30 days, soonest first, 'this week' marked. Empty without the file or the tool."""
    renewals = _sibling_tool("renewals", "renewals")
    text = _read(os.path.join(root, "renewals.md"))
    if renewals is None or not text:
        return []
    b = renewals.sort_items(renewals.parse(text), today)
    out = [renewals.line_for(it) + ", ask if renewed" for it in b["past"]]
    out += [renewals.line_for(it) + ", this week" for it in b["soon"]]
    out += [renewals.line_for(it) for it in b["month"]]
    return out


REPEAT_DAYS = 90
REPEAT_MIN = 3
STOP = {"a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "at", "by", "with", "from", "into", "up",
        "new", "old", "this", "that", "it", "its", "my", "our", "his", "her", "their", "some", "more", "again",
        "added", "add", "made", "make", "did", "do", "done", "put", "got", "get", "set", "ran", "run", "saved",
        "save", "wrote", "write", "sent", "send", "fixed", "fix", "updated", "update", "changed", "change",
        "january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
        "november", "december"}


def _words(summary):
    """The content words of a six-word undo summary: lowercase, no numbers, no filler, no plurals."""
    out = set()
    for w in re.findall(r"[a-z]+", summary.lower()):
        if w in STOP or len(w) < 3:
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def _history_summaries(root, since_days):
    """The undo history's save summaries in the window, newest first. Empty when there is no history."""
    if not os.path.isdir(os.path.join(root, ".git")):
        return []
    import subprocess
    try:
        r = subprocess.run(["git", "log", "--since=%d days ago" % since_days, "--format=%s"], cwd=root,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []


def repeats(summaries, minimum=REPEAT_MIN):
    """Groups save summaries that share two or more content words, and returns the groups seen `minimum`
    or more times as (count, first summary) pairs, most repeated first. Greedy; good enough to notice."""
    groups = []  # [words, count, label]
    for s in summaries:
        words = _words(s)
        if len(words) < 2:
            continue
        for g in groups:
            if len(words & g[0]) >= 2:
                g[0] |= words
                g[1] += 1
                break
        else:
            groups.append([words, 1, s])
    hits = [(g[1], g[2]) for g in groups if g[1] >= minimum]
    hits.sort(key=lambda t: (-t[0], t[1]))
    return hits


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
        "renewals": _renewals(root, today),
        "waiting": _waiting_on(root, today),
        "decisions": _dated_lines(os.path.join(root, "decisions.md"), start, today),
        "gaps": _dated_lines(os.path.join(root, "setup", "gap-log.md"), start, today),
        "repeats": ["%d times: %s" % (n, label) for n, label in repeats(_history_summaries(root, REPEAT_DAYS))],
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
    lines += _section("Renewals coming up (30 days)", data.get("renewals", []))
    lines += _section("Waiting on, overdue", data.get("waiting", []))
    lines += _section("Decided this week", data.get("decisions", []))
    lines += _section("Gaps logged", data["gaps"])
    lines += _section("Jobs that keep coming back (last %d days)" % REPEAT_DAYS, data.get("repeats", []))
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
