# money-log

A bank, card or budgeting-app CSV export in; a monthly summary by category, the recurring charges, and an offline dashboard out. No bank connection, no network, no upload.

```
python tools/money-log/money.py export.csv --source "Example Bank checking" --month 2026-09
python tools/money-log/money.py tools/money-log/sample/bank-export.sample.csv   # try it on the sample
```

Writes only inside `money/` in the workspace (`--money-dir` to point elsewhere):

- `money/ledger.csv`: every transaction loaded so far; overlapping exports are not doubled.
- `money/rules.csv`: category rules, `match,category,subcategory`, copied from `rules.example.csv` on the first run.
- `money/<YYYY>/<YYYY-MM>-summary.md` and `<YYYY-MM>-dashboard.html`: the month.
- `money/.gitignore`: keeps the whole folder out of git.

Options: `--format <shape>` when detection fails, `--rules <file>`, `--drop-exact-duplicates` (identical rows inside one export are kept unless you pass it).

Files: `money.py` (entry point), `money_adapters.py` (export shapes), `money_dedup.py` (repeated rows), `money_enrich.py` (categories, recurring charges), `money_dashboard.py` (the HTML page). Standard library only.

Adapted from djspiceroute/money-map (MIT); the live bank-connection part of that project is left out on purpose.
