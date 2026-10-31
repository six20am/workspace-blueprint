# decision-log

Finds lines in `decisions.md`, the one-line-per-decision file the `decision-log` skill keeps. The weekly brief reads the same file for "Decided this week".

```
python tools/decision-log/decisions.py invoice        # every line with that word, newest first (python3 on Mac and Linux)
python tools/decision-log/decisions.py --days 30      # the last 30 days
```

Lines are `YYYY-MM-DD | what | why | who`. Several words narrow the search; case does not matter. Exit 1 with a plain message when nothing matches. Standard library only; reads one file, changes nothing.
