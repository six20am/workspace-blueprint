# video-watcher: gotchas

- **DLLs must sit next to `whisper-cli.exe`.** The BLAS/ggml `*.dll` files ship in `bin/Release`
  alongside the exe. Don't move the exe out on its own: it won't load its backend.
- **`base.en` is English-only.** Feeding it non-English audio yields garbage or forced-English
  output. Switch `WHISPER_MODEL` to a multilingual model (`ggml-base.bin` / `ggml-small.bin`) and set
  `WHISPER_LANG` for other languages. Never present a guessed translation as the transcript.
- **whisper.cpp wants 16 kHz mono.** `transcribe.sh` already converts via ffmpeg; don't feed raw
  video straight to `whisper-cli` even though it lists mp3/wav/flac/ogg support: resample first.
- **Frame timestamps are approximate.** `frame_k ≈ (k-1) × interval`. Good enough for scene mapping,
  not frame-exact. For precise shot-cut times use scene detection:
  `ffmpeg -i in -vf "select='gt(scene,0.4)',showinfo" -vsync vfr out_%04d.jpg` and read `showinfo`
  `pts_time` from stderr.
- **Token cost is frames, not audio.** A 5-min ad at 1 frame/2s = 150 images. Downscale (already
  capped at 768px wide) and widen the interval on long/slow content. Always honor the 10-min length
  guard before extracting.
- **YouTube captions ≠ transcript quality.** Auto-captions can be wrong/unpunctuated. `try_captions.sh`
  is a free first pass; if the user needs fidelity, skip captions and run Whisper on the audio.
- **Always clean up `$WORK`.** Extracted audio + hundreds of frames pile up fast. Delete the temp dir
  after delivering unless the user asked to keep artifacts.
- **Age-gated / private / region-locked URLs** may fail in `yt-dlp`: surface the yt-dlp error to the
  user; don't pretend a transcript exists.
