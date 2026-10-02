#!/usr/bin/env python3
"""Mac side of the installer. Reads setup/tools.json, runs each tool's Mac column,
writes setup/setup-report.md in the same shape as the Windows report, then opens Claude.
Standard library only. Never stops on a failed tool."""
import datetime
import json
import os
import platform
import shlex
import socket
import subprocess
import sys

OK = ("present", "installed", "planned")


def load_tools(path):
    with open(path, encoding="utf-8") as f:
        tools = json.load(f)
    for t in tools:
        t.setdefault("needs", [])
        t.setdefault("install_mac", [])
        t.setdefault("check_mac", None)
        t.setdefault("login", None)
    return tools


def shell_quote(s):
    return shlex.quote(s)


def select_tools(tools, only):
    """Every tool in file order, or one tool and its needs (needs first). Mirrors setup/lib/planner.ps1."""
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


def default_check(expr):
    if not expr:
        return False
    return subprocess.call(expr, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def default_run(cmd):
    print("  $ " + cmd, flush=True)
    return subprocess.call(cmd, shell=True)


def run_tools(tools, run, check, dry_run=False):
    done = {}
    results = []
    for t in tools:
        r = {"id": t["id"], "name": t["name"], "area": t.get("area", ""), "status": "", "detail": "", "login": t.get("login")}
        missing = [n for n in t.get("needs", []) if done.get(n) not in OK]
        if check(t.get("check_mac")):
            r["status"] = "present"
        elif missing:
            r["status"], r["detail"] = "skipped", "needs " + ", ".join(missing)
        elif not t.get("install_mac"):
            r["status"] = "manual"
        elif dry_run:
            r["status"] = "planned"
        else:
            print("Installing " + t["name"] + "...", flush=True)
            try:
                for cmd in t["install_mac"]:
                    code = run(cmd)
                    if code != 0:
                        raise RuntimeError("exit code %d" % code)
                r["status"] = "installed" if check(t.get("check_mac")) else "failed"
                if r["status"] == "failed":
                    r["detail"] = "install ran but the check still fails"
            except Exception as e:  # one failed tool never stops the run
                if check(t.get("check_mac")):
                    # brew and pip sometimes exit non-zero after a successful install; a passing check is the better witness
                    r["status"], r["detail"] = "installed", "installer reported %s, but the check passes" % e
                else:
                    r["status"], r["detail"] = "failed", str(e)
        done[r["id"]] = r["status"]
        results.append(r)
    return results


def write_report(results, path, host, dry_run=False):
    lines = ["# Setup report" + (" (dry run, nothing installed)" if dry_run else ""), "",
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


def main(argv):
    dry = "--dry-run" in argv
    no_launch = "--no-launch" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv and argv.index("--only") + 1 < len(argv) else None
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(setup_dir)
    os.chdir(root)
    print("\nThis sets up your workspace. It installs the tools Claude uses, then opens Claude.")
    print("It takes 15 to 30 minutes and downloads about 500 MB. It signs in to nothing.")
    print("If a tool fails, it is written down and setup keeps going. Claude will help with it after.\n")
    if not online():
        print("No internet connection. Connect to the internet, then run setup again.")
        return 4
    tools = select_tools(load_tools(os.path.join(setup_dir, "tools.json")), only)
    results = run_tools(tools, default_run, default_check, dry_run=dry)
    report = os.path.join(setup_dir, "setup-report.md")
    write_report(results, report, platform.node(), dry_run=dry)
    failed = sum(1 for r in results if r["status"] == "failed")
    print("\nDone. %d failed. Report: %s" % (failed, report))
    have_claude = subprocess.call("command -v claude", shell=True, stdout=subprocess.DEVNULL) == 0
    if not have_claude:
        print("Claude Code did not install. Run setup again. If it still fails, install Claude Code from claude.com/code, then run setup again.")
        return 2
    if dry or no_launch:
        print("Open this folder in Claude Code and type: set this up")
        return 2 if failed else 0
    print("Opening Claude. Sign in if your browser asks, then answer its questions.")
    os.execvp("claude", ["claude", "set this up"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
