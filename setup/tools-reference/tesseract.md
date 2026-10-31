# Tesseract

Reads printed text in images and turns it into plain text (OCR).

```
tesseract scan.png out
tesseract scan.png out -l eng pdf
```

**Gotcha:** On Windows the installer may not put `tesseract` on the PATH. If the command is not found, use the full path in `C:\Program Files\Tesseract-OCR`. Only English is installed by default.
