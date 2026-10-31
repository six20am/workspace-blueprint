---
name: voice-memo
description: "Turns a voice recording from a phone into a transcript, a few lines of notes and a to-do list, filed by date. Runs on the person's own computer with the speech-to-text that video-watcher already uses; nothing is uploaded. Use when the person drops in an audio file, says they recorded a memo, a note to self, a thought in the car, or asks what they said in a recording."
---

# voice-memo

Setup installed the pieces for `video-watcher`: ffmpeg, whisper.cpp and its English model. This skill reuses them. Nothing leaves the computer.

## When

A recording lands in the workspace (`.m4a`, `.mp3`, `.wav`, `.ogg`, `.opus`, `.aac`, `.webm`), or the person says "I recorded something", "voice memo", "listen to this", "what did I say in the car". A recording the person forwarded themselves from a phone is the usual case.

## The one command

```
python tools/voice-memo/memo.py <recording>   # python3 on Mac and Linux
```

It converts the audio, runs the transcript on this machine, and writes `voice-memos/YYYY-MM-DD-<name>.md` with the transcript under its own heading and two empty headings, `## Notes` and `## To do`. It prints the path. The recording stays where it was. Exit 3 means a program is missing; it says which, and `doctor` puts it back.

## Then read it and fill the two headings

Read the transcript once. Write three to eight note lines and the to-dos, in the person's words, not a summary voice. A memo that said this:

> uh so the Hendersons want the fence done before the fourth, I need to call the lumber yard about the posts, and remind me we're out of the brown stain, oh and Sam's invoice is still not paid, that's two weeks now

gets this:

```
## Notes
- Hendersons: fence done before July 4.
- Out of brown stain.
- Sam's invoice unpaid, two weeks now.

## To do
- [ ] Call the lumber yard about posts
- [ ] Buy brown stain
- [ ] Chase Sam's invoice
```

Then say it back in two lines: "Three to-dos: lumber yard, stain, Sam's invoice. The Hendersons want the fence before the fourth." Offer, once, to put anything owed into `waiting-on` and any date into `paperwork/dates.md`. The person says yes or no.

## When the transcript is rough

Whisper misses names and mumbles. Keep what it heard, mark what it did not: `[unclear]` in the transcript, and a note line "Two names did not come through; listen at about 0:40." Never fill a gap with a guess.

## Never

- Upload the recording or the transcript to any service. Local only.
- Do a to-do. Listing "call the lumber yard" is the job; calling is the person's.
- Delete or move the recording.
- Invent a name, a number or a date the recording did not say.
- Transcribe a recording of someone else without the person saying it is theirs to transcribe.
