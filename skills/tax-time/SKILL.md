---
name: tax-time
description: "Once a year, gathers what the accountant needs from what is already filed in the workspace: receipts, invoices, tax forms, donation letters, mileage logs and the money-log monthly summaries, copied into one folder by category with a cover sheet, then zipped. Nothing new is made, nothing is moved. Use when the person says tax time, tax season, the accountant wants everything, what do I need for my taxes, or asks to gather receipts for a year."
---

# tax-time

Nothing to install beyond Python, which setup put in. The year's work was already done by `paperwork` (filing scans by date, sender and title) and `money-log` (monthly summaries). This skill only collects it.

## When

January through April for last year, or whenever the person asks. Also when the accountant sends a list: run it, then check the list against the cover sheet and name what is missing.

## The two commands

```
python tools/tax-time/taxtime.py --year 2026 --dry-run   # python3 on Mac and Linux
python tools/tax-time/taxtime.py --year 2026
```

The dry run prints the plan: every file it would copy, the category, and why. Show it. The person usually spots two things: a receipt filed under the wrong year, and a folder outside the workspace (a receipts box on the desktop, a scanner's output folder). Add one with `--also <folder>` and run again. Then run it for real.

## What it gathers, and how it decides

A file belongs to the year when its name starts with that year (the way `paperwork` names things) or, with no date in the name, when it was last changed that year. It is kept when the name says what it is:

| Category | The name says |
|---|---|
| Income | invoice, in a sent or delivery folder; sales, payout, income |
| Receipts and expenses | receipt, expense, purchase; an invoice anywhere else |
| Tax forms | 1099, W-2, 1098, 1095, K-1, tax, estimated payment |
| Donations | donation, charity, contribution |
| Medical | medical, dental, pharmacy, prescription |
| Mileage and travel | mileage, travel, hotel, flight, parking |
| Home and property | mortgage, property tax, rent, HOA |
| Bank summaries | the `money/<year>/<month>-summary.md` files from money-log |

Everything lands as a copy in `taxes/<year>/<Category>/`, with the original left where it was. A file already copied is skipped the next time, so running it twice in March costs nothing. `taxes/` stays out of the undo history, like `paperwork/` and `money/`, because it holds the same private papers.

## The cover sheet and the zip

`taxes/<year>/COVER.md` lists each category, the count, and every file with where it came from. It ends with the categories that have nothing in them, so the person can see a gap before the accountant does: "No donation letters this year. Did you give anything?" is one line worth saying.

`taxes/<year>/taxes-<year>-for-accountant.zip` holds the category folders and the cover sheet. The person sends it; this skill does not. Before it goes, say in one line what is in it: "Forty-one files: 12 receipts, 9 invoices, 12 bank summaries, 3 tax forms, 5 donation letters. No mileage log this year."

## Never

- Send, upload or email the zip, or hand it to a tax service. The person sends it to their own accountant.
- File a return, fill a tax form, or give tax advice. Say "ask the accountant" and stop.
- Move, rename or delete an original. Copies only.
- Add a number, a total or a document that is not already in the workspace. If the accountant wants a total, the money-log summaries have them; nothing is added up here.
- Guess a category for a file whose name says nothing. It is left out and listed under "Not gathered" so the person can name it.
- Reach into email, a bank or an online account to find anything.
