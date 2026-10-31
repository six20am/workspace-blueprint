import contextlib
import datetime as dt
import importlib.util
import io
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("renewals", os.path.join(HERE, "..", "tools", "renewals", "renewals.py"))
renewals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renewals)

TODAY = dt.date(2026, 11, 2)
FILE = """# Renewals

2027-03-15 | car insurance | Example Mutual, policy ends | every 6 months
2027-01-31 | business license | city hall | every year
2026-10-28 | truck registration | state motor vehicles | every year
2031-08-20 | passport | | every 10 years
2026-11-19 | web domain example.com | the registrar | every year
2026-11-05 | furnace service plan | Northwind Heating | once
2026-10-01 | old gym pass | | once
2026-12-01 | something with no cadence | the shop
"""
DATES = """# Dates that matter

2026-11-10 | water bill due | from paperwork/2026/2026-10-15 - Northwind Power - Bill.pdf
2027-02-14 | Renew liability policy by Feb 14 | from paperwork/2026/2026-10-20 - Example Mutual - Notice.pdf
2026-12-31 | driver license expires | from paperwork/2026/2026-10-01 - State - Notice.pdf
2027-01-31 | business license | from paperwork/2026/2026-10-05 - City - Notice.pdf
"""


class RenewalsTest(unittest.TestCase):
    def test_parse_reads_cadence_and_who(self):
        items = renewals.parse(FILE)
        self.assertEqual(len(items), 8)
        car = items[0]
        self.assertEqual((car["what"], car["who"], car["cadence"]), ("car insurance", "Example Mutual, policy ends", (6, "month")))
        self.assertEqual(items[3]["who"], "")
        self.assertEqual(items[3]["cadence"], (10, "year"))
        self.assertTrue(items[5]["once"])
        self.assertEqual(items[7]["who"], "the shop")
        self.assertIsNone(items[7]["cadence"])

    def test_sort_into_buckets(self):
        b = renewals.sort_items(renewals.parse(FILE), TODAY)
        self.assertEqual([i["what"] for i in b["past"]], ["old gym pass", "truck registration"])
        self.assertEqual([i["what"] for i in b["soon"]], ["furnace service plan"])
        self.assertEqual([i["what"] for i in b["month"]], ["web domain example.com", "something with no cadence"])
        self.assertEqual([i["what"] for i in b["later"]], ["business license", "car insurance", "passport"])

    def test_roll_forward(self):
        self.assertEqual(renewals.roll(dt.date(2026, 10, 28), (1, "year"), TODAY), dt.date(2027, 10, 28))
        self.assertEqual(renewals.roll(dt.date(2026, 3, 15), (6, "month"), TODAY), dt.date(2027, 3, 15))
        self.assertEqual(renewals.roll(dt.date(2024, 2, 29), (1, "year"), TODAY), dt.date(2027, 2, 28))
        self.assertEqual(renewals.roll(dt.date(2026, 10, 26), (2, "week"), TODAY), dt.date(2026, 11, 9))

    def test_render_shape(self):
        text = renewals.render(renewals.sort_items(renewals.parse(FILE), TODAY), TODAY)
        self.assertIn("# Renewals, as of 2026-11-02", text)
        self.assertIn("- 5 days past: truck registration, state motor vehicles (2026-10-28, every year)", text)
        self.assertIn("  renewed? then replace the line with: 2027-10-28 | truck registration | state motor vehicles | every year", text)
        self.assertIn("  one-off: drop the line once it is done", text)
        self.assertIn("- in 3 days: furnace service plan, Northwind Heating (2026-11-05, once)", text)
        self.assertIn("- in 17 days: web domain example.com, the registrar (2026-11-19, every year)", text)
        self.assertIn("- in 133 days: car insurance, Example Mutual, policy ends (2027-03-15, every 6 months)", text)
        self.assertNotIn("—", text)
        self.assertEqual(renewals.render(renewals.sort_items([], TODAY), TODAY).count("Nothing."), 4)

    def test_from_dates_suggests_renewal_lines_not_already_listed(self):
        lines = renewals.from_dates(DATES, FILE)
        self.assertEqual(lines, [
            "2027-02-14 | Renew liability policy by Feb 14 | from paperwork/2026/2026-10-20 - Example Mutual - Notice.pdf | every year",
            "2026-12-31 | driver license expires | from paperwork/2026/2026-10-01 - State - Notice.pdf | every year",
        ])

    def test_main(self):
        d = tempfile.mkdtemp()
        f = os.path.join(d, "renewals.md")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(FILE)
        dates = os.path.join(d, "dates.md")
        with open(dates, "w", encoding="utf-8") as fh:
            fh.write(DATES)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = renewals.main(["--file", f, "--today", "2026-11-02"])
        self.assertEqual(rc, 0)
        self.assertIn("## Within 7 days", out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = renewals.main(["--file", f, "--dates", dates, "--from-dates"])
        self.assertEqual(rc, 0)
        self.assertIn("driver license expires", out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = renewals.main(["--file", f + ".missing"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
