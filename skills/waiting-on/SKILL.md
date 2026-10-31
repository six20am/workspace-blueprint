---
name: waiting-on
description: "Keeps one list of what the person is waiting for from someone else: a quote, a reply, a part, a refund, a signature, a callback. Each line carries the date they asked. The weekly brief lists what is overdue, and the skill drafts the nudge in the person's voice; it never sends it. Use when the person says they asked someone for something, is waiting to hear back, wants to chase or follow up, or asks who owes them what."
---

# waiting-on

Nothing to install. One file, `waiting-on.md` in the workspace folder, one line per thing someone else owes. The brief reads it every week.

## When something is asked for

The person says "I asked the plumber for a quote", "sent the contract to Sam to sign", "still waiting on that refund". Add one line:

```
2026-10-19 | Harbor Plumbing | quote for the back bathroom | emailed
2026-10-24 | Sam Ortiz | signed contract back | texted
2026-10-27 | the card company | refund of the double charge, 84.00 | called, case 4471
```

Date asked, who, what, how. Nothing else. If they expect it by a day, add `by 2026-11-05` at the end of the line; otherwise seven days is the wait before it counts as overdue.

Keep the file flat. When the thing arrives, move its line under `## Came back` at the bottom and add the date it came, so the person can see how long people take:

```
## Came back
2026-10-19 | Harbor Plumbing | quote for the back bathroom | emailed | came back 2026-10-26
```

## Each week

```
python tools/waiting-on/waiting.py   # python3 on Mac and Linux
```

It prints the overdue items with the days waited, then the rest with the days so far. Nothing is changed. The `weekly-brief` skill carries the overdue list on its own.

## The nudge

For each overdue item, draft one short message with the `writer` skill, in the person's voice from `voice.md`. Say what was asked and when, ask once, give them an easy out. Shaped like this, in the person's words, not these:

> Hi Dana, checking on the bathroom quote I asked about on the 19th. Still planning to go ahead; is this week realistic? If you are swamped, say so and I will look elsewhere, no hard feelings.

Save it next to the file as `<date>-<who>-nudge-draft.md` and show it in the chat. The person sends it. Then note the nudge on the line (`| nudged 2026-11-02`) so next week's brief does not draft the same one again unless they ask.

## What to say on the brief

One line per overdue item, plainest first: "The plumber's quote is 14 days out; here is a nudge you can send." Then stop. Three overdue items get three lines, not a lecture about following up.

## Never

- Send, email, text or post a nudge. Draft, save, show.
- Add a line the person did not ask about. Only what they said they are waiting for.
- Invent a date asked. If they do not remember, use today and say so on the line: `| date is a guess`.
- Nudge the same person twice in a week without being asked.
- Read the person's email or messages to find what is owed. The file is what they told you.
