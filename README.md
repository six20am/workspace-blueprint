# Workspace Blueprint

A base workspace template for anyone, in any line of work. You double-click one file. It installs a fixed base of tools for reading videos, web pages, social posts and documents, installs Claude Code, then opens Claude and says "set this up" for you. Claude asks four questions, builds your folders in the filing style you pick, and writes the routing files an AI needs to find its way around.

No file editing. Fifteen to thirty minutes, most of it installs. Windows first; the Mac installer ships as beta.

**Status:** built. Windows installer tested on one machine; the setup conversation tested for all six filing styles. Mac installer untested (beta). The design is `docs/design.md`.

## What you get

- A workspace laid out in one of six filing styles: military, by stage, by client or project, PARA, numbered index, or by date.
- Three routing files (`CLAUDE.md`, `CONTEXT.md`, one `CONTEXT.md` per workspace) so an AI loads only what a task needs.
- A voice file, so anything written for you sounds like you.
- Twenty-two baseline skills from one core that every platform shares: most pull outside material in, the rest look after the workspace, including one that notices when a task has no tool and offers to build one, and one that pulls new skills and tools from this repo without touching the owner's files. The full list, one line each, is `skills/INDEX.md`.
- Pointer files for Codex and Antigravity, so the same workspace works in all three.

## Layout

One core of skills, tools and setup method, and a thin adapter per platform.

```
six20am/workspace-blueprint/
  skills/                      the core skills, one folder each, SKILL.md plus any scripts
  skills/INDEX.md              generated: one line per skill, read only when no router row matches
  setup/
    SETUP.md                   the four questions and the build, platform-neutral
    filing-styles.md           six styles, each saying where the owner's sections go
    tools.json                 every program, with win / mac / linux check and install columns
    tools-reference/           one short page per program: what it does, two example commands
    lib/, tests/               installer internals (Windows today; Linux runner added)
  tools/                       scripts some skills run (update, x-read, image-search-mcp, ...)
  _reference/                  the teaching kit (redistribution approved 2026-10-02)
  adapters/
    claude-code/               CLAUDE.md loader, setup.cmd, setup.command, setup.ps1, setup.sh, publish.md
    grok-bot/                  memory-rule loader text, install.sh, publish.md
  site/                        the one-page site (built, live)
  build.py                     one output per adapter: the zip; the Bot-ready folder pushed to grokbot-blueprint
  .github/workflows/publish.yml
  docs/design.md               this document's product-level twin, updated to match
```

`setup.ps1`, `setup.sh` and `runner.py` stay in the core `setup/` folder, not in the adapter, because `doctor` and both adapters call them.

1. A skill is edited in `skills/` and nowhere else. `grokbot-blueprint` becomes a mirror that `build.py` pushes to; its README says so.
2. Anything that names one platform (`CLAUDE.md`, `claude mcp add`, plugin names, `/workspace/<bot>`) lives in the adapter or in a neutral phrasing. Inventory the skills for platform words before moving them.
3. `tools/update/update.py` keeps working for owners who installed from the old layout: its `OWNED` list is updated to the new paths, and the old paths are removed from the owner's copy once on first update.
4. `update` on Grok Bot is `doctor` plus the same file sync; both adapters share the Python.

## How it will work

1. Unzip the folder somewhere you will keep it. `build.py` builds both outputs from this repo: the zip for Claude Code and the Grok Bot folder. On every push, `.github/workflows/publish.yml` publishes the zip as the latest release and pushes the Grok Bot folder to `six20am/grokbot-blueprint`; the one-page site under `site/` deploys the same way.
2. Windows: double-click `setup.cmd`. Mac: right-click `setup.command` and choose Open.
3. Wait for Claude to open, sign in when the browser asks, and answer four questions.

## Built from

The three-layer routing method (map, router, workspace) from the original workspace-blueprint teaching kit, kept in `_reference/`.

## Maintained by

Six20AM. The zip people download is a build output of this repo and is never hand-edited.

On Windows, clone with `git clone -c core.longpaths=true` or Git stops on the long paths under `skills/last30days/`.
