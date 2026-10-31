# OCRmyPDF

Adds a hidden text layer to a scanned PDF so it can be searched and copied. The pages look the same.

```
ocrmypdf scan.pdf searchable.pdf
ocrmypdf --skip-text mixed.pdf out.pdf
```

**Gotcha:** It needs Tesseract on the PATH, and on Windows also Ghostscript. A PDF that already has text stops with an error unless you add `--skip-text` or `--force-ocr`.
