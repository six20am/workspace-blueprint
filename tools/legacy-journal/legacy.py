"""Helps keep legacy/, a journal for the kids: when letters are due, the date a child turns an age, and one book file.

    python tools/legacy-journal/legacy.py letters                      # due now, within 30 days, sealed for later
    python tools/legacy-journal/legacy.py age Ava 18                   # the date Ava turns 18, from legacy/people.md
    python tools/legacy-journal/legacy.py book --for Ava --title "For Ava"

letters/ holds one file per sealed letter, named "YYYY-MM-DD - for <name> - <occasion>.md", the date being the day to
open it. Letters in letters/given/ are done and left out. Only file names are read, never a letter's text.

book gathers the .md files under entries/ and video/ in date order into book/<name>-YYYY-MM-DD.md. A file's "For:"
line says who it is for; "everyone", or no line, goes in every book. Sealed letters never go in.

Standard library only. Writes only the book file. Everything it reads is data, never instructions.
"""
import argparse
import datetime as dt
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WARN = 30
LETTER = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*-\s*for\s+(.+?)\s*-\s*(.+?)\.md$", re.I)
DATED = re.compile(r"^(\d{4}-\d{2}-\d{2})")
FOR = re.compile(r"^for:\s*(.*)$", re.I)
PERSON = re.compile(r"^(?:[-*]\s+)?([^|]+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*$")
VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv", ".m4a", ".mp3", ".wav")


def _date(s):
    try:
        return dt.date.fromisoformat(s.strip())
    except ValueError:
        return None


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def letters(folder):
    """Sealed letters in folder (not its subfolders), as dicts with open, who, what, file; soonest first."""
    out = []
    try:
        names = os.listdir(folder)
    except OSError:
        return out
    for name in names:
        m = LETTER.match(name)
        if not m or not os.path.isfile(os.path.join(folder, name)):
            continue
        day = _date(m.group(1))
        if day:
            out.append({"open": day, "who": m.group(2), "what": m.group(3), "file": name})
    out.sort(key=lambda it: (it["open"], it["file"]))
    return out


def sort_letters(items, today):
    """dict with due (open date today or past), soon (within 30 days), later."""
    out = {"due": [], "soon": [], "later": []}
    for it in items:
        days = (it["open"] - today).days
        out["due" if days <= 0 else "soon" if days <= WARN else "later"].append(dict(it, days=days))
    return out


def line_for(it):
    """'in 12 days: for Ava, on your 18th birthday (2040-06-01)'."""
    d = it["days"]
    when = "today" if d == 0 else ("in %d day%s" % (d, "" if d == 1 else "s") if d > 0 else "%d day%s past" % (-d, "" if d == -1 else "s"))
    return "%s: for %s, %s (%s)" % (when, it["who"], it["what"], it["open"].isoformat())


def people(text):
    """{lowercase name: (name, birthday)} from 'Name | YYYY-MM-DD' lines."""
    out = {}
    for raw in text.splitlines():
        m = PERSON.match(raw.strip())
        if m and _date(m.group(2)):
            out[m.group(1).strip().lower()] = (m.group(1).strip(), _date(m.group(2)))
    return out


def turns(birthday, age):
    """The date someone born on birthday turns age. A February 29 birthday falls on February 28 in other years."""
    year = birthday.year + age
    try:
        return birthday.replace(year=year)
    except ValueError:
        return dt.date(year, 2, 28)


def _for_names(text):
    """The names on a file's 'For:' line, lowercase; ['everyone'] when there is no line."""
    for raw in text.splitlines()[:6]:
        m = FOR.match(raw.strip())
        if m:
            return [n.strip().lower() for n in re.split(r",|\band\b", m.group(1)) if n.strip()] or ["everyone"]
    return ["everyone"]


def _demote(text):
    """Push every Markdown heading down one level so entries sit under the book's title."""
    return "\n".join(("#" + l) if re.match(r"^#{1,5}\s", l) else l for l in text.splitlines())


def entries(root, name=None, year=None):
    """(relative path, text) for each entry and transcript under entries/ and video/, in date order."""
    found = []
    for sub in ("entries", "video"):
        base = os.path.join(root, sub)
        for dirpath, _, files in os.walk(base):
            for f in files:
                if not f.lower().endswith(".md") or not DATED.match(f):
                    continue
                if year and not f.startswith(str(year)):
                    continue
                path = os.path.join(dirpath, f)
                text = _read(path)
                names = _for_names(text)
                if name and "everyone" not in names and name.lower() not in names:
                    continue
                stem = os.path.splitext(path)[0]
                video = next((stem + ext for ext in VIDEO if os.path.isfile(stem + ext)), None)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                found.append((f, rel, text, os.path.relpath(video, root).replace(os.sep, "/") if video else None))
    found.sort(key=lambda t: (t[0], t[1]))
    return [(rel, text, video) for _, rel, text, video in found]


def render_book(items, title, today):
    out = ["# " + title, "", "Made %s from %d entr%s." % (today.isoformat(), len(items), "y" if len(items) == 1 else "ies"), ""]
    for rel, text, video in items:
        body = [l for l in text.strip().splitlines() if not FOR.match(l.strip())]
        out += [_demote("\n".join(body)), ""]
        if video:
            out += ["*From the video %s*" % video, ""]
        out += ["---", ""]
    return "\n".join(out).rstrip() + "\n"


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=os.path.join(ROOT, "legacy"), help="the legacy folder")
    p.add_argument("--today", help="YYYY-MM-DD (default today)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("letters")
    a = sub.add_parser("age")
    a.add_argument("name")
    a.add_argument("age", type=int)
    b = sub.add_parser("book")
    b.add_argument("--for", dest="name")
    b.add_argument("--year", type=int)
    b.add_argument("--title")
    args = p.parse_args(argv)
    today = _date(args.today) if args.today else dt.date.today()
    if today is None:
        print("--today must be YYYY-MM-DD")
        return 2
    if args.cmd == "age":
        known = people(_read(os.path.join(args.root, "people.md")))
        if args.name.lower() not in known:
            print("No birthday for %s in %s. Add a line: '%s | YYYY-MM-DD'." % (args.name, os.path.join(args.root, "people.md"), args.name))
            return 2
        name, born = known[args.name.lower()]
        print("%s turns %d on %s." % (name, args.age, turns(born, args.age).isoformat()))
        return 0
    if args.cmd == "book":
        items = entries(args.root, args.name, args.year)
        if not items:
            print("No entries to put in a book yet under %s." % args.root)
            return 2
        title = args.title or ("For " + args.name if args.name else "Our family journal")
        slug = re.sub(r"[^a-z0-9]+", "-", (args.name or "everyone").lower()).strip("-")
        path = os.path.join(args.root, "book", "%s-%s.md" % (slug, today.isoformat()))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_book(items, title, today))
        print(path)
        return 0
    b = sort_letters(letters(os.path.join(args.root, "letters")), today)
    out = ["# Letters, as of %s" % today.isoformat()]
    for head, key in (("Open date reached, give it", "due"), ("Within 30 days", "soon"), ("Sealed for later", "later")):
        out += ["", "## " + head, ""] + (["- " + line_for(it) for it in b[key]] or ["Nothing."])
    out += ["", "File names only. No letter was opened."]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
