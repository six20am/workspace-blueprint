# Test: voice-memo

## The ask
"I recorded a memo in the truck this morning, it's in the inbox folder. What did I say?"

## The input
One audio file in the workspace. ffmpeg, whisper.cpp and its model, which setup installed for video-watcher.

## Done looks like
`python tools/voice-memo/memo.py <file>` run; `voice-memos/YYYY-MM-DD-<name>.md` written with the transcript, then `## Notes` (three to eight lines in the person's words) and `## To do` (one `- [ ]` line per task), filled in by reading the transcript. Two lines said back: the to-dos, and the one fact worth knowing. Unclear passages marked, not guessed. The recording left where it was; nothing uploaded; no to-do carried out.
