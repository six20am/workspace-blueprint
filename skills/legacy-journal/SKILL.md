---
name: legacy-journal
description: "A journal a parent or grandparent keeps for their kids: written entries from one good question at a time, video and voice entries transcribed on this computer, sealed letters to open on a set date or birthday, and a printable book of it all. Everything stays in one plain folder the kids can open with no app. Use when the person says legacy, journal for my kids, letters to my children, time capsule, something to leave them, stories for the grandkids, record my life, or asks for a question to write about."
---

# legacy-journal

Nothing to install. Everything lives in `legacy/` in the workspace folder, in files any computer can open in fifty years:

```
legacy/
  README.md                         a short note to the kids: what this is and how to open it
  people.md                         one line per child: "Ava | 2022-06-01"
  entries/2026/2026-11-02 - the kitchen on Elm Street.md
  video/2026/2026-11-02 - first snow.mp4    and the transcript beside it, same name, .md
  letters/2040-06-01 - for Ava - on your 18th birthday.md
  letters/given/                    letters already handed over
  book/                             printable books, made on request
```

## Set up once

Ask for each child's first name and birthday and write `people.md`. Write `README.md` in the person's voice (`voice.md` if there is one): two or three lines on what this folder is, then "Written entries are in entries, videos in video. Open any .md file with Notepad or TextEdit." Offer `backup` once: a journal for the kids is the one folder that must outlive this computer.

## A written entry

Offer one question, wait, and let them talk or type. Ask for a scene, not a summary. "Tell me about your childhood" gets a paragraph; "walk me into the kitchen you grew up in: who is there, what does it smell like?" gets the story. One question at a time, and when they stop, one follow-up at most: "What did she say, exactly?"

Questions to draw from, gentlest first:

- The house you grew up in. Walk me through the front door.
- A meal you still think about. Who cooked it?
- The first job you had. What did your hands do all day?
- Someone who was kind to you when they did not have to be.
- How you met their mother or father. What were you wearing?
- The day each of them was born. What was the weather?
- Something you got wrong, and what you did next.
- What you were afraid of at their age.
- A place you want them to see, and why.
- What you know now that you wish someone had told you.

An object helps: "Grab one thing from the house that has a story." Start there.

Write it down in their words. Fix spelling, keep the detours, the "anyway, where was I", the way they say things. That is the voice the kids will want. File it as `entries/YYYY/YYYY-MM-DD - <a few words>.md`:

```
# The kitchen on Elm Street
For: everyone
Asked: Walk me into the kitchen you grew up in.

Grandma Rose had the radio on every morning, a station out of ...
```

`For:` is `everyone` or one or more names. If a date or name is unsure, keep it unsure ("around 1985, I think"). If they tell it differently next time, keep both.

## A video or voice entry

They record on the phone, close to the face, in a quiet room, and drop the file in. Move it to `video/YYYY/YYYY-MM-DD - <a few words>.<ext>`, then make the transcript beside it:

```
python tools/voice-memo/memo.py "legacy/video/2026/2026-11-02 - first snow.mp4" --into legacy/video/2026   # python3 on Mac and Linux
```

Rename the transcript to the video's name with `.md`, add the `# title` and `For:` lines at the top, and delete the empty `## Notes` and `## To do` headings; a legacy entry has no to-do list. Mark what whisper missed as `[unclear]`; never guess a name. Large files: `media-tools` can shrink a copy, never replace the original.

## A sealed letter

Ask who it is for and when they should open it: a date, or an age ("when Ava turns 18"). For an age:

```
python tools/legacy-journal/legacy.py age Ava 18
```

It prints the date from `people.md`. Write the letter in their words to `letters/YYYY-MM-DD - for <name> - <occasion>.md`, the date being the day to open it. After that it is sealed: do not quote it, summarize it, or put it in a book. The weekly brief names a letter 30 days before its date, by file name only, so the person can print it or hand it over. When it is given, move it to `letters/given/`.

```
python tools/legacy-journal/legacy.py letters
```

lists what is due, coming, and sealed for later.

## The book

```
python tools/legacy-journal/legacy.py book --for Ava --title "For Ava, from Dad"
```

It gathers the entries and video transcripts in date order (the ones for everyone and the ones for that name) into one Markdown file in `book/`, and prints the path. Sealed letters stay out. Then `document-builder` turns it into a PDF or Word file to print and bind. Show the person the draft before anyone else sees it.

## Never

- Read, quote or summarize a sealed letter, or put one in a book, until it is moved to `letters/given/`.
- Upload, post, email or share anything in `legacy/`. Print and hand-over are the person's to do.
- Smooth their words into polished prose, or add a feeling or memory they did not say.
- Guess a date, a name or what a recording said.
- Push a hard topic. "Skip that" means skip it, and do not bring it back up.
- Delete or replace an original video or recording.
