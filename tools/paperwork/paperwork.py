#!/usr/bin/env python3
"""Reads a scan, photo or PDF of a letter, bill or form, names it by date and sender, files it,
and pulls out the dates that matter.

    python tools/paperwork/paperwork.py <file> [--dry-run] [--sender "<name>"] [--title "<title>"] [--into <folder>]

A photo (.jpg .jpeg .png .tif .tiff .heic) becomes a searchable PDF through OCRmyPDF. A PDF with
no text layer gets one the same way (ocrmypdf --skip-text). Poppler's pdftotext then reads the
text. The first date in the letter is its date; dates later than that, on a line that says due,
pay, renew, respond and the like, are the dates that matter. The file is copied (never moved) to
paperwork/<year>/YYYY-MM-DD - Sender - Title.pdf and the dates are added to paperwork/dates.md.
--dry-run prints the plan and changes nothing. Exit 0 on success, 1 when a step fails, 3 when a
program is missing. Standard library only.
"""
import argparse
import datetime
import glob
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCTOR = "python tools/doctor/doctor.py"
TIMEOUT = 600
IMAGES = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic")
DATES_HEADER = "# Dates that matter\n\nWritten by paperwork, one line each: `YYYY-MM-DD | what | from <file>`.\n\n"

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
MONTH_WORD = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
              r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
DATE_RE = re.compile(
    r"\b(?P<iy>\d{4})-(?P<im>\d{1,2})-(?P<id>\d{1,2})\b"
    r"|\b(?P<um>\d{1,2})/(?P<ud>\d{1,2})/(?P<uy>\d{4}|\d{2})\b"
    r"|\b(?P<mm>" + MONTH_WORD + r")\.?\s+(?P<md>\d{1,2}),?\s+(?P<my>\d{4})\b"
    r"|\b(?P<dd>\d{1,2})\s+(?P<dm>" + MONTH_WORD + r")\.?,?\s+(?P<dy>\d{4})\b",
    re.I)
MATTERS_RE = re.compile(r"\b(?:due|by\b|before|no later than|deadline|expire|respond|appointment|hearing|pay|renew)",
                        re.I)
TITLE_WORDS = ("invoice", "statement", "notice", "bill", "letter", "receipt", "explanation of benefits",
               "appointment", "renewal", "summons", "contract")
MINOR_WORDS = {"of", "and", "the", "for", "&", "to", "in", "on", "at", "de"}
ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


# ---------- finding programs ----------

def _program_files():
    return os.environ.get("ProgramFiles") or os.path.join("C:" + os.sep, "Program Files")


def _first_file(paths):
    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None


def find_pdftotext():
    """Poppler's pdftotext: PATH first, then the folders its installers use."""
    found = shutil.which("pdftotext")
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    winget = glob.glob(os.path.join(local, "Microsoft", "WinGet", "Packages", "*Poppler*", "*", "Library", "bin",
                                    "pdftotext.exe")) if local else []
    return _first_file(sorted(winget, reverse=True) + [
        os.path.join(_program_files(), "poppler", "Library", "bin", "pdftotext.exe"),
        "/opt/homebrew/bin/pdftotext", "/usr/local/bin/pdftotext", "/usr/bin/pdftotext",
    ])


def find_ocrmypdf():
    """OCRmyPDF: PATH first, then the Python Scripts folders pip installs it into."""
    found = shutil.which("ocrmypdf")
    if found:
        return found
    folders = [sysconfig.get_path("scripts")]
    try:
        folders.append(sysconfig.get_path("scripts", "%s_user" % os.name))
    except KeyError:
        pass
    names = ("ocrmypdf.exe", "ocrmypdf")
    return _first_file([os.path.join(f, n) for f in folders if f for n in names] + [
        "/opt/homebrew/bin/ocrmypdf", "/usr/local/bin/ocrmypdf", "/usr/bin/ocrmypdf",
    ])


def find_tesseract():
    """Tesseract, the engine OCRmyPDF calls: PATH first, then its usual folders."""
    found = shutil.which("tesseract")
    if found:
        return found
    return _first_file([
        os.path.join(_program_files(), "Tesseract-OCR", "tesseract.exe"),
        "/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract", "/usr/bin/tesseract",
    ])


def find_ghostscript():
    """Ghostscript, which OCRmyPDF uses for PDFs: PATH first, then its usual Windows folder."""
    for name in ("gswin64c", "gs"):
        found = shutil.which(name)
        if found:
            return found
    return _first_file(sorted(glob.glob(os.path.join(_program_files(), "gs", "*", "bin", "gswin64c.exe")),
                              reverse=True))


def find_magick():
    """ImageMagick, used only to turn a HEIC photo into a PNG first."""
    return shutil.which("magick")


def _ocr_env():
    """PATH with the Tesseract and Ghostscript folders added, so OCRmyPDF finds them even when the
    installer did not put them on PATH."""
    env = dict(os.environ)
    extra = [os.path.dirname(p) for p in (find_tesseract(), find_ghostscript()) if p]
    if extra:
        env["PATH"] = os.pathsep.join(extra + [env.get("PATH", "")])
    return env


def _run(cmd, env=None):
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=TIMEOUT, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, "", str(e)
    return done.returncode == 0, done.stdout or "", (done.stderr or "").strip()


def _missing(name):
    print("Missing: %s. Run: %s" % (name, DOCTOR))
    return 3


# ---------- reading ----------

def ocr(pdf, out, program="ocrmypdf"):
    """OCRmyPDF argv that adds a text layer to the pages that have none."""
    return [program, "--skip-text", pdf, out]


def image_command(img, out, program="ocrmypdf"):
    """OCRmyPDF argv that turns a photo or scan image into a searchable PDF."""
    return [program, "--image-dpi", "300", img, out]


def has_text(pdf, prog=None):
    """True when page one already carries at least 20 characters of text."""
    ok, out, _ = _run([prog or find_pdftotext() or "pdftotext", "-l", "1", pdf, "-"])
    return ok and len(re.sub(r"\s", "", out)) >= 20


def read_text(pdf, prog=None):
    """The whole text of the PDF, laid out the way the page is."""
    ok, out, _ = _run([prog or find_pdftotext() or "pdftotext", "-layout", pdf, "-"])
    return out if ok else ""


# ---------- dates ----------

def _iso(year, month, day):
    try:
        return datetime.date(year, month, day).isoformat()
    except ValueError:
        return None


def _match_iso(m):
    g = m.groupdict()
    if g["iy"]:
        return _iso(int(g["iy"]), int(g["im"]), int(g["id"]))
    if g["uy"]:
        year = int(g["uy"])
        if len(g["uy"]) == 2:
            year += 2000
        return _iso(year, int(g["um"]), int(g["ud"]))
    if g["my"]:
        return _iso(int(g["my"]), MONTHS[g["mm"][:3].lower()], int(g["md"]))
    return _iso(int(g["dy"]), MONTHS[g["dm"][:3].lower()], int(g["dd"]))


def _clean_line(line):
    return re.sub(r"\s+", " ", line).strip()


def find_dates(text):
    """Every date in the text as (YYYY-MM-DD, the line it sits on), in the order they appear."""
    found = []
    for line in text.splitlines():
        context = _clean_line(line)[:80]
        for m in DATE_RE.finditer(line):
            iso = _match_iso(m)
            if iso:
                found.append((iso, context))
    return found


def file_date(dates):
    """The letter's own date: the first one found, or today when there is none."""
    return dates[0][0] if dates else datetime.date.today().isoformat()


def dates_that_matter(dates):
    """Dates later than the letter's date on a line that asks for something by then."""
    first = file_date(dates)
    return [(d, c) for d, c in dates if d > first and MATTERS_RE.search(c)]


# ---------- naming ----------

def _segments(text):
    """Each line split where a laid-out page puts wide gaps between columns."""
    for line in text.splitlines():
        for part in re.split(r"\s{3,}", line):
            part = _clean_line(part)
            if part:
                yield part


def _looks_like_name(seg):
    words = seg.split()
    if not 2 <= len(words) <= 6 or re.search(r"\d", seg):
        return False
    letters = [w.strip(".,'()-") for w in words]
    if not all(letters):
        return False
    if seg.upper() == seg and re.search(r"[A-Z]", seg):
        return True
    for i, w in enumerate(letters):
        if i > 0 and w.lower() in MINOR_WORDS:
            continue
        if not w[0].isupper():
            return False
    return True


def guess_sender(text):
    """The first short line in Title Case or ALL CAPS with no digits, or 'Unknown sender'."""
    for seg in _segments(text):
        if _looks_like_name(seg):
            return seg
    return "Unknown sender"


def guess_title(text):
    """The first line naming the kind of document, else the first line, at most 40 characters."""
    segs = list(_segments(text))
    for seg in segs:
        low = seg.lower()
        if any(w in low for w in TITLE_WORDS):
            return seg[:40].strip()
    return segs[0][:40].strip() if segs else "Document"


def _safe(part):
    part = re.sub(r"\s+", " ", ILLEGAL.sub(" ", part)).strip(" .")
    return part or "Unknown"


def target_path(root, into, date, sender, title):
    """<into or root/paperwork>/<YYYY>/<YYYY-MM-DD> - <Sender> - <Title>.pdf, never over an existing file."""
    folder = os.path.join(into or os.path.join(root, "paperwork"), date[:4])
    stem = "%s - %s - %s" % (date, _safe(sender), _safe(title))
    path = os.path.join(folder, stem + ".pdf")
    n = 2
    while os.path.exists(path):
        path = os.path.join(folder, "%s (%d).pdf" % (stem, n))
        n += 1
    return path


def append_dates(root, entries, source_rel):
    """Add 'YYYY-MM-DD | what | from <file>' lines to paperwork/dates.md, skipping ones already there."""
    path = os.path.join(root, "paperwork", "dates.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = ""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            existing = fh.read()
    have = set(l.strip() for l in existing.splitlines())
    new = []
    for date, context in entries:
        line = "%s | %s | from %s" % (date, context.replace("|", "/"), source_rel)
        if line not in have:
            have.add(line)
            new.append(line)
    if not new and existing:
        return []
    with open(path, "a" if existing else "w", encoding="utf-8", newline="\n") as fh:
        if not existing:
            fh.write(DATES_HEADER)
        elif not existing.endswith("\n"):
            fh.write("\n")
        for line in new:
            fh.write(line + "\n")
    return new


def _rel(path, root):
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel.replace(os.sep, "/")


# ---------- the run ----------

def _make_pdf(src, tmp):
    """A PDF with a text layer for src, or an exit code. Returns (pdf_path, code)."""
    ext = os.path.splitext(src)[1].lower()
    pdftotext = find_pdftotext()
    if not pdftotext:
        return None, _missing("pdftotext")
    if ext == ".pdf" and has_text(src, pdftotext):
        return src, 0
    if ext not in IMAGES and ext != ".pdf":
        print("not a PDF or a photo: %s" % src)
        return None, 1
    magick = find_magick() if ext == ".heic" else None
    if ext == ".heic" and not magick:
        print("HEIC photos are not supported without ImageMagick. Save the photo as JPG, or run: %s" % DOCTOR)
        return None, 3
    program = find_ocrmypdf()
    if not program:
        return None, _missing("ocrmypdf")
    if not find_tesseract():
        return None, _missing("tesseract")
    out = os.path.join(tmp, "read.pdf")
    if ext == ".pdf":
        cmd = ocr(src, out, program)
    else:
        image = src
        if ext == ".heic":
            image = os.path.join(tmp, "photo.png")
            ok, _, err = _run([magick, src, image])
            if not ok:
                print("ImageMagick could not read %s: %s" % (src, err))
                return None, 1
        cmd = image_command(image, out, program)
    ok, _, err = _run(cmd, env=_ocr_env())
    if not ok or not os.path.isfile(out):
        print("OCRmyPDF could not read %s: %s" % (src, err))
        return None, 1
    return out, 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Read, name and file a scan, photo or PDF; pull out the dates that matter.")
    p.add_argument("file", help="the scan, photo or PDF")
    p.add_argument("--dry-run", action="store_true", help="print the plan and change nothing")
    p.add_argument("--sender", help="the sender, when the guess is wrong")
    p.add_argument("--title", help="the title, when the guess is wrong")
    p.add_argument("--into", help="file under this folder instead of paperwork/")
    args = p.parse_args(argv)
    src = os.path.abspath(args.file)
    if not os.path.isfile(src):
        print("not found: %s" % args.file)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        pdf, code = _make_pdf(src, tmp)
        if code:
            return code
        text = read_text(pdf)
        if not text.strip():
            print("no text could be read from %s" % args.file)
            return 1
        dates = find_dates(text)
        date = file_date(dates)
        sender = args.sender or guess_sender(text)
        title = args.title or guess_title(text)
        matter = dates_that_matter(dates)
        into = os.path.abspath(args.into) if args.into else None
        target = target_path(ROOT, into, date, sender, title)
        if args.dry_run:
            print("Would file: %s" % target)
            print("Letter date: %s%s" % (date, "" if dates else " (none found; today)"))
            for d, c in matter:
                print("Date that matters: %s | %s" % (d, c))
            if not matter:
                print("No dates that matter found.")
            return 0
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(pdf, target)
    append_dates(ROOT, matter, _rel(target, ROOT))
    print("Filed: %s" % target)
    for d, c in matter:
        print("%s | %s" % (d, c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
