import os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.join(HERE, "..", "tools", "money-log")
sys.path.insert(0, TOOL_DIR)
import money  # noqa: E402
import money_adapters  # noqa: E402

MONEY_PY = os.path.join(TOOL_DIR, "money.py")
FIXTURE = os.path.join(TOOL_DIR, "sample", "bank-export.sample.csv")  # Jul to Sep 2026, two recurring, one repeated row


class MoneyLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.money_dir = os.path.join(self.tmp, "money")
        self.res = money.run(FIXTURE, source="Example Bank checking", month="2026-09", money_dir=self.money_dir)
        with open(self.res["summary"], encoding="utf-8") as f:
            self.summary = f.read()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_fixture_covers_three_months(self):
        with open(FIXTURE, encoding="utf-8") as f:
            months = set(re.findall(r"^(\d\d)/\d\d/2026", f.read(), re.M))
        self.assertEqual({"07", "08", "09"}, months)

    def test_dedupe_removes_the_duplicate(self):
        self.assertEqual(1, len(self.res["removed"]))
        self.assertEqual("HARBOR HARDWARE", self.res["removed"][0]["description"])
        with open(self.res["ledger"], encoding="utf-8") as f:
            self.assertEqual(1, f.read().count("HARBOR HARDWARE"))

    def test_rerun_adds_nothing_to_the_ledger(self):
        again = money.run(FIXTURE, source="Example Bank checking", month="2026-09", money_dir=self.money_dir)
        self.assertEqual(0, again["added"])

    def test_categories_apply_from_the_rules(self):
        cats = dict(self.res["categories"])
        self.assertAlmostEqual(198.99, cats["Groceries"])
        self.assertAlmostEqual(91.75, cats["Utilities"])
        self.assertAlmostEqual(15.49, cats["Subscriptions"])
        self.assertNotIn("Uncategorized", cats)

    def test_rules_file_is_editable_and_used(self):
        with open(self.res["rules"], "a", encoding="utf-8") as f:
            f.write("bookshop,Books,\n")
        res = money.run(FIXTURE, source="Example Bank checking", month="2026-08", money_dir=self.money_dir)
        self.assertAlmostEqual(22.99, dict(res["categories"])["Books"])

    def test_summary_shape_month_category_total(self):
        self.assertIn("| Month | Category | Total |", self.summary)
        rows = re.findall(r"^\| (\d{4}-\d\d) \| ([^|]+) \| ([\d,]+\.\d\d) \|$", self.summary, re.M)
        self.assertTrue(rows)
        self.assertTrue(all(m == "2026-09" for m, _, _ in rows))
        self.assertIn(("2026-09", "Groceries", "198.99"), rows)
        self.assertTrue(self.res["summary"].endswith(os.path.join("money", "2026", "2026-09-summary.md")))

    def test_recurring_names_both_charges_with_monthly_amount(self):
        rec = {r["name"]: r["monthly"] for r in self.res["recurring"]}
        self.assertEqual({"NORTHSIDE FITNESS CLUB": 39.0, "STREAMPLUS SUBSCRIPTION": 15.49}, rec)
        self.assertRegex(self.summary, r"\| NORTHSIDE FITNESS CLUB \| monthly \| 39\.00 \|")
        self.assertRegex(self.summary, r"\| STREAMPLUS SUBSCRIPTION \| monthly \| 15\.49 \|")

    def test_dashboard_written_offline_with_the_month(self):
        path = self.res["dashboard"]
        self.assertEqual(os.path.dirname(self.res["summary"]), os.path.dirname(path))
        with open(path, encoding="utf-8") as f:
            page = f.read()
        self.assertIn("2026-09", page)
        self.assertNotIn("<script", page)
        self.assertNotRegex(page, r"(src|href)=")

    def test_writes_stay_inside_the_money_folder(self):
        for dirpath, _dirs, files in os.walk(self.tmp):
            for f in files:
                self.assertTrue(os.path.join(dirpath, f).startswith(self.money_dir))
        with open(os.path.join(self.money_dir, ".gitignore"), encoding="utf-8") as f:
            self.assertIn("*", f.read())

    def test_card_export_with_positive_purchases_is_flipped(self):
        h = ["Transaction Date", "Merchant", "Category", "Amount (USD)"]
        rows = [{"Transaction Date": "06/01/2026", "Merchant": "Shop", "Category": "x", "Amount (USD)": "5.75"}]
        self.assertEqual("card_positive_spend", money_adapters.detect_adapter(h))
        self.assertEqual(-5.75, money_adapters.apply_adapter(h, rows, "card_positive_spend")[0]["amount"])

    def test_command_line_entry_point(self):
        out = subprocess.run([sys.executable, MONEY_PY, FIXTURE, "--source", "Example Bank checking", "--month", "2026-08",
                              "--money-dir", self.money_dir], capture_output=True, text=True)
        self.assertEqual(0, out.returncode, out.stderr)
        self.assertIn("2026-08-summary.md", out.stdout)
        self.assertTrue(os.path.isfile(os.path.join(self.money_dir, "2026", "2026-08-dashboard.html")))


if __name__ == "__main__":
    unittest.main()
