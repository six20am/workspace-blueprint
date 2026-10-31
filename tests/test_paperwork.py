import contextlib, datetime, io, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "paperwork"))
import paperwork

ELECTRIC = """NORTHWIND POWER
Electric Bill
PO Box 1200, Springfield 62701
Account Number: 4455-2210
Statement Date: October 15, 2026
Amount Due: $84.12
Please pay by November 10, 2026 to avoid a late fee.
"""

EOB = """Example Health Plan
Explanation of Benefits
THIS IS NOT A BILL
Member: Jordan Lee
Date: 09/22/2026
Service date: 08/30/2026
Amount billed: $240.00
If you disagree, respond by 11/21/2026.
"""

VEHICLE = """Department of Motor Vehicles
State of Example
Registration Renewal Notice
Notice date: 10/01/26
Plate: ABC 123
Your registration expires 11/30/26.
"""


def tiny_pdf(lines):
    """A minimal valid one-page PDF whose text layer holds the given lines."""
    ops = ["BT", "/F1 12 Tf", "14 TL", "72 720 Td"]
    for line in lines:
        ops.append("(%s) Tj T*" % line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))
    ops.append("ET")
    stream = "\n".join(ops).encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n" % (len(objs) + 1, xref)
    out += b"%" + b"%EOF\n"
    return bytes(out)


def run_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = paperwork.main(argv)
    return code, buf.getvalue()


class Patch:
    """Swap module attributes for the length of a with-block."""
    def __init__(self, **values):
        self.values = values
        self.saved = {}

    def __enter__(self):
        for k, v in self.values.items():
            self.saved[k] = getattr(paperwork, k)
            setattr(paperwork, k, v)

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(paperwork, k, v)


class DateTests(unittest.TestCase):
    def test_find_dates_six_forms(self):
        text = ("Letter dated 2026-10-31\n"
                "Second notice 10/31/2026 and again 11/01/26\n"
                "Hearing on October 31, 2026 at noon\n"
                "Pay by Nov 5, 2026\n"
                "Expires 31 December 2026\n")
        found = paperwork.find_dates(text)
        self.assertEqual([d for d, _ in found],
                         ["2026-10-31", "2026-10-31", "2026-11-01", "2026-10-31", "2026-11-05", "2026-12-31"])
        self.assertEqual(found[0][1], "Letter dated 2026-10-31")
        self.assertEqual(found[4][1], "Pay by Nov 5, 2026")
        long_line = "x" * 100 + " 2026-01-02"
        self.assertLessEqual(len(paperwork.find_dates(long_line)[0][1]), 80)

    def test_file_date_first_or_today(self):
        self.assertEqual(paperwork.file_date([("2026-03-04", "a"), ("2026-05-06", "b")]), "2026-03-04")
        self.assertEqual(paperwork.file_date([]), datetime.date.today().isoformat())

    def test_dates_that_matter_keywords_and_later_only(self):
        dates = [("2026-10-15", "Statement Date: October 15, 2026"),
                 ("2026-11-10", "Please pay by November 10, 2026"),
                 ("2026-09-01", "Payment due 2026-09-01 was received"),
                 ("2026-12-01", "Office closed 2026-12-01 for the holiday")]
        self.assertEqual(paperwork.dates_that_matter(dates), [("2026-11-10", "Please pay by November 10, 2026")])
        vehicle = paperwork.dates_that_matter(paperwork.find_dates(VEHICLE))
        self.assertEqual([d for d, _ in vehicle], ["2026-11-30"])


class GuessTests(unittest.TestCase):
    def test_guess_sender_and_title(self):
        self.assertEqual(paperwork.guess_sender(ELECTRIC), "NORTHWIND POWER")
        self.assertEqual(paperwork.guess_title(ELECTRIC), "Electric Bill")
        self.assertEqual(paperwork.guess_sender(EOB), "Example Health Plan")
        self.assertEqual(paperwork.guess_title(EOB), "Explanation of Benefits")
        self.assertEqual(paperwork.guess_sender(VEHICLE), "Department of Motor Vehicles")
        self.assertEqual(paperwork.guess_title(VEHICLE), "Registration Renewal Notice")
        self.assertEqual(paperwork.guess_sender("12 Main St\nhello there friend\n"), "Unknown sender")
        self.assertEqual(paperwork.guess_title("\n  A plain first line that runs on and on past forty characters\n"),
                         "A plain first line that runs on and on p")


class FilingTests(unittest.TestCase):
    def test_target_path_sanitizes_and_dedupes(self):
        with tempfile.TemporaryDirectory() as root:
            p = paperwork.target_path(root, None, "2026-10-15", 'North/wind: "Power"', "Bill?  *now*")
            self.assertEqual(p, os.path.join(root, "paperwork", "2026", "2026-10-15 - North wind Power - Bill now.pdf"))
            os.makedirs(os.path.dirname(p))
            open(p, "wb").close()
            p2 = paperwork.target_path(root, None, "2026-10-15", 'North/wind: "Power"', "Bill?  *now*")
            self.assertEqual(p2, p[:-4] + " (2).pdf")
            into = os.path.join(root, "elsewhere")
            p3 = paperwork.target_path(root, into, "2025-01-02", "A", "B")
            self.assertEqual(p3, os.path.join(into, "2025", "2025-01-02 - A - B.pdf"))

    def test_append_dates_creates_header_and_skips_duplicates(self):
        with tempfile.TemporaryDirectory() as root:
            entries = [("2026-11-10", "Please pay by November 10, 2026")]
            paperwork.append_dates(root, entries, "paperwork/2026/a.pdf")
            paperwork.append_dates(root, entries + [("2026-12-01", "Renew | by then")], "paperwork/2026/a.pdf")
            with open(os.path.join(root, "paperwork", "dates.md"), encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            self.assertTrue(lines[0].startswith("# "))
            dated = [l for l in lines if l[:4].isdigit()]
            self.assertEqual(dated, ["2026-11-10 | Please pay by November 10, 2026 | from paperwork/2026/a.pdf",
                                     "2026-12-01 | Renew / by then | from paperwork/2026/a.pdf"])


class CliTests(unittest.TestCase):
    def test_dry_run_changes_nothing(self):
        if not paperwork.find_pdftotext():
            self.skipTest("pdftotext not found; install Poppler to run this test")
        with tempfile.TemporaryDirectory() as root:
            src = os.path.join(root, "scan.pdf")
            data = tiny_pdf(ELECTRIC.splitlines())
            with open(src, "wb") as fh:
                fh.write(data)
            before = sorted(os.listdir(root))
            with Patch(ROOT=root):
                code, out = run_main([src, "--dry-run"])
            self.assertEqual(code, 0, out)
            self.assertIn("2026-10-15 - NORTHWIND POWER - Electric Bill.pdf", out)
            self.assertIn("2026-11-10", out)
            self.assertEqual(sorted(os.listdir(root)), before)
            with open(src, "rb") as fh:
                self.assertEqual(fh.read(), data)

    def test_real_filing_copies_and_writes_dates(self):
        if not paperwork.find_pdftotext():
            self.skipTest("pdftotext not found; install Poppler to run this test")
        with tempfile.TemporaryDirectory() as root:
            src = os.path.join(root, "scan.pdf")
            with open(src, "wb") as fh:
                fh.write(tiny_pdf(EOB.splitlines()))
            with Patch(ROOT=root):
                code, out = run_main([src, "--sender", "Example Health Plan"])
            self.assertEqual(code, 0, out)
            name = "2026-09-22 - Example Health Plan - Explanation of Benefits.pdf"
            target = os.path.join(root, "paperwork", "2026", name)
            self.assertTrue(os.path.isfile(target), out)
            self.assertTrue(os.path.isfile(src))
            self.assertIn("Filed: " + target, out)
            with open(os.path.join(root, "paperwork", "dates.md"), encoding="utf-8") as fh:
                self.assertIn("2026-11-21 | If you disagree, respond by 11/21/2026. | from paperwork/2026/" + name,
                              fh.read())

    def test_missing_program_exit_3(self):
        with tempfile.TemporaryDirectory() as root:
            src = os.path.join(root, "scan.pdf")
            with open(src, "wb") as fh:
                fh.write(tiny_pdf(["x"]))
            with Patch(ROOT=root, find_pdftotext=lambda: None):
                code, out = run_main([src, "--dry-run"])
            self.assertEqual(code, 3)
            self.assertIn("Missing: pdftotext. Run: python tools/doctor/doctor.py (python3 on Mac and Linux)", out)
            with Patch(ROOT=root, find_pdftotext=lambda: "pdftotext", has_text=lambda pdf, prog=None: False,
                       find_ocrmypdf=lambda: None):
                code, out = run_main([src])
            self.assertEqual(code, 3)
            self.assertIn("Missing: ocrmypdf. Run: python tools/doctor/doctor.py (python3 on Mac and Linux)", out)
            self.assertFalse(os.path.exists(os.path.join(root, "paperwork")))

    def test_ocr_and_image_commands(self):
        self.assertEqual(paperwork.ocr("in.pdf", "out.pdf"), ["ocrmypdf", "--skip-text", "in.pdf", "out.pdf"])
        self.assertEqual(paperwork.image_command("a.jpg", "a.pdf"),
                         ["ocrmypdf", "--image-dpi", "300", "a.jpg", "a.pdf"])

    def test_real_ocr_when_installed(self):
        if not (paperwork.find_ocrmypdf() and paperwork.find_tesseract() and paperwork.find_pdftotext()):
            self.skipTest("ocrmypdf, tesseract or pdftotext not found; skipping the real OCR run")
        with tempfile.TemporaryDirectory() as root:
            src = os.path.join(root, "scan.pdf")
            with open(src, "wb") as fh:
                fh.write(tiny_pdf(VEHICLE.splitlines()))
            with Patch(ROOT=root, has_text=lambda pdf, prog=None: False):
                code, out = run_main([src, "--dry-run"])
            self.assertEqual(code, 0, out)
            self.assertIn("Registration Renewal Notice", out)


if __name__ == "__main__":
    unittest.main()
