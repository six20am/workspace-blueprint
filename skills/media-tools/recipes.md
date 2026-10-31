# media-tools recipes

Known-good ffmpeg and ImageMagick commands. Adapt one of these instead of writing a command from memory: ffmpeg cares about the order of its flags, and small slips give black frames or wrong lengths.

In every recipe, `<name>.mp4` (or `.jpg`, `.wav`) is the person's file and `<name>` is that file name without its extension. Every output is a new file beside the input. None of these commands use `-y`, so ffmpeg asks before it would replace a file; answer no and pick another name.

## Before you edit: look at the file

```sh
ffprobe -hide_banner -show_streams -show_format <name>.mp4
magick identify <name>.jpg
```

This tells you the length, size, codecs and whether there is audio. Most surprises (no audio track, a portrait phone video, a huge frame size) show up here.

## Video with ffmpeg

### Convert format

Change only the container (fast, no quality loss), when the codecs fit the new container:

```sh
ffmpeg -i <name>.mp4 -c copy <name>.mkv
ffmpeg -i <name>.mov -c copy <name>.mp4
```

Re-encode to an MP4 that plays almost anywhere:

```sh
ffmpeg -i <name>.mov -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k <name>-web.mp4
```

- `-c copy` copies the streams as they are. Never use it together with a filter (`-vf`, `-af`), a trim you want exact, or compression.
- `-crf` is the quality dial: lower is better and bigger. 18 looks like the source, 23 is the default, 28 is small. Each +6 roughly halves the size.
- `-pix_fmt yuv420p` keeps the file playable in browsers and on phones.
- `-movflags +faststart` lets a web video start playing before it has fully downloaded.

### Trim

Exact cut from 0:10 to 0:25 (re-encodes the kept part):

```sh
ffmpeg -i <name>.mp4 -ss 00:00:10 -to 00:00:25 <name>-trim.mp4
```

Fast cut that lands on the nearest keyframe (no re-encode, may be off by a second or two):

```sh
ffmpeg -ss 00:00:10 -i <name>.mp4 -t 15 -c copy <name>-trim.mp4
```

`-ss` after `-i` is exact; `-ss` before `-i` is fast but only lands on keyframes. Do not mix exact cutting with `-c copy`, or the start can be black.

### Resize

Fit inside 1280 wide, height chosen to keep the shape (and kept even, which H.264 needs):

```sh
ffmpeg -i <name>.mp4 -vf "scale=1280:-2" -c:a copy <name>-1280.mp4
```

Fit inside a fixed box and fill the rest with black bars, for example a 1080x1920 vertical frame:

```sh
ffmpeg -i <name>.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" -c:a copy <name>-vertical.mp4
```

`setsar=1` stops the result from looking stretched. Ask the person for the size; do not pick one for them unless they name a platform.

### Make a GIF

Two passes give far better colors than one. First ten seconds, 480 wide, 12 frames a second:

```sh
ffmpeg -t 10 -i <name>.mp4 -vf "fps=12,scale=480:-1:flags=lanczos,palettegen" <name>-palette.png
ffmpeg -t 10 -i <name>.mp4 -i <name>-palette.png -lavfi "fps=12,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" -loop 0 <name>.gif
```

- Change `-t 10` for a different length; add `-ss 00:00:05` before `-i` to start later.
- 480 wide suits chat and email; 320 for a small file, 640 at most. GIFs get large fast.
- `-loop 0` loops forever. Delete the palette PNG afterwards; it was made by this recipe, not the person's file.

### Pull the audio out

```sh
ffmpeg -i <name>.mp4 -vn -c:a libmp3lame -q:a 2 <name>.mp3
ffmpeg -i <name>.mp4 -vn -map 0:a:0 -c:a copy <name>.m4a
ffmpeg -i <name>.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le <name>-speech.wav
```

The first gives a good MP3, the second copies AAC audio untouched, the third gives the 16 kHz mono file speech-to-text tools want. Drop audio from a video with `-an -c:v copy <name>-silent.mp4`.

### Compress

```sh
ffmpeg -i <name>.mp4 -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 96k <name>-small.mp4
```

Raise `-crf` for smaller, lower it for better. To hit an exact file size, CRF cannot do it; use a two-pass bitrate encode or `transcode.py` with a smaller preset.

### Strip metadata

```sh
ffmpeg -i <name>.mp4 -map 0 -map_metadata -1 -c copy <name>-clean.mp4
```

For photos, and for a thorough clean of any file, use `python tools/media-tools/exif.py strip <file>`.

## Images with ImageMagick

Always `magick <input> ... <output>` with a new output name. Never use `mogrify`: it writes over the original.

### Resize

```sh
magick <name>.jpg -resize 1200x <name>-1200.jpg
magick <name>.jpg -resize 800x800 <name>-fit.jpg
magick <name>.jpg -resize 1200x630^ -gravity center -extent 1200x630 <name>-1200x630.jpg
```

The first sets the width, the second fits inside a box, the third fills the box exactly and crops the overflow from the center. Add `>` (as in `1200x>`) to never enlarge a small image.

### Convert format

```sh
magick <name>.heic <name>.jpg
magick <name>.png -quality 82 <name>.webp
magick <name>.jpg -auto-orient <name>.png
```

`-auto-orient` bakes a phone's rotation flag into the pixels, so the picture stays upright after metadata is removed.

### Crop

```sh
magick <name>.jpg -crop 800x600+100+50 +repage <name>-crop.jpg
magick <name>.jpg -gravity center -crop 1:1 +repage <name>-square.jpg
```

`800x600+100+50` is width x height, then left and top offsets. `+repage` clears the old canvas size so later steps behave.

### Compress

```sh
magick <name>.jpg -strip -quality 80 -sampling-factor 4:2:0 <name>-small.jpg
magick <name>.png -strip -define png:compression-level=9 <name>-small.png
```

`-strip` also removes metadata, including GPS. Check the result by eye before saying it is done.

### Montage (a sheet of images)

```sh
magick montage <a>.jpg <b>.jpg <c>.jpg -tile 3x -geometry 400x400+10+10 -background white <name>-sheet.jpg
magick <a>.jpg <b>.jpg +append <name>-side-by-side.jpg
```

`montage` makes a grid with labels and gaps; `+append` sets images side by side (`-append` stacks them).

## Batch a folder

Write every result into a new folder, never back into the source folder.

PowerShell (Windows):

```powershell
New-Item -ItemType Directory -Force out | Out-Null
Get-ChildItem *.mov | ForEach-Object { ffmpeg -i $_.FullName -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac "out\$($_.BaseName).mp4" }
Get-ChildItem *.jpg | ForEach-Object { magick $_.FullName -resize 1600x "out\$($_.Name)" }
```

Bash (Mac, Linux, Git Bash):

```sh
mkdir -p out
for f in *.mov; do ffmpeg -i "$f" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac "out/${f%.*}.mp4"; done
for f in *.jpg; do magick "$f" -resize 1600x "out/$f"; done
```

Run the command on one file first, show the person the result, then run the folder.
