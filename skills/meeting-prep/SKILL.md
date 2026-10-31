---
name: meeting-prep
description: "Writes a one-page brief on a person or company before a call or meeting: who they are, what we have done together, what they want, three questions, one risk. Use when the person asks to prep for a call."
---

# meeting-prep

One page on one person or company, ready to read in a minute before a call. The person reads it; this skill only drafts it.

## When to use it

The person says "prep me for", "brief me on", "get me ready for a call with", or names someone they are about to meet. One page per person or company. If they name several, make one page each.

## What goes in

Three sources, in this order. Use only what these give you.

1. **What the workspace already holds.** Open the router file, find the folder for people, clients or companies, and look for one named for them. Then search the sections for the name, the company, and any email address or domain: grep for each across the notes and project folders. Read only the files that match.
2. **What the person pastes.** An invite, the last email thread, call notes, a text. If the person pastes the invite, take the time, the place or link, the attendees and any agenda from it. If they paste the thread, take the open asks, who owes what, and the tone. This workspace holds no mail and no calendar, so if nothing is pasted, say so once and ask: "Paste the invite or the last thread if you have it." Carry on without it if they have none.
3. **The public web.** Use `web-read` on the company's own site and one recent news page if the name is likely to have any. Keep it to the facts that bear on this call. Name each page you used.

If a source gives nothing, write "Nothing found" for that part. Never fill the gap with a guess.

## The page

Plain headings, no icons.

```
# [Name], [date and time of the call]

Where: [place or link]    With: [names and roles]

## Who they are
Two or three lines. Role, company, what the company does.

## What we have done together
The history in dated lines. If there is none, "No history in the workspace. New contact."

## What they want now
From the invite, the thread or the notes. Quote the ask where you can. List any open
action items as "[who] owes [what], from [date]".

## Three questions to ask
Three. Each one tied to a fact above, and each one something the answer would change.

## One risk
The single thing most likely to go wrong, and one line on how to handle it.
```

## Rules

- Every fact traces to the thread, a workspace note or a named web page. Add the source in brackets after the line, such as [thread, 3 Nov] or [notes/acme.md] or [their About page].
- Do not invent a title, a date, a number, a past conversation or a quote.
- If two sources disagree, show both and say which is newer.
- Short sentences. Aim for one screen. A 60-second read, not a report.
- A recurring internal meeting with no outside guest needs no page. Say so and offer the agenda instead.

## Where it goes

Beside the person's or company's folder if one exists, named `<date>-meeting-prep.md`. If there is no folder, put it where the router file says notes go. If the router names none, ask. Show the page in the chat as well.

## Never

- Email, message or invite anyone. Draft only.
- Search for private details about a person that are not about the work: home address, family, health, finances.
- Save pasted email or notes anywhere except inside the page, in short.

Adapted from analystacademy/claude-skills (MIT).
