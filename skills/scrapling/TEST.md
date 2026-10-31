# Test: scrapling

## The ask
"Read this public page that WebFetch refuses and give me the main text."

## The input
A public URL that returns 403 or an empty page to a normal fetch.

## Done looks like
The normal fetch is tried first, then the stealth fetch, and the main text comes back. If both fail, the skill says so plainly and does not try a login.
