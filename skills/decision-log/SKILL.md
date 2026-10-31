---
name: decision-log
description: "Keeps one dated line for every decision made in a chat: what was decided, why, and who said so. One file, searchable, so the same question is not argued twice and the weekly brief can look back at what was decided. Use after any decision in a conversation, when the person says let's go with, we decided, from now on, or asks what did we decide about something or why did we do it that way."
---

# decision-log

Nothing to install. One file, `decisions.md` in the workspace folder, one line per decision. It is the memory the chat does not have.

## When a decision is made

The moment the person settles something ("go with the blue", "we'll invoice monthly from now on", "drop the Tuesday class"), add one line and say so in five words: "Logged that in decisions.md."

```
2026-10-14 | invoice monthly, not per job | fewer chases, clients asked for it | owner
2026-10-21 | the website uses the dark logo | reads better on the photos | owner, after seeing both
2026-10-28 | no Tuesday evening class this winter | three sign-ups, room costs more than it brings | owner
2026-10-30 | keep the old phone number on the van | people still call it | owner's partner
```

Date, what, why, who. Each part short enough to read in one glance. The why is the part people forget and argue about later; one line of it is enough.

Log the decision, not the discussion. A chat that weighs three options and picks one gets one line. A chat that picks nothing gets nothing.

## Finding one later

```
python tools/decision-log/decisions.py invoice          # python3 on Mac and Linux
python tools/decision-log/decisions.py --days 30
```

The first prints every line with that word in it, newest first. The second prints the last 30 days. Both read the file and change nothing. Answer the person with the line itself: "On the 14th you decided to invoice monthly, not per job, because clients asked for fewer chases."

## On the brief

The `weekly-brief` skill lists this week's lines under "Decided this week". Read them back as they are. When a decision from an earlier week is about to be undone by the week's work, say so once: "On the 28th you dropped the Tuesday class; this flyer still lists it."

## When a decision changes

Do not edit the old line. Add a new one that says so:

```
2026-11-12 | Tuesday class is back, 6 pm | twelve people asked at the open house | owner
```

The file is a record. A record that gets edited is not one.

## Never

- Log a decision the person did not make. A suggestion from the assistant is not a decision until they say yes.
- Edit or delete an old line. Add a new one.
- Put anything private about a third party in the why. "Client asked for it" is enough; their reasons are theirs.
- Log more than one line per decision, or a line longer than the screen is wide.
