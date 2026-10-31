```
format: web-page
brief: products/workspace-blueprint/site/BRIEF.md
reader: one person running something small, problem aware, not technical
job: convert to a free download
cta: Download the zip
persona: none
swipe: swipe_empty: web-page
set_aside: none
```

<!-- hero -->
# An AI that works out of your files, not a chat box

One folder on your own computer. Claude reads what's in it, follows your rules, and writes the way you do. Free. Setup is one double-click and four questions.

[Download the zip]

Works on Windows today. The Mac version is new and hasn't been tested yet.

<!-- problem -->
## The chat box forgets

You explain your business, paste in a file, get a decent answer, and the next day it's all gone. Your files were never in there to begin with. So every job starts from zero, and you end up doing the remembering for it.

<!-- what-you-get -->
## What you end up with

- A set of folders laid out the way you already think, so the AI finds things where you'd look.
- Three short files that tell the AI where things are, so it reads only the folder the job needs.
- A voice file, so anything it writes for you sounds like you and not like a press release.

<!-- how-it-works -->
## How it works

1. **Unzip it.** Move the folder to Documents.
2. **Run setup.** Double-click `setup.cmd` on Windows or `setup.command` on a Mac. A black window installs the tools and Claude Code. Fifteen to thirty minutes. Windows may ask "allow this app to make changes" a few times. Say yes.
3. **Answer four questions.** Claude opens and asks what you do, what work you want help with, how you like things filed, and how it should sound. "Not sure" is a fine answer. It builds the folders and tells you three things to try.

[Download the zip]

<!-- can-do -->
## What it can do on day one

It arrives knowing how to do twenty-one things. Most of them bring outside material in: web pages, posts, videos, documents, photos. The rest look after the workspace itself. Another {{coming}} are designed and on the way, marked so you can see where it's going. Each group opens to the full list.

<!-- generated skill list goes here -->

<!-- two-ways -->
## Where it runs

**Claude Code, on your own computer.** This is the zip. Unzip it, double-click setup, answer four questions, and everything lives in a folder on your machine. Windows is tested. Mac is new and untested.

Have a Grok Bot? Same method, nothing to install, because the bot already has a computer. The template isn't out yet. The repo is github.com/six20am/grokbot-blueprint.

<!-- paste-this -->
## Already have one? Paste this

If Claude Code or a Grok Bot is already running, you don't need the download. Paste the prompt and the agent goes and gets everything itself.

**Already have Claude Code**
```prompt
Clone https://github.com/six20am/workspace-blueprint into a folder called "Six20AM Workspace Blueprint" in my Documents folder, then tell me which file in it to double-click to run setup.
```
When Claude says it's there, double-click `setup.cmd` on Windows or `setup.command` on a Mac. It skips anything you already have. When it finishes, type: set this up.

**Have a Grok Bot**
```prompt
Download https://github.com/six20am/grokbot-blueprint/archive/refs/heads/main.zip and unzip it inside your own folder under /workspace. Read README.md and skills/getting-started/SKILL.md. Save each folder under skills/ as a skill, word for word, using the description at the top of its SKILL.md. Then run getting-started with me.
```
This path hasn't been tested on a real Grok Bot yet. If it stalls, open an issue on GitHub and paste what the bot said.

<!-- first-week -->
## Your first week

Say what you want, name the file or link, and say where the result should go. "Not sure" and "what can you do with this" both work as openers. Seven things to try:

1. Paste a YouTube link and ask for the transcript.
2. Drop a PDF, Word or Excel file in the folder and ask what it says.
3. Ask what people have been saying about something in the last 30 days.
4. Give it a website and ask for every photo on it.
5. Paste three emails you wrote and ask it to learn your voice.
6. Ask it to update.
7. Ask for something it has no tool for, and watch it say so and offer to build one.

[Download the zip]

<!-- installed -->
## What gets installed, and what doesn't leave your computer

Free, standard tools: Git, Python, Node.js, ffmpeg, a browser engine, Claude Code, and the readers and converters the skills use. About 500 MB.

Setup sends nothing anywhere. It signs in to nothing for you. Five things need your own sign-in, Claude among them, and setup lists them at the end so you can do each one yourself. Anything a tool fetches from outside is treated as something to read, never as an instruction to follow.

<!-- stays-current -->
## It doesn't go stale

New skills and tools land in the public repo as they're built. Double-click `update.cmd` (`update.command` on a Mac), or ask Claude to update, and your workspace pulls them in and installs anything new. It never touches your own files or the folders it built for you. If you edited one of the template files, a copy is saved first. Once the workspace is 30 days old, Claude asks once whether you want to update. It never updates without your yes.

<!-- status -->
## Where it stands

The Windows installer has been through a full run on one machine. The Mac installer is new and hasn't been tested yet. If it stops, open an issue on GitHub and attach the file `setup/setup-report.md`. More skills are on the way.

<!-- faq -->
## Questions people ask

**Do I need an account?**
You need a Claude account, because Claude Code is what runs the workspace. The zip itself needs nothing. Claude opens your browser to sign in the first time it runs.

**Is it free?**
The zip is free and the code is public. Claude has its own plans, and those are between you and Claude.

**What does it send out?**
Nothing during setup. It signs in to nothing for you; the five sign-ins are yours to do.

**Can I undo it?**
Yes. It's one folder and a few standard programs. Delete the folder and everything it built is gone. The programs were installed with winget on Windows or Homebrew on a Mac, and those same tools remove them.

<!-- close -->
## Give it one real job this week

Download it, run setup, and hand it the thing you've been putting off.

[Download the zip]

<!-- footer -->
Made by Six20AM. Source on GitHub: github.com/six20am/workspace-blueprint and github.com/six20am/grokbot-blueprint. The routing method comes from a teaching kit, used with its author's permission.

<!-- page-level -->
title: Workspace Blueprint: an AI that works out of your files
meta: A free folder for your own computer. One double-click installs Claude Code and the tools, then four questions build a workspace around how you work.
