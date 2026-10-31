# SoX

Edits audio from the command line: trim, join, change volume, convert formats, remove silence.

```
sox input.wav output.mp3
sox input.wav trimmed.wav trim 0 30
```

**Gotcha:** On Windows the installer may not put `sox` on the PATH. If the command is not found, use the full path in `C:\Program Files (x86)\sox-14-4-2`. MP3 output needs an MP3 library; WAV and FLAC always work.
