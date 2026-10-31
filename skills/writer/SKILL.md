---
name: writer
description: "Writes everyday messages in the person's own voice: emails, replies, notes, short documents, a thank-you, a complaint. Use for anything they will send or hand over that is not marketing, a resume or a formal letter."
---

# writer

Everyday writing in the person's voice. The person sends it; this skill only drafts.

## When to use it

The person says "write", "reply to this", "draft", "a note saying", "tell them", or hands over a message and wants an answer back. Typical jobs: an email, a reply, a thank-you, a complaint, a message to a landlord, a note to a teacher, a short update.

Route these elsewhere in one line, then stop:

- Marketing copy and social posts: `social-copywriter`.
- A resume, or a formal letter with stakes: `resume-and-letter`.

## Steps

1. Read `voice.md`. If it does not exist, say so, offer `voice-extractor`, and write plain and direct in the meantime.
2. Ask only for what is missing, at most three questions, from this list: who it is for, the one point, the ask or next step, anything that must or must not be said. If the person already gave an answer, do not ask again.
3. Draft in the voice, in the shape from `forms.md` that fits the job.
4. Read it once as the reader would. Can they get it in one pass? If not, cut or reorder until they can.
5. If the draft is leaving the workspace, run `python tools/outbound-check/check.py <file>` (python3 on Mac and Linux) on the Markdown or text draft, not a built docx or pdf, and show the person any finding. Fix what they approve.
6. Hand the draft over in the chat and say where it is saved. Never send, post or email it.

## Where drafts go

A reply goes next to the message it answers. Anything else goes in the folder the router file names for drafts; if the router names none, ask the person where it goes. Name the file `<date>-<to>-<topic>-draft.md`, for example `2026-11-02-sam-saturday-shift-draft.md`.

## Rules

- Say the point first.
- One ask per message.
- Short sentences.
- Use only the person's facts. Never invent a detail. When a fact is missing, leave a placeholder in square brackets, such as [date].
- No em dashes.
- Match the register of what they are replying to: a casual text gets a casual reply, a formal note gets a formal one.
- Keep a reply shorter than the message it answers.
- Match `voice.md` over any rule here about style. The never list in `voice.md` always wins.

## Never

- Send anything, on any channel.
- Sign the person's name to a claim they did not make.
- Write to a third party about someone else's private matter without the person's yes. Ask first: "This mentions [name]'s [matter]. Do you want it in?"
