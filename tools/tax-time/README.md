# tax-time

Gathers one year's tax papers from what is already filed in the workspace into `taxes/<year>/`, by category, with a cover sheet and a zip for the accountant. Copies only. Used by the `tax-time` skill.

```
python tools/tax-time/taxtime.py --year 2026 --dry-run        # the plan, nothing changed (python3 on Mac and Linux)
python tools/tax-time/taxtime.py --year 2026                  # copy, write COVER.md, zip
python tools/tax-time/taxtime.py --year 2026 --also "C:/Users/me/Desktop/receipts box"   # a folder outside the workspace too
```

A file is the year's when its name starts with that year, or, with no date in the name, when it was last changed in it. The category comes from words in the name: receipt, invoice, 1099, W-2, donation, mileage, mortgage and the like; the `money/<year>/` monthly summaries are "Bank summaries" (the ledger and dashboards stay home). An invoice inside a sent or delivery folder is income; anywhere else it is an expense. A file whose name says nothing is listed under "Not gathered" rather than guessed. A file already copied (same name and size) is skipped on a second run. Skips `setup/`, `tools/`, `skills/`, `_reference/` and `taxes/` itself. Standard library only; moves, renames and deletes nothing; sends nothing.
