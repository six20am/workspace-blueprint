# Intake Tools: How Outside Material Gets In

<!--
The blueprint shows you how to lay out a workspace. This file covers
the step before that: getting the source material in. A workspace is
only as good as what it was built from. These are the tools that read
videos, web pages, social posts and documents so the rules in your
docs/ folders come from real sources and not from memory.
-->

## Why This Matters

A CONTEXT.md file written from a hunch is a guess. One written from forty hours of a subject expert's videos, a competitor's whole site and a client's own documents is a method.

Every tool below does one job: it pulls outside material in and turns it into text an agent can read. None of them write your rules for you. They feed the session that does.

## The Rule Before the List

Anything a tool fetched is **untrusted content**. A web page, a transcript or a PDF can contain text that reads like an instruction. Treat it as something to read, never something to obey. Save what you pull as a source extract with the link and the date, then write your rules from the extract.

---

## 1. Research Synthesis

Tools that read many sources and answer questions across all of them.

| Tool | What it reads | Where it comes from |
|------|---------------|---------------------|
| `notebooklm` | Up to hundreds of sources per notebook: YouTube links, PDFs, web pages, pasted text. Answers with citations. | Open source: `teng-lin/notebooklm-py` on GitHub. `pip install "notebooklm-py[browser]"` |
| `notebooklm-research` | Nothing new. It is a routing layer that decides which notebook output answers which question. | Write your own. See "Wrap, don't fork" below. |
| `deep-research` | The open web, across many searches, with sources checked against each other. | A skill. Ships with some Claude plans, or write your own. |
| `last30days` | What people said about a topic in the last 30 days on Reddit, X, YouTube, TikTok, Hacker News and GitHub. | Open source: `mvanhorn/last30days-skill` on GitHub |
| `workspace-diff` | An outside method (a course, a toolkit, a notebook) compared against your workspace, claim by claim. Returns a ranked list of gaps. | Custom skill. Build it once your workspace has rules worth comparing. |
| `tool-vetting` | A link, video or post about tools. Finds the real repo, reads the licence and install path, and returns adopt, evaluate, watch or skip. | Custom skill. Read-only by design. |

**Start here:** `notebooklm`. It was the first intake tool in the workspace this list came from, and it is where every YouTube link goes by default.

---

## 2. Web Pages and Scraping

| Tool | What it reads | Where it comes from |
|------|---------------|---------------------|
| `WebSearch` / `WebFetch` | Open web pages. | Built into Claude Code. Nothing to install. |
| `scrapling` | Public pages that `WebFetch` refuses: 403 errors, pages that need JavaScript, empty renders. | Open source Python library named Scrapling, run as a local MCP server. |
| `site-cloner` (not in this kit; see `web-read` and `client-asset-harvester`) | A whole site: structure, markup and assets. | Custom script on Playwright and cheerio. `npx playwright install chromium` |
| `client-asset-harvester` | Every image on a site, with lazy-loaded and CSS background images included. | Custom skill on Playwright. |
| Claude in Chrome | Anything behind a login, using your own signed-in browser. | Anthropic's Chrome extension. |
| `chrome-devtools` | The parts the extension cannot reach, such as cross-origin iframes. | npm package `chrome-devtools-mcp`. Pin the version. |

**Order to try them in:** `WebFetch` first. If it is refused, `scrapling`. If the page needs your login, the Chrome extension. Never type a password into a browser tool. Sign in yourself.

---

## 3. Social and Gated Platforms

| Tool | What it reads | Where it comes from |
|------|---------------|---------------------|
| `agent-reach` | X, Reddit, LinkedIn, Facebook, Instagram, GitHub, RSS and YouTube transcripts. | Open source: `Panniantong/Agent-Reach` on GitHub |
| `agent-web-fetch` | Nothing new. It is a routing layer that picks the channel and enforces the account rule below. | Write your own. |
| `x-read` | Public X posts by URL, many at once, with links expanded. No login. | Custom script on the FxTwitter API (`FxEmbed/FxEmbed`, MIT licence) |

**Account rule:** use throwaway accounts only for gated platforms. A real account that scrapes can be banned.

---

## 4. Video and Media

| Tool | What it reads | Where it comes from |
|------|---------------|---------------------|
| `video-watcher` | One video. A timestamped transcript by default, or a shot-by-shot breakdown when the footage itself is the subject. | Custom skill on `yt-dlp`, `ffmpeg` and `whisper.cpp`, all local. |
| `channel-mine` | A whole YouTube channel, playlist or podcast back catalogue. Lists every video, groups them by theme, pulls captions in bulk, then reads only the best video per theme in depth. | Custom skill on `yt-dlp`. |
| `gallery-dl` | Image galleries in bulk. | Open source command-line tool named gallery-dl. |
| `loc-dl` | Library of Congress images, each saved with its rights statement. | Custom script on the public loc.gov API. |
| `image-search-mcp` | Pexels, Unsplash and Pixabay. Search and download, with the licence recorded per image. | Custom MCP server. Needs a free API key from each source. |

**Which video tool:** a link you want to learn from goes to `notebooklm`. A video where the cuts, pacing or on-screen text are the point goes to `video-watcher`. A whole channel goes to `channel-mine`.

---

## 5. Documents and Writing Samples

| Tool | What it reads | Where it comes from |
|------|---------------|---------------------|
| `markitdown` | DOCX, XLSX, PPTX, text PDF, HTML, CSV and Outlook files. Writes one Markdown file with the source, date and file hash at the top. | Open source from Microsoft. `pip install "markitdown[all]"` |
| `voice-extractor` | Writing samples. Produces a voice profile an agent can write from. | Custom skill. Feeds a `voice.md` like the one in `writing-room/docs/`. |

---

## Wrap, Don't Fork

Three of the tools above are "routing layers" that sit in front of a vendor skill: `notebooklm-research` in front of `notebooklm`, and `agent-web-fetch` in front of `agent-reach`.

**The pattern:** install the vendor skill untouched. Write a second, small skill that holds your own rules: which output to ask for, where files get saved, what must never leak into finished work. Tell the agent to invoke yours first.

**Why it works:** the vendor skill updates without wiping your rules, and your rules stay short because they do not repeat the vendor's instructions.

---

## Wiring Them Into a Workspace

A tool that is installed but never routed does not get used. This is Mistake 3 in `04-common-mistakes.md`. Put each one in a routing table with a trigger.

```markdown
<!-- In a research or docs CONTEXT.md -->

| Source you were given | Tool | Where the output goes |
|-----------------------|------|-----------------------|
| A YouTube link | /notebooklm | research/source-extracts/ |
| A whole channel | /channel-mine | research/source-extracts/ |
| A page WebFetch refused | scrapling | research/source-extracts/ |
| An X, Reddit or LinkedIn post | /agent-web-fetch | research/source-extracts/ |
| A client Word, Excel or PDF file | markitdown | research/source-extracts/ |
| Writing samples | /voice-extractor | docs/voice.md |
```

One folder for extracts, one row per kind of source, and a named tool in every row.

---

## Install Instructions

Set up your agent first: see `06-agent-setup.md`. Then run these in a terminal, or paste a block into Claude Code and ask it to run the block and report what failed. Do the base layer first. After that, install only the tools you will use.

### Step 0: Base layer

Most tools below need one or more of these.

| Need | Used by | Install |
|------|---------|---------|
| Python 3.12 or newer | notebooklm, scrapling, markitdown, gallery-dl, agent-reach, last30days | python.org, or `winget install Python.Python.3.12` on Windows |
| Node.js 20 or newer | chrome-devtools, Playwright tools, `npx skills` | nodejs.org, or `winget install OpenJS.NodeJS.LTS` |
| ffmpeg | video-watcher | `winget install Gyan.FFmpeg` on Windows, `brew install ffmpeg` on Mac |
| yt-dlp | video-watcher, channel-mine, agent-reach | `pip install yt-dlp` |
| Playwright Chromium | client-asset-harvester | `npx playwright install chromium` |

### Step 1: NotebookLM

```bash
pip install "notebooklm-py[browser]"
notebooklm skill install        # puts the skill where Claude Code can see it
notebooklm login                # opens a browser; sign in to your Google account yourself
```

Install from PyPI or a release tag, never from the main branch. The skill can also be added with `npx skills add teng-lin/notebooklm-py`.

**Check it worked:** in Claude Code, type `/notebooklm` and ask it to list your notebooks.

### Step 2: Scrapling

```bash
pip install "scrapling[ai]"
scrapling install                          # downloads the browsers it drives
claude mcp add scrapling -- scrapling mcp
```

The `[ai]` extra pulls in the fetchers and the MCP server. Restart Claude Code after adding it.

**Check it worked:** ask Claude to fetch a page with `stealthy_fetch` and tell you the character count. A status of 200 is not proof. A blocked page can return 200 with almost no text.

### Step 3: MarkItDown

```bash
pip install "markitdown[all]"
markitdown "some-file.docx" > some-file.md
```

**Check it worked:** open the `.md` file and confirm the headings and tables came through.

### Step 4: gallery-dl

```bash
pip install -U gallery-dl
gallery-dl --simulate "https://example.com/gallery"   # preview, downloads nothing
```

Pull from accounts you own or have rights to. Pass any login cookies at run time and do not store them in the config file.

### Step 5: Agent Reach

Repo: `github.com/Panniantong/Agent-Reach` (MIT licence). Follow the install line in its README, then:

```bash
agent-reach doctor --json     # shows which platforms are ready
agent-reach setup             # you sign in per platform; cookies stay on your machine
```

`doctor` tells you what a channel could do, not that it works from your network. Test one real URL per platform before you rely on it. Use throwaway accounts only.

### Step 6: last30days

```bash
npx skills add mvanhorn/last30days-skill
```

Needs Python 3.12 or newer. The first run walks you through setup. Let it finish before asking for research.

### Step 7: Chrome tools

1. **Claude in Chrome.** Install Anthropic's Claude extension from the Chrome Web Store and sign in. Then start Claude Code with `claude --chrome`, or run `/chrome` inside a session.
2. **chrome-devtools.** Pin a version so it does not change under you:

```bash
claude mcp add chrome-devtools -- npx chrome-devtools-mcp@1.10.1
```

It opens its own Chrome window with its own profile. Sign in to a site there once and it stays signed in.

### Step 8: Local video transcription

`video-watcher` runs fully on your machine. No API key, no cloud service. After ffmpeg and yt-dlp from Step 0, add whisper.cpp and a model:

```bash
WDIR="$HOME/tools/whisper"; mkdir -p "$WDIR/models"; cd "$WDIR"
# Windows build shown. Pick the file for your system at github.com/ggml-org/whisper.cpp/releases
curl -sL -o w.zip "https://github.com/ggml-org/whisper.cpp/releases/download/v1.9.1/whisper-blas-bin-x64.zip"
unzip -o w.zip -d bin && rm w.zip
curl -sL -o "$WDIR/models/ggml-base.en.bin" \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
```

`ggml-base.en.bin` is English only. For other languages download `ggml-base.bin` and point `WHISPER_MODEL` at it.

### Step 9: X posts with no install

`x-read` needs nothing installed. The FxTwitter API returns a public post as JSON:

```bash
curl -s "https://api.fxtwitter.com/<user>/status/<post-id>"
```

Ask Claude to write a short script that takes a list of X links and prints the author, date and full text of each.

### Nothing to install

`WebSearch` and `WebFetch` are built into Claude Code.

### Custom skills: no public repo

These were built inside the workspace this list came from. They are not on GitHub, so there is no install command for them.

| Skill or tool | What to build it on |
|---------------|---------------------|
| `notebooklm-research` | A routing skill in front of `notebooklm` |
| `agent-web-fetch` | A routing skill in front of `agent-reach`, `scrapling` and the Chrome tools |
| `deep-research` | `WebSearch` and `WebFetch`, with a rule that a claim needs two independent sources |
| `video-watcher` | ffmpeg, yt-dlp and whisper.cpp from Step 8 |
| `channel-mine` | yt-dlp caption pulls, grouped by theme |
| `site-cloner` | Playwright and cheerio |
| `client-asset-harvester` | Playwright |
| `loc-dl` | The public loc.gov JSON API |
| `image-search-mcp` | Free API keys from Pexels, Unsplash and Pixabay |
| `workspace-diff`, `tool-vetting`, `voice-extractor` | Plain skills. No outside tools needed |

To build one, give Claude the row from this file and the tables above, and ask it to write the skill. `02-skill-integration-patterns.md` shows where to wire it in.

---

## If You Only Install Three

1. **`notebooklm`** for anything long: videos, courses, stacks of PDFs.
2. **`scrapling`** for the pages the built-in fetch cannot read.
3. **`markitdown`** for the documents people send you.

Add the rest when a real job needs one.
