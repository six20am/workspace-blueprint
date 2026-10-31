---
name: weekly-brief
description: "Writes a one-page brief of the week: what came in, what went out, dates coming up, gaps logged, sign-ins needed. Use when the person asks what happened this week, says catch me up, or on Monday morning."
---

# weekly-brief

Run this when the person asks what happened this week, says "catch me up", on a Monday morning, or every week if the router file says so.

## The one command

```
python tools/weekly-brief/brief.py   # python3 on Mac and Linux
```

Run it from the workspace folder. It looks at the last 7 days, ending today. Add `--days 14` for two weeks, or `--out <path>` to save it somewhere else. It prints the path of the brief it saved.

## What is in the brief

- **Came in**: files changed this week, newest first, up to 40.
- **Went out**: the ones inside a delivery or sent folder.
- **Dates coming up**: the next 14 days from `paperwork/dates.md`, if the paperwork skill has written it.
- **In town this week**: the next 7 days from the newest file in `local-events/`, if the local-events skill has written one.
- **Renewals coming up**: anything in `renewals.md` past its date or due within 30 days, "this week" on the ones inside 7, if the renewals skill keeps that file. Say what to do, not just the date.
- **Waiting on, overdue**: the lines in `waiting-on.md` past their wait, with the days, if the waiting-on skill keeps that file. Offer the nudge draft for each; the person sends it.
- **Decided this week**: this week's lines in `decisions.md`, if the decision-log skill keeps it. Read them back as written; flag once if the week's work undoes an earlier one.
- **Gaps logged**: this week's lines in `setup/gap-log.md`.
- **Jobs that keep coming back**: the undo-history summaries from the last 90 days that repeat three or more times, with the count. This is the look-back: the work got done, now ask whether it should become a pipeline.
- **Sign-ins needed**: the accounts the last doctor run said the person connects by hand.

It is saved as `weekly-brief-<date>.md` in the notes folder the router file names, or the workspace folder if it names none. Empty sections say "Nothing."

## What to say

Read it back in five lines, one per section, in plain words: "Twelve files came in, mostly client notes." Name a date by what it is and when ("The water bill is due on the 10th"). Then offer to open any item.

If a job repeated, say it once, plainly: "You've done the Monday update four times since August. Want me to set it up as a pipeline so it runs the same way each time?" One offer, for the most repeated job. A no is the answer until the next brief; do not raise it again that week.

## What it does not know

Only what is inside the workspace folder. Not email, not the calendar, not anything in another app or online. Say so if the person asks about those. It knows a file changed, not what changed in it.

## Never

- Send the brief anywhere, post it, or email it. It stays in the workspace.
- Read the files it lists to "add detail" unless the person asks to open one.
- Invent a date or a deadline that is not in `paperwork/dates.md`.
