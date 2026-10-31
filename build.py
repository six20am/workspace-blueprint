#!/usr/bin/env python3
"""Builds one output per adapter: the zip people download (Claude Code) and the folder mirrored
to the Grok Bot repo. Writes skills/INDEX.md first, then scans every text file and refuses on any leak.
Standard library only.

    python build.py                                    # both: the zip in ~/Downloads, the folder in dist/grokbot-blueprint
    python build.py --adapter claude-code --out <path.zip>
    python build.py --adapter grok-bot --grok-dir <dir> [--push]
    python build.py [--adapter claude-code|grok-bot|all] [--out <zip>] [--grok-dir <dir>] [--push] [--names <file>]
"""
import argparse
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

TOP = "Six20AM Workspace Blueprint"
ADAPTERS = {
    "claude-code": {"skills_dir": ".claude/skills", "map": "CLAUDE.md", "router": "CONTEXT.md", "notes": "CONTEXT.md"},
    "grok-bot": {"skills_dir": "skills", "map": "MAP.md", "router": "ROUTER.md", "notes": "NOTES.md"},
}
# core paths an adapter leaves out: a Bot has no Windows installer
ADAPTER_SKIP = {"grok-bot": ("setup/setup.ps1", "setup/lib/", "setup/tests/")}
GROK_REPO = "github.com/six20am/grokbot-blueprint.git"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".pytest_cache", ".superpowers", ".impeccable",
             ".agents", ".remotion"}  # .agents: skills a setup run installs (remotion-dev/skills has no license); .remotion: render staging
# folders skipped by repo-relative path: render output left in a tool folder
SKIP_PATHS = {"tools/motion/out"}
# the repo's own test suite, design doc, website, CI, build outputs, and the adapter folders (overlaid per output); setup/tests ships
SKIP_ROOT_DIRS = {"tests", "docs", "site", ".github", "dist", "adapters"}
SKIP_FILES = {".git", "build.py", "setup-report.md", "update-report.md"}  # .git is a file in a submodule checkout
SKIP_ROOT_FILES = {"README.md"}     # the GitHub readme; START-HERE.md is the product's front page
GENERATED = ("setup/adapter.json", "setup/version.json")
TEXT = (".md", ".json", ".ps1", ".sh", ".command", ".cmd", ".py", ".txt", ".mjs", ".js", ".cjs", ".yml", ".yaml", ".toml", ".ts", ".tsx")
LF = (".sh", ".command", ".py", ".md", ".json", ".mjs", ".js", ".cjs", ".yml", ".yaml", ".toml", ".ts", ".tsx")
EXEC = (".command", ".sh")
SECRET_RE = re.compile(r"(^|/)(\.env(\.[^/]*)?|accounts\.json|instances\.json|[^/]*secret[^/]*\.(json|env)|[^/]*\.pem|[^/]*\.key)$", re.I)
SECRET_ALLOW = re.compile(r"\.example(\.json)?$", re.I)
FIXED = ["\u2014", "mtesi", "C:\\Users\\", "/c/Users/", "shared-core", "shared-systems", "work-log"]
# the maintainer's own names, caught even when no parent-workspace names list exists (a public clone)
FIXED_CI = ["six20am", "motus", "machado", "michael"]
HARD_RULE = re.compile(r"Hard Rule \d", re.I)     # a numbered rule from the parent workspace; a "Hard rules" heading is fine
HEX_ID = re.compile(r"\b[0-9a-f]{32}\b")
# files that may name the maintainer, keyed by repo-relative source path: the updater and the publish notes name the public repos
ALLOWED = {"README.md", "docs/design.md", "tools/update/update.py",
           "adapters/grok-bot/README.md"}  # the mirror repo's README: names the two public repos on purpose
# maintainer notes inside an adapter folder; never walked, scanned or shipped (like the root README.md)
ADAPTER_SKIP_FILES = ("publish.md",)
# vendor code shipped as-is; scanned by eye, not by string (same exemption as tests/test_shipped.py)
VENDOR = ("skills/last30days/scripts/", "skills/agent-reach/_references")
SENTENCE_END = re.compile(r"(?<!\be\.g)(?<!\bi\.e)(?<!\betc)\.(?=\s|$)")


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


def git_sha(repo):
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def version_json(repo):
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()
        date = subprocess.check_output(["git", "log", "-1", "--format=%cs"], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        sha, date = None, None
    return '{\n "commit": %s,\n "date": %s,\n "updated": null,\n "layout": 2\n}\n' % (
        ('"%s"' % sha) if sha else "null", ('"%s"' % date) if date else "null")


def adapter_json(adapter):
    return json.dumps(dict({"adapter": adapter}, **ADAPTERS[adapter]), indent=1) + "\n"


def first_sentence(skill_md):
    """The first sentence of a SKILL.md description: a one-line quoted value or a folded/literal block (>, >-, |)."""
    with open(skill_md, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    text = ""
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            break
        if not line.startswith("description:"):
            continue
        value = line[len("description:"):].strip()
        if value[:1] in (">", "|"):
            parts = []
            for nxt in lines[i + 1:]:
                if not nxt.strip() or not nxt[:1].isspace():
                    break   # a blank line ends the first paragraph; an unindented line ends the block
                parts.append(nxt.strip())
            text = " ".join(parts)
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            text = value
        break
    text = " ".join(text.split())
    m = SENTENCE_END.search(text)
    return text[:m.end()] if m else text


def write_index(repo):
    """Writes skills/INDEX.md: one line per core skill, `- \\`name\\`: first sentence of its description`."""
    skills = os.path.join(repo, "skills")
    rows = []
    for name in sorted(os.listdir(skills)) if os.path.isdir(skills) else []:
        md = os.path.join(skills, name, "SKILL.md")
        if os.path.isfile(md):
            rows.append("- `%s`: %s" % (name, first_sentence(md)))
    text = "# Skills index\n\nOne line per skill, from its description. Generated by the build; do not edit by hand.\n\n" + "\n".join(rows) + "\n"
    os.makedirs(skills, exist_ok=True)
    with open(os.path.join(skills, "INDEX.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text


def walk(base, skip_root_dirs=(), skip_root_files=()):
    for dirpath, dirs, fs in os.walk(base):
        at_root = os.path.abspath(dirpath) == os.path.abspath(base)
        here = os.path.relpath(dirpath, base).replace("\\", "/")
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (at_root and d in skip_root_dirs)
                         and (d if at_root else here + "/" + d) not in SKIP_PATHS)
        for f in sorted(fs):
            if f in SKIP_FILES or (at_root and f in skip_root_files):
                continue
            p = os.path.join(dirpath, f)
            yield os.path.relpath(p, base).replace("\\", "/"), p


def files(repo):
    """Core files, repo-relative: everything outside the skipped root folders and the adapter folders."""
    return walk(repo, SKIP_ROOT_DIRS, SKIP_ROOT_FILES)


def map_skills(rel, skills_dir):
    return skills_dir + rel[len("skills"):] if rel.startswith("skills/") else rel


def entries(repo, adapter):
    """(source_rel, arc_rel, path) for one output: core files, then the adapter folder overlaid at the root.
    An adapter file overrides a core file at the same arc path; generated files are never taken from disk."""
    cfg = ADAPTERS[adapter]
    skip = ADAPTER_SKIP.get(adapter, ())
    overlay = []
    for rel, p in walk(os.path.join(repo, "adapters", adapter), skip_root_files=ADAPTER_SKIP_FILES):
        arc = "setup/platform.md" if rel == "platform.md" else map_skills(rel, cfg["skills_dir"])
        overlay.append(("adapters/%s/%s" % (adapter, rel), arc, p))
    taken = {arc for _, arc, _ in overlay}
    out = []
    for rel, p in files(repo):
        if skip and rel.startswith(skip):
            continue
        arc = map_skills(rel, cfg["skills_dir"])
        if arc not in taken:
            out.append((rel, arc, p))
    return [e for e in out + overlay if e[1] not in GENERATED]


def output_files(repo, adapter):
    """Yields (arc_rel, source_path) for every file an adapter's output ships, before the generated ones."""
    for _, arc, p in entries(repo, adapter):
        yield arc, p


def collect(repo, adapter, names):
    """Writes the index, scans every shipped source, and returns [(arc_rel, path)] or raises LeakError."""
    if adapter not in ADAPTERS:
        raise ValueError("unknown adapter %r" % adapter)
    write_index(repo)
    leaks = []
    included = []
    for rel, arc, p in entries(repo, adapter):
        if is_secret(rel):
            leaks.append("%s: secret-shaped file" % rel)
            continue
        if rel.endswith(TEXT) and rel not in ALLOWED and not rel.startswith(VENDOR):
            with open(p, encoding="utf-8", errors="replace") as fh:
                probs = scan_text(fh.read(), names)
            if probs:
                leaks.append("%s: %s" % (rel, ", ".join(probs)))
        included.append((arc, p))
    if leaks:
        raise LeakError("refusing to build:\n  " + "\n  ".join(leaks))
    return included


def read_shipped(arc, p):
    with open(p, "rb") as fh:
        data = fh.read()
    if arc.endswith(LF):
        data = data.replace(b"\r\n", b"\n")   # an output built on Windows must not ship CRLF scripts to a Mac or a Bot
    return data


def generated(repo, adapter):
    # the commit this output was built from, so tools/update can tell whether anything is newer
    return [("setup/adapter.json", adapter_json(adapter)), ("setup/version.json", version_json(repo))]


def write_report(path, adapter, target, rels):
    lines = ["# Build report", "", "Built %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "Adapter: %s" % adapter, "Output: %s" % target, "Files: %d" % len(rels), ""]
    lines += ["- " + rel for rel in rels]
    report = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report)
    return report


def build(repo, out, names, adapter="claude-code", top=TOP):
    """Writes the zip for one adapter under a single top folder. Returns the build report."""
    included = collect(repo, adapter, names)
    gen = generated(repo, adapter)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, p in included:
            zi = zipfile.ZipInfo.from_file(p, top + "/" + arc)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3   # Unix: a Mac honors the mode bits only when the creator says Unix
            zi.external_attr = ((0o755 if arc.endswith(EXEC) else 0o644) << 16)
            z.writestr(zi, read_shipped(arc, p))
        for arc, text in gen:
            zi = zipfile.ZipInfo(top + "/" + arc, datetime.datetime.now().timetuple()[:6])
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = 0o644 << 16
            z.writestr(zi, text)
    rels = [arc for arc, _ in included] + [arc for arc, _ in gen]
    return write_report(os.path.splitext(out)[0] + "-build-report.md", adapter, out, rels)


def _inside(path, parent):
    """True when path is parent or anywhere below it (case-insensitive on Windows)."""
    path, parent = os.path.normcase(path), os.path.normcase(parent)
    try:
        return os.path.commonpath([path, parent]) == parent
    except ValueError:   # different drives
        return False


def check_out_dir(repo, out_dir):
    """Refuses an output folder that would wipe or pollute the repo: the repo itself, any folder above it,
    or any folder inside it other than one under <repo>/dist/."""
    out, root = os.path.realpath(out_dir), os.path.realpath(repo)
    if _inside(root, out):
        raise ValueError("refusing to build into %s: it is the repo or a folder above it, and clearing it would delete the repo" % out_dir)
    dist = os.path.join(root, "dist")
    if _inside(out, root) and not (_inside(out, dist) and os.path.normcase(out) != os.path.normcase(dist)):
        raise ValueError("refusing to build into %s: inside the repo, only a folder under dist/ may be an output" % out_dir)


def build_folder(repo, out_dir, names, adapter):
    """Writes one adapter's output as a plain folder, cleared first except its .git. Returns the build report."""
    check_out_dir(repo, out_dir)
    included = collect(repo, adapter, names)
    os.makedirs(out_dir, exist_ok=True)
    for entry in os.listdir(out_dir):
        if entry == ".git":
            continue
        p = os.path.join(out_dir, entry)
        if os.path.isdir(p) and not os.path.islink(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
    items = [(arc, read_shipped(arc, p)) for arc, p in included]
    items += [(arc, text.encode("utf-8")) for arc, text in generated(repo, adapter)]
    for arc, data in items:
        dest = os.path.join(out_dir, *arc.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        os.chmod(dest, 0o755 if arc.endswith(EXEC) else 0o644)
    report_path = os.path.abspath(out_dir).rstrip("\\/") + "-build-report.md"
    return write_report(report_path, adapter, out_dir, [arc for arc, _ in items])


def push_command(url, token):
    """(argv, env_additions) for the force-push. With a token, the credential travels as an http header set
    through GIT_CONFIG_* env vars, so it is in neither the URL, the process list, .git/config nor a credential
    helper (helpers are switched off for this push). Without one, the user's own credentials are used."""
    argv = ["git", "push", "--force", url, "HEAD:main"]
    if not token:
        return argv, {}
    basic = base64.b64encode(("x-access-token:" + token).encode("utf-8")).decode("ascii")
    return argv, {
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "http.https://github.com/.extraHeader",
        "GIT_CONFIG_VALUE_0": "Authorization: Basic " + basic,
        "GIT_CONFIG_KEY_1": "credential.helper",
        "GIT_CONFIG_VALUE_1": "",
    }


def push_grok(out_dir, sha):
    """Commits the grok folder and force-pushes it to the mirror's main. The token never reaches the output."""
    token = os.environ.get("GROKBOT_PUSH_TOKEN")
    secrets = [s for s in (token, token and base64.b64encode(("x-access-token:" + token).encode("utf-8")).decode("ascii")) if s]

    def git(argv, extra_env=None):
        env = dict(os.environ, **(extra_env or {}))
        try:
            r = subprocess.run(argv, cwd=out_dir, env=env, check=True, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            msg = "git %s failed: %s" % (argv[1], (e.stderr or "").strip())
            for s in secrets:
                msg = msg.replace(s, "***")
            raise RuntimeError(msg) from None
        return r.stdout

    if not os.path.isdir(os.path.join(out_dir, ".git")):
        git(["git", "init", "-b", "main"])
    git(["git", "add", "-A"])
    if git(["git", "status", "--porcelain"]).strip():
        git(["git", "commit", "-m", "Mirror of six20am/workspace-blueprint %s" % (sha or "unknown")])
    argv, extra = push_command("https://" + GROK_REPO, token)
    git(argv, extra)


def main():
    repo = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", choices=["claude-code", "grok-bot", "all"], default="all")
    ap.add_argument("--out", default=os.path.join(os.path.expanduser("~"), "Downloads", TOP + ".zip"), help="the Claude Code zip")
    ap.add_argument("--grok-dir", default=os.path.join(repo, "dist", "grokbot-blueprint"), help="the Grok Bot folder")
    ap.add_argument("--push", action="store_true", help="commit and force-push the Grok Bot folder to its mirror repo")
    ap.add_argument("--names", help="file with one extra forbidden string per line")
    a = ap.parse_args()
    if a.push and a.adapter != "grok-bot":
        ap.error("--push is only valid with --adapter grok-bot")
    names = default_names(repo)
    if a.names:
        with open(a.names, encoding="utf-8") as fh:
            names += [l.strip() for l in fh if l.strip()]
    try:
        if a.adapter in ("claude-code", "all"):
            report = build(repo, a.out, names, adapter="claude-code")
            print("claude-code: wrote %s (%s)" % (a.out, report.splitlines()[5]))
        if a.adapter in ("grok-bot", "all"):
            report = build_folder(repo, a.grok_dir, names, adapter="grok-bot")
            print("grok-bot: wrote %s (%s)" % (a.grok_dir, report.splitlines()[5]))
            if a.push:
                push_grok(a.grok_dir, git_sha(repo))
                print("grok-bot: pushed to https://" + GROK_REPO)
    except (LeakError, ValueError) as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
