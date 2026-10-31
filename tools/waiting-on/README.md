# waiting-on

Reads `waiting-on.md` in the workspace folder and prints what is overdue and what is still within its wait. Used by the `waiting-on` skill; the weekly brief reads the same file.

```
python tools/waiting-on/waiting.py                       # python3 on Mac and Linux
python tools/waiting-on/waiting.py --today 2026-11-02 --after 10
```

One line per thing owed: `YYYY-MM-DD | who | what | how`. Add `by YYYY-MM-DD` to give a line its own due date, `nudged YYYY-MM-DD` once a reminder went out. Lines under `## Came back` are finished and skipped. Without a `by` date an item is overdue after 7 days (`--after` changes that). Standard library only; reads one file, changes nothing, sends nothing.
