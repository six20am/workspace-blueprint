import datetime as dt
import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("waiting", os.path.join(HERE, "..", "tools", "waiting-on", "waiting.py"))
waiting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(waiting)

TODAY = dt.date(2026, 11, 2)
FILE = """# Waiting on

2026-10-19 | Harbor Plumbing | quote for the back bathroom | emailed
2026-10-24 | Sam Ortiz | signed contract back | texted | by 2026-11-01
2026-10-27 | the card company | refund of the double charge, 84.00 | called, case 4471
2026-10-20 | Dana Lee | the spare key | asked in person | nudged 2026-10-28
- 2026-10-31 | Pat | the photos from Saturday | texted
not a line
## Came back
2026-10-10 | Harbor Plumbing | first visit date | emailed | came back 2026-10-12
"""


class WaitingOnTest(unittest.TestCase):
    def test_parse_skips_came_back_and_reads_parts(self):
        items = waiting.parse(FILE)
        self.assertEqual([i["who"] for i in items], ["Harbor Plumbing", "Sam Ortiz", "the card company", "Dana Lee", "Pat"])
        self.assertEqual(items[1]["by"], dt.date(2026, 11, 1))
        self.assertEqual(items[3]["nudged"], dt.date(2026, 10, 28))
        self.assertEqual(items[2]["what"], "refund of the double charge, 84.00")
        self.assertEqual(items[2]["how"], "called, case 4471")

    def test_sort_by_default_wait_and_by_date(self):
        overdue, still = waiting.sort_items(waiting.parse(FILE), TODAY)
        self.assertEqual([i["who"] for i in overdue], ["Harbor Plumbing", "Dana Lee", "Sam Ortiz"])
        self.assertEqual([i["who"] for i in still], ["the card company", "Pat"])
        self.assertEqual(overdue[0]["days"], 14)
        overdue, still = waiting.sort_items(waiting.parse(FILE), TODAY, after=20)
        self.assertEqual([i["who"] for i in overdue], ["Sam Ortiz"])

    def test_render_shape(self):
        overdue, still = waiting.sort_items(waiting.parse(FILE), TODAY)
        text = waiting.render(overdue, still, TODAY)
        self.assertIn("# Waiting on, as of 2026-11-02", text)
        self.assertIn("- 14 days: Harbor Plumbing, quote for the back bathroom (asked 2026-10-19, emailed)", text)
        self.assertIn("- 9 days: Sam Ortiz, signed contract back (asked 2026-10-24, texted, wanted by 2026-11-01)", text)
        self.assertIn("nudged 2026-10-28)", text)
        self.assertIn("- 2 days: Pat, the photos from Saturday (asked 2026-10-31, texted)", text)
        self.assertNotIn("first visit date", text)
        self.assertNotIn("—", text)
        self.assertIn("Nothing.", waiting.render([], [], TODAY))

    def test_main_reads_file_and_handles_missing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(FILE)
            path = fh.name
        try:
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = waiting.main(["--file", path, "--today", "2026-11-02"])
            self.assertEqual(rc, 0)
            self.assertIn("## Overdue", out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = waiting.main(["--file", path + ".missing"])
            self.assertEqual(rc, 2)
            self.assertIn("No file at", out.getvalue())
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
