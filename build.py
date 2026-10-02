#!/usr/bin/env python3
"""Builds the zip people download. Scans every text file first and refuses on any leak.
Standard library only.

    python build.py                       # writes ~/Downloads/Six20AM Workspace Blueprint.zip
    python build.py --out <path.zip> --names <file>
"""
import argparse
import datetime
import os
import re
import sys
import zipfile

TOP = "Six20AM Workspace Blueprint"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".superpowers"}
SKIP_ROOT_DIRS = {"tests", "docs"}  # the repo's own test suite and design doc; setup/tests ships
SKIP_FILES = {"build.py", "setup-report.md"}
SKIP_ROOT_FILES = {"README.md"}     # the GitHub readme; START-HERE.md is the product's front page
TEXT = (".md", ".json", ".ps1", ".sh", ".command", ".cmd", ".py", ".txt", ".mjs", ".js", ".cjs", ".yml", ".yaml", ".toml")
LF = (".sh", ".command", ".py", ".md", ".json", ".mjs", ".js", ".cjs", ".yml", ".yaml", ".toml")
EXEC = (".command", ".sh")
SECRET_RE = re.compile(r"(^|/)(\.env(\.[^/]*)?|accounts\.json|instances\.json|[^/]*secret[^/]*\.(json|env)|[^/]*\.pem|[^/]*\.key)$", re.I)
SECRET_ALLOW = re.compile(r"\.example(\.json)?$", re.I)
FIXED = ["\u2014", "mtesi", "C:\\Users\\", "/c/Users/", "shared-core", "shared-systems", "work-log"]
# the maintainer's own names, caught even when no parent-workspace names list exists (a public clone)
FIXED_CI = ["six20am", "motus", "machado", "michael"]
HARD_RULE = re.compile(r"Hard Rule \d", re.I)     # a numbered rule from the parent workspace; a "Hard rules" heading is fine
HEX_ID = re.compile(r"\b[0-9a-f]{32}\b")
ALLOWED = {"README.md", "docs/design.md"}
# vendor code shipped as-is; scanned by eye, not by string (same exemption as tests/test_shipped.py)
VENDOR = (".claude/skills/last30days/scripts/", ".claude/skills/agent-reach/_references")


class LeakError(Exception):
    pass


def is_secret(rel):
    rel = rel.replace("\\", "/")
    return bool(SECRET_RE.search(rel)) and not SECRET_ALLOW.search(rel)


def scan_text(text, names):
    problems = []
    low = text.lower()
    for s in FIXED:
        if s in text:
            problems.append(repr(s))
    for n in FIXED_CI + list(names):
        if n and n.lower() in low:
            problems.append(n)
    if HARD_RULE.search(text):
        problems.append("Hard Rule N")
    if HEX_ID.search(text):
        problems.append("32-char hex id")
    return problems


def default_names(repo):
    """Client slugs and sanitize terms from the parent workspace, when this repo sits inside it."""
    names = []
    ws = os.path.abspath(os.path.join(repo, "..", ".."))
    clients = os.path.join(ws, "clients")
    if os.path.isdir(clients):
        names += [d for d in os.listdir(clients) if os.path.isdir(os.path.join(clients, d)) and not d.startswith("_")]
    terms = os.path.join(ws, "tools", "workspace-export", "sanitize_terms.txt")
    if os.path.isfile(terms):
        with open(terms, encoding="utf-8") as fh:
            names += [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    return names


def files(repo):
    for dirpath, dirs, fs in os.walk(repo):
        at_root = os.path.abspath(dirpath) == os.path.abspath(repo)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (at_root and d in SKIP_ROOT_DIRS)]
        for f in sorted(fs):
            if f in SKIP_FILES or (at_root and f in SKIP_ROOT_FILES):
                continue
            p = os.path.join(dirpath, f)
            yield os.path.relpath(p, repo).replace("\\", "/"), p


def build(repo, out, names, top=TOP):
    leaks = []
    included = []
    for rel, p in files(repo):
        if is_secret(rel):
            leaks.append("%s: secret-shaped file" % rel)
            continue
        if rel.endswith(TEXT) and rel not in ALLOWED and not rel.startswith(VENDOR):
            with open(p, encoding="utf-8", errors="replace") as fh:
                probs = scan_text(fh.read(), names)
            if probs:
                leaks.append("%s: %s" % (rel, ", ".join(probs)))
        included.append((rel, p))
    if leaks:
        raise LeakError("refusing to build:\n  " + "\n  ".join(leaks))
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, p in included:
            arc = top + "/" + rel
            zi = zipfile.ZipInfo.from_file(p, arc)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3   # Unix: a Mac honours the mode bits only when the creator says Unix
            zi.external_attr = ((0o755 if rel.endswith(EXEC) else 0o644) << 16)
            with open(p, "rb") as fh:
                data = fh.read()
            if rel.endswith(LF):
                data = data.replace(b"\r\n", b"\n")   # a zip built on Windows must not ship CRLF scripts to a Mac
            z.writestr(zi, data)
    lines = ["# Build report", "", "Built %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Zip: %s" % out, "Files: %d" % len(included), ""]
    lines += ["- " + rel for rel, _ in included]
    report = "\n".join(lines) + "\n"
    with open(os.path.splitext(out)[0] + "-build-report.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.expanduser("~"), "Downloads", TOP + ".zip"))
    ap.add_argument("--names", help="file with one extra forbidden string per line")
    a = ap.parse_args()
    repo = os.path.dirname(os.path.abspath(__file__))
    names = default_names(repo)
    if a.names:
        with open(a.names, encoding="utf-8") as fh:
            names += [l.strip() for l in fh if l.strip()]
    try:
        report = build(repo, a.out, names)
    except LeakError as e:
        print(e)
        return 1
    print(report.splitlines()[4])
    print("Wrote " + a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
