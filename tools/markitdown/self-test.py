#!/usr/bin/env python3
"""Prove convert.py reads a DOCX, an XLSX, an HTML and a CSV built from scratch, writes the
provenance header, refuses to overwrite without --force, and fails on a missing file."""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONVERT = HERE / "convert.py"
MARK = "Quartzfern seventeen"  # a string that cannot appear by accident

CT = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{}</Types>'
RELS = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{}</Relationships>'


def docx(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", CT.format(
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'))
        z.writestr("_rels/.rels", RELS.format(
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'))
        z.writestr("word/document.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            f'<w:p><w:r><w:t>{MARK} in a paragraph.</w:t></w:r></w:p>'
            '</w:body></w:document>')


def xlsx(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", CT.format(
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'))
        z.writestr("_rels/.rels", RELS.format(
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'))
        z.writestr("xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Leads" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", RELS.format(
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'))
        z.writestr("xl/worksheets/sheet1.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            '<row r="1"><c r="A1" t="inlineStr"><is><t>name</t></is></c><c r="B1" t="inlineStr"><is><t>count</t></is></c></row>'
            f'<row r="2"><c r="A2" t="inlineStr"><is><t>{MARK}</t></is></c><c r="B2"><v>3</v></c></row>'
            '</sheetData></worksheet>')


def run(*args):
    return subprocess.run([sys.executable, str(CONVERT), *map(str, args)], capture_output=True, text=True)


def main():
    checks = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        docx(td / "brief.docx")
        xlsx(td / "leads.xlsx")
        (td / "page.html").write_text(f"<html><body><h1>{MARK}</h1><p>body</p></body></html>", encoding="utf-8")
        (td / "export.csv").write_text(f"name,count\n{MARK},3\n", encoding="utf-8")
        out = td / "out"

        r = run(td, "--out", out)
        checks.append(("four files convert, exit 0", r.returncode == 0, r.stderr.strip()))
        for stem in ("brief", "leads", "page", "export"):
            f = out / f"{stem}.md"
            text = f.read_text(encoding="utf-8") if f.exists() else ""
            checks.append((f"{stem}.md carries the marker", MARK in text, f"exists={f.exists()}"))
            checks.append((f"{stem}.md carries the provenance header",
                           text.startswith("---\nsource:") and "sha256:" in text and "trust: untrusted" in text, ""))

        r = run(td / "page.html", "--out", out)
        checks.append(("second run refuses to overwrite without --force",
                       r.returncode == 0 and "exists; pass --force" in r.stderr, r.stderr.strip()))
        r = run(td / "page.html", "--out", out, "--force")
        checks.append(("--force overwrites", r.returncode == 0 and "wrote" in r.stdout, r.stderr.strip()))

        r = run(td / "missing.docx", "--out", out)
        checks.append(("missing input exits 1", r.returncode == 1, r.stderr.strip()))

        r = run(td / "page.html", "--stdout", "--no-header")
        checks.append(("--stdout --no-header prints bare markdown",
                       r.returncode == 0 and r.stdout.startswith("# ") and MARK in r.stdout, ""))

    ok = all(c[1] for c in checks)
    for name, passed, note in checks:
        print(f"  {'ok  ' if passed else 'FAIL'} {name}" + (f"  [{note}]" if note and not passed else ""))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        import markitdown  # noqa: F401
    except ImportError:
        print('markitdown is not installed. Run: pip install "markitdown[all]"')
        sys.exit(2)
    sys.exit(main())
