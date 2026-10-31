# Grok Bot Blueprint

A base workspace for a Grok Bot, built the way the Workspace Blueprint is built: the bot sets itself up on the first conversation, then works out of the space it made.

**This repo is a mirror.** Every file here is written by `build.py --adapter grok-bot` in `six20am/workspace-blueprint` and pushed on each release. Edit the skills there, never here.

No file editing. Four questions, one filing style.

**Status:** mirrored from the core repo; not yet run with a new owner on a clean import. The checks still open are in `publish.md`.

The design is `docs/design.md` in `six20am/workspace-blueprint`.

## What you get

- A workspace in one of six filing styles: military, by stage, by client or project, PARA, numbered index, or by date.
- Three routing layers: a map, a router, and a notes file for each section of the work, so the bot loads only what a task needs. A saved memory rule makes the bot read them before every task.
- A voice file, so anything written for the owner sounds like the owner.
- A gap-finder, so a task with no skill gets a one-line offer to build one, find a tool, or do it by hand, and the gap gets logged.
- Every skill in `skills/`, one line each in `skills/INDEX.md`.

## How it works

1. Add the template to Grok Bot from its link, or import it from **Connect apps**, **Bot templates**.
2. The first conversation runs `getting-started`: four questions, one at a time.
3. The bot builds its folder inside `/workspace`, writes the three routing layers and `voice.md`, saves the rule that loads them, then proves it on one real task in a new chat.
4. The bot runs `bash install.sh` for its tools, then the `doctor` skill to check them.

Nothing to download. The bot's cloud computer is the machine.

Publishing a new version is in `publish.md`.

## Built from

The Workspace Blueprint (`six20am/workspace-blueprint`), which does the same job for Claude Code on a personal computer with a double-click installer. This repo is that same core with the Grok Bot adapter on top: the same skills and installer list, with files named for a Bot.

## Maintained by

Six20AM.
