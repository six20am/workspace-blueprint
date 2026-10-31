---
name: doctor
description: "Checks every tool and sign-in the workspace needs and re-installs only what is missing. Use when the person asks, after a reset of the machine, after an update, or at the end of setup."
---

# doctor

Run this when the person asks for it, after the machine was reset or rebuilt, after `update` finishes, and at the end of setup.

## The one command

```
python tools/doctor/doctor.py   # python3 on Mac and Linux
```

Run it from the workspace folder; on Windows `python` works from there too. It runs the platform's installer in check-then-install mode, so anything already present is left alone. Add `--dry-run` to check without installing anything. A first run on a new machine can take 15 to 30 minutes; a re-run picks up where the last one stopped.

## Reading the result

It prints three lines, then the sign-ins:

- `Present: N` is what was already installed and working.
- `Installed now: N (names)` is what this run added.
- `Failed: N`, with one indented line per tool and the reason. `Failed: 0, nothing to fix` means all is well.
- `Sign in yourself:` lists the accounts the person connects by hand, one line each with what to do.

Exit 0 means nothing failed; exit 2 means something did. The full report is `setup/setup-report.md`.

## What to say

Two lines. First: how many tools are ready, and what was installed now. Second: what failed and the one thing to try, or the sign-ins that need them, as "Two things need you: ...". If nothing failed and nothing needs them, say the workspace is healthy.

## Never

- Type a password, key, code or token for the person. Sign-ins are theirs to do.
- Re-install a tool that is present, or uninstall one to "start fresh".
- Run install commands from `setup/tools.json` by hand. Fix the cause, then run the doctor again.
