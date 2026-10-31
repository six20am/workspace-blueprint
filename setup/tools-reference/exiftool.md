# ExifTool

Reads and writes the hidden details inside photos and videos: camera, date, GPS location, copyright.

```
exiftool photo.jpg
exiftool -all= -overwrite_original photo.jpg
```

**Gotcha:** Without `-overwrite_original` it keeps a copy named `photo.jpg_original` next to every file it changes.
