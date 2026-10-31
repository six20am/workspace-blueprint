# Workspace Blueprint: Design

**Date:** 2026-10-31
**Status:** Phases 1 and 2 built; Phase 4 partly built; later phases marked in Section 6
**Repos:** core `six20am/workspace-blueprint`; Grok mirror `six20am/grokbot-blueprint`. Both public.
**Companions:** `adapters/grok-bot/publish.md` (how the Grok Bot template is published), and the mirror repo `six20am/grokbot-blueprint`.

## What this is

One core of skills, tools and setup method, and a thin adapter per platform. Today there are two products that share a method and drift: the Claude Code zip (20 skills plus `update`, installer, tested on Windows) and the Grok Bot template (6 skills, no installer, never run on a clean import). After this, one repo is edited, `build.py` produces one output per adapter, and a third platform is a folder.

Decisions already made and not reopened here:

- Email and texting on the bot's behalf are out. The bot never holds an address or a number. (2026-10-31)
- The same setup runs on every platform: install everything, then list the sign-ins for the owner. No per-trade tool subset.
- Install at setup, with `doctor` as the re-run path (Grok resets lose installed packages).
- Design tokens for anything visual come from `ui-ux-pro-max`; `impeccable` diagnoses only.

## Section 1: Repo layout

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

Rules:

1. A skill is edited in `skills/` and nowhere else. `grokbot-blueprint` becomes a mirror that `build.py` pushes to; its README says so.
2. Anything that names one platform (`CLAUDE.md`, `claude mcp add`, plugin names, `/workspace/<bot>`) lives in the adapter or in a neutral phrasing. Inventory the skills for platform words before moving them.
3. `tools/update/update.py` keeps working for owners who installed from the old layout: its `OWNED` list is updated to the new paths, and the old paths are removed from the owner's copy once on first update.
4. `update` on Grok Bot is `doctor` plus the same file sync; both adapters share the Python.

Deviation from the tree above, as built: `setup.ps1`, `setup.sh` and `runner.py` stay in the core `setup/` folder, not in `adapters/claude-code/`, because `doctor` and both adapters call them. The adapter keeps only the files that start them (`setup.cmd`, `setup.command`, and the update pair).

## Section 2: Setup and routing at 38 skills

- `ROUTER.md` (Grok) and `CLAUDE.md` (Claude) carry one row per kind of task naming one or two skills. `skills/INDEX.md` holds every skill's one line and is read only when no row matches, which is also when `gap-finder` fires.
- Question 2's answers pick the owner's starting rows: a photographer gets `media-tools` and `photo-organizer`; a bookkeeper gets `money-log` and `paperwork`. A mapping table in `setup/SETUP.md` from common answers to rows; unmatched answers get `summarize` and `writer`.
- `getting-started` ends by running `doctor`, then the first-week card (five things to try, from the four answers), then one line on `gap-finder`.
- Every skill ships one test task in `skills/<name>/TEST.md`: the ask, the input, what done looks like. The adapters' acceptance test runs them.

## Section 3: The skills (38 core)

Status key: **built** (in the box today), **adopt** (from a vetted MIT repo, with its gate), **trial** (evaluate first, named gate), **new** (write fresh). Repo picks and licenses: the vetting file. Before any adopt is copied: its README and license into a NotebookLM notebook in the AI Build collection, and a SkillSpector scan.

| Skill | Group | Status | Source and gate |
|---|---|---|---|
| web-read, x-read, scrapling, agent-reach, agent-web-fetch, chrome-tools, last30days | Reading the web | built | move; neutralize platform words |
| video-watcher, channel-mine | Video and audio | built | move |
| media-tools | Video and audio | trial | `kajisho5/ffmpeg-skill` + `imagemagick-skill` (MIT) if the npx installer, Python scripts and MCP are acceptable and `doctor` passes on clean Windows; else `n0an/ffmpeg-skill` recipes (MIT). ExifTool, SoX, HandBrakeCLI, MKVToolNix wrappers written new |
| markitdown | Documents | built | move |
| summarize | Documents | new | nothing license-clean exists |
| explain-this | Documents | new | mine `fayerman-source/deslop` rules and `anna128x/bureaucracy-decoder` output schema (both MIT) |
| paperwork | Documents | trial | OCRmyPDF as the engine (MPL-2.0, called never vendored; Windows install note); naming from `vlow/pdf-processor` (MIT); date extraction new |
| document-builder | Documents | new | over `pandoc` + `soffice --headless`; Anthropic document skills are proprietary and stay out |
| image-search, gallery-dl, loc-dl, client-asset-harvester | Images | built | move |
| photo-organizer | Images | trial | `RanchoGao/photo-organizer` (MIT, stdlib); translate SKILL.md from Chinese, test Windows paths and HEIC/MOV |
| deep-research, notebooklm-research | Research | built | move |
| meeting-prep | Research | adopt | `analystacademy/claude-skills` (MIT); remove emoji headers, make calendar and mail optional |
| writer | Writing | new | everyday writing in `voice.md` |
| social-copywriter | Writing | adopt | `blacktwist/social-media-skills` post-writer and caption-writer (MIT); strip the BlackTwist publishing section and `tools/REGISTRY.md`; read `voice.md` not its context file; platform formats in a reference table |
| resume-and-letter | Writing | adopt | `varunr89/resume-tailoring-skill` + `kevinryan-au/claude-cover-letter` (MIT); trim LinkedIn lookups and multi-job mode; replace the docx dependency with `document-builder`; formal letters new |
| money-log | Everyday life | trial | `djspiceroute/money-map` (MIT, stdlib); sample run on Windows, drop the Plaid file, confirm the monthly summary shape |
| trip-plan | Everyday life | adopt | `AdeDeepFishing/trip-itinerary-page` (MIT) for the output; confirmation reading new |
| voice-extractor, gap-finder, tool-vetting, workspace-diff, update | Care | built | move; `update` gains the Grok path |
| workspace-audit | Care | built (Grok) | move to core |
| doctor | Care | new | check every tool and sign-in from `tools.json`, re-install only what is missing, report |
| undo | Care | new | `git init` at setup with a `.gitignore` for secrets and large media; commit after each task; "undo what you just did" |
| outbound-check | Care | new | before anything leaves: secrets, account numbers, other people's names, the owner's address; same idea as `build.py`'s leak scan |
| weekly-brief | Care | new | what came in, went out, dates due (from `paperwork`), gap log, sign-ins needed |

Held back, with the trigger that reopens each: `reminders` (a calendar connector, adapter-level), `form-filler` (no installed tool fills PDF forms reliably), `meal-plan` (`writer` covers it), trade packs (after ten real owners), `task-capture` (first thing `gap-finder` builds).

## Section 4: Installed programs

`setup/tools.json` gains a `linux` column (apt, pipx or uv) beside `win` and `mac`. Every entry keeps check-then-install so `doctor` and Grok resets re-run safely.

| Program | Why | Win / Mac / Linux |
|---|---|---|
| ImageMagick, ExifTool, SoX, HandBrakeCLI, MKVToolNix | media-tools, photo-organizer | winget / brew / apt |
| LibreOffice (headless), Pandoc | document-builder; 300 MB+, stated at install | winget / brew cask / apt |
| Tesseract, Poppler, qpdf, jq | paperwork, summarize, explain-this | winget / brew / apt |
| RTK (oss edition) | shell output trimmed before the model sees it; the Claude adapter states the settings hook it writes; the Grok adapter calls `rtk` from the memory rule | winget / brew tap / install.sh with `RTK_EDITION=oss` |
| Defuddle, Trafilatura | main-text-only web reads for `web-read` | npm / pip |
| ccusage | cost view, Claude adapter only | npx |
| Repomix, codeburn | trial: pack one section; waste audit once Grok logs confirmed | npx |
| Ghostscript | needed by OCRmyPDF; Windows has no winget package, so the installer downloads the pinned official release | direct download / brew / apt |

Dropped: GraphicsMagick (ImageMagick covers it). Declined on license or fit: Headroom, Caveman, Claude-Mem, Serena (link only), Docling, token-optimizer, context-mode.

## Section 5: Adapters

| | Claude Code | Grok Bot |
|---|---|---|
| Loads the map and router | `CLAUDE.md`, read automatically | a memory rule saved at setup, proven in a new chat |
| Where the workspace lives | the folder the zip made | `/workspace/<bot-name>/` (shared `/workspace`) |
| Installs | `setup.cmd` / `setup.command` | `install.sh` run by the Bot at setup; `doctor` re-runs it |
| Publishes as | the zip, `latest` release | a template built from a source Bot per `adapters/grok-bot/publish.md`; `build.py` pushes the Bot-ready folder to `grokbot-blueprint` |
| Extra skills | none | none |
| Status | built, Windows tested, Mac untested | designed; no clean import yet |

A third platform needs four things: files that persist, a way to load the map and router every time, saved instructions, and a shell.

## Section 6: Build order

1. **Split.** (built 2026-10-31) Move the 21 skills to `skills/`, write `adapters/claude-code/` and `adapters/grok-bot/`, update `build.py`, `update.py`, the tests and the workflow. The zip must still install and pass the Windows test. Ship nothing new in this phase.
2. **Programs and care.** (built 2026-10-31) `tools.json` linux column and the eleven new programs; `doctor`, `undo`, `outbound-check`, `update` for Grok. Installer tested on Windows and on a Linux container.
3. **Adopt and trial.** The five adopts and four trials, each behind its gate, each with `TEST.md`.
4. **New skills.** (five of nine built 2026-10-31: summarize, explain-this, document-builder, writer, weekly-brief) The nine written fresh, each with `TEST.md`.
5. **Grok clean import.** Build the source Bot, publish, run the four checks in `adapters/grok-bot/publish.md` on a clean account.

Each phase ends with the site rebuilt (the skills grid moves entries from coming to in the box on its own) and a commit.

## Risks

- **Scope.** 17 skills and 11 programs is weeks of work for one person. Phases 1 and 2 are the ones nothing else survives without; 3 and 4 can land one skill at a time.
- **Licenses.** Every adopt is MIT or Apache; OCRmyPDF is MPL and is only called. The core repo itself still has no license file.
- **Grok unknowns.** Whether the Bot's computer reaches github.com, whether a template carries files, whether the first conversation auto-starts. Phase 5 answers them; nothing before it depends on the answers.
- **Public repo.** No client names, agency paths or Six20AM-internal rules may enter `skills/`. `build.py`'s leak scan and `tests/test_shipped.py` stay the gate.
