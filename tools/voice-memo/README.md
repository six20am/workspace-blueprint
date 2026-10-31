# voice-memo

Turns a voice recording into `voice-memos/YYYY-MM-DD-<name>.md`: the transcript, then empty `## Notes` and `## To do` headings the `voice-memo` skill fills in by reading it. Runs ffmpeg and whisper.cpp on this machine, the same ones setup installs for `video-watcher`. Nothing is uploaded.

```
python tools/voice-memo/memo.py inbox/truck-memo.m4a            # python3 on Mac and Linux
python tools/voice-memo/memo.py memo.mp3 --into notes/memos --date 2026-11-02
```

Looks for `whisper-cli` on PATH or at `$WHISPER_HOME/bin/Release/whisper-cli.exe` (`WHISPER_HOME` defaults to `~/tools/whisper`) and the model at `$WHISPER_MODEL` (default `ggml-base.en.bin` in `$WHISPER_HOME/models`). Set `WHISPER_LANG` for a non-English memo with a multilingual model. Exit 3 names a missing program and points at `doctor`. The file date is the recording's date unless `--date` says otherwise; an existing memo of the same name gets ` (2)`. The recording is read, never moved or changed. Standard library only.
