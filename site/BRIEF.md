# Brief: Workspace Blueprint one-page site

Format: web-page. Written 2026-10-31 for `/copywriter`. Facts below come from `README.md`, `START-HERE.md`, `setup/tools.json`, `docs/design.md` and the skill files in `skills/`. Nothing else is a fact.

## Who reads this

One person who runs something: a small business, a practice, a side project, a household with too much paperwork. They have tried an AI chat box and found it forgets everything and knows nothing about their files. Not technical. They use, or are about to try, an AI service that gives the AI its own computer. They can copy and paste. Some would rather keep everything on their own machine, and for them Claude Code comes second. They have heard "Claude" and may or may not have an account.

Awareness: problem aware. They know the chat box is not enough. They have not heard of a "workspace" as the fix.

## The one job this page does

Get them to copy the prompt and paste it into their AI. Nothing else.

## The offer

Free. One prompt for an AI service that gives the AI its own computer: the AI fetches the blueprint, fits it to its own setup from `ADAPT.md`, asks a few questions and builds a workspace around the answers. Second path: a zip for Claude Code on the reader's own computer. Services are never named on the page (Michael, 2026-10-31).

## Facts (binding)

**What it is.** A base workspace for anyone, in any line of work. A folder on their own computer where an AI can find their files, follow their rules and do real work. Not a chat box.

**Setup.** Unzip, move the folder to Documents, double-click `setup.cmd` (Windows) or `setup.command` (Mac). Fifteen to thirty minutes, most of it installs, in a black window. Windows may ask "allow this app to make changes" a few times. When it finishes, Claude opens and asks, one at a time: what you do, what work you want help with, how you want it to sound when it writes for you. It shows the folder tree it picked and asks if it looks right. Then it says the three things it will never do without asking (send, spend, delete) and asks if anything should be added to that list. "Not sure" is an acceptable answer to each; it picks something sensible. Then it builds the folders and says what to try first. (`setup/SETUP.md`, revised 2026-10-31; the filing-style pick was dropped because a first-time owner has no basis to choose.) On Claude Code, a Mac refuses the setup file the first time; the fix is System Settings, Privacy and Security, Open Anyway (`adapters/claude-code/START-HERE.md`).

**Status.** Setup writes `setup/setup-report.md` (what installed, what failed, what needs a sign-in); that file is what to attach to an issue. Windows installer tested on one machine. Mac installer is new and untested; the page must say so in those words or plainer. What is next: the first run on an AI service, and the Mac installer test.

**What gets built.** Folders in one of six filing styles (military, by stage, by client or project, PARA, numbered index, by date). Three routing files so the AI loads only what a task needs. A voice file so anything it writes sounds like the owner.

**What it can do, today.** Thirty-nine skills (the build counts them from the skill folders; `motion-video` landed 2026-10-31). Reading the web: open web pages and searches, X posts, pages that block fetching, posts behind logins on X, Reddit, LinkedIn, Facebook, Instagram and YouTube (throwaway accounts only), a picker that chooses the right reader and says plainly when nothing can reach a page, pages the owner is signed in to in their own browser, what people said about a topic in the last 30 days across eight platforms. Video and audio: a timestamped transcript of any video, on the owner's own computer; a whole YouTube channel or podcast read and sorted by theme; video edited (clips joined, speed changed, captions burned in, a watermark added, reframed for social, fades), and video, audio and image files converted, trimmed, resized or shrunk, a GIF made, the audio pulled out. Documents: Word, Excel, PowerPoint, PDF and Outlook files into text with a record of where each came from; notes into a Word, PDF, PowerPoint, HTML or OpenDocument file, or a table into a spreadsheet-ready CSV; a long document, folder or thread cut to a short brief with decisions, open items and dates. Images: free stock photos with the license recorded; the owner's own galleries; Library of Congress; every image on an existing website; the owner's photos renamed by date taken, exact duplicates set aside, sorted by year and month, nothing deleted or uploaded. Research: a sourced multi-pass brief; Google NotebookLM run from the workspace; a one-page brief on a person or company before a call. Writing: a voice file built from the owner's own writing; everyday emails, replies and notes in that voice; social posts and captions for nine platforms, drafts only, never posted; a resume tailored to a posting, the cover letter, and formal letters with stakes (a dispute, a landlord, a refund). Everyday life: a contract, bill, medical letter or notice explained in plain words with the dates and three things to do; a scan or photo of a letter, bill or form named, filed and its dates pulled out; a bank or card export turned into a monthly summary by category and a list of recurring charges, with no bank connection; booking confirmations turned into one itinerary in date order with what is still unbooked. Care of the workspace: a gap finder that notices when a task has no tool and offers to build one, a tool-vetting checklist, a workspace diff, a workspace audit, a doctor that checks every tool and sign-in and re-installs only what is missing, an undo history, an outbound check for secrets, account numbers, other people's names and the owner's address before anything leaves, a one-page weekly brief, and an update skill. The one plain line per skill the page shows lives in `site/skills.json`.

**What is not built.** Nothing, as of 2026-10-31: `motion-video` (animated video over Remotion) landed and counts among the thirty-nine. A skill designed and not built goes in `site/roadmap.json` and renders marked "coming" until its folder lands; the page may say how many are coming, with no dates, and never as if they work today.

**Updates.** `update.cmd` / `update.command`, or asking Claude to update, pulls the newest skills and tools from the public repo and installs anything new. It never touches the owner's files, map, routing or voice file. If the owner edited a template file, a copy is saved first. The workspace offers the update once when it is more than 30 days old, and never runs it unasked (`.claude/skills/update/SKILL.md`). Problems with setup go to the repo's GitHub issues page: `github.com/six20am/workspace-blueprint/issues`.

**What gets installed.** Free, standard tools: Git, Python, Node.js, uv, ffmpeg, yt-dlp, a browser engine, Claude Code and three plugins, NotebookLM, Scrapling, MarkItDown, gallery-dl, Agent Reach, whisper.cpp with an English model, and three connections into Claude. The largest, LibreOffice, is 300 MB and more; no total is stated. Animated video (`motion-video`) uses Remotion, free for individuals and companies of three people or fewer; bigger companies need its company license (source: the motion-video spec).

**The boundary.** At setup the AI says the three things it will never do without asking (send anything, spend money, delete anything) and asks the owner what else belongs on that list. The list is written into the map and every section's notes, so it holds in every chat (`setup/SETUP.md` Q5, 2026-10-31).

**Privacy.** Nothing is sent anywhere by setup. Nothing signs in for the owner. Five things need the owner's own sign-in (Claude, NotebookLM, Agent Reach, two image-search keys, the Chrome extension) and setup lists them at the end. Anything a tool fetches from outside is treated as data to read, never as instructions.

**Cost.** The zip is free. Claude Code needs a Claude account; the page does not state Claude's prices. Claude Code opens the browser to sign in the first time it runs (`setup/tools.json`, the `claude` entry).

**Undo.** The workspace is one folder; deleting it removes everything it built. The programs setup installed came through winget (Windows) or Homebrew (Mac) and uninstall the same way; Python tools came through pip or uv (`setup/tools.json`).

**License.** The repo has no license file as of 2026-10-31. The page says nothing about a license until one is chosen.

**Who makes it.** Six20AM, a two-brand marketing agency run by one person. The repo is public: `github.com/six20am/workspace-blueprint`. The routing method comes from a teaching kit whose author approved redistribution.

**Two ways to run it.** AI service first, Claude Code second. On a service, files live on the computer the service gives the AI, under that service's rules, and chats and files go through it; "nothing leaves your computer" and the Windows and Mac status apply to Claude Code only.

- *Claude Code, on your own computer.* The zip. Unzip, double-click setup, answer a few questions. Everything installs on the reader's machine. Windows tested, Mac untested.
- *An AI service that gives the AI its own computer.* This is the path the CTA sells. It adapts the blueprint itself from the neutral file `ADAPT.md` at the repo root: download the repo zip, unzip into its own folder, write a small adapter file, run `bash setup/setup.sh --no-launch`, save one standing rule, follow setup, run doctor. **Not yet run on a real service.** The page names no vendor.

**Paste-in prompts.** For a reader who already has the tool, the page gives one prompt to paste, and the agent fetches everything itself.

- *Already have Claude Code:* the prompt tells Claude to download the release zip (the Guardrails link) and unzip it into Documents, which gives a folder named `Six20AM Workspace Blueprint`. A clone of the repo does not work: `setup.cmd` and `CLAUDE.md` sit in `adapters/claude-code/` and reach the root only in the zip. The page then tells the reader to double-click `setup.cmd` (Windows) or `setup.command` (Mac) in that folder, because the installer puts in the tools and skips anything already present, and then to say "set this up". The repo's `CLAUDE.md` routes "set this up" to `setup/SETUP.md`.
- *The main prompt, in the hero:* the prompt tells the agent to download `https://github.com/six20am/workspace-blueprint/archive/refs/heads/main.zip`, unzip it into a folder of its own (not the shared root of its file area), read `ADAPT.md` and follow it, asking the reader the setup questions when it says to. **Untested on a real service**; the page must say so.
- Each prompt is shown in a box with a Copy button. The Copy button is microcopy.

**Your first week (asks that work today, each backed by a shipped skill).** Paste a YouTube link and ask for the transcript (`video-watcher`). Drop a PDF, Word or Excel file in the folder and ask what it says (`markitdown`). Ask what people have said about a topic in the last 30 days (`last30days`). Give it a website and ask for every photo on it (`client-asset-harvester`). Paste three emails you wrote and ask it to learn your voice (`voice-extractor`). Hand it three clips and ask for one video with a fade at the end (`media-tools`). Ask for something it has no tool for and watch it say so and offer to build one (`gap-finder`). How to ask: say the outcome you want, name the file or link, say where the result should land. "Not sure" and "what can you do with this" are both fine openers.

## Guardrails

- No em dashes.
- Grade 8 or lower.
- No invented numbers, testimonials, logos or names of users. There are none.
- Never say "supercharge", "unlock", "seamless", "powerful". Say "AI service" or "your AI", not "AI agent".
- Name no AI vendor other than Claude.
- Do not name the agency's clients or the two agency brands.
- The download link is `https://github.com/six20am/workspace-blueprint/releases/latest/download/Six20AM-Workspace-Blueprint.zip`. The GitHub repo link is footer microcopy, not a second CTA.

## CTA

One: **Copy the prompt**. The same action sits in the hero, the header, after how-it-works, after first-week and at the close, and a phone-only sticky bar carries it once the hero scrolls away. Download the zip appears once, inside the Claude Code section. The AI service path is untested, and the hero status table must say so.

## Sections, in order (the page framework for this piece)

```
hero            headline, one line under it, the prompt in a box, the CTA, a small status table, and a sample folder tree (by stage, generic names, labeled as a sample) where three jobs each light the files the AI opens
problem         the chat box forgets; your files are not in it
what-you-get    three outcomes, one line each
why             the reasons to use it, as a marketing section (added 2026-10-31 on Michael's word): a headline and five to seven reasons, each a bold lead of a few words and one or two plain sentences. Every reason rests on a binding fact above; the candidates are: it remembers (files and rules persist between chats); it works from your files, not pasted text; it writes like you (the voice file); it only reads what the job needs (the three routing files); it arrives able to do thirty-nine things on day one; it asks before it sends, spends or deletes; it tells you when it has no tool and offers to build one; it is free, public and one folder you can delete; it keeps getting new skills without touching your files. Pick the strongest; no claims about speed, savings or results, because there are none to cite.
how-it-works    three steps: copy the prompt, paste it into your AI, answer a few questions; if the AI can only chat, use Claude Code
can-do          one line introducing the skills; one schedule of skills by group, each group with a plain headline (from site/skills.json), columns skill, what it does, status; shipped and coming both generated at build time
two-ways        Claude Code on your own computer: three zip steps, the zip button, the already-have-Claude-Code prompt
first-week      seven asks that work today, and how to ask
installed       what the zip installs, size, privacy; the full tool list behind a disclosure, the sign-in list visible
stays-current   the update path in three sentences
status          AI service untested, Windows tested, Mac untested, what is next (the first run on an AI service, and the Mac installer test)
faq             five questions: Do I need an account? Is it free? Where do my files live? What does it send? Can I undo it?
close           one line and the CTA again, then a short signed note from the maker, signed Six20AM
footer          microcopy: Six20AM, the GitHub link for the repo, teaching-kit credit
```
