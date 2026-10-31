```
format: web-page
brief: products/workspace-blueprint/site/BRIEF.md
reader: one person running something small, using or trying an AI service, not technical
job: get the prompt copied and pasted into an AI service
cta: Copy the prompt
persona: none
swipe: swipe_empty: web-page
set_aside: none
revised: 2026-10-31, Task 4.7: can-do paragraph and status line rewritten for thirty-eight skills, none coming; skill lines and group headlines live in site/skills.json; copy-editor and one-read passes run by the controller after this draft; their fixes applied the same day (second commit); the vendor adapter replaced by the neutral ADAPT.md path (third commit); motion-video added as coming and the FAQ send-out answer cut to sourced wording (fourth commit); round-two editor and one-read fixes (sixth commit); page repositioned to AI services first, Claude Code second, on Michael's word; why section added 2026-10-31 (Michael: reasons to use it, as a marketing page), how-it-works step 3 and the meta line follow the revised setup questions
```

<!-- hero -->
# One prompt, and your AI works out of your files, not a chat box

Paste this into an AI service where the AI can run programs and keep files. It builds a folder for your work, follows your rules, and writes the way you do. Free.

```prompt
Download https://github.com/six20am/workspace-blueprint/archive/refs/heads/main.zip, unzip it into a folder of your own (not the shared root of your file area), read ADAPT.md in it, and follow it step by step. Ask me the setup questions when it tells you to.
```

[Copy the prompt]

<!-- hero-status -->
AI services | Run once; fixes from that run are in
Claude Code on Windows | Tested on one machine
Claude Code on a Mac | New, not tested yet
Cost | Free. Your AI service has its own plans
Undo | Delete the folder to remove what it built

<!-- hero-jobs -->
Transcribe a video | For a transcript, your AI opens only the files that job needs.
Read a PDF | To read a PDF, your AI checks the map, then looks in the intake folder.
Learn my voice | To learn your voice, your AI checks the map, then opens your voice file.

<!-- hero-figure -->
A sample folder. Yours gets named for your work. Pick a job to see what your AI opens.

<!-- problem -->
## The chat box forgets

You explain your business, paste in a file, get a decent answer, and the next day it's all gone. Your files were never in there to begin with. So every job starts from zero, and you end up doing the remembering for it.

<!-- what-you-get -->
## What you end up with

- A set of folders laid out the way you already think, so the AI finds things where you'd look.
- Three short files that tell the AI where things are, so it reads only the folder the job needs.
- A voice file, so anything it writes for you sounds like you and not like a press release.

<!-- why -->
## Why a folder beats a chat box

- **It remembers.** Your files, your rules and how you like things done live in one folder. The next chat picks up where the last one stopped.
- **It works from your files, not from what you pasted.** Drop in the PDF, the bank export, the three emails you wrote. It reads them where they sit.
- **It sounds like you.** It builds a voice file from your own writing, so the email it drafts could have come from your desk.
- **It already knows how to do thirty-nine things.** Transcribe a video, read a bill, sort your photos, plan a trip, write the post. The full list is further down.
- **It asks before it sends, spends or deletes.** It says so at setup, and you can add to that list. The rule holds in every chat after.
- **It tells you when it can't.** Ask for something it has no tool for and it says so, then offers to build one. It doesn't fake it.
- **It's free, and it's one folder.** The code is public. Delete the folder and it's gone.

<!-- how-it-works -->
## How it works

1. **Copy the prompt.** It's at the top of this page.
2. **Paste it into your AI.** Use a service where the AI can run programs, keep files between chats, and keep a standing instruction. It downloads this blueprint and sets it up for itself.
3. **Answer a few questions.** It asks what you do, names the kinds of work it would set up and checks them with you, and asks how it should sound. Then it shows you the folders, names the three things it will never do without asking (send, spend, delete), and asks what to add. "Not sure" is a fine answer. It builds the folders and tells you what to try first.

If your AI can only chat, this won't work. Use Claude Code instead.

[Copy the prompt]

<!-- can-do -->
## What it can do on day one

It arrives knowing how to do thirty-nine things. It reads web pages, videos, documents and photos, and answers a question from many sources. It writes emails, posts and letters in your voice. It handles everyday jobs like bills, trips and spending. And it looks after the workspace itself. How many work on day one depends on what your AI's computer can run. Each group opens to the full list.

<!-- generated skill list goes here -->

<!-- two-ways -->
## Or run it on your own computer with Claude Code

Claude Code is Claude's tool for working on your own machine. Download the zip and everything installs on your computer. Windows is tested. Mac is new and untested.

1. **Unzip the download.** Move the folder to Documents.
2. **Run setup.** Double-click `setup.cmd` on Windows or `setup.command` on a Mac. A black window installs the tools and Claude Code. Fifteen to thirty minutes. Windows may ask "allow this app to make changes" a few times. Say yes. A Mac refuses it the first time: open System Settings, then Privacy and Security, and click Open Anyway.
3. **Answer a few questions.** Claude opens and asks them one at a time, then builds the folders.

[Download the zip]

**Already have Claude Code?** Paste this and it fetches the zip itself.
```prompt
Download https://github.com/six20am/workspace-blueprint/releases/latest/download/Six20AM-Workspace-Blueprint.zip and unzip it into my Documents folder. Then tell me which file in the new "Six20AM Workspace Blueprint" folder to double-click to run setup.
```
When Claude says the folder is ready, open it and double-click the file it names. Setup skips anything you already have. When it finishes, type `set this up` in Claude.

<!-- first-week -->
## Your first week

Say what you want, name the file or link, and say where the result should go. "Not sure" and "what can you do with this" both work as openers. Seven things to try:

1. Paste a YouTube link and ask for the transcript.
2. Give it a PDF, Word or Excel file and ask what it says.
3. Ask what people have been saying about something in the last 30 days.
4. Give it a website and ask for every photo on it.
5. Paste three emails you wrote and ask it to learn your voice.
6. Hand it three clips and ask for one video with a fade at the end.
7. Ask for something it has no tool for, and watch it say so and offer to build one.

[Copy the prompt]

<!-- installed -->
## What the zip installs, and what doesn't leave your computer

Free, standard tools: Git, Python, Node.js, ffmpeg, a browser engine, Claude Code, and the readers and converters the skills use. The largest, LibreOffice, is 300 MB and more. Animated video uses Remotion, which is free for individuals and companies of three people or fewer; bigger companies need its company license.

On Claude Code, setup sends nothing anywhere and signs in to nothing for you. Five things need your own sign-in, Claude among them, and setup lists them at the end. Anything it fetches from the web or a document is treated as reading material, never as orders.

<!-- stays-current -->
## It doesn't go stale

New skills and tools are added to the public download as they're built. On an AI service, ask it to download the blueprint again and add what's new. On Claude Code, double-click `update.cmd` (`update.command` on a Mac), or ask Claude to update, and your workspace pulls them in and installs anything new. It never touches your own files or the folders it built for you. If you edited one of the files that came with the download, a copy is saved first. Once the workspace is 30 days old, Claude asks once whether you want to update. It never updates without your yes.

<!-- status -->
## Where it stands

The AI service path has been run once on a real service. It got as far as the setup questions. That computer couldn't reach its package source, so the installer now says so up front instead of looking fine, and the questions were tightened from what that run showed. The Claude Code installer has been tested on one Windows machine. The Mac installer is new and hasn't been tested yet. If something stops, open an issue on GitHub. On Claude Code, attach the setup report, the file named setup-report.md in the setup folder. Next up: a full run on an AI service through the build and the first task, and the Mac installer test.

<!-- faq -->
## Questions people ask

**Do I need an account?**
Yes, with whichever AI service you use. The blueprint itself needs nothing. On Claude Code, Claude opens your browser to sign in the first time it runs.

**Is it free?**
The blueprint is free and the code is public. AI services have their own plans, and those are between you and them.

**Where do my files live?**
On the computer your AI service gives it, under that service's rules. If you want them on your own machine, use Claude Code.

**What does it send out?**
On an AI service, your chats and files go through that service. On Claude Code, setup sends nothing. It signs in to nothing for you; the five sign-ins are yours to do, and setup lists them.

**Can I undo it?**
Yes. Delete the folder and everything it built is gone. On an AI service, also ask it to remove the standing rule it saved and the programs it installed. On Claude Code, the programs uninstall the normal way: with the app installer on Windows (winget) or Homebrew on a Mac.

<!-- close -->
## Give it one real job this week

Copy the prompt, paste it in, and hand it the thing you've been putting off.

[Copy the prompt]

<!-- signed -->
One person makes this. The code is public, so you can read all of it before you run it. If it stalls, tell us on GitHub.

Six20AM

<!-- footer -->
Made by Six20AM. Source on GitHub: github.com/six20am/workspace-blueprint. The routing method comes from a teaching kit, used with its author's permission.

<!-- page-level -->
title: Workspace Blueprint: an AI that works out of your files
meta: A free prompt for an AI service that gives the AI its own computer. A few questions build a workspace around how you work. Claude Code version included.
