# doctor

Checks every tool and sign-in the workspace needs and re-installs only what is missing.

```
python tools/doctor/doctor.py             # check, install what is missing, print the summary
python tools/doctor/doctor.py --dry-run   # check only, install nothing
```

It reads `setup/adapter.json` (no file means claude-code), then runs the platform's installer in
check-then-install mode: `setup/setup.ps1 -Yes -NoLaunch` on Windows, `setup/runner.py --doctor
--no-launch --adapter <adapter>` on a Mac or Linux. Every entry in `setup/tools.json` is checked
first, so a present tool is never touched and a re-run picks up where the last one stopped.

Then it reads `setup/setup-report.md` and prints:

```
Present: 34
Installed now: 2 (jq (reads and edits JSON), Pandoc (document converting))
Failed: 0, nothing to fix
```

followed by `Sign in yourself:` and one line per account the person connects by hand. Exit 0 when nothing failed, 2 when something did or the installer stopped before writing a report.
`tools/update/update.py` runs it after a sync on the neutral path (`ADAPT.md`).
