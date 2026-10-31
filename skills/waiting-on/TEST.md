# Test: waiting-on

## The ask
"I asked Harbor Plumbing for a quote on the 19th and never heard back. Who else owes me something?"

## The input
What the person says in the chat, and whatever `waiting-on.md` already holds. No email, no messages read.

## Done looks like
A new line in `waiting-on.md`: `2026-10-19 | Harbor Plumbing | quote for the back bathroom | emailed`. Then `python tools/waiting-on/waiting.py` run, and its output read back in one line per item: the overdue ones first with the days waited. For each overdue item, a nudge drafted with `writer` in the person's voice, saved as `<date>-<who>-nudge-draft.md`, shown in the chat, not sent. The line gets `| nudged <date>` once the person says they sent it.
