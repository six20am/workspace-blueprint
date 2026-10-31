# paperwork

Reads a scan, photo or PDF of a letter, bill or form, names it by date, sender and type, files a copy,
and pulls out the dates that matter.

```
python tools/paperwork/paperwork.py scan.pdf --dry-run                  # show the plan, change nothing (python3 on Mac and Linux)
python tools/paperwork/paperwork.py photo.jpg                           # file it under paperwork/<year>/
python tools/paperwork/paperwork.py scan.pdf --sender "Northwind Power" --title "Bill"
```

The copy lands at `paperwork/<year>/YYYY-MM-DD - Sender - Title.pdf` (or under `--into <folder>`);
the original is never moved or changed. Dates that matter are added to `paperwork/dates.md` as
`YYYY-MM-DD | what | from <file>`, the lines `weekly-brief` reads.

Three programs do the reading, all found on PATH first, then in their usual install folders:

- **OCRmyPDF** adds a text layer to a scan or turns a photo into a PDF. It is MPL-2.0 and is called
  as a separate program, never shipped in this workspace.
- **Tesseract** is the engine OCRmyPDF uses to recognize the text.
- **Poppler's pdftotext** reads the text out of the PDF.

OCR runs only when the PDF has no text; a HEIC photo also needs ImageMagick. Standard library only.
Exit 0 on success, 1 when a step fails, 3 with `Missing: ocrmypdf. Run: python tools/doctor/doctor.py`.
