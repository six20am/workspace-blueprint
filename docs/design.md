# Workspace Blueprint: Design

**Date:** 2026-10-01
**Status:** built 2026-10-01. Windows installer tested on one machine; setup conversation tested for all six filing styles. Mac installer untested (beta). Implementation plan: `docs/superpowers/plans/2026-10-01-workspace-blueprint.md` in the parent workspace
**Product:** public repo `six20am/workspace-blueprint`, submodule at `products/workspace-blueprint/`, built to `Six20AM Workspace Blueprint.zip`

## What this is

A base workspace template for anyone, in any line of work, that a non-technical person sets up by double-clicking one file. The file installs a fixed base of tools and Claude Code, then opens Claude with the words "set this up". Claude asks four questions, builds the folders in the filing style the person picked, writes the routing files an AI needs, and tests one task end to end. The person never opens a terminal on purpose and never edits a file by hand.

It is built on the three-layer routing method from the original `workspace-blueprint.zip` (map, router, workspace), which stays in the product as the method every generated workspace uses.

## Who it is for

Anyone. The setup does not assume a trade. The four questions decide what gets built.

## Decisions made

| Decision | Choice | Rejected |
|---|---|---|
| Front door | A script. `setup.cmd` on Windows, `setup.command` on Mac. It installs the base and Claude Code, writes a report, and launches Claude with "set this up". | Claude desktop app as the only entry (needs a manual app install first); Claude running every install itself (slow, and a 20-minute narrated install is the worst part of the experience) |
| Split of work | The script installs. Claude configures: the four questions, the folders, the routing files, the test task. | Either side doing both |
| Windows installer | This workspace's existing `setup/` installer (`setup.ps1`, `lib/`, `tests/`, `tools.json`), with a new manifest for the base. Windows PowerShell 5.1, so nothing to install first. | A new installer |
| Mac installer | `setup.command`, bash, Homebrew. Same tool list. **Beta until one clean run on a real Mac.** | Windows only |
| Setup questions | Four, one at a time, each with a "not sure" default | Three (too much guessing); eight or more (people quit) |
| Base install | Always the full base: 19 intake tools, the gap-finder skill, three plugins, Claude Code. No per-trade subset. | Install only what the trade needs |
| Gap handling | A baseline skill that asks before building, every time | Build silently; never build |
| Source of truth | The public repo, checked out as a submodule at `products/workspace-blueprint/`, with a build script that writes the zip. The zip is never hand-edited. A copy of this spec lives in the repo as `docs/design.md`. | Edit the zip directly; keep the source private |
| The original blueprint's content | Kept, moved to `_reference/` | Deleted |
| `claude-office-skills-ref/` | Dropped. The `document-skills` plugin does the job and installs as part of the base. | Keep |

## The zip

```
Six20AM Workspace Blueprint/
├── START-HERE.md
├── setup.cmd                 Windows: double-click this
├── setup.command             Mac: right-click, Open (beta)
├── CLAUDE.md
├── AGENTS.md
├── GEMINI.md
├── setup/
│   ├── setup.ps1             Windows installer entry
│   ├── setup.sh              Mac installer body, called by setup.command
│   ├── lib/                  planner, runner, report, toollist (from this workspace)
│   ├── tests/                the installer's test suite
│   ├── tools.json            the base manifest: one entry per tool, Windows and Mac commands
│   ├── SETUP.md              Claude's playbook
│   ├── filing-styles.md
│   ├── gap-log.md            empty at ship; the gap skill appends to it
│   └── setup-report.md       written by the installer at run time, not shipped
├── .claude/
│   └── skills/
│       ├── gap-finder/
│       └── <19 intake skills and tool wrappers>
└── _reference/
    ├── 01-how-to-adapt-this.md
    ├── 02-skill-integration-patterns.md
    ├── 03-context-md-anatomy.md
    ├── 04-common-mistakes.md
    ├── 05-intake-tools.md
    ├── 06-agent-setup.md
    └── example-workspace/    the Acme writing-room, production and community folders as shipped
```

### `START-HERE.md`

For a person, not an AI. Three steps:

1. Unzip this folder somewhere you will keep it, like Documents.
2. **Windows:** double-click `setup.cmd`. **Mac:** right-click `setup.command`, choose Open, then Open again. The Mac version is new; if it stops, send us the `setup/setup-report.md` file.
3. Wait. It installs for 15 to 30 minutes and then opens Claude. Sign in when the browser asks, then answer four questions.

Below the steps, one paragraph on what gets installed and that nothing is sent anywhere.

### The installer

**Windows.** `setup.cmd` runs `powershell -ExecutionPolicy Bypass -File setup\setup.ps1`. That is this workspace's installer with a new `tools.json`. Behaviour it already has and keeps: idempotent (re-running skips what is installed), per-tool check and install commands from the manifest, a written report, a `-DryRun` flag, a test suite. Behaviour added for this product:

- Never stops on a failed tool. It records the failure and the one thing to try, and moves on. The only hard stops are no internet and no `winget`, each reported in one plain sentence.
- Says before it starts: what it will install, roughly how long, and that it signs in to nothing.
- Last step: `claude "set this up"` in the workspace folder. The first run opens the browser for the Claude sign-in.

**Mac.** `setup.command` sets its own folder as the working directory and calls `setup/setup.sh`. The bash script installs Homebrew if missing (says first that the Mac will ask for a password and may download Apple's command-line tools, which can take ten minutes), then walks the same `tools.json` list using the Mac column, with the same never-stop rule and the same report, then runs `claude "set this up"`. No dry-run, no area flags. The build script sets the executable bit on `setup.command` inside the zip, because a zip built on Windows does not carry it.

**`tools.json`.** One entry per item, in install order, each with `id`, `name`, `needs`, `check`, `install` (Windows), `install_mac`, and `login` when the person has to sign in. Groups:

1. **Base layer:** Git, Node.js LTS, Python 3.12, uv, ffmpeg, yt-dlp, Playwright Chromium.
2. **Claude Code CLI** and its three plugins: superpowers, frontend-design, document-skills.
3. **Intake tools with a public source:** NotebookLM (`notebooklm-py`), Scrapling, MarkItDown, gallery-dl, Agent Reach, last30days, chrome-devtools, whisper.cpp and the base English model.
4. **Sign-ins the person does:** Claude in Chrome extension, `notebooklm login`, `agent-reach setup` (throwaway accounts only), free API keys for image search. Listed in the report under "needs you".

The shipped skills need nothing installed; their entries name what they depend on from groups 1 and 3.

### `CLAUDE.md` as shipped

Short. The first lines say this is an unconfigured template and that on "set this up", or on any first open where `setup/setup-report.md` exists and no workspace has been built, the AI follows `setup/SETUP.md`. Below that, a map of the shipped folders. Setup overwrites this file with the person's real map.

### `AGENTS.md` and `GEMINI.md`

Pointer files. Each says: read `CLAUDE.md` for the map, `CONTEXT.md` for routing, `setup/SETUP.md` if the workspace is not yet set up. No rules of their own. A rule lives in one file.

### `setup/SETUP.md`

Claude's playbook. Sections, in order:

1. **Read the report.** Open `setup/setup-report.md`. Tell the person in three lines what installed, what failed, and what needs them. Offer to fix the failures now or after setup. Do not re-run installs that succeeded.
2. **The four questions.** Asked one at a time. Each has a "not sure" option and names the default it picks.
   1. "What do you do?" Free text. Decides workspace names and the examples used in the files.
   2. "What are the two or three kinds of work you would hand to an assistant?" Free text. Each becomes a workspace. "Not sure" picks three from the answer to question 1.
   3. "How do you like things filed?" The six styles from `filing-styles.md`, each shown as a two-line example. "Not sure" picks by-stage.
   4. "How should the AI sound when it writes for you?" Plain and direct, warm, formal, or paste a sample. Becomes `voice.md`. "Not sure" picks plain and direct.
3. **Build.** Create the folders in the chosen style. Write `CLAUDE.md` (map, naming rules, placement rules), `CONTEXT.md` (router), one `CONTEXT.md` per workspace with a what-to-load and skip-these table, and `voice.md`. Every file follows the anatomy in `_reference/03-context-md-anatomy.md`. Remove the "unconfigured template" block from `CLAUDE.md`.
4. **Fix.** If the person said "now" in step 1, work through the failed installs one at a time, in plain words, never typing a credential.
5. **Test.** Run one real task from the answer to question 2. Check it loaded the right workspace, loaded only the listed docs, and put the output file where the placement rules say. If not, fix the routing file, not the task.
6. **Close.** Three things to try right now, drawn from question 2. The sign-in list from the report. One line on the gap skill: "If you ask for something I have no tool for, I will say so and offer to build one."

### `setup/filing-styles.md`

Six styles. For each: the name, who it suits in one line, and a sample tree of six to ten lines built from a generic example. The AI substitutes the person's workspaces.

| Style | Shape |
|---|---|
| Military | Numbered sections with fixed jobs (S-1 admin, S-3 operations, S-4 supply, and so on). One home per thing. |
| By stage | Folders follow the work: intake, production, delivery. The original blueprint's shape. Default. |
| By client or project | One folder per client, the same sub-folders inside each. |
| PARA | Projects, Areas, Resources, Archive, sorted by how active something is. |
| Numbered index | Ten top-level ranges (10-19, 20-29) with numbered folders inside. Find by number. |
| By date | Year, month, item. |

The three-layer routing works under every style. Only the folder names and nesting change.

### `.claude/skills/`

Twenty baseline skills. Nineteen are the intake set listed in `_reference/05-intake-tools.md`. The custom ones from this workspace (`notebooklm-research`, `agent-web-fetch`, `deep-research`, `video-watcher`, `channel-mine`, `site-cloner`, `client-asset-harvester`, `loc-dl`, `image-search-mcp`, `x-read`, `workspace-diff`, `tool-vetting`, `voice-extractor`) are copied and cleaned: no client names, no Six20AM paths, no `shared-core/` references, no agency rules. Each keeps its `SKILL.md` and any scripts it needs. Scripts that depend on this repo's folder layout are rewritten to take a path argument. Paths inside them use the workspace root, never a user's home folder.

The twentieth is new.

### `gap-finder` skill

**Trigger.** A task arrives that matches no row in the routing tables and no skill in `.claude/skills/`. Also invoked by name.

**Behaviour.**

1. Say so in one line and offer three choices: build a skill, find an outside tool, or do it by hand this once.
2. **Build:** a short interview (what the task is, what goes in, what comes out, what must never happen), then write `SKILL.md`, add a routing row to the right `CONTEXT.md`, and run the task with it. Adapted from this workspace's `skill-builder`.
3. **Find:** run `tool-vetting` on whatever the person or a search turns up. Nothing installs without a verdict of adopt. Adapted from this workspace's `tool-vetting`, with the Six20AM-specific "what we use today" step replaced by a read of the person's own `tools.json`.
4. **By hand:** do the task. Append one line to `setup/gap-log.md`: date, the task in a few words, the choice made.
5. **The three-strikes rule.** Before offering the choices, read `gap-log.md`. If the same kind of task has been done by hand three times, say so and recommend build.

**Never.** Builds without asking. Installs without vetting. Edits `CLAUDE.md` or a router beyond adding one row.

## The build script

`build.py` at the repo root. Standard library only. It:

1. Copies the repo to a temp directory, leaving out `.git`, `build.py` and the build report.
2. Fails on any em dash, any string from a names list (client slugs, personal paths, account ids), or any `.env`, `accounts.json` or key file.
3. Sets the executable bit on `setup.command` and `setup/setup.sh` in the zip entries.
4. Writes `~/Downloads/Six20AM Workspace Blueprint.zip` and a `-build-report.md` beside it listing every file included.

Same discipline as `tools/workspace-export/` and `tools/roster/`: the output is generated, never hand-edited.

## Testing

| Test | How | Pass when |
|---|---|---|
| Manifest | `setup.ps1 -Validate` and `setup/tests/run-tests.ps1` | Every entry has a check, an install for both platforms or a stated reason not, and the dependency order resolves |
| Dry run | `setup.ps1 -DryRun` on this machine | The report lists every tool with would-install or already-present and nothing else changes |
| Live run, Windows | `setup.ps1` on this machine | Everything already installed is skipped; the report is written; `claude "set this up"` launches |
| Build | Run `build.py` | Zip opens, report lists every file, no name or em dash leaks, `setup.command` carries the exec bit |
| Routing | `routing-integrity` agent on the repo | Every path in every table resolves |
| Setup walk-through | Unzip to a clean folder, run `claude "set this up"`, answer the four questions | Folders match the chosen style; `CLAUDE.md`, `CONTEXT.md`, workspace routers and `voice.md` exist and read correctly; the test task lands in the right folder |
| Gap skill | Ask for a task no skill covers | One-line offer with three choices; the log line is written |
| Each filing style | Repeat the walk-through once per style | Six distinct trees, each with the three layers intact |
| Fresh Windows machine | A clean VM or a real non-technical person | **Cannot be run from this workspace.** Flagged. |
| Mac | A real Mac, double-click `setup.command` | **Cannot be run from this workspace.** Beta label stays in `START-HERE.md` until one clean run. |

## Out of scope

- A per-trade tool subset at setup.
- Linux.
- Translating the setup into other languages.
- Signing the scripts. Gatekeeper and SmartScreen warnings are handled with one sentence of instructions, not a certificate.

## Risks

- **Install time.** 15 to 30 minutes and around 500 MB. `START-HERE.md` and the script both say so before anything starts.
- **A failed tool.** The script records it and carries on; Claude offers the fix at step 1. A failed tool never blocks the workspace from being built.
- **Mac is untested here.** Shipped beta. The first Mac user's `setup-report.md` is the test.
- **Gatekeeper and SmartScreen.** A downloaded script gets a warning on both platforms. The instructions name the exact clicks.
- **The cleaned skills may still carry a Six20AM assumption.** The build script's names list catches strings; it does not catch a rule that only makes sense for an agency. Each cleaned skill gets one read for that before it ships.
- **The original kit came from someone else.** Its teaching files are redistributed in a public repo under the Six20AM name. Confirm the licence or the author's permission before `_reference/` is pushed.
