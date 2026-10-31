---
name: undo
description: "Keeps a save history of the workspace folder so any change can be taken back. Use after every task that changed files, when the person says undo what you just did, or asks what changed lately."
---

# undo

## After every task that changed files

```
python tools/undo/undo.py save "<six-word summary of the task>"   # python3 on Mac and Linux
```

Six words, plain: "renamed March invoices by date", "added voice notes to reference". "nothing to save" is fine; say nothing about it.

## When the person says "undo what you just did"

```
python tools/undo/undo.py undo
```

It prints `Undid: <what>` and the files that came back. Tell the person in one line what is back, in their words: "The three invoices have their old names again."

If it says `Unsaved changes in: <files>`, it stopped without touching anything. Name those files to the person and ask whether to save them first. On a yes, run `save` with a short summary, then `undo`. Nothing is lost, because nothing is ever taken without a save.

If the person wants the undo taken back, run `python tools/undo/undo.py redo`. It prints `Redid: <what>`; tell them in one line what is back.

If it says `No history yet`, run `python tools/undo/undo.py init` and tell them history starts now; there is nothing earlier to undo. If it says `Nothing to undo yet.`, say so.

## When they ask what changed lately

```
python tools/undo/undo.py list
```

Read the last few saves back as a short list with the day, not the ids.

## What history skips

Photos, RAW files, scans and the `paperwork/` and `money/` folders stay out of history because they are large or private, so undo cannot bring them back. Photo moves have their own undo file in photo-organizer.

## Never

- Push the history anywhere, or delete the `.git` folder.
- Undo more than once without asking. After one undo, ask before stepping back again.
- Edit files by hand to "undo" something. Use the tool so the history stays whole.
