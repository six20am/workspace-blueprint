#!/usr/bin/env python3
"""Mac and Linux installer. Reads setup/tools.json and runs each tool's column for this platform:
check_mac and install_mac on a Mac (Homebrew), check_linux and install_linux on Linux (apt). A tool
whose check passes runs nothing. A failed tool is written down and the run keeps going. Writes
setup/setup-report.md in the same shape as the Windows report, then, on a Mac with the Claude Code
adapter, opens Claude.

Linux install commands start root steps with a literal "$SUDO ". It becomes "sudo -n " when the run
is not root and sudo exists, and is removed when the run is root (or there is no sudo).

Flags:
  --platform mac|linux  which column to run (default: linux on Linux, mac everywhere else)
  --only <id>           one tool and the tools it needs
  --dry-run             check only; tools that would install are listed, nothing is installed
  --no-launch           do not open Claude at the end
  --doctor              check-and-repair run: same work, a quiet summary, report titled "Doctor report"
  --adapter <name>      claude-code or other (default: setup/adapter.json, else claude-code);
                        tools.json entries marked for the other adapter are skipped

Exit codes: 0 clean, 2 something failed (or Claude is missing), 4 no internet.
Standard library only."""
import argparse
import datetime
import json
import os
import platform as platform_mod
import re
import shlex
import shutil
import socket
import subprocess
import sys

OK = ("present", "installed", "planned")
COLS = {"mac": ("check_mac", "install_mac"), "linux": ("check_linux", "install_linux")}
DEFAULT_ADAPTER = "claude-code"
SUDO_TOKEN = re.compile(r"\$SUDO(?![A-Za-z0-9_])\s*")


def load_tools(path):
    with open(path, encoding="utf-8") as f:
        tools = json.load(f)
    for t in tools:
        t.setdefault("needs", [])
        t.setdefault("install_mac", [])
        t.setdefault("install_linux", [])
        t.setdefault("check_mac", None)
        t.setdefault("check_linux", None)
        t.setdefault("login", None)
        t.setdefault("adapter", None)
    return tools


def shell_quote(s):
    return shlex.quote(s)


def select_tools(tools, only, adapter=None):
    """Every tool in file order, or one tool and its needs (needs first). Mirrors setup/lib/planner.ps1.
    With an adapter, entries marked for a different adapter are dropped; a dropped need is skipped."""
    if adapter:
        tools = [t for t in tools if not t.get("adapter") or t.get("adapter") == adapter]
    by_id = {t["id"]: t for t in tools}
    if only is not None and only not in by_id:
        print("no tool with id '%s'" % only)
        raise SystemExit(1)
    roots = [by_id[only]] if only else list(tools)
    ordered, seen = [], set()

    def add(t):
        if t["id"] in seen:
            return
        seen.add(t["id"])
        for n in t.get("needs", []):
            if n in by_id:
                add(by_id[n])
        ordered.append(t)

    for t in roots:
        add(t)
    return ordered


def with_sudo(cmd, sudo):
    """Replaces the literal $SUDO token with the sudo prefix, or removes it when there is none."""
    return SUDO_TOKEN.sub(lambda m: (sudo + " ") if sudo else "", cmd).strip()


def default_check(expr):
    if not expr:
        return False
    return subprocess.call(expr, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def default_run(cmd):
    print("  $ " + cmd, flush=True)
    return subprocess.call(cmd, shell=True)


def run_tools(tools, run, check, dry_run=False, platform="mac", doctor=False, sudo=""):
    check_col, install_col = COLS[platform]
    done = {}
    results = []
    present = 0
    for t in tools:
        r = {"id": t["id"], "name": t["name"], "area": t.get("area", ""), "status": "", "detail": "", "login": t.get("login")}
        # a need that is not in this run (dropped by the adapter filter) is ignored, not counted as missing
        missing = [n for n in t.get("needs", []) if done.get(n) not in OK + (None,)]
        check_expr = t.get(check_col)
        installs = [with_sudo(c, sudo) for c in (t.get(install_col) or [])]
        if check(check_expr):
            r["status"] = "present"
            present += 1
            if not doctor:
                print("  %s: already present" % t["name"], flush=True)
        elif missing:
            r["status"], r["detail"] = "skipped", "needs " + ", ".join(missing)
        elif not installs:
            r["status"] = "manual"
        elif dry_run:
            r["status"] = "planned"
        else:
            print("Installing " + t["name"] + "...", flush=True)
            try:
                for cmd in installs:
                    code = run(cmd)
                    if code != 0:
                        raise RuntimeError("exit code %d" % code)
                r["status"] = "installed" if check(check_expr) else "failed"
                if r["status"] == "failed":
                    r["detail"] = "install ran but the check still fails"
            except Exception as e:  # one failed tool never stops the run
                if check(check_expr):
                    # brew, apt and pip sometimes exit non-zero after a successful install; a passing check is the better witness
                    r["status"], r["detail"] = "installed", "installer reported %s, but the check passes" % e
                else:
                    r["status"], r["detail"] = "failed", str(e)
        done[r["id"]] = r["status"]
        results.append(r)
    if doctor:
        print("%d already present" % present, flush=True)
    return results


def write_report(results, path, host, dry_run=False, doctor=False):
    heading = "# Doctor report" if doctor else "# Setup report"
    lines = [heading + (" (dry run, nothing installed)" if dry_run else ""), "",
             "Run: %s on %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), host), ""]
    attention = ([r for r in results if r["status"] == "failed"]
                 + [r for r in results if r["status"] == "skipped"]
                 + [r for r in results if r["status"] == "manual"])
    if attention:
        lines += ["## Needs attention", ""]
        for r in attention:
            lines.append("- **%s** (%s): %s" % (r["name"], r["status"], r["detail"] or r["login"] or ""))
        lines.append("")
    logins = [r for r in results if r.get("login")]
    if logins:
        lines += ["## Sign in yourself", ""] + ["- **%s**: %s" % (r["name"], r["login"]) for r in logins] + [""]
    sections = [("Installed now", "installed"), ("Already present", "present")]
    if dry_run:
        sections.append(("Would install", "planned"))
    for title, status in sections:
        rows = [r for r in results if r["status"] == status]
        if rows:
            lines += ["## " + title, ""] + ["- %s (%s)" % (r["name"], r["area"]) for r in rows] + [""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def online():
    try:
        socket.create_connection(("github.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


def default_platform():
    return "linux" if sys.platform.startswith("linux") else "mac"


def default_adapter(setup_dir):
    try:
        with open(os.path.join(setup_dir, "adapter.json"), encoding="utf-8") as f:
            return json.load(f).get("adapter") or DEFAULT_ADAPTER
    except (OSError, ValueError, AttributeError):
        return DEFAULT_ADAPTER


def sudo_prefix():
    geteuid = getattr(os, "geteuid", None)
    is_root = geteuid is not None and geteuid() == 0
    return "sudo -n" if not is_root and shutil.which("sudo") else ""


def parse_args(argv, setup_dir):
    p = argparse.ArgumentParser(description="Installs the workspace tools on a Mac or on Linux.")
    p.add_argument("--platform", choices=sorted(COLS), default=default_platform())
    p.add_argument("--only", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-launch", action="store_true")
    p.add_argument("--doctor", action="store_true")
    p.add_argument("--adapter", default=None)
    args, _unknown = p.parse_known_args(argv)  # setup.sh passes through flags meant for other steps (--yes)
    if not args.adapter:
        args.adapter = default_adapter(setup_dir)
    return args


def main(argv):
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    args = parse_args(argv, setup_dir)
    root = os.path.dirname(setup_dir)
    os.chdir(root)
    launches = args.platform == "mac" and args.adapter == "claude-code"
    if args.doctor:
        print("\nChecking the workspace tools. Anything missing is installed again.\n")
    else:
        print("\nThis sets up your workspace. It installs the tools the workspace uses" + (", then opens Claude." if launches else "."))
        print("It takes 15 to 30 minutes and downloads about 500 MB. It signs in to nothing.")
        print("If a tool fails, it is written down and setup keeps going.\n")
    if not online():
        print("No internet connection. Connect to the internet, then run setup again.")
        return 4
    tools = select_tools(load_tools(os.path.join(setup_dir, "tools.json")), args.only, adapter=args.adapter)
    sudo = sudo_prefix() if args.platform == "linux" else ""
    results = run_tools(tools, default_run, default_check, dry_run=args.dry_run, platform=args.platform,
                        doctor=args.doctor, sudo=sudo)
    report = os.path.join(setup_dir, "setup-report.md")
    write_report(results, report, platform_mod.node(), dry_run=args.dry_run, doctor=args.doctor)
    failed = sum(1 for r in results if r["status"] == "failed")
    print("\nDone. %d failed. Report: %s" % (failed, report))
    if not launches:
        return 2 if failed else 0
    have_claude = subprocess.call("command -v claude", shell=True, stdout=subprocess.DEVNULL) == 0
    if not have_claude:
        print("Claude Code did not install. Run setup again. If it still fails, install Claude Code from claude.com/code, then run setup again.")
        return 2
    if args.dry_run or args.no_launch:
        print("Open this folder in Claude Code and type: set this up")
        return 2 if failed else 0
    print("Opening Claude. Sign in if your browser asks, then answer its questions.")
    os.execvp("claude", ["claude", "set this up"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
