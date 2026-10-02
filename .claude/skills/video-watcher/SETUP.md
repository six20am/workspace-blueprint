# video-watcher: one-time setup

Fully local. No API keys, no cloud. Repeat these steps on any new machine/environment.

## Dependencies

| Tool | Purpose | This machine |
|---|---|---|
| ffmpeg / ffprobe | audio + frame extraction, duration | ✅ installed (winget gyan.dev build) |
| yt-dlp | YouTube download + caption pulling | ✅ installed (Python Scripts dir) |
| whisper.cpp | offline transcription (no Python) | setup installs it at `~/tools/whisper` |
| model file | Whisper weights | ✅ `ggml-base.en.bin` (English) |

## Installed layout (this machine)

```
~/tools/whisper/
├── bin\Release\whisper-cli.exe   # the binary the skill calls
├── bin\Release\*.dll             # ggml/BLAS backends (must sit next to the exe)
└── models\ggml-base.en.bin       # default model
```

The skill defaults to these paths. Override with env vars if you move them:
`WHISPER_HOME`, `WHISPER_MODEL`.

## Reinstall from scratch (new machine)

1. **ffmpeg:** `winget install Gyan.FFmpeg` (or any static build on PATH).
2. **yt-dlp:** `winget install yt-dlp.yt-dlp` (or `pip install yt-dlp`).
3. **whisper.cpp (prebuilt, no compiler):**
   ```bash
   WDIR="$HOME/tools/whisper"; mkdir -p "$WDIR/models"; cd "$WDIR"
   # CPU build with BLAS: pick the tag from github.com/ggml-org/whisper.cpp/releases
   curl -sL -o w.zip "https://github.com/ggml-org/whisper.cpp/releases/download/v1.9.1/whisper-blas-bin-x64.zip"
   unzip -o w.zip -d bin && rm w.zip
   # binary lands at bin/Release/whisper-cli.exe with its DLLs alongside
   ```
   (A machine with an NVIDIA GPU can use `whisper-cublas-12.4.0-bin-x64.zip` instead for speed.)
4. **Model:**
   ```bash
   curl -sL -o "$WDIR/models/ggml-base.en.bin" \
     "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
   ```
5. **Verify:**
   ```bash
   curl -sL -o /tmp/jfk.wav https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/samples/jfk.wav
   "$WDIR/bin/Release/whisper-cli.exe" -m "$WDIR/models/ggml-base.en.bin" -f /tmp/jfk.wav -nt
   # expect: "...ask not what your country can do for you..."
   ```

## Model options (speed ↔ accuracy ↔ language)

Download any of these into `models/` and set `WHISPER_MODEL` to switch:

| Model | Size | Notes |
|---|---|---|
| `ggml-base.en.bin` | ~148 MB | **default**, English-only, fast |
| `ggml-small.en.bin` | ~488 MB | English-only, more accurate |
| `ggml-base.bin` | ~148 MB | multilingual (needed for non-English) |
| `ggml-small.bin` | ~488 MB | multilingual, more accurate |

URL pattern: `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/<model-file>`

> **Model-size TODO (from PRD §10):** base vs small is unconfirmed pending accuracy/speed testing on
> real videos. Default is `base.en`; bump to `small`/`small.en` if base under-performs on your clips.
