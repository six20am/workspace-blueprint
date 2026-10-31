# media-tools

Four small wrappers the `media-tools` skill calls. Each builds the command, finds the program on PATH or in its usual install folder (and the WinGet Links folder), and writes a new file beside the input. None of them edits an original or overwrites an existing file.

```
python tools/media-tools/exif.py show|strip <file>   # python3 on Mac and Linux
python tools/media-tools/audio.py trim|convert|normalize <file> [--start S --end S] [--to wav|mp3|flac]
python tools/media-tools/transcode.py <in> [--preset "Fast 1080p30"] [--out <file>]
python tools/media-tools/container.py info|mux <file> [--audio <file>] [--subs <file>]
```

Programs, in order: ExifTool, SoX, HandBrakeCLI, MKVToolNix (`mkvmerge`).

New files: `<name>-clean.<ext>`, `<name>-trim.<ext>`, `<name>-normalized.<ext>`, `<name>.<to>`, `<name>-handbrake.mp4`, `<name>.mkv`.

Exit codes: 0 done, 1 refused (the output is an input or already exists), 2 bad arguments, 3 program missing. A missing program prints `Missing: <program>. Run: python tools/doctor/doctor.py`.

Each script exposes `command(...)`, which returns the argument list without running anything; `tests/test_media_tools.py` tests those. Standard library only.
