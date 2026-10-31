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

Windows now. Mac is new and untested.

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

<!-- can-do -->
## What it can do on day one

It arrives knowing how to do twenty-one things. Most of them bring outside material in: web pages, posts, videos, documents, photos. The rest look after the workspace itself. Here's the list, straight from the files.

<!-- generated skill list goes here -->

<!-- two-ways -->
## Two ways to run it

**Claude Code, on your own computer.** This is the zip. Unzip it, double-click setup, answer four questions, and everything lives in a folder on your machine. Windows is tested. Mac is new and untested.

**Grok Bot, on its own cloud computer.** Same method, rebuilt as a Grok Bot template. Nothing to install, because the bot already has a computer. Its first conversation asks the four questions, builds its folder, and saves a rule so it reads the map before every task. The template isn't out yet. The repo is: github.com/six20am/grokbot-blueprint.

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

<!-- installed -->
## What gets installed, and what doesn't leave your computer

Free, standard tools: Git, Python, Node.js, ffmpeg, a browser engine, Claude Code, and the readers and converters the skills use. About 500 MB.

Setup sends nothing anywhere. It signs in to nothing for you. Five things need your own sign-in, Claude among them, and setup lists them at the end so you can do each one yourself. Anything a tool fetches from outside is treated as something to read, never as an instruction to follow.

<!-- stays-current -->
## It doesn't go stale

New skills and tools land in the public repo as they're built. Double-click `update.cmd`, or ask Claude to update, and your workspace pulls them in and installs anything new. It never touches your own files or the folders it built for you. If you edited one of the template files, a copy is saved first. Once the workspace is 30 days old, Claude asks once whether you want to update. It never updates without your yes.

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
Nothing during setup. Afterward, the only things that leave are what you ask Claude to go fetch or send, and the sign-ins you do yourself.

**Can I undo it?**
Yes. It's one folder and a few standard programs. Delete the folder and everything it built is gone. The programs came in through winget on Windows or Homebrew on a Mac, and they come out the same way.

<!-- close -->
## Give it one real job this week

Download it, run setup, and hand it the thing you've been putting off.

[Download the zip]

<!-- footer -->
Made by Six20AM. Source on GitHub: github.com/six20am/workspace-blueprint and github.com/six20am/grokbot-blueprint. The routing method comes from a teaching kit, used with its author's permission.

<!-- page-level -->
title: Workspace Blueprint: an AI that works out of your files
meta: A free folder for your own computer. One double-click installs Claude Code and the tools, then four questions build a workspace around how you work.
