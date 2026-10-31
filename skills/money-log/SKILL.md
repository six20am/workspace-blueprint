---
name: money-log
description: "Turns a bank or card CSV export into a monthly summary by category, a list of recurring charges, and an offline dashboard. No bank connection, nothing uploaded. Use when the person asks what they spent, or hands over a bank export."
---

# money-log

Use this when the person asks "what did I spend last month", "where is my money going", "what subscriptions am I paying for", or hands over a CSV their bank, card or budgeting app exported.

## No bank connection, ever

The skill reads a file the person downloaded themselves. It never connects to a bank, never asks for a bank login, and never uploads anything. Everything it writes stays in the `money` folder of the workspace, and that folder keeps itself out of git. If the person offers a bank password or a link to connect an account, say no and ask for an export instead.

## Getting an export

One line to tell the person: sign in to the bank's website, open the account, find Download or Export on the transactions page, pick CSV and the months you want.

Three months or more is best; recurring charges need charges in three different months to show up.

## The one command

```
python tools/money-log/money.py <export.csv> --source "<bank or app name>" --month YYYY-MM
```

Run it from the workspace folder. `--source` names the account (use the same name every time for the same account). `--month` is the month to summarize; leave it off for the latest month in the export. If it says it cannot tell what kind of export this is, it lists the shapes it knows; pick one with `--format <shape>`. Run doctor if `python` is missing.

Each run adds the export to `money/ledger.csv`. Loading an overlapping export again adds nothing new, so the person can export a fresh range each month without worrying about doubles.

## What it writes

- `money/<YYYY>/<YYYY-MM>-summary.md`, the summary.
- `money/<YYYY>/<YYYY-MM>-dashboard.html`, the same month as one page that opens in any browser with the network off.

## The summary shape

```
# Money summary: 2026-09
From <source>. Covers <first date> to <last date>, N transactions.
## Spending by category
| Month | Category | Total |      one row per category, biggest first, then All spending
Money in, spent, net, and transfers (not counted as spending)
## Recurring charges
| Charge | Cadence | Monthly amount | Last seen | Status |
## No category yet        (only when some spending has no rule)
## Repeated rows removed  (only when the export repeated a row)
```

Money out is spending; transfers between accounts and card payments are left out of the totals so nothing counts twice. A recurring charge is the same merchant at a steady amount in at least three different months. One that stopped for longer than usual is marked "possibly cancelled", which is how forgotten subscriptions surface.

## Adding a category rule

Rules live in `money/rules.csv`, made from `tools/money-log/rules.example.csv` on the first run. Each line is `match,category,subcategory`: if the match words appear anywhere in a description, that spending gets the category. Case does not matter. Rules only touch money out, so a paycheck is never relabeled. The first matching line wins, so put specific rules above general ones. To fix a wrong or missing category, add one line and run the command again; the whole ledger is re-sorted.

```
harbor hardware,Home,Repairs
```

Look at "No category yet" in the summary for the biggest ones to add.

## What to say

Three lines. Total spent and the top three categories. The recurring charges with their monthly amounts, and any marked possibly cancelled. Where the summary and dashboard landed. Then offer to add rules for anything in "No category yet".

## Before it is shared

The summary holds real amounts and merchant names. Before it goes to anyone, run `outbound-check` on it (`python tools/outbound-check/check.py <file>`) and show the person what it found.

## More detail

Export shapes it reads, how to add a new one, how repeated rows are handled, and a monthly routine: `reference.md` in this folder.

## Never

- Connect to a bank, ask for a bank login, or type a password, card number or account number.
- Upload, email or post the ledger, a summary or the dashboard.
- Write outside the `money` folder.
- Delete or hand-edit `money/ledger.csv` to change a total. Fix a category with a rule; fix a bad import by re-exporting.
- Guess a category the rules and the export do not give. Leave it in "No category yet".
- Give investment, tax or debt advice. Report what was spent.

Adapted from djspiceroute/money-map (MIT).
