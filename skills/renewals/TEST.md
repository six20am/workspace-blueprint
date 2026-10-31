# Test: renewals

## The ask
"My car insurance renews in March and the business license is due end of January. Keep track of those for me."

## The input
What the person says, plus `paperwork/dates.md` if the paperwork skill has written one. No email, no accounts read.

## Done looks like
A `renewals.md` with one line per item in `YYYY-MM-DD | what | who | every ...` shape: the two the person named, plus any `--from-dates` suggestions they confirmed, none they did not. Then `python tools/renewals/renewals.py` run and read back soonest first, one line each with what to do. On the weekly brief, each item inside 30 days appears, with "this week" on anything inside 7. Nothing paid, renewed or submitted; no date guessed.
