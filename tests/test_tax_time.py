import contextlib
import datetime as dt
import importlib.util
import io
import os
import shutil
import tempfile
import time
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("taxtime", os.path.join(HERE, "..", "tools", "tax-time", "taxtime.py"))
taxtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(taxtime)

YEAR = 2026


def build():
    root = tempfile.mkdtemp()

    def put(rel, text="x", day=None):
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        if day:
            t = time.mktime(dt.datetime(day.year, day.month, day.day, 12).timetuple())
            os.utime(p, (t, t))
        return p

    put("money/2026/2026-09-summary.md", "# Money summary: 2026-09")
    put("money/2026/2026-09-dashboard.html", "<html>")
    put("money/ledger.csv", "date,amount")
    put("money/2025/2025-12-summary.md", "old")
    put("paperwork/2026/2026-03-04 - Harbor Hardware - Receipt.pdf", "receipt pdf")
    put("paperwork/2026/2026-02-01 - Example Bank - 1099-INT.pdf", "form")
    put("paperwork/2026/2026-11-20 - Food Pantry - Donation letter.pdf", "thanks")
    put("paperwork/2026/2026-06-15 - Northwind Power - Bill.pdf", "bill")
    put("paperwork/2025/2025-12-01 - Shop - Receipt.pdf", "last year")
    put("clients/acme/delivery/2026-05-01 acme invoice 12.pdf", "sent invoice")
    put("S1-admin/2026-07-02 - Office Depot - Invoice.pdf", "bought")
    put("S1-admin/mileage log.csv", "miles", day=dt.date(2026, 12, 30))
    put("S1-admin/mileage log 2025.csv", "miles", day=dt.date(2025, 12, 30))
    put("receipts-box/parking receipt.jpg", "jpg", day=dt.date(2026, 4, 1))
    put("setup/2026-01-01 - receipt.md", "never")
    put("tools/x/2026-receipt.py", "never")
    put("taxes/2026/Income/old.pdf", "never")
    return root


class TaxTimeTest(unittest.TestCase):
    def setUp(self):
        self.root = build()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_plan_picks_the_year_and_categories(self):
        found, skipped = taxtime.plan(self.root, YEAR)
        self.assertEqual([(c, r) for c, r, _ in found], [
            ("Income", "clients/acme/delivery/2026-05-01 acme invoice 12.pdf"),
            ("Receipts and expenses", "S1-admin/2026-07-02 - Office Depot - Invoice.pdf"),
            ("Receipts and expenses", "paperwork/2026/2026-03-04 - Harbor Hardware - Receipt.pdf"),
            ("Tax forms", "paperwork/2026/2026-02-01 - Example Bank - 1099-INT.pdf"),
            ("Donations", "paperwork/2026/2026-11-20 - Food Pantry - Donation letter.pdf"),
            ("Mileage and travel", "S1-admin/mileage log.csv"),
            ("Mileage and travel", "receipts-box/parking receipt.jpg"),
            ("Bank summaries", "money/2026/2026-09-summary.md"),
        ])
        self.assertEqual(skipped, ["paperwork/2026/2026-06-15 - Northwind Power - Bill.pdf"])

    def test_also_folder_outside_and_dry_run_changes_nothing(self):
        outside = tempfile.mkdtemp()
        try:
            with open(os.path.join(outside, "2026-01-05 - Cafe - Receipt.pdf"), "w") as fh:
                fh.write("outside")
            found, _ = taxtime.plan(self.root, YEAR, also=[outside])
            cats = [(c, os.path.basename(r)) for c, r, _ in found]
            self.assertIn(("Receipts and expenses", "2026-01-05 - Cafe - Receipt.pdf"), cats)
        finally:
            shutil.rmtree(outside, ignore_errors=True)
        before = sorted(os.listdir(os.path.join(self.root, "taxes", "2026")))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = taxtime.main(["--year", "2026", "--dry-run"], root=self.root)
        self.assertEqual(rc, 0)
        self.assertIn("dry run, nothing changed", out.getvalue())
        self.assertIn("Receipts and expenses  <- paperwork/2026/2026-03-04 - Harbor Hardware - Receipt.pdf", out.getvalue())
        self.assertIn("Not gathered", out.getvalue())
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "taxes", "2026"))), before)

    def test_gather_copies_writes_cover_and_zip_and_is_idempotent(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = taxtime.main(["--year", "2026"], root=self.root)
        self.assertEqual(rc, 0)
        self.assertIn("8 files", out.getvalue())
        self.assertIn("8 copied now, 0 already there", out.getvalue())
        tax = os.path.join(self.root, "taxes", "2026")
        self.assertTrue(os.path.isfile(os.path.join(tax, "Receipts and expenses", "2026-03-04 - Harbor Hardware - Receipt.pdf")))
        self.assertTrue(os.path.isfile(os.path.join(tax, "Bank summaries", "2026-09-summary.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.root, "paperwork", "2026", "2026-03-04 - Harbor Hardware - Receipt.pdf")))
        cover = open(os.path.join(tax, "COVER.md"), encoding="utf-8").read()
        self.assertIn("# Tax papers for 2026", cover)
        self.assertIn("- Receipts and expenses: 2 files", cover)
        self.assertIn("- 2026-09-summary.md (from money/2026/2026-09-summary.md, 24 B)", cover)
        self.assertIn("## Nothing found for\n\n- Medical\n- Home and property", cover)
        self.assertIn("- paperwork/2026/2026-06-15 - Northwind Power - Bill.pdf", cover)
        self.assertNotIn("—", cover)
        with zipfile.ZipFile(os.path.join(tax, "taxes-2026-for-accountant.zip")) as z:
            names = z.namelist()
        self.assertIn("COVER.md", names)
        self.assertIn("Income/2026-05-01 acme invoice 12.pdf", names)
        self.assertIn("Income/old.pdf", names)  # what was already in the folder ships too
        self.assertFalse(any(n.endswith(".zip") for n in names))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            taxtime.main(["--year", "2026"], root=self.root)
        self.assertIn("0 copied now, 8 already there", out.getvalue())
        self.assertFalse(os.path.exists(os.path.join(tax, "Bank summaries", "2026-09-summary (2).md")))

    def test_different_file_same_name_gets_a_number(self):
        folder = os.path.join(self.root, "taxes", "2026", "Income")
        with open(os.path.join(folder, "receipt.pdf"), "w") as fh:
            fh.write("one")
        self.assertIsNone(taxtime.target_name(folder, "receipt.pdf", 3))
        self.assertEqual(os.path.basename(taxtime.target_name(folder, "receipt.pdf", 9)), "receipt (2).pdf")

    def test_nothing_found_says_so(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = taxtime.main(["--year", "2019"], root=self.root)
        self.assertEqual(rc, 1)
        self.assertIn("Nothing found for 2019", out.getvalue())


if __name__ == "__main__":
    unittest.main()
