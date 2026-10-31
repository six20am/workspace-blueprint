# document-builder

Turns a Markdown file into a Word, PDF, PowerPoint, HTML or OpenDocument file, or its first table into CSV.

```
python tools/document-builder/build_doc.py notes.md --to docx            # notes.docx beside it (python3 on Mac and Linux)
python tools/document-builder/build_doc.py notes.md --to pdf --out report.pdf
python tools/document-builder/build_doc.py notes.md --csv                # the first table as notes.csv
```

| `--to` | Needs |
|---|---|
| `docx`, `pptx`, `html`, `odt` | pandoc |
| `pdf` | pandoc, then LibreOffice headless (Markdown to Word to PDF; no LaTeX) |

`--csv` needs neither program. `--reference <file.docx>` borrows that file's styles; without it a
Word build uses `setup/reference.docx` when that file exists. The output lands beside the source
unless `--out` says otherwise, and its path is printed.

Exit 0 on success, 1 when a conversion fails or there is no table, 3 when a program is missing,
with `Missing: pandoc. Run: python tools/doctor/doctor.py` (or `soffice`). Both programs are found
on PATH first, then in their usual install folders on Windows, Mac and Linux. Standard library only.
