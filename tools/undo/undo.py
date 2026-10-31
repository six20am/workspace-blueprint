"""Version history for the workspace folder: save after each task, undo on request.

Usage:
  python tools/undo/undo.py init            start history (safe to run again)
  python tools/undo/undo.py save "<what>"   save everything that changed
  python tools/undo/undo.py list            the last ten saves
  python tools/undo/undo.py undo            step back one save, keeping the history
  python tools/undo/undo.py redo            take back the last undo

Never pushes anywhere and never deletes the .git folder.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gitignore-template")
NO_HISTORY = "No history yet. Run: python tools/undo/undo.py init"
NOT_OURS = "This folder's history was not started by undo. Run: python tools/undo/undo.py init"
CLONE = ("This folder is a copy of a repository, not a workspace history. "
         "Undo only works on a folder made by the installer.")
MARKER = "workspace.undo"


def run_git(args, cwd=ROOT, check=True):
    """Run one git command with captured output. On failure print git's error in one line and exit 1."""
    if args and args[0] == "push":
        fail("undo never pushes.")
    try:
        r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except FileNotFoundError:
        fail("git is not installed. Run the doctor: python tools/doctor/doctor.py (python3 on Mac and Linux)")
    if check and r.returncode != 0:
        msg = " ".join((r.stderr or r.stdout or "git failed").split())
        fail("git %s failed: %s" % (args[0], msg))
    return r


def fail(msg):
    print(msg)
    sys.exit(1)


def has_history():
    return os.path.exists(os.path.join(ROOT, ".git"))


def has_marker():
    return run_git(["config", "--local", "--get", MARKER], check=False).stdout.strip() == "1"


def require_history():
    """save, list and undo only work on a history that init started."""
    if not has_history():
        fail(NO_HISTORY)
    if not has_marker():
        fail(NOT_OURS)


def template_groups():
    """The template as (comment, [patterns]) groups."""
    groups = []
    if not os.path.exists(TEMPLATE):
        return groups
    with open(TEMPLATE, encoding="utf-8") as fh:
        for line in fh.read().splitlines():
            line = line.strip()
            if line.startswith("#"):
                groups.append((line, []))
            elif line:
                if not groups:
                    groups.append(("", []))
                groups[-1][1].append(line)
    return groups


def merge_gitignore():
    """Write .gitignore from the template, or append every template line it is missing."""
    path = os.path.join(ROOT, ".gitignore")
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as fh:
            existing = fh.read()
    have = set(l.strip() for l in existing.splitlines())
    blocks = []
    for comment, patterns in template_groups():
        missing = [p for p in patterns if p not in have]
        if missing:
            blocks.append("\n".join(([comment] if comment else []) + missing))
    if not blocks:
        return
    text = existing
    if text and not text.endswith("\n"):
        text += "\n"
    if text:
        text += "\n"
    text += "\n\n".join(blocks) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def is_dirty():
    return run_git(["status", "--porcelain"]).stdout.strip() != ""


def dirty_files():
    """The paths git status lists as changed or new."""
    out = run_git(["status", "--porcelain"]).stdout
    files = []
    for line in out.splitlines():
        if len(line) > 3:
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            files.append(path.strip('"'))
    return files


def refuse_if_dirty(action):
    """Never take unsaved work: stop and say which files need a save first."""
    if is_dirty():
        print("Unsaved changes in: %s" % ", ".join(dirty_files()))
        fail('Save them first (python tools/undo/undo.py save "...") or set them aside, then %s.' % action)


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
    created = adopted = False
    if not has_history():
        if run_git(["init", "-q", "-b", "main"], check=False).returncode != 0:
            run_git(["init", "-q"])
            run_git(["symbolic-ref", "HEAD", "refs/heads/main"])
        created = True
    elif not has_marker() and commit_count() > 0:
        if run_git(["config", "--get", "remote.origin.url"], check=False).stdout.strip():
            fail(CLONE)
        adopted = True
    merge_gitignore()
    if run_git(["config", "user.name"], check=False).stdout.strip() == "":
        run_git(["config", "user.name", "Workspace"])
    if run_git(["config", "user.email"], check=False).stdout.strip() == "":
        run_git(["config", "user.email", "workspace@localhost"])
    sha = commit_all("workspace built") if (commit_count() == 0 or adopted) else None
    run_git(["config", "--local", MARKER, "1"])
    if adopted:
        print("History adopted, %d saves." % commit_count())
    elif sha:
        print("History started: %s workspace built" % sha)
    elif created:
        print("History started, nothing to save yet.")
    else:
        print("History already on, %d saves." % commit_count())


def cmd_save(message):
    require_history()
    sha = commit_all(message)
    if sha is None:
        print("nothing to save")
    else:
        print("%s %s" % (sha, message))


def cmd_list():
    require_history()
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
    for record in out.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        sha, parents, subject, body = (record.split("\x1f") + ["", "", ""])[:4]
        reverted = reverted_sha(body)
        if sha in undone:
            continue
        if reverted:
            undone.add(reverted)
            continue
        if not parents.strip():
            return None
        return sha, subject
    return None


def reverted_sha(body):
    """The commit a revert commit's body names, or None for an ordinary save."""
    found = None
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("This reverts commit ") and line.endswith("."):
            found = line[len("This reverts commit "):-1].strip()
    return found


def cmd_undo():
    require_history()
    refuse_if_dirty("undo")
    if commit_count() < 2:
        fail("Nothing to undo yet.")
    target = undo_target()
    if target is None:
        fail("Nothing to undo yet.")
    sha, message = target
    r = run_git(["revert", "--no-edit", sha], check=False)
    if r.returncode != 0:
        if run_git(["revert", "--abort"], check=False).returncode != 0:
            print("History is mid-undo; run: git revert --abort")
        fail("Could not undo %s cleanly: %s" % (message, " ".join((r.stderr or r.stdout).split())))
    files = run_git(["show", "--stat", "--format=", "HEAD"]).stdout.rstrip()
    print("Undid: %s" % message)
    if files:
        print(files)


def cmd_redo():
    """Take back the most recent undo by reverting it. Only an undo can be redone."""
    require_history()
    refuse_if_dirty("redo")
    if commit_count() < 2:
        fail("Nothing to redo: the last save is not an undo.")
    body = run_git(["log", "-1", "--format=%b", "HEAD"]).stdout
    target = reverted_sha(body)
    if not target:
        fail("Nothing to redo: the last save is not an undo.")
    target_body = run_git(["log", "-1", "--format=%b", target], check=False).stdout
    if reverted_sha(target_body):
        fail("Nothing to redo: the last undo was already taken back.")
    message = run_git(["log", "-1", "--format=%s", target], check=False).stdout.strip()
    r = run_git(["revert", "--no-edit", "HEAD"], check=False)
    if r.returncode != 0:
        if run_git(["revert", "--abort"], check=False).returncode != 0:
            print("History is mid-redo; run: git revert --abort")
        fail("Could not redo cleanly: %s" % " ".join((r.stderr or r.stdout).split()))
    files = run_git(["show", "--stat", "--format=", "HEAD"]).stdout.rstrip()
    print("Redid: %s" % message)
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
    elif cmd == "redo":
        cmd_redo()
    else:
        fail("Unknown command: %s. Use init, save, list, undo or redo." % cmd)


if __name__ == "__main__":
    main(sys.argv[1:])
