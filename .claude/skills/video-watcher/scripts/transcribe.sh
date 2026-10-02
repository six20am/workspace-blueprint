#!/usr/bin/env bash
# transcribe.sh <audio_or_video> <outdir>
# ffmpeg -> 16kHz mono wav -> whisper.cpp -> $outdir/transcript.srt + transcript.txt
# Prints the .srt path on stdout.
set -euo pipefail

IN="${1:?usage: transcribe.sh <audio_or_video> <outdir>}"
OUTDIR="${2:?missing outdir}"
mkdir -p "$OUTDIR"

WHISPER_HOME="${WHISPER_HOME:-$HOME/tools/whisper}"
CLI="$WHISPER_HOME/bin/Release/whisper-cli.exe"
MODEL="${WHISPER_MODEL:-$WHISPER_HOME/models/ggml-base.en.bin}"

[[ -x "$CLI" ]]   || { echo "ERROR: whisper-cli not found at $CLI (see SETUP.md)" >&2; exit 1; }
[[ -f "$MODEL" ]] || { echo "ERROR: model not found at $MODEL (see SETUP.md)" >&2; exit 1; }

WAV="$OUTDIR/audio_16k.wav"
ffmpeg -hide_banner -loglevel error -y -i "$IN" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"

# -osrt: timestamped subtitle file; -otxt: plain text; -of: output prefix (no extension)
# WHISPER_LANG optional (e.g. es, fr). Ignored/English for *.en models.
"$CLI" -np -m "$MODEL" -f "$WAV" -osrt -otxt -of "$OUTDIR/transcript" \
       ${WHISPER_LANG:+-l "$WHISPER_LANG"} >&2

echo "$OUTDIR/transcript.srt"
