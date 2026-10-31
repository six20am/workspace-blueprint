# Ghostscript

Reads, renders and rewrites PDF and PostScript files. OCRmyPDF uses it to build the final PDF.

```
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o smaller.pdf big.pdf
gs -sDEVICE=png16m -r150 -o page-%03d.png in.pdf
```

**Gotcha:** On Windows the command is `gswin64c`, not `gs`, and winget does not carry it: install the 64-bit build from ghostscript.com/releases.
