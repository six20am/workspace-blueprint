"""Brings a workspace up to the latest Workspace Blueprint without touching the owner's files.

    python tools/update/update.py            # check, then update if newer
    python tools/update/update.py --check    # say whether an update exists, change nothing
    python tools/update/update.py --force    # update even when the version matches
    python tools/update/update.py --no-install   # copy files only, skip the installer or doctor

Which platform: setup/adapter.json, written by the build and never overwritten here, names the
adapter (claude-code, or other for the neutral path in ADAPT.md) and where its skills live. A workspace built before adapters
existed has no adapter.json and keeps its skills in .claude/skills; it is treated as claude-code,
and after its first sync the claude-code adapter.json is created (never overwritten).

Layout migration: setup/version.json gets "layout": 2 whenever this script writes it. A version.json
without it (stamped by the old updater, which could not see the new layout) means one full sync
even when the commit matches; --check reports it as an update.

What it replaces: the download is the raw repo, so this script applies the build's mapping itself
(see owned_pairs). The repo's skills/ lands in the adapter's skills folder (.claude/skills or
skills). For claude-code, adapters/claude-code/skills/ lands there too,
adapters/claude-code/platform.md lands at setup/platform.md, and every other file directly in
adapters/claude-code/ lands at the same name at the top of the workspace (publish.md never
ships). The neutral path has no adapter folder. The core tools/, _reference/, ADAPT.md and
installer files under setup/ are copied for both. A template file the owner edited is backed up
to setup/update-backup/<date>/ before it is overwritten.

Stale files: inside a skill folder that exists upstream, a file upstream no longer has (an old
helper, a leftover .bak) is backed up the same way and then removed. A skill folder the owner
built, one that does not exist upstream, is never touched.

What it never reads or writes: the adapter's map and router files (CLAUDE.md and CONTEXT.md, or
MAP.md, ROUTER.md and NOTES.md), voice.md, setup/adapter.json, setup/setup-report.md,
setup/gap-log.md and setup/update-report.md (written only as this run's report), plus every
folder the owner made.

After the files land: claude-code runs the installer with the no-launch flag, which installs any
tool new to setup/tools.json and skips everything already present. The neutral path runs the
doctor instead, because a reset of the agent's computer can lose installed programs. It writes
setup/update-report.md.

Standard library only. Needs a network connection to github.com.
"""
import argparse
import datetime as dt
import io
import json
import os
import posixpath
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

# The adapters the build knows, with the same fields it writes to setup/adapter.json.
ADAPTERS = {
    "claude-code": {"adapter": "claude-code", "skills_dir": ".claude/skills", "map": "CLAUDE.md", "router": "CONTEXT.md", "notes": "CONTEXT.md"},
    "other": {"adapter": "other", "skills_dir": "skills", "map": "MAP.md", "router": "ROUTER.md", "notes": "NOTES.md"},
}
DEFAULT_ADAPTER = "claude-code"
# Core paths the template owns, copied to the same place. Everything else belongs to the owner.
CORE_OWNED = (
    "ADAPT.md",
    "tools",
    "_reference",
    "setup/lib",
    "setup/tests",
    "setup/tools.json",
    "setup/SETUP.md",
    "setup/filing-styles.md",
    "setup/setup.ps1",
    "setup/setup.sh",
    "setup/runner.py",
    "setup/tools-reference",
)
# Adapters with a folder under adapters/ that overlays the core. The neutral path has none.
ADAPTER_FOLDERS = ("claude-code",)
# Files in an adapter folder that never land at the top of the workspace: maintainer notes, and
# platform.md, which lands at setup/platform.md instead.
ADAPTER_KEEP_OUT = ("publish.md", "platform.md")
IGNORED_DIRS = ("__pycache__", "node_modules", ".git")
# Never read or written, whatever the adapter. The map and router names are added per adapter.
ALWAYS_NEVER = ("voice.md", "setup/adapter.json", "setup/setup-report.md", "setup/gap-log.md", "setup/update-report.md")
EXEC = (".sh", ".command")
# setup/version.json carries "layout": 2 once this updater has synced the workspace at least once.
LAYOUT = 2


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


def clean_rel(rel):
    """A workspace-relative path in forward slashes, or ValueError when it is empty, absolute or climbs out."""
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError(f"empty path: {rel!r}")
    r = posixpath.normpath(rel.replace("\\", "/"))
    if r in (".", "") or r.startswith("/") or r == ".." or r.startswith("../") or ":" in r:
        raise ValueError(f"path outside the workspace: {rel!r}")
    return r


def safe_join(base, rel):
    """base joined with a relative path, refusing any result outside base (symlinks resolved)."""
    r = clean_rel(rel)
    path = os.path.join(base, *r.split("/"))
    real_base = os.path.realpath(base)
    real = os.path.realpath(path)
    try:
        inside = os.path.commonpath([os.path.normcase(real), os.path.normcase(real_base)]) == os.path.normcase(real_base)
    except ValueError:   # different drives
        inside = False
    if not inside or os.path.normcase(real) == os.path.normcase(real_base):
        raise ValueError(f"refusing to write outside {base}: {rel}")
    return path


def read_adapter(root):
    """The adapter this workspace was built for, from setup/adapter.json. A workspace without one
    (built before adapters existed), or one naming an adapter not in ADAPTERS, is claude-code. A bad skills_dir falls back to the adapter's default."""
    data = {}
    try:
        with open(os.path.join(root, "setup", "adapter.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    name = data.get("adapter")
    if not isinstance(name, str) or name not in ADAPTERS:
        return dict(ADAPTERS[DEFAULT_ADAPTER])   # unknown or hostile name: the claude-code default, entirely
    adapter = dict(ADAPTERS[name])
    for key in ("skills_dir", "map", "router", "notes"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            try:
                adapter[key] = clean_rel(value)
            except ValueError:
                pass   # keep the default rather than follow a path out of the workspace
    return adapter


def never_paths(adapter):
    """Workspace-relative paths update never reads or writes, for this adapter."""
    names = set(ALWAYS_NEVER)
    for key in ("map", "router", "notes"):
        if adapter.get(key):
            names.add(clean_rel(adapter[key]))
    return names


def owned_pairs(adapter, src_root):
    """[(src_rel, dst_rel)] from the raw repo tree to the owner's workspace, in copy order: core first,
    then the adapter folder, so an adapter file wins over a core file at the same place (as in the build).
    The neutral path (other) has no adapter folder: the core alone."""
    name = adapter["adapter"]
    skills_dir = clean_rel(adapter["skills_dir"])
    pairs = [("skills", skills_dir)]
    pairs += [(rel, rel) for rel in CORE_OWNED]
    if name not in ADAPTER_FOLDERS:
        return pairs
    adir = f"adapters/{name}"
    pairs.append((f"{adir}/skills", skills_dir))
    pairs.append((f"{adir}/platform.md", "setup/platform.md"))
    folder = os.path.join(src_root, "adapters", name)
    if os.path.isdir(folder):
        for f in sorted(os.listdir(folder)):
            if f not in ADAPTER_KEEP_OUT and os.path.isfile(os.path.join(folder, f)):
                pairs.append((f"{adir}/{f}", f))
    return pairs


def _files_under(base):
    """Relative forward-slash paths of every file under base, skipping ignored folders."""
    out = set()
    if not os.path.isdir(base):
        return out
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            out.add(os.path.relpath(os.path.join(dirpath, f), base).replace(os.sep, "/"))
    return out


def stale(src_dir, dst_dir):
    """Files in dst_dir that no upstream folder has. src_dir is one folder or a list of them (a skill can
    exist in the core and in the adapter). Returns sorted paths relative to dst_dir."""
    srcs = [src_dir] if isinstance(src_dir, str) else list(src_dir)
    upstream = set()
    for s in srcs:
        upstream |= _files_under(s)
    return sorted(_files_under(dst_dir) - upstream)


def _skill_folders(src_root, adapter):
    """{skill folder name: [upstream folders]} for every skill folder in the core or the adapter."""
    found = {}
    bases = [os.path.join(src_root, "skills")]
    if adapter["adapter"] in ADAPTER_FOLDERS:
        bases.append(os.path.join(src_root, "adapters", adapter["adapter"], "skills"))
    for base in bases:
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            if d not in IGNORED_DIRS and os.path.isdir(os.path.join(base, d)):
                found.setdefault(d, []).append(os.path.join(base, d))
    return found


def _is_never(rel, never):
    return os.path.normcase(rel) in {os.path.normcase(n) for n in never}


def sync(src_root, root, adapter, backup_dir, log):
    """Copies the template-owned files from the raw repo tree into root for this adapter, then removes
    stale files from skill folders that exist upstream. Returns (added, changed, removed)."""
    never = never_paths(adapter)
    plan = {}   # dst_rel -> src path; a later pair overrides an earlier one
    for src_rel, dst_rel in owned_pairs(adapter, src_root):
        src = os.path.join(src_root, *src_rel.split("/"))
        if os.path.isfile(src):
            plan[dst_rel] = src
        elif os.path.isdir(src):
            for r in sorted(_files_under(src)):
                plan[f"{dst_rel}/{r}"] = os.path.join(src, *r.split("/"))
    added = changed = removed = 0
    for dst_rel in sorted(plan):
        if _is_never(dst_rel, never):
            continue
        a, c = copy_file(plan[dst_rel], safe_join(root, dst_rel), dst_rel, backup_dir, log)
        added += a; changed += c

    skills_dir = clean_rel(adapter["skills_dir"])
    for name, srcs in sorted(_skill_folders(src_root, adapter).items()):
        folder_rel = f"{skills_dir}/{name}"
        dst_dir = safe_join(root, folder_rel)
        if not os.path.isdir(dst_dir):
            continue
        for r in stale(srcs, dst_dir):
            rel = f"{folder_rel}/{r}"
            if _is_never(rel, never):
                continue
            target = safe_join(root, rel)
            bk = safe_join(backup_dir, rel)
            os.makedirs(os.path.dirname(bk), exist_ok=True)
            shutil.copy2(target, bk)
            os.remove(target)
            log.append(f"removed  {rel}")
            removed += 1
        # empty folders left behind go too; the skill folder itself still holds upstream files
        for dirpath, dirnames, filenames in os.walk(dst_dir, topdown=False):
            if dirpath != dst_dir and not os.listdir(dirpath):
                os.rmdir(dirpath)
    return added, changed, removed


def needs_update(local, remote, force):
    """Returns "up-to-date", "update" or "migrate". A version.json without "layout": 2 was stamped by an
    updater from before the adapters (or by the build) and gets one full sync even when the commit matches."""
    try:
        layout = int(local.get("layout") or 0)
    except (TypeError, ValueError):
        layout = 0
    if layout < LAYOUT:
        return "migrate"
    if local.get("commit") == remote and not force:
        return "up-to-date"
    return "update"


def write_default_adapter(root):
    """Creates setup/adapter.json with the claude-code default when it is missing. Never overwrites one."""
    path = safe_join(root, "setup/adapter.json")
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(ADAPTERS[DEFAULT_ADAPTER], indent=1) + "\n")
    return True


def write_version(root, remote, date):
    with open(safe_join(root, "setup/version.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"commit": remote, "date": date, "updated": dt.date.today().isoformat(), "layout": LAYOUT}, fh, indent=1)


def apply_update(src_root, root, backup_dir, log, remote, date):
    """One update from an extracted tree: sync for this workspace's adapter, create adapter.json when an
    old install has none, stamp version.json with the commit and the layout. Returns (adapter, counts)."""
    adapter = read_adapter(root)
    counts = sync(src_root, root, adapter, backup_dir, log)
    if write_default_adapter(root):
        log.append("added    setup/adapter.json")
    write_version(root, remote, date)
    return adapter, counts


def same_file(a, b):
    """Byte-equal after line-ending normalization, so a Windows checkout does not look changed."""
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read().replace(b"\r\n", b"\n") == fb.read().replace(b"\r\n", b"\n")
    except OSError:
        return False


def _place(src, dst, rel):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    if rel.endswith(EXEC) and os.name != "nt":
        os.chmod(dst, 0o755)   # the zip download does not keep the executable bit


def copy_file(src, dst, rel, backup_dir, log):
    if os.path.exists(dst):
        if same_file(src, dst):
            return 0, 0
        bk = safe_join(backup_dir, rel)
        os.makedirs(os.path.dirname(bk), exist_ok=True)
        shutil.copy2(dst, bk)
        log.append(f"changed  {rel}")
        _place(src, dst, rel)
        return 0, 1
    _place(src, dst, rel)
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


def doctor_command(root):
    """The neutral path's check-and-repair run, first one present: the doctor, then the setup runner in doctor mode."""
    candidates = (
        ("tools/doctor/doctor.py", []),
        ("setup/runner.py", ["--doctor", "--no-launch"]),
    )
    for rel, args in candidates:
        path = os.path.join(root, *rel.split("/"))
        if os.path.isfile(path):
            return [sys.executable, path] + args
    return None


def run_doctor():
    cmd = doctor_command(ROOT)
    if cmd is None:
        print("no doctor found: tools/doctor/doctor.py and setup/runner.py are both missing")
        return 1
    try:
        return subprocess.call(cmd, cwd=ROOT)
    except OSError as e:
        print(f"doctor did not start: {e}")
        return 1


def write_report(status, lines, remote, date, installer_rc, counts=None):
    with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Update report\n\nRun: {dt.date.today().isoformat()}\nResult: {status}\nNow at: {remote[:12] if remote else 'unknown'} ({date or 'unknown'})\n")
        if counts:
            fh.write(f"Files: {counts[0]} added, {counts[1]} changed, {counts[2]} removed\n")
        fh.write("\n")
        if lines:
            fh.write("## Files\n\n" + "\n".join(f"- {l}" for l in lines) + "\n\n")
            if any(l.startswith(("changed", "removed")) for l in lines):
                fh.write("Changed and removed files were backed up to setup/update-backup/ first.\n\n")
        if installer_rc is not None:
            fh.write(f"## Installer\n\n{'Finished.' if installer_rc == 0 else 'Finished with problems. See setup/setup-report.md.'}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-install", action="store_true", help="copy files only, skip the installer or doctor")
    args = ap.parse_args()

    local = local_version()
    try:
        remote, date = remote_commit()
    except Exception as e:  # network, rate limit, offline
        print(f"Could not reach github.com: {e}")
        return 2

    decision = needs_update(local, remote, args.force)
    if decision == "up-to-date":
        print(f"Up to date ({remote[:12]}, {date}).")
        return 0
    if args.check:
        if decision == "migrate":
            print("Update available (layout migration).")
        else:
            print(f"Update available: {(local.get('commit') or 'none')[:12]} -> {remote[:12]} ({date}).")
        return 10
    if decision == "migrate":
        print("First update on the new layout; syncing everything.")

    print(f"Updating {(local.get('commit') or 'none')[:12]} -> {remote[:12]} ({date})...")
    tmp, src_root = download_tree()
    backup_dir = os.path.join(ROOT, "setup", "update-backup", dt.date.today().isoformat())
    log = []
    try:
        adapter, (added, changed, removed) = apply_update(src_root, ROOT, backup_dir, log, remote, date)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if args.no_install:
        rc = None
    elif adapter["adapter"] == "other":
        rc = run_doctor()
    else:
        rc = run_installer()
    write_report("updated", log, remote, date, rc, (added, changed, removed))
    backups = f", backups in setup/update-backup/{os.path.basename(backup_dir)}/" if (changed or removed) else ""
    print(f"Done. {added} added, {changed} changed, {removed} removed{backups}. Report: setup/update-report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
