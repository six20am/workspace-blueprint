#!/usr/bin/env python3
"""Checks every tool and sign-in the workspace needs and re-installs only what is missing.

    python tools/doctor/doctor.py             # check, install what is missing, print the summary
    python tools/doctor/doctor.py --dry-run   # check only, install nothing

It runs the platform's installer in its check-then-install mode (setup/setup.ps1 on Windows,
setup/runner.py --doctor elsewhere), then reads setup/setup-report.md and prints three lines:
what was already present, what it installed now, and what failed, then the sign-ins the person
does themselves. Exit 0 when nothing failed, 2 when something did. Standard library only.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ADAPTERS = ("claude-code", "other")
DEFAULT_ADAPTER = "claude-code"


def read_adapter(root):
    """The adapter named in setup/adapter.json. Missing, unreadable or unknown means claude-code
    (the same rule as tools/update/update.py)."""
    try:
        with open(os.path.join(root, "setup", "adapter.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return DEFAULT_ADAPTER
    name = data.get("adapter") if isinstance(data, dict) else None
    return name if name in ADAPTERS else DEFAULT_ADAPTER


def installer_command(root, adapter, dry_run, is_windows):
    """The installer argv. Windows reads the adapter itself from setup/adapter.json; the runner is
    told it, and picks the platform (mac or linux) on its own."""
    if is_windows:
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
               os.path.join(root, "setup", "setup.ps1"), "-Yes", "-NoLaunch"]
        return cmd + (["-DryRun"] if dry_run else [])
    cmd = [sys.executable, os.path.join(root, "setup", "runner.py"), "--doctor", "--no-launch", "--adapter", adapter]
    return cmd + (["--dry-run"] if dry_run else [])


def _sections(text):
    """{heading: [bullet text]} for every '## ' section of the report."""
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        elif current and line.startswith("- "):
            out[current].append(line[2:].strip())
    return out


def _strip_area(item):
    """'ImageMagick (images) (programs)' -> 'ImageMagick (images)': drop the trailing area tag."""
    return re.sub(r"\s*\([^()]*\)$", "", item)


def summarize(report_text):
    """Three lines (present, installed now, failed with each detail), then the sign-in list."""
    sec = _sections(report_text)
    present = sec.get("Already present", [])
    installed = [_strip_area(i) for i in sec.get("Installed now", [])]
    failed = []
    for item in sec.get("Needs attention", []):
        m = re.match(r"\*\*(.+?)\*\* \((\w+)\):\s*(.*)$", item)
        if m and m.group(2) == "failed":
            failed.append((m.group(1), m.group(3)))
    logins = []
    for item in sec.get("Sign in yourself", []):
        m = re.match(r"\*\*(.+?)\*\*:\s*(.*)$", item)
        if m:
            logins.append((m.group(1), m.group(2)))

    lines = ["Present: %d" % len(present)]
    lines.append("Installed now: %d (%s)" % (len(installed), ", ".join(installed)) if installed else "Installed now: 0")
    if failed:
        lines.append("Failed: %d" % len(failed))
        lines += ["  - %s: %s" % f for f in failed]
    else:
        lines.append("Failed: 0, nothing to fix")
    planned = [_strip_area(i) for i in sec.get("Would install", [])]
    if planned:   # a dry run only: what a real run would install
        lines.append("Would install: %d (%s)" % (len(planned), ", ".join(planned)))
    if logins:
        lines += ["", "Sign in yourself:"] + ["  - %s: %s" % l for l in logins]
    return "\n".join(lines)


def failed_count(report_text):
    return sum(1 for item in _sections(report_text).get("Needs attention", []) if re.search(r"^\*\*.+?\*\* \(failed\):", item))


def main(argv=None):
    p = argparse.ArgumentParser(description="Checks every workspace tool and re-installs only what is missing.")
    p.add_argument("--dry-run", action="store_true", help="check only, install nothing")
    args = p.parse_args(argv)
    report = os.path.join(ROOT, "setup", "setup-report.md")
    cmd = installer_command(ROOT, read_adapter(ROOT), args.dry_run, os.name == "nt")
    started = time.time()
    try:
        rc = subprocess.call(cmd, cwd=ROOT)
    except OSError as e:
        print("The installer did not start: %s" % e)
        return 2
    if not os.path.isfile(report) or os.path.getmtime(report) < started - 2:
        print("The installer stopped before writing setup/setup-report.md (exit %d). Read its output above." % rc)
        return 2
    with open(report, encoding="utf-8") as fh:
        text = fh.read()
    print("")
    print(summarize(text))
    return 2 if failed_count(text) else 0


if __name__ == "__main__":
    sys.exit(main())
