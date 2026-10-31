```
format: web-page
brief: products/workspace-blueprint/site/BRIEF.md
reader: one person running something small, problem aware, not technical
job: convert to a free download
cta: Download the zip
persona: none
swipe: swipe_empty: web-page
set_aside: none
revised: 2026-10-31, Task 4.7: can-do paragraph and status line rewritten for thirty-eight skills, none coming; skill lines and group headlines live in site/skills.json; copy-editor and one-read passes run by the controller after this draft; their fixes applied the same day (second commit); the vendor adapter replaced by the neutral ADAPT.md path (third commit); motion-video added as coming and the FAQ send-out answer cut to sourced wording (fourth commit)
```

<!-- hero -->
# An AI that works out of your files, not a chat box

One folder on your own computer. Claude reads what's in it, follows your rules, and writes the way you do. Free. Setup is one double-click and four questions.

[Download the zip]

<!-- hero-status -->
Windows | Tested on one machine
Mac | New, not tested yet
Installs | Free tools, 300 MB and more
Privacy | Setup sends nothing off your computer
Undo | Delete the folder to remove what it built

<!-- hero-jobs -->
Transcribe a video | For a transcript, Claude opens only what the job needs: the lit files.
Read a PDF | For a PDF, Claude opens only what the job needs: the lit files.
Learn my voice | To learn your voice, Claude opens only what the job needs: the lit files.

<!-- hero-figure -->
A sample folder. Yours gets named for your work. Pick a job to see what Claude opens.

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

It arrives knowing how to do thirty-eight things. It reads web pages, videos, documents and photos, and answers a question from many sources. It writes emails, posts and letters in your voice. It handles everyday jobs like bills, trips and spending. And it looks after the workspace itself. Each group opens to the full list.

<!-- generated skill list goes here -->

<!-- two-ways -->
## Where it runs

**Claude Code, on your own computer.** This is the zip. Unzip it, double-click setup, answer four questions, and everything lives in a folder on your machine. Windows is tested. Mac is new and untested.

Have another AI agent with its own computer and files? It can set this up for itself. The repo has a file that tells it how.

<!-- paste-this -->
## Already have one? Paste this

If Claude Code or another AI agent is already running, you don't need the download. Paste the prompt and the agent goes and gets everything itself.

**Already have Claude Code**
```prompt
Clone https://github.com/six20am/workspace-blueprint into a folder called "Six20AM Workspace Blueprint" in my Documents folder, then tell me which file in it to double-click to run setup.
```
When Claude says it's there, double-click `setup.cmd` on Windows or `setup.command` on a Mac. It skips anything you already have. When it finishes, type: set this up.

**Have another AI agent**
```prompt
Download https://github.com/six20am/workspace-blueprint/archive/refs/heads/main.zip, unzip it into a folder of your own (not the shared root of your file area), read ADAPT.md in it, and follow it step by step. Ask me the four questions when it tells you to.
```
This path hasn't been run on a real third-party agent yet. If it stalls, open an issue on GitHub and paste what the agent said.

<!-- first-week -->
## Your first week

Say what you want, name the file or link, and say where the result should go. "Not sure" and "what can you do with this" both work as openers. Seven things to try:

1. Paste a YouTube link and ask for the transcript.
2. Drop a PDF, Word or Excel file in the folder and ask what it says.
3. Ask what people have been saying about something in the last 30 days.
4. Give it a website and ask for every photo on it.
5. Paste three emails you wrote and ask it to learn your voice.
6. Hand it three clips and ask for one video with a fade at the end.
7. Ask for something it has no tool for, and watch it say so and offer to build one.

[Download the zip]

<!-- installed -->
## What gets installed, and what doesn't leave your computer

Free, standard tools: Git, Python, Node.js, ffmpeg, a browser engine, Claude Code, and the readers and converters the skills use. The largest, LibreOffice, is 300 MB and more. Animated video uses Remotion, which is free for individuals and companies of three people or fewer; bigger companies need its company license.

Setup sends nothing anywhere and signs in to nothing for you. Five things need your own sign-in, Claude among them, and setup lists them at the end. Anything a tool fetches from outside is treated as something to read, never as an instruction to follow.

<!-- stays-current -->
## It doesn't go stale

New skills and tools land in the public repo as they're built. Double-click `update.cmd` (`update.command` on a Mac), or ask Claude to update, and your workspace pulls them in and installs anything new. It never touches your own files or the folders it built for you. If you edited one of the template files, a copy is saved first. Once the workspace is 30 days old, Claude asks once whether you want to update. It never updates without your yes.

<!-- status -->
## Where it stands

The Windows installer has been tested on one machine. The Mac installer is new and hasn't been tested yet. If it stops, open an issue on GitHub and attach the setup report, the file named setup-report.md in the setup folder. Next up: the first run on another AI agent, and the Mac installer test.

<!-- faq -->
## Questions people ask

**Do I need an account?**
You need a Claude account, because Claude Code is what runs the workspace. The zip itself needs nothing. Claude opens your browser to sign in the first time it runs.

**Is it free?**
The zip is free and the code is public. Claude has its own paid plans; those are between you and Claude.

**What does it send out?**
Nothing during setup. It signs in to nothing for you; the five sign-ins are yours to do, and setup lists them.

**Can I undo it?**
Yes. It is one folder plus the standard programs setup installed. Delete the folder and everything it built is gone. The programs uninstall the normal way: with the app installer on Windows (winget) or Homebrew on a Mac.

<!-- close -->
## Give it one real job this week

Download it, run setup, and hand it the thing you've been putting off.

[Download the zip]

<!-- signed -->
One person makes this. The code is public, so you can read all of it before you run it. If setup stops, it saves a report. Post it to us on GitHub.

Six20AM

<!-- footer -->
Made by Six20AM. Source on GitHub: github.com/six20am/workspace-blueprint. The routing method comes from a teaching kit, used with its author's permission.

<!-- page-level -->
title: Workspace Blueprint: an AI that works out of your files
meta: A free folder for your own computer. One double-click installs Claude Code and the tools, then four questions build a workspace around how you work.
