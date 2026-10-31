# Test: decision-log

## The ask
In a chat about billing, the person says: "OK, let's go monthly invoices from now on, the per-job ones are a pain to chase." Two weeks later: "Why did we switch to monthly invoices?"

## The input
What the person said in the chat, and `decisions.md`.

## Done looks like
On the day: one line added to `decisions.md` in the shape `YYYY-MM-DD | what | why | who`, and "Logged that in decisions.md" said in the chat. Two weeks later: `python tools/decision-log/decisions.py invoice` run and the line read back in one sentence with the date and the why. No old line edited; a reversal would be a new line.
