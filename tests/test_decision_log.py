import contextlib
import datetime as dt
import importlib.util
import io
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("decisions", os.path.join(HERE, "..", "tools", "decision-log", "decisions.py"))
decisions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decisions)

TODAY = dt.date(2026, 11, 2)
FILE = """# Decisions

2026-10-14 | invoice monthly, not per job | fewer chases, clients asked for it | owner
2026-10-21 | the website uses the dark logo | reads better on the photos | owner, after seeing both
- 2026-10-28 | no Tuesday evening class this winter | three sign-ups, room costs more than it brings | owner
2026-10-30 | keep the old phone number on the van | people still call it | owner's partner
not a decision line
2026-13-99 | bad date | x | y
"""


class DecisionLogTest(unittest.TestCase):
    def test_parse(self):
        items = decisions.parse(FILE)
        self.assertEqual(len(items), 4)
        self.assertEqual(items[2][1], "2026-10-28 | no Tuesday evening class this winter | three sign-ups, room costs more than it brings | owner")

    def test_find_by_word_and_days(self):
        items = decisions.parse(FILE)
        self.assertEqual(decisions.find(items, ["Invoice"], today=TODAY),
                         ["2026-10-14 | invoice monthly, not per job | fewer chases, clients asked for it | owner"])
        self.assertEqual([l[:10] for l in decisions.find(items, days=7, today=TODAY)], ["2026-10-30", "2026-10-28"])
        self.assertEqual(decisions.find(items, ["class", "winter"], days=7, today=TODAY)[0][:10], "2026-10-28")
        self.assertEqual(decisions.find(items, ["nothing"], today=TODAY), [])

    def test_main(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(FILE)
            path = fh.name
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = decisions.main(["--file", path, "logo"])
            self.assertEqual(rc, 0)
            self.assertIn("- 2026-10-21 | the website uses the dark logo", out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = decisions.main(["--file", path, "zebra"])
            self.assertEqual(rc, 1)
            self.assertIn("No decision logged for zebra.", out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = decisions.main(["--file", path + ".missing"])
            self.assertEqual(rc, 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
