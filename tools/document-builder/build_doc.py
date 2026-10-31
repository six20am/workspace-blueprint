#!/usr/bin/env python3
"""Turns a Markdown file into a Word, PDF, PowerPoint, HTML or OpenDocument file, or a table into CSV.

    python tools/document-builder/build_doc.py notes.md --to docx|pdf|pptx|html|odt [--out PATH] [--reference REF.docx]
    python tools/document-builder/build_doc.py notes.md --csv [--out PATH.csv]

Word, PowerPoint, HTML and OpenDocument come from pandoc. PDF goes Markdown to Word with pandoc,
then Word to PDF with LibreOffice headless, so no LaTeX is ever needed. --csv needs neither program:
the first pipe table in the file becomes CSV. The output lands beside the source unless --out says
otherwise. Exit 0 and print the output path on success, 1 on a failed conversion or no table, 3 when
a program is missing. Standard library only.
"""
import argparse
import csv
import io
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMATS = ("docx", "pdf", "pptx", "html", "odt")
DOCTOR = "python tools/doctor/doctor.py (python3 on Mac and Linux)"
TIMEOUT = 300


def _program_files():
    return os.environ.get("ProgramFiles") or r"C:\Program Files"


def _first_file(paths):
    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None


def find_pandoc():
    """The pandoc program: PATH first, then the folders its installers use."""
    found = shutil.which("pandoc")
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    return _first_file([
        os.path.join(_program_files(), "Pandoc", "pandoc.exe"),
        os.path.join(local, "Pandoc", "pandoc.exe") if local else None,
        "/opt/homebrew/bin/pandoc",
        "/usr/local/bin/pandoc",
        "/usr/bin/pandoc",
    ])


def find_soffice():
    """The LibreOffice program: PATH first, then its usual folders on Windows, Mac and Linux."""
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    return _first_file([
        os.path.join(_program_files(), "LibreOffice", "program", "soffice.exe"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ])


def default_reference():
    """setup/reference.docx at the workspace root, the optional house template, when it exists."""
    path = os.path.join(ROOT, "setup", "reference.docx")
    return path if os.path.isfile(path) else None


def pandoc_command(src, out, fmt, reference=None, pandoc="pandoc"):
    """pandoc argv for one conversion. HTML is standalone; PowerPoint names its writer."""
    cmd = [pandoc, src, "-o", out]
    if fmt == "pptx":
        cmd += ["-t", "pptx"]
    elif fmt == "html":
        cmd += ["-s"]
    if reference is None and fmt == "docx":
        reference = default_reference()
    if reference:
        cmd += ["--reference-doc", reference]
    return cmd


def soffice_command(soffice, src, out_dir):
    """LibreOffice headless argv that writes <src name>.pdf into out_dir."""
    return [soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, src]


def default_out(src, ext):
    """The source path with the new extension, beside the source."""
    return os.path.splitext(src)[0] + "." + ext


def _is_row(line):
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 2


def _is_separator(line):
    cells = _cells(line)
    return bool(cells) and all(c and set(c) <= set("-: ") and "-" in c for c in cells)


def _cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def markdown_table_to_csv(text):
    """The first pipe table in the Markdown as CSV: header kept, the |---| line dropped, cells
    stripped. An empty string when there is no table."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if _is_row(lines[i]) and _is_separator(lines[i + 1]):
            rows = [_cells(lines[i])]
            for line in lines[i + 2:]:
                if not _is_row(line):
                    break
                rows.append(_cells(line))
            buf = io.StringIO()
            csv.writer(buf, lineterminator="\n").writerows(rows)
            return buf.getvalue()
    return ""


def _run(cmd):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return done.returncode == 0, (done.stderr or done.stdout or "").strip()


def _missing(name):
    print("Missing: %s. Run: %s" % (name, DOCTOR))
    return 3


def build_csv(src, out):
    with open(src, encoding="utf-8") as fh:
        text = markdown_table_to_csv(fh.read())
    if not text:
        print("no table found in %s" % src)
        return 1
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(out)
    return 0


def build(src, out, fmt, reference=None):
    pandoc = find_pandoc()
    if not pandoc:
        return _missing("pandoc")
    if fmt != "pdf":
        ok, err = _run(pandoc_command(src, out, fmt, reference, pandoc=pandoc))
        if not ok or not os.path.isfile(out):
            print("pandoc could not build %s: %s" % (out, err))
            return 1
        print(out)
        return 0
    soffice = find_soffice()
    if not soffice:
        return _missing("soffice")
    with tempfile.TemporaryDirectory() as tmp:
        docx = os.path.join(tmp, os.path.splitext(os.path.basename(out))[0] + ".docx")
        ok, err = _run(pandoc_command(src, docx, "docx", reference, pandoc=pandoc))
        if not ok or not os.path.isfile(docx):
            print("pandoc could not build the Word step: %s" % err)
            return 1
        ok, err = _run(soffice_command(soffice, docx, tmp))
        pdf = os.path.splitext(docx)[0] + ".pdf"
        if not ok or not os.path.isfile(pdf):
            print("LibreOffice could not make the PDF (close any open LibreOffice window and retry): %s" % err)
            return 1
        shutil.move(pdf, out)
    print(out)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Markdown to Word, PDF, PowerPoint, HTML, OpenDocument or CSV.")
    p.add_argument("src", help="the Markdown file")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--to", choices=FORMATS, help="the file type to make")
    mode.add_argument("--csv", action="store_true", help="the first table in the file as CSV")
    p.add_argument("--out", help="where to write it (default: beside the source)")
    p.add_argument("--reference", help="a .docx whose styles the output uses")
    args = p.parse_args(argv)
    if not os.path.isfile(args.src):
        print("not found: %s" % args.src)
        return 1
    if args.csv:
        return build_csv(args.src, os.path.abspath(args.out or default_out(args.src, "csv")))
    out = os.path.abspath(args.out or default_out(args.src, args.to))
    return build(os.path.abspath(args.src), out, args.to, args.reference)


if __name__ == "__main__":
    sys.exit(main())
