# Poppler

A set of small PDF tools: pull out the text, turn pages into images, read page counts and other details.

```
pdftotext -layout file.pdf file.txt
pdftoppm -png -r 150 file.pdf page
```

**Gotcha:** A scanned PDF has no text inside it, so `pdftotext` returns nothing. Run OCRmyPDF on it first.
