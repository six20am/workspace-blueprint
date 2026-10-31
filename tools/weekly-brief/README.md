# weekly-brief

Writes a one-page brief of the week in this workspace.

```
python tools/weekly-brief/brief.py                      # the last 7 days, ending today
python tools/weekly-brief/brief.py --days 14 --out x.md
python tools/weekly-brief/brief.py --today 2026-10-31   # end the week on that date
```

The brief is titled `# Week of <start> to <end>` and has five sections, each saying `Nothing.` when empty:

- **Came in**: files changed in the window, newest first, capped at 40. Skips `setup/`, `tools/`, `_reference/`, the skills folder, hidden files, `node_modules`, `__pycache__` and earlier briefs.
- **Went out**: the subset inside a folder named `delivery`, `delivered`, `sent`, `out`, `3-delivery` or `6-comms` (any case).
- **Dates coming up**: lines in `paperwork/dates.md` dated today to 14 days out. The file is optional.
- **Gaps logged**: lines in `setup/gap-log.md` dated inside the window.
- **Sign-ins needed**: the bullets under `## Sign in yourself` in `setup/setup-report.md`.

It reads file dates only, plus those three files and the router file (named in `setup/adapter.json`).
It saves `weekly-brief-YYYY-MM-DD.md` to `--out`, else the folder a router line names after the word
"notes" in backticks, else the workspace folder, and prints the path. Standard library only.
