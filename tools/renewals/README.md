# renewals

Reads `renewals.md` in the workspace folder and prints what is past, due within 7 days, within 30 days, and later. Used by the `renewals` skill; the weekly brief reads the same file for its 30-day list.

```
python tools/renewals/renewals.py                       # python3 on Mac and Linux
python tools/renewals/renewals.py --today 2026-11-02
python tools/renewals/renewals.py --from-dates          # suggest lines from paperwork/dates.md
```

One line per thing that renews: `YYYY-MM-DD | what | who | every year`. The cadence is `every year`, `every 2 years`, `every 6 months`, or `once`. For a past item it prints the line to paste once the person says it was renewed, with the date moved forward by the cadence. `--from-dates` lists lines in `paperwork/dates.md` whose text reads like a renewal and that are not in `renewals.md` yet. Standard library only; reads, never writes, never pays or submits anything.
