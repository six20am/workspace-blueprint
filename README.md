# Workspace Blueprint

A base workspace template for anyone, in any line of work. You double-click one file. It installs a fixed base of tools for reading videos, web pages, social posts and documents, installs Claude Code, then opens Claude and says "set this up" for you. Claude asks four questions, builds your folders in the filing style you pick, and writes the routing files an AI needs to find its way around.

No file editing. Fifteen to thirty minutes, most of it installs. Windows first; the Mac installer ships as beta.

**Status:** built. Windows installer tested on one machine; the setup conversation tested for all six filing styles. Mac installer untested (beta). The design is `docs/design.md`.

## What you get

- A workspace laid out in one of six filing styles: military, by stage, by client or project, PARA, numbered index, or by date.
- Three routing files (`CLAUDE.md`, `CONTEXT.md`, one `CONTEXT.md` per workspace) so an AI loads only what a task needs.
- A voice file, so anything written for you sounds like you.
- Twenty-one baseline skills: nineteen for pulling outside material in, one that notices when a task has no tool and offers to build one, and one that pulls new skills and tools from this repo without touching the owner's files.
- Pointer files for Codex and Antigravity, so the same workspace works in all three.

## How it will work

1. Unzip the folder somewhere you will keep it. The zip is built by `build.py` and published on every push by `.github/workflows/publish.yml`; the one-page site under `site/` deploys the same way.
2. Windows: double-click `setup.cmd`. Mac: right-click `setup.command` and choose Open.
3. Wait for Claude to open, sign in when the browser asks, and answer four questions.

## Built from

The three-layer routing method (map, router, workspace) from the original workspace-blueprint teaching kit, kept in `_reference/`.

## Maintained by

Six20AM. The zip people download is a build output of this repo and is never hand-edited.

On Windows, clone with `git clone -c core.longpaths=true` or Git stops on the long paths under `.claude/skills/last30days/`.
