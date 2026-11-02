# Test: legacy-journal

## The ask
"I want to start a journal for my kids. Ava was born June 1, 2022 and Leo March 3, 2024. Give me something to write about, and I want to write Ava a letter for her 18th birthday."

## The input
What the person says and types, plus any phone video they drop in. Nothing read from email, accounts or the web.

## Done looks like
`legacy/people.md` with both birthdays and a short `legacy/README.md` for the kids. One scene question asked, one at a time, and the answer filed as `legacy/entries/YYYY/YYYY-MM-DD - <title>.md` with `For:` and `Asked:` lines, in the person's own words. `python tools/legacy-journal/legacy.py age Ava 18` run, and the letter saved as `legacy/letters/2040-06-01 - for Ava - on your 18th birthday.md`, never quoted back afterward. `backup` offered once. Nothing uploaded or shared; no date or name guessed.
