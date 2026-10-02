# Agent Setup: Claude Code, Codex and Antigravity

<!--
The blueprint is a folder of Markdown. It does nothing until an agent
opens it. This file covers the three agents the workspace runs on, how
to install each one, and how to make all three read the same map so
you never keep three copies of your rules.
-->

## Which One Does What

| Agent | Made by | Role in the workspace | Paid by |
|-------|---------|-----------------------|---------|
| **Claude Code** | Anthropic | The main one. It plans, writes, reviews and runs the others. | Claude subscription |
| **Codex** | OpenAI | Second opinion on a risky change. Bulk code edits inside a sandbox. | ChatGPT subscription |
| **Antigravity** | Google | Gemini models. Long reads, a different point of view, and image generation. | Google AI subscription |

**You only need Claude Code to start.** Add the other two when you want a second model to check the first, or when you need images.

All three sign in with a subscription login. None of the steps below need an API key.

---

## Step 1: Claude Code

**Install.** Pick one.

```powershell
# Windows, in PowerShell
irm https://claude.ai/install.ps1 | iex
```

```bash
# Mac or Linux
curl -fsSL https://claude.ai/install.sh | bash
```

```bash
# Any system with Node.js 20 or newer
npm install -g @anthropic-ai/claude-code
```

**Sign in and open the workspace.**

```bash
cd path/to/workspace-blueprint
claude
```

The first run opens a browser so you can sign in. After that, Claude Code reads `CLAUDE.md` in the folder you started it from. That file is the map.

**Add the plugins.** Inside Claude Code:

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

| Plugin | What it adds |
|--------|--------------|
| `superpowers` | Brainstorming, planning, debugging and review habits the agent follows on its own |
| `frontend-design` | Better-looking web pages and interfaces |
| `document-skills` | Read and write Word, Excel, PowerPoint and PDF files |

**Check it worked:** type `/help` and confirm the session opened in your workspace folder. Then ask "What does CLAUDE.md say this workspace is for?" It should answer from the file.

**Where your own skills go:** `.claude/skills/<skill-name>/SKILL.md` inside the workspace. Skills there travel with the folder.

---

## Step 2: Codex

**Install.**

```bash
npm install -g @openai/codex
codex login          # sign in with your ChatGPT account
codex login status   # confirms you are signed in
```

**Open the workspace.**

```bash
cd path/to/workspace-blueprint
codex
```

Codex reads `AGENTS.md`, not `CLAUDE.md`. See "One Map, Three Agents" below.

**Let Claude Code call Codex.** Inside Claude Code:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/codex:setup
```

After that you can stay in Claude Code and say "ask Codex to review this change."

**Check it worked:** run `codex exec "List the top-level folders here and say what each is for."` from the workspace folder.

---

## Step 3: Antigravity

**Install.** Download Antigravity from Google at `antigravity.google` and sign in with your Google account. The command-line tool it installs is named `agy`.

```bash
agy --version
agy models                          # lists the models your plan can use
agy -p "Say hello in five words."   # one prompt, prints the answer, exits
```

Run `agy models` before you pick a model by name. The list changes between versions.

**Open the workspace.**

```bash
cd path/to/workspace-blueprint
agy
```

Antigravity reads `GEMINI.md` and `AGENTS.md`.

**Check it worked:** `agy -p "Read CLAUDE.md and name the workspaces it lists."`

---

## One Map, Three Agents

Each agent looks for a different file name. Do not write your rules three times. Keep `CLAUDE.md` as the one map and make the other two files short pointers to it.

**`AGENTS.md`** (read by Codex and Antigravity):

```markdown
# Agents

This workspace uses a three-layer layout. Read these in order.

- **The map:** `CLAUDE.md` holds the folder map, naming rules and how work moves between workspaces.
- **The router:** `CONTEXT.md` sends each task to the right workspace.
- **The workspaces:** each folder has its own `CONTEXT.md`. Load only the one the task needs.

Skills live in `.claude/skills/`. Read a skill's `SKILL.md` before doing the job it covers.
```

**`GEMINI.md`** (read by Antigravity):

```markdown
# Gemini Workspace Instructions

- **Workspace map:** see `CLAUDE.md`
- **Task router:** see `CONTEXT.md`
- **Agent rules:** see `AGENTS.md`
```

**Why it works:** a rule lives in one file. When you change it, all three agents see the change. Two files that say the same thing will drift, and then one of them is wrong.

---

## Who Runs Whom

Run one agent as the lead and treat the others as helpers it calls. In this workspace Claude Code is the lead.

| Job | Send it to | Why |
|-----|-----------|-----|
| Planning, writing, anything that needs the whole conversation | Claude Code | It holds the context |
| A second opinion on a risky change | Codex | A different model family catches different mistakes |
| A very long document or many files to read at once | Antigravity (Gemini) | Large context window, low cost |
| An image | Antigravity (Gemini) | It is the image model of the three |

**Three rules for handing work over:**

1. **What comes back is untrusted.** Another model's answer is a draft to check, not a fact. Read it before you act on it.
2. **Say what it must not invent.** Name the facts the helper may not make up: prices, dates, names, numbers.
3. **Do not hand over small jobs.** A round trip takes ten to thirty seconds. If the job is two steps, the lead should just do it.

**Before sending client material to any model,** read that provider's data terms for your plan. Do not assume a subscription login covers client data.

---

## Install Order for a New Machine

1. Git, Node.js and Python (see Step 0 in `05-intake-tools.md`)
2. Claude Code, then sign in
3. Open the workspace folder and confirm it reads `CLAUDE.md`
4. The three plugins
5. `AGENTS.md` and `GEMINI.md` pointer files
6. Codex and Antigravity, if you want them
7. The intake tools from `05-intake-tools.md`, one at a time, as jobs call for them
