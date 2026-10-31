"""Copies the workspace to a folder the person named, new and changed files only, and logs the run.

    python tools/backup/backup.py --to "D:\\backup\\my-workspace"   # the first time: names the place
    python tools/backup/backup.py                                    # after that: the last place used
    python tools/backup/backup.py --dry-run

The place is remembered in setup/backup-log.md, one line per run: "YYYY-MM-DD HH:MM | N copied, M unchanged | to <folder>".
A file is copied when the backup has no copy, or its copy has a different size or an older date. Nothing is ever deleted
or overwritten with something older, on either side. The undo history (.git) is copied; node_modules and other
installs are not. A target inside the workspace, or a target whose parent folder does not exist (the drive is not
plugged in), is refused before anything is touched.

Standard library only.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG = os.path.join("setup", "backup-log.md")
LOG_HEADER = "# Backup log\n\nOne line per run, written by tools/backup/backup.py: `YYYY-MM-DD HH:MM | N copied, M unchanged | to <folder>`.\n\n"
SKIP_DIRS = {"node_modules", "__pycache__", ".venv", ".pytest_cache", ".cache"}
LOG_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?: \d{2}:\d{2})?\s*\|\s*(.*?)\s*\|\s*to (.+)$")


def read_log(root):
    """[(date, counts, folder)] oldest first; empty without the file."""
    out = []
    try:
        with open(os.path.join(root, LOG), encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                m = LOG_LINE.match(raw.strip())
                if m:
                    try:
                        out.append((dt.date.fromisoformat(m.group(1)), m.group(2), m.group(3).strip()))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def last_run(root):
    """(date, folder) of the newest log line, or None."""
    runs = read_log(root)
    return (runs[-1][0], runs[-1][2]) if runs else None


def check_target(root, to):
    """A plain reason the target is no good, or None."""
    root = os.path.abspath(root)
    to = os.path.abspath(to)
    if to == root or to.startswith(root + os.sep):
        return "%s is inside the workspace. A backup lives somewhere else: a drive, or a synced folder." % to
    if root.startswith(to + os.sep):
        return "%s holds the workspace itself. Pick a folder beside it, not above it." % to
    parent = os.path.dirname(to)
    if not os.path.isdir(parent) and not os.path.isdir(to):
        return "Nothing at %s. Is the drive plugged in?" % parent
    return None


def plan(root, to):
    """[(src, dest)] for files that need copying, and the count of files already there and unchanged."""
    to_copy, unchanged = [], 0
    to_abs = os.path.abspath(to)
    for dirpath, dirs, files in os.walk(root):
        if os.path.abspath(dirpath) == to_abs:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            src = os.path.join(dirpath, f)
            dest = os.path.join(to, os.path.relpath(src, root))
            try:
                s = os.stat(src)
            except OSError:
                continue
            try:
                d = os.stat(dest)
            except OSError:
                to_copy.append((src, dest))
                continue
            if d.st_size != s.st_size or d.st_mtime < s.st_mtime - 2:
                to_copy.append((src, dest))
            else:
                unchanged += 1
    return to_copy, unchanged


def copy_all(to_copy):
    done, failed = 0, []
    for src, dest in to_copy:
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            done += 1
        except OSError as e:
            failed.append("%s: %s" % (src, e))
    return done, failed


def write_log(root, when, copied, unchanged, to):
    path = os.path.join(root, LOG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as fh:
        if new:
            fh.write(LOG_HEADER)
        fh.write("%s | %d copied, %d unchanged | to %s\n" % (when.strftime("%Y-%m-%d %H:%M"), copied, unchanged, to))


def status_line(root, today=None, stale_days=7):
    """One line for the weekly brief."""
    today = today or dt.date.today()
    last = last_run(root)
    if not last:
        return "No backup yet. The backup skill sets one up."
    day, folder = last
    age = (today - day).days
    when = "today" if age == 0 else "yesterday" if age == 1 else "%d days ago" % age
    line = "Last backup %s (%s), to %s." % (when, day.isoformat(), folder)
    if age > stale_days:
        line += " Run it."
    return line


def main(argv, root=None, now=None):
    root = root or ROOT
    p = argparse.ArgumentParser()
    p.add_argument("--to", help="the backup folder; remembered for next time")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    to = args.to
    if not to:
        last = last_run(root)
        if not last:
            print("No backup place yet. Run once with --to <folder>: a drive, or a folder another program syncs.")
            return 2
        to = last[1]
    reason = check_target(root, to)
    if reason:
        print(reason)
        return 2
    to_copy, unchanged = plan(root, to)
    if args.dry_run:
        print("Would copy %d file%s to %s; %d unchanged. Nothing done." % (len(to_copy), "" if len(to_copy) == 1 else "s", to, unchanged))
        return 0
    os.makedirs(to, exist_ok=True)
    copied, failed = copy_all(to_copy)
    write_log(root, now or dt.datetime.now(), copied, unchanged, os.path.abspath(to))
    print("%d file%s copied, %s unchanged, to %s." % (copied, "" if copied == 1 else "s", format(unchanged, ","), os.path.abspath(to)))
    if failed:
        print("%d could not be copied:" % len(failed))
        for f in failed[:20]:
            print("- " + f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
