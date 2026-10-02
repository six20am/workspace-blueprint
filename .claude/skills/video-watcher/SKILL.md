---
name: video-watcher
description: >-
  Analyze video locally: no third-party video-analysis service.
  Mode A (transcript-only, DEFAULT, cheap) produces a timestamped transcript from a
  local file or YouTube URL. Mode B (AI Watch) adds ffmpeg frame extraction for a
  scene-by-scene visual + audio breakdown. Use when the user wants to transcribe,
  watch, summarize, review, or break down a video / ad / UGC clip, pull quotes or
  spoken copy, or do an ad-creative / shot teardown. Triggers: /video-watcher,
  "transcribe this video", "watch this video", "what does this ad say", "break down
  the shots", "ad teardown", "scene breakdown".
---

# video-watcher

Two modes. Pick the cheapest one that answers the question.

- **Mode A: Transcript-Only (DEFAULT):** what was *said*. Content questions, quote pulling,
  summaries, script review, spoken ad-copy extraction. No frame processing.
- **Mode B: AI Watch:** what was *shown* + said. Ad-creative teardown, UGC style analysis,
  scene composition, shot breakdown, product-demo review. Costs scale with length × frame density.

## 0. Preconditions

This skill shells out to local tooling. Resolve paths once at the top of a run:

```bash
export WHISPER_HOME="${WHISPER_HOME:-$HOME/tools/whisper}"
export WHISPER_MODEL="${WHISPER_MODEL:-$WHISPER_HOME/models/ggml-base.en.bin}"
```

Before doing anything, verify tools exist:

```bash
command -v ffmpeg >/dev/null || echo "MISSING: ffmpeg"
[ -x "$WHISPER_HOME/bin/Release/whisper-cli.exe" ] || echo "MISSING: whisper.cpp: see SETUP.md"
[ -f "$WHISPER_MODEL" ] || echo "MISSING: model: see SETUP.md"
command -v yt-dlp >/dev/null || echo "NOTE: yt-dlp absent: URLs won't work, local files still will"
```

If whisper.cpp or the model is missing, stop and point the user to `SETUP.md`. Do not silently fall
back to any cloud service.

> **Language note:** the default model `ggml-base.en.bin` is **English-only**. For other languages,
> download a multilingual model (`ggml-base.bin` / `ggml-small.bin`) per SETUP.md and set
> `WHISPER_MODEL`. Never guess a translation the model didn't produce.

## 1. Mode selection

- If the user named a mode, use it.
- If the request clearly needs visuals ("how does this ad *look*", "break down the shots",
  "what's on screen"), use **Mode B**.
- Otherwise **default to Mode A** and, if it's genuinely ambiguous, ask exactly one question:
  *"Do you need the visual content analyzed, or just what was said?"*

## 2. Set up a work directory

Use a scratch dir so temp files are easy to clean:

```bash
WORK="$(mktemp -d)"   # or a named dir under the scratchpad if the user wants artifacts kept
```

## 3. Get the source

**A YouTube link the person sends goes to NotebookLM first, not here.** Route it through the
`notebooklm-research` skill, § YOUTUBE ROUTING.
This skill takes a YouTube URL only when the job is the footage itself (cuts, on-screen text,
shot breakdown), when a raw timestamped transcript is the deliverable, or when NotebookLM's
source never reaches READY.

- **Local file:** use the path directly.
- **YouTube / URL, Mode A:** try existing captions first (free, instant), then fall back to audio:

  ```bash
  bash scripts/try_captions.sh "$URL" "$WORK"     # prints a .vtt path if captions exist
  bash scripts/get_source.sh   "$URL" "$WORK" audio   # prints source.mp3 if we must transcribe
  ```

  If captions came back, you can read the `.vtt` directly and skip Whisper.
- **YouTube / URL, Mode B:** you need the pixels, so download video:

  ```bash
  bash scripts/get_source.sh "$URL" "$WORK" video   # prints the downloaded video path
  ```

## 4. Mode A: Transcript

```bash
bash scripts/transcribe.sh "<audio_or_video_path>" "$WORK"   # writes $WORK/transcript.srt + .txt
```

Read `$WORK/transcript.srt` for timestamps, or `.txt` for plain text. Deliver a **timestamped
transcript**. Add a summary only if asked. Do not invent words: if a stretch is `[inaudible]` or
Whisper emitted nothing, say so.

## 5. Mode B: AI Watch

1. Transcribe (step 4) to get the timeline of spoken content.
2. Extract frames:

   ```bash
   bash scripts/extract_frames.sh "<video_path>" "$WORK/frames" 2   # 1 frame / 2s (arg is interval sec)
   ```

   Frame `frame_00001.jpg` ≈ t=0s, `frame_00002.jpg` ≈ t=(interval)s, … i.e.
   `timestamp ≈ (index − 1) × interval`.
3. **Length guard:** before extracting, check duration. If > **10 minutes**, warn the user that
   interval sampling leaves gaps and accuracy degrades: offer (a) denser frames, or (b) splitting
   the video into segments: and let them choose before proceeding.
4. Read the frames as images (Read tool, in timestamp order) and build a scene description. Group
   consecutive similar frames into scenes; note the timestamp where the shot changes.
5. Merge visual + spoken content on a shared timeline into the output table below.

## 6. Output formats

**Mode A**: timestamped transcript (SRT-style ranges), optional summary.

**Mode B**: scene-by-scene table:

| Timestamp | Visual description | Spoken content | Notes |
|-----------|--------------------|----------------|-------|
| 00:00–00:04 | … what is on screen … | … what is said … | camera / text-on-screen / product / cut |

## 7. Hard rules

- **Never fabricate.** No content that isn't in the source. Ambiguous frame → say "ambiguous".
  Unclear audio → "[unclear]". Silence → note it. Don't fill gaps with plausible guesses.
- **No cloud fallback.** Fully local (ffmpeg + whisper.cpp). Never route to any
  third-party analysis API.

  This governs *analysis*: do not send a video off this machine for someone else's model to
  watch, describe or summarize. A video containing other people's personal details or
  unreleased material does not leave this machine for any provider.
- **Clean up.** Delete `$WORK` (extracted audio + frames) after delivering, unless the user asked to
  keep artifacts. Frames are the bulk of the disk/token cost.

## 8. Tuning

- `interval` (Mode B): lower = denser frames, more detail, more tokens. Default 2s; try 1s for
  fast-cut ads, 3–5s for talking-head/long content.
- `WHISPER_MODEL`: `base.en` (fast, English) → `small`/`small.en` (slower, more accurate) →
  multilingual base/small for non-English. See SETUP.md.

See `gotchas.md` for edge cases and `SETUP.md` for one-time install.
