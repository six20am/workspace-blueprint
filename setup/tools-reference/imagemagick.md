# ImageMagick

Resizes, crops, converts and combines images from the command line. It handles almost every image format.

```
magick photo.png -resize 1200x photo-small.jpg
magick mogrify -format webp *.png
```

**Gotcha:** On Windows and Mac the command is `magick`. Older Linux versions only have `convert`, which takes the same options.
