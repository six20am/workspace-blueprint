---
name: renewals
description: "Keeps the dates that come back every year or two in one place: insurance, licenses, vehicle registration, domains, warranties, subscriptions, passports, inspections, permits, memberships. The weekly brief warns 30 days out and again at 7. Use when the person says something expires, renews, is up for renewal, asks when a license or policy runs out, or hands over a renewal notice."
---

# renewals

Nothing to install. One file, `renewals.md` in the workspace folder, one line per thing that renews. The brief reads it every week.

## Set up once

Ask one question: "What runs out if you forget it?" Most people name five or six things straight off. Then look in `paperwork/dates.md`, if the paperwork skill has written it, for lines that say renew, expires, license, registration, insurance, policy, warranty, passport, inspection or permit:

```
python tools/renewals/renewals.py --from-dates   # python3 on Mac and Linux
```

It prints those lines shaped for this file. Show them and add the ones the person confirms. Write each line as the date it is due, what it is, who it is with, how often:

```
2027-03-15 | car insurance | Example Mutual, policy ends | every 6 months
2027-01-31 | business license | city hall | every year
2026-12-02 | truck registration | state motor vehicles | every year
2031-08-20 | passport | | every 10 years
2026-11-19 | web domain example.com | the registrar, auto-renews on the card ending 0000 | every year
2026-11-30 | furnace service plan | Northwind Heating | once
```

An empty "who" is fine. `once` means it does not come back; drop the line after. A card that auto-renews still goes in: the warning is the moment to check the card has not expired and the price has not jumped.

## Each week

```
python tools/renewals/renewals.py
```

It prints what is past, what is due within 7 days, within 30 days, and the rest by date. Nothing is changed. The `weekly-brief` skill carries the 30-day list on its own.

## When a date passes

Ask in one line: "The truck registration was due on the 2nd. Done?" On yes, move the line forward by its cadence; the script prints the new line ready to paste. On no, leave it where it is; it stays at the top of the brief until it is handled or the person says to drop it.

## What to say on the brief

One line each, soonest first, with what to do: "Car insurance ends in 6 days. Check the renewal price before it auto-renews." Nothing more. A renewal that needs a form or a payment is the person's to do; the skill can draft a note to the agent or office with `writer`, never pay or submit.

## Never

- Pay, renew, submit, sign or click through a renewal. Warn, draft a note if asked, stop.
- Add a line the person did not confirm. The `--from-dates` list is a suggestion.
- Guess a date. If the person does not know when a policy ends, put the line in with `date unknown` in the what field and ask them to check the paper; the brief will show it until a date replaces it.
- Read email or accounts to find renewals. The file is what they told you and what the paperwork skill filed.
