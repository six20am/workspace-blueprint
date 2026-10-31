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

## Editing video

Each recipe below changes the picture or the sound, so each one re-encodes (except the matched join). Ask the person for the choices in each recipe before you run it; do not pick them yourself.

### Join clips in order

Puts several clips end to end, in the order the person named. First check whether they match. Run this once per clip and compare the lines:

```sh
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -of csv=p=0 <a>.mp4
```

Same codecs, size, frame rate and audio on every clip (clips from the same camera or phone usually are): write a list file in the order asked, then join without re-encoding:

```sh
printf "file '%s'\n" <a>.mp4 <b>.mp4 <c>.mp4 > <name>-list.txt
ffmpeg -f concat -safe 0 -i <name>-list.txt -c copy <name>-joined.mp4
```

Anything differs: use the concat filter, which fits every clip into one frame size and frame rate and re-encodes:

```sh
ffmpeg -i <a>.mp4 -i <b>.mp4 -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac <name>-joined.mp4
```

The one thing to know: `-c copy` on clips that do not match gives a file that freezes, skips or loses sound partway, so compare the `ffprobe` lines first. Set the frame size and `fps` to the main clip's, or to what the person names (1280:720 and 30 above are examples). For three clips, add a third input and a `[2:v]...[v2]` chain, and set `n=3`. Every clip needs an audio track for `a=1`; for silent clips, drop the audio with `a=0` and `[v0][v1]`. Delete the list file afterwards; this recipe made it.

### Speed up or slow down

Changes the speed and keeps the sound in step. Twice as fast, then half speed:

```sh
ffmpeg -i <name>.mp4 -vf "setpts=PTS/2" -af "atempo=2.0" <name>-2x.mp4
ffmpeg -i <name>.mp4 -vf "setpts=PTS/0.5" -af "atempo=0.5" <name>-half.mp4
```

Outside 0.5 to 2.0, chain two `atempo` filters whose product is the speed:

```sh
ffmpeg -i <name>.mp4 -vf "setpts=PTS/4" -af "atempo=2.0,atempo=2.0" <name>-4x.mp4
ffmpeg -i <name>.mp4 -vf "setpts=PTS/0.25" -af "atempo=0.5,atempo=0.5" <name>-quarter.mp4
```

The one thing to know: the number in `setpts=PTS/<speed>` and the product of the `atempo` values must be the same speed, or the sound drifts away from the picture. `atempo` keeps voices at their normal pitch.

### Burn captions into the picture

Draws the captions from an `.srt` file onto every frame, so they show on any player and any platform:

```sh
ffmpeg -i <name>.mp4 -vf "subtitles=<name>.srt" -c:a copy <name>-captions.mp4
```

This is different from adding captions as a track the viewer can turn off. For that, mux them without re-encoding: `python tools/media-tools/container.py mux <name>.mp4 --subs <name>.srt`.

The one thing to know: the file name inside `subtitles=` is read by the filter, not by the shell, and a Windows path breaks it (`C:\clips\x.srt` fails on the colon and the backslashes). Run ffmpeg from the folder that holds the `.srt` and give the bare file name, as above. If you must give a full path, use forward slashes, escape the drive colon and wrap it in single quotes: `subtitles='C\:/clips/<name>.srt'`. Burned captions cannot be removed later, so keep the original.

### Overlay a logo or watermark

Puts an image (a PNG with a transparent background works best) in a corner, 20 pixels in from the edges. Bottom right:

```sh
ffmpeg -i <name>.mp4 -i <logo>.png -filter_complex "overlay=W-w-20:H-h-20" -c:a copy <name>-logo.mp4
```

Other corners: top left `overlay=20:20`, top right `overlay=W-w-20:20`, bottom left `overlay=20:H-h-20`. `W` and `H` are the video's size, `w` and `h` the logo's; change 20 for a wider or narrower margin.

Picture in picture: shrink the second video and place it in a corner of the first, keeping the first video's sound:

```sh
ffmpeg -i <name>.mp4 -i <second>.mp4 -filter_complex "[1:v]scale=480:-2[pip];[0:v][pip]overlay=W-w-20:H-h-20:shortest=1" -map 0:a -c:a copy <name>-pip.mp4
```

The one thing to know: the logo goes on at its own pixel size. If it is too big, shrink it in the same command: `"[1:v]scale=200:-1[logo];[0:v][logo]overlay=W-w-20:H-h-20"`. For picture in picture, about a quarter of the main video's width (480 on a 1920-wide video) reads well; `shortest=1` ends the result when the shorter clip ends.

### Reframe for social (9:16 or 1:1)

Turns a wide video into a vertical (9:16) or square (1:1) one. Two ways; the person picks.

Centered crop: cuts the sides away and keeps the middle.

```sh
ffmpeg -i <name>.mp4 -vf "crop=trunc(ih*9/16/2)*2:ih,setsar=1" -c:a copy <name>-9x16.mp4
ffmpeg -i <name>.mp4 -vf "crop=min(iw\,ih):min(iw\,ih),setsar=1" -c:a copy <name>-1x1.mp4
```

Blurred-background pad: keeps the whole picture, centered, over a blurred and enlarged copy of itself.

```sh
ffmpeg -i <name>.mp4 -filter_complex "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[blur];[fg]scale=1080:1920:force_original_aspect_ratio=decrease[sharp];[blur][sharp]overlay=(W-w)/2:(H-h)/2,setsar=1" -c:a copy <name>-9x16-pad.mp4
```

For square, change every `1080:1920` to `1080:1080` and name the file `<name>-1x1-pad.mp4`.

The one thing to know: the crop looks right when the subject stays in the middle (one person talking to the camera); it cuts off anything at the sides, so check the result. The pad looks right when the whole frame matters (a group, a screen, text near the edges), at the cost of a smaller picture. The crop keeps the source's pixels, so a small source gives a small result; add `,scale=1080:1920` after the crop if the person wants full size.

### Fade in and out

Fades the picture from and to black and the sound from and to silence. Read the length first, so the out-fade starts at the right second:

```sh
ffprobe -v error -show_entries format=duration -of csv=p=0 <name>.mp4
```

For a 30-second clip with one-second fades, the out-fade starts at 29 (length minus fade length):

```sh
ffmpeg -i <name>.mp4 -vf "fade=t=in:st=0:d=1,fade=t=out:st=29:d=1" -af "afade=t=in:st=0:d=1,afade=t=out:st=29:d=1" <name>-fade.mp4
```

The one thing to know: `st` is the start second and `d` the length. A wrong `st` for the out-fade gives a black tail or no fade at all, so compute it from the `ffprobe` number, never guess. For a fade out only, drop the two `t=in` parts. After a join, read the length of the joined file, not of one clip.

### Still image plus audio into a video

Makes a video from one picture and a sound file, for a podcast clip or a song on a platform that only takes video:

```sh
ffmpeg -loop 1 -i <image>.png -i <audio>.mp3 -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac -b:a 192k -shortest <name>-video.mp4
```

The one thing to know: `-shortest` ends the video when the audio ends; without it the looped picture runs forever. The `scale` step rounds the size down to even numbers, which H.264 needs, and `-pix_fmt yuv420p` keeps it playable on phones and in browsers.

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
