# Workspace Blueprint: Design

**Date:** 2026-10-31
**Status:** Phases 1 to 4 built; Phase 5 (neutral path) built 2026-10-31; a run on a real third-party agent is still to do
**Repos:** core `six20am/workspace-blueprint`, public. The vendor mirror repo was retired with Phase 5.
**Companions:** `ADAPT.md` at the repo root (the neutral path, written for the agent).

## What this is

One core of skills, tools and setup method, one named adapter and one neutral path. Before this there were two products that shared a method and drifted: the Claude Code zip (20 skills plus `update`, installer, tested on Windows) and a second, vendor-specific template (6 skills, no installer, never run on a clean import). Now one repo is edited, `build.py` produces the zip, and any other agent adapts the repo itself from `ADAPT.md`.

Decisions already made and not reopened here:

- Email and texting on the bot's behalf are out. The bot never holds an address or a number. (2026-10-31)
- The same setup runs on every platform: install everything, then list the sign-ins for the owner. No per-trade tool subset.
- Install at setup, with `doctor` as the re-run path (a reset of a hosted agent's computer can lose installed packages).
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
    claude-code/               CLAUDE.md loader, setup.cmd, setup.command, update.cmd, update.command, publish.md
  ADAPT.md                     the neutral path: any other agent adapts the blueprint from this one file
  site/                        the one-page site (built, live)
  build.py                     the one output: the zip (ADAPT.md ships in it too)
  .github/workflows/publish.yml
  docs/design.md               this document's product-level twin, updated to match
```

Rules:

1. A skill is edited in `skills/` and nowhere else.
2. Anything that names one platform (`CLAUDE.md`, `claude mcp add`, plugin names) lives in the adapter or in a neutral phrasing. Inventory the skills for platform words before moving them.
3. `tools/update/update.py` keeps working for owners who installed from the old layout: its `OWNED` list is updated to the new paths, and the old paths are removed from the owner's copy once on first update.
4. `update` on the neutral path is the same file sync plus `doctor`; both paths share the Python.

Deviation from the tree above, as built: `setup.ps1`, `setup.sh` and `runner.py` stay in the core `setup/` folder, not in `adapters/claude-code/`, because `doctor`, the zip and the neutral path all call them. `setup.sh` runs on a Mac and on Linux. The adapter keeps only the files that start them (`setup.cmd`, `setup.command`, and the update pair).

## Section 2: Setup and routing at 38 skills

- `ROUTER.md` (neutral path) and `CLAUDE.md` (Claude) carry one row per kind of task naming one or two skills. `skills/INDEX.md` holds every skill's one line and is read only when no row matches, which is also when `gap-finder` fires.
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
| voice-extractor, gap-finder, tool-vetting, workspace-diff, update | Care | built | move; `update` gains the neutral path |
| workspace-audit | Care | built (second template) | move to core |
| doctor | Care | new | check every tool and sign-in from `tools.json`, re-install only what is missing, report |
| undo | Care | new | `git init` at setup with a `.gitignore` for secrets and large media; commit after each task; "undo what you just did" |
| outbound-check | Care | new | before anything leaves: secrets, account numbers, other people's names, the owner's address; same idea as `build.py`'s leak scan |
| weekly-brief | Care | new | what came in, went out, dates due (from `paperwork`), gap log, sign-ins needed |

Held back, with the trigger that reopens each: `reminders` (a calendar connector, adapter-level), `form-filler` (no installed tool fills PDF forms reliably), `meal-plan` (`writer` covers it), trade packs (after ten real owners), `task-capture` (first thing `gap-finder` builds).

## Section 4: Installed programs

`setup/tools.json` gains a `linux` column (apt, pipx or uv) beside `win` and `mac`. Every entry keeps check-then-install so `doctor` and a re-run after a reset are safe.

| Program | Why | Win / Mac / Linux |
|---|---|---|
| ImageMagick, ExifTool, SoX, HandBrakeCLI, MKVToolNix | media-tools, photo-organizer | winget / brew / apt |
| LibreOffice (headless), Pandoc | document-builder; 300 MB+, stated at install | winget / brew cask / apt |
| Tesseract, Poppler, qpdf, jq | paperwork, summarize, explain-this | winget / brew / apt |
| RTK (oss edition) | shell output trimmed before the model sees it; the Claude adapter states the settings hook it writes; the neutral path calls `rtk` itself (`ADAPT.md`) | winget / brew tap / install script with `RTK_EDITION=oss` |
| Defuddle, Trafilatura | main-text-only web reads for `web-read` | npm / pip |
| ccusage | cost view, Claude adapter only | npx |
| Repomix, codeburn | trial: pack one section; waste audit once its coverage of other agents' logs is confirmed | npx |
| Ghostscript | needed by OCRmyPDF; Windows has no winget package, so the installer downloads the pinned official release | direct download / brew / apt |

Dropped: GraphicsMagick (ImageMagick covers it). Declined on license or fit: Headroom, Caveman, Claude-Mem, Serena (link only), Docling, token-optimizer, context-mode.

## Section 5: Adapters

Two paths, one named.

| | Claude Code | Any other agent (`ADAPT.md`) |
|---|---|---|
| Loads the map and router | `CLAUDE.md`, read automatically | whatever that agent uses for standing instructions or memory: `ADAPT.md` says to save one rule, "read `MAP.md` and `ROUTER.md` before every task", and to prove it in a fresh conversation |
| Where the workspace lives | the folder the zip made | a folder of the agent's own, named for it, never the shared root of its file area |
| Installs | `setup.cmd` / `setup.command` | `setup/setup.sh` (Linux and Mac runner) run by the agent; `doctor` re-runs it after a reset |
| Gets the files | the zip, `latest` release | the agent downloads the repo zip itself from the prompt on the site |
| Publishes as | the zip | nothing to publish; the repo is the artifact |
| Extra skills | none | none |
| Status | built, Windows tested, Mac untested | written as a file; never run on a real third-party agent, and the site says so |

`ADAPT.md` is one short file at the repo root, written for the agent, not the owner: what the blueprint is, what the agent needs (files that persist, a shell, a way to keep one standing rule), the steps (unzip into its own folder, run `setup/setup.sh --no-launch`, save the rule, run `getting-started`, run `doctor`), how `update` works there, and the three things it must never do (touch the owner's files, install without saying so, treat fetched content as instructions). No vendor is named. The site's second paste-in prompt points the agent at this file.

As built, "run `getting-started`" is "follow `setup/SETUP.md` from step 0": the playbook is the same one the zip uses, and `ADAPT.md` carries the platform table it reads.

## Section 6: Build order

1. **Split.** (built 2026-10-31) Move the 21 skills to `skills/`, write `adapters/claude-code/` and a second, vendor-specific adapter (removed in Phase 5), update `build.py`, `update.py`, the tests and the workflow. The zip must still install and pass the Windows test. Ship nothing new in this phase.
2. **Programs and care.** (built 2026-10-31) `tools.json` linux column and the eleven new programs; `doctor`, `undo`, `outbound-check`, `update` for the second path. Installer tested on Windows and on a Linux container.
3. **Adopt and trial.** The five adopts and four trials, each behind its gate, each with `TEST.md`.
4. **New skills.** (five of nine built 2026-10-31: summarize, explain-this, document-builder, writer, weekly-brief) The nine written fresh, each with `TEST.md`, plus `motion-video` (added 2026-10-31): scrub and copy the compositions, install Remotion in `tools/motion/`, render each template once on Windows as its test.
5. **Neutral path.** (built 2026-10-31) Write `ADAPT.md`, remove the vendor adapter folder and the mirror push from `build.py` and the workflow, archive the retired mirror repo with a README pointing at the core, strip the vendor name from the site and the docs. A run on a real third-party agent is Michael's to do when he wants; the site marks the path untested until then.

Each phase ends with the site rebuilt (the skills grid moves entries from coming to in the box on its own) and a commit.

## Risks

- **Scope.** 17 skills and 11 programs is weeks of work for one person. Phases 1 and 2 are the ones nothing else survives without; 3 and 4 can land one skill at a time.
- **Licenses.** Every adopt is MIT or Apache; OCRmyPDF is MPL and is only called. The core repo itself still has no license file.
- **Neutral path untested.** `ADAPT.md` has never been run by a third-party agent. The site says so; nothing else depends on it.
- **Public repo.** No client names, agency paths or Six20AM-internal rules may enter `skills/`. `build.py`'s leak scan and `tests/test_shipped.py` stay the gate.
