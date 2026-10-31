# MKVToolNix

Joins, splits and inspects MKV video files, and adds or removes audio and subtitle tracks without re-encoding.

```
mkvmerge -i movie.mkv
mkvmerge -o out.mkv movie.mkv subtitles.srt
```

**Gotcha:** On Windows the installer may not put `mkvmerge` on the PATH. If the command is not found, use the full path in `C:\Program Files\MKVToolNix`.
