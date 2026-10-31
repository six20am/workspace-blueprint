"""Brings a workspace up to the latest Workspace Blueprint without touching the owner's files.

    python tools/update/update.py            # check, then update if newer
    python tools/update/update.py --check    # say whether an update exists, change nothing
    python tools/update/update.py --force    # update even when the version matches

What it replaces: the template-owned paths listed in OWNED below, and only those. A skill
folder the owner built (one that does not exist upstream) is never removed. A template
file the owner edited is backed up to setup/update-backup/<date>/ before it is overwritten.
CLAUDE.md, CONTEXT.md, voice.md, the owner's folders, setup/setup-report.md and
setup/gap-log.md are never read or written.

After the files land it runs the installer with the no-launch flag, which installs any tool
new to setup/tools.json and skips everything already present. It writes setup/update-report.md.

Standard library only. Needs a network connection to github.com.
"""
import argparse
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

REPO = "six20am/workspace-blueprint"
BRANCH = "main"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VERSION_FILE = os.path.join(ROOT, "setup", "version.json")
REPORT = os.path.join(ROOT, "setup", "update-report.md")

# Paths the template owns. Everything else in the workspace belongs to the owner.
OWNED = (
    ".claude/skills",
    "tools",
    "_reference",
    "setup/lib",
    "setup/tests",
    "setup/tools.json",
    "setup/SETUP.md",
    "setup/filing-styles.md",
    "setup/setup.ps1",
    "setup/setup.sh",
    "setup/mac_runner.py",
    "setup.cmd",
    "setup.command",
    "update.cmd",
    "update.command",
    "START-HERE.md",
    "AGENTS.md",
    "GEMINI.md",
)
NEVER = ("CLAUDE.md", "CONTEXT.md", "voice.md", "setup/setup-report.md", "setup/gap-log.md", "setup/update-report.md")


def fetch(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "workspace-blueprint-update", **({"Accept": accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def local_version():
    try:
        with open(VERSION_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"commit": None, "date": None}


def remote_commit():
    data = json.loads(fetch(f"https://api.github.com/repos/{REPO}/commits/{BRANCH}", "application/vnd.github+json"))
    return data["sha"], data["commit"]["committer"]["date"][:10]


def download_tree():
    """Returns (tempdir, extracted repo root)."""
    blob = fetch(f"https://codeload.github.com/{REPO}/zip/refs/heads/{BRANCH}")
    tmp = tempfile.mkdtemp(prefix="wb-update-")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            # Refuse paths that would land outside the temp dir.
            dest = os.path.realpath(os.path.join(tmp, info.filename))
            if not dest.startswith(os.path.realpath(tmp) + os.sep):
                raise RuntimeError(f"unsafe path in archive: {info.filename}")
        z.extractall(tmp)
    inner = [d for d in os.listdir(tmp) if os.path.isdir(os.path.join(tmp, d))]
    return tmp, os.path.join(tmp, inner[0])


def same_file(a, b):
    """Byte-equal after line-ending normalization, so a Windows checkout does not look changed."""
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read().replace(b"\r\n", b"\n") == fb.read().replace(b"\r\n", b"\n")
    except OSError:
        return False


def sync(src_root, backup_dir, log):
    """Copies OWNED paths from src_root into ROOT. Returns (added, changed) counts."""
    added = changed = 0
    for rel in OWNED:
        src = os.path.join(src_root, rel)
        dst = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        if os.path.isfile(src):
            a, c = copy_file(src, dst, rel, backup_dir, log)
            added += a; changed += c
            continue
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "node_modules", ".git")]
            for f in filenames:
                s = os.path.join(dirpath, f)
                r = os.path.relpath(s, src_root).replace(os.sep, "/")
                if r in NEVER:
                    continue
                a, c = copy_file(s, os.path.join(ROOT, r), r, backup_dir, log)
                added += a; changed += c
    return added, changed


def copy_file(src, dst, rel, backup_dir, log):
    if os.path.exists(dst):
        if same_file(src, dst):
            return 0, 0
        bk = os.path.join(backup_dir, rel)
        os.makedirs(os.path.dirname(bk), exist_ok=True)
        shutil.copy2(dst, bk)
        log.append(f"changed  {rel}")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return 0, 1
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    log.append(f"added    {rel}")
    return 1, 0


def run_installer():
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, "setup", "setup.ps1"), "-Yes", "-NoLaunch"]
    else:
        cmd = ["bash", os.path.join(ROOT, "setup", "setup.sh"), "--yes", "--no-launch"]
    try:
        return subprocess.call(cmd, cwd=ROOT)
    except OSError as e:
        print(f"installer did not start: {e}")
        return 1


def write_report(status, lines, remote, date, installer_rc):
    with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Update report\n\nRun: {dt.date.today().isoformat()}\nResult: {status}\nNow at: {remote[:12] if remote else 'unknown'} ({date or 'unknown'})\n\n")
        if lines:
            fh.write("## Files\n\n" + "\n".join(f"- {l}" for l in lines) + "\n\n")
        if installer_rc is not None:
            fh.write(f"## Installer\n\n{'Finished.' if installer_rc == 0 else 'Finished with problems. See setup/setup-report.md.'}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-install", action="store_true", help="copy files only, skip the installer")
    args = ap.parse_args()

    local = local_version()
    try:
        remote, date = remote_commit()
    except Exception as e:  # network, rate limit, offline
        print(f"Could not reach github.com: {e}")
        return 2

    if local.get("commit") == remote and not args.force:
        print(f"Up to date ({remote[:12]}, {date}).")
        return 0
    if args.check:
        print(f"Update available: {(local.get('commit') or 'none')[:12]} -> {remote[:12]} ({date}).")
        return 10

    print(f"Updating {(local.get('commit') or 'none')[:12]} -> {remote[:12]} ({date})...")
    tmp, src_root = download_tree()
    backup_dir = os.path.join(ROOT, "setup", "update-backup", dt.date.today().isoformat())
    log = []
    try:
        added, changed = sync(src_root, backup_dir, log)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"commit": remote, "date": date, "updated": dt.date.today().isoformat()}, fh, indent=1)

    rc = None if args.no_install else run_installer()
    write_report("updated", log, remote, date, rc)
    print(f"Done. {added} added, {changed} changed" + (f", backups in setup/update-backup/{os.path.basename(backup_dir)}/" if changed else "") + ". Report: setup/update-report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
