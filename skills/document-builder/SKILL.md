---
name: document-builder
description: "Turns notes or Markdown into a Word, PDF, PowerPoint, HTML or OpenDocument file, or a table into a spreadsheet-ready CSV. Use when the person wants a document file made."
---

# document-builder

Use this when the person wants a Word, PDF, PowerPoint, HTML or OpenDocument file from notes or Markdown, or a CSV they can open in a spreadsheet from a table.

## How

1. Write the content as Markdown first: `#` headings, lists, and pipe tables. Save it as a `.md` file where the person keeps the work.
2. Run one command from the workspace folder:

```
python tools/document-builder/build_doc.py notes.md --to docx   # python3 on Mac and Linux
```

Swap `docx` for the format they asked for. For a CSV: `python tools/document-builder/build_doc.py notes.md --csv` (the first table in the file).

## Formats

| Ask | `--to` | Needs |
|---|---|---|
| Word | `docx` | pandoc |
| PDF | `pdf` | pandoc and LibreOffice |
| PowerPoint | `pptx` | pandoc |
| Web page | `html` | pandoc |
| OpenDocument | `odt` | pandoc |
| Spreadsheet | `--csv` | nothing extra |

PDF goes through Word and LibreOffice, never LaTeX.

## Slide decks

One `#` heading per slide, bullets under it. Keep each slide to a few short bullets.

## Where it lands

Beside the source, same name, new extension, unless `--out <path>` says otherwise. The command prints the path.

## House template

If `setup/reference.docx` exists, Word files take its fonts and styles. `--reference <file.docx>` uses a different one for this build.

## When a program is missing

The command prints `Missing: pandoc` (or `soffice`) and exits 3. Say which program is missing and offer to run `doctor`, which installs it. Do not install it by hand.

## What to say

One line: what was made and where it is.

## Never

- Email, upload or share the file. Hand the path to the person; sending is theirs.
- Overwrite a file the person did not name without asking.
