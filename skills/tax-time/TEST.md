# Test: tax-time

## The ask
"My accountant wants everything for last year. Can you pull it together?"

## The input
What `paperwork` and `money-log` already filed in the workspace for that year. Nothing from email, a bank or any online account.

## Done looks like
`python tools/tax-time/taxtime.py --year <year> --dry-run` run first and its plan shown; any folder the person names added with `--also`. Then the real run: copies in `taxes/<year>/<Category>/`, every original untouched, `taxes/<year>/COVER.md` listing each file with where it came from and the categories that came up empty, and `taxes/<year>/taxes-<year>-for-accountant.zip`. One line to the person with the counts and what is missing. Nothing sent, nothing uploaded, no total added up, no file whose name says nothing guessed into a category.
