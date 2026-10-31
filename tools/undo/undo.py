"""Version history for the workspace folder: save after each task, undo on request.

Usage:
  python tools/undo/undo.py init            start history (safe to run again)
  python tools/undo/undo.py save "<what>"   save everything that changed
  python tools/undo/undo.py list            the last ten saves
  python tools/undo/undo.py undo            step back one save, keeping the history

Never pushes anywhere and never deletes the .git folder.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gitignore-template")
NO_HISTORY = "No history yet. Run: python tools/undo/undo.py init"


def run_git(args, cwd=ROOT, check=True):
    """Run one git command with captured output. On failure print git's error in one line and exit 1."""
    if args and args[0] == "push":
        fail("undo never pushes.")
    try:
        r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except FileNotFoundError:
        fail("git is not installed. Run the doctor: python tools/doctor/doctor.py")
    if check and r.returncode != 0:
        msg = " ".join((r.stderr or r.stdout or "git failed").split())
        fail("git %s failed: %s" % (args[0], msg))
    return r


def fail(msg):
    print(msg)
    sys.exit(1)


def has_history():
    return os.path.exists(os.path.join(ROOT, ".git"))


def is_dirty():
    return run_git(["status", "--porcelain"]).stdout.strip() != ""


def commit_count():
    r = run_git(["rev-list", "--count", "HEAD"], check=False)
    if r.returncode != 0:
        return 0
    return int(r.stdout.strip() or 0)


def commit_all(message):
    """Stage everything and commit. Returns the short sha, or None when there was nothing to commit."""
    run_git(["add", "-A"])
    if run_git(["diff", "--cached", "--quiet"], check=False).returncode == 0:
        return None
    run_git(["commit", "-q", "-m", message])
    return run_git(["rev-parse", "--short", "HEAD"]).stdout.strip()


def cmd_init():
    created = False
    if not has_history():
        if run_git(["init", "-q", "-b", "main"], check=False).returncode != 0:
            run_git(["init", "-q"])
            run_git(["symbolic-ref", "HEAD", "refs/heads/main"])
        created = True
    gitignore = os.path.join(ROOT, ".gitignore")
    if not os.path.exists(gitignore) and os.path.exists(TEMPLATE):
        shutil.copyfile(TEMPLATE, gitignore)
    if run_git(["config", "user.name"], check=False).stdout.strip() == "":
        run_git(["config", "user.name", "Workspace"])
    if run_git(["config", "user.email"], check=False).stdout.strip() == "":
        run_git(["config", "user.email", "workspace@localhost"])
    sha = commit_all("workspace built") if commit_count() == 0 else None
    if sha:
        print("History started: %s workspace built" % sha)
    elif created:
        print("History started, nothing to save yet.")
    else:
        print("History already on, %d saves." % commit_count())


def cmd_save(message):
    if not has_history():
        fail(NO_HISTORY)
    sha = commit_all(message)
    if sha is None:
        print("nothing to save")
    else:
        print("%s %s" % (sha, message))


def cmd_list():
    if not has_history():
        fail(NO_HISTORY)
    if commit_count() == 0:
        print("No saves yet.")
        return
    out = run_git(["log", "-10", "--date=format:%Y-%m-%d %H:%M", "--format=%h  %ad  %s"]).stdout
    print(out.rstrip())


def undo_target():
    """The newest save that an earlier undo has not already stepped back over.

    Each undo is a revert commit whose body names the commit it reverts, so a second
    undo skips the first undo and the save it undid, and steps back one save further
    instead of putting the first undo back. Returns (sha, message), or None when only
    the first save is left.
    """
    out = run_git(["log", "--first-parent", "--format=%H%x1f%P%x1f%s%x1f%b%x1e"]).stdout
    undone = set()
    for record in out.split(""):
        record = record.strip()
        if not record:
            continue
        sha, parents, subject, body = (record.split("") + ["", "", ""])[:4]
        reverted = None
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("This reverts commit ") and line.endswith("."):
                reverted = line[len("This reverts commit "):-1].strip()
        if sha in undone:
            continue
        if reverted:
            undone.add(reverted)
            continue
        if not parents.strip():
            return None
        return sha, subject
    return None


def cmd_undo():
    if not has_history():
        fail(NO_HISTORY)
    if is_dirty():
        commit_all("before undo")
    if commit_count() < 2:
        fail("Nothing to undo yet.")
    target = undo_target()
    if target is None:
        fail("Nothing to undo yet.")
    sha, message = target
    r = run_git(["revert", "--no-edit", sha], check=False)
    if r.returncode != 0:
        run_git(["revert", "--abort"], check=False)
        fail("Could not undo %s cleanly: %s" % (message, " ".join((r.stderr or r.stdout).split())))
    files = run_git(["show", "--stat", "--format=", "HEAD"]).stdout.rstrip()
    print("Undid: %s" % message)
    if files:
        print(files)


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return
    cmd = argv[0]
    if cmd == "init":
        cmd_init()
    elif cmd == "save":
        if len(argv) < 2 or not argv[1].strip():
            fail('Say what changed: python tools/undo/undo.py save "<what>"')
        cmd_save(" ".join(argv[1:]).strip())
    elif cmd == "list":
        cmd_list()
    elif cmd == "undo":
        cmd_undo()
    else:
        fail("Unknown command: %s. Use init, save, list or undo." % cmd)


if __name__ == "__main__":
    main(sys.argv[1:])
