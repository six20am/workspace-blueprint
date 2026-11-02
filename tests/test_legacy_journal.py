import contextlib
import datetime as dt
import importlib.util
import io
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("legacy", os.path.join(HERE, "..", "tools", "legacy-journal", "legacy.py"))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)

TODAY = dt.date(2026, 11, 2)


def write(root, rel, text="x"):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class LegacyJournalTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        write(self.root, "people.md", "# People\n\nAva | 2022-06-01\n- Leo | 2024-02-29\n")
        write(self.root, "letters/2026-11-20 - for Ava - first day of kindergarten.md", "SEALED TEXT")
        write(self.root, "letters/2026-10-30 - for Leo - his first bike.md", "SEALED TEXT")
        write(self.root, "letters/2040-06-01 - for Ava - on your 18th birthday.md", "SEALED TEXT")
        write(self.root, "letters/given/2026-06-01 - for Ava - fourth birthday.md", "SEALED TEXT")
        write(self.root, "letters/notes to self.md", "not a letter")
        write(self.root, "entries/2026/2026-11-02 - the kitchen on Elm Street.md",
              "# The kitchen on Elm Street\nFor: everyone\nAsked: Walk me into the kitchen.\n\n## The radio\nIt was always on.\n")
        write(self.root, "entries/2026/2026-10-15 - for Ava only.md", "# Your name\nFor: Ava\n\nWe picked it in the car.\n")
        write(self.root, "entries/2025/2025-12-25 - Christmas.md", "# Christmas\nFor: Leo and Ava\n\nSnow.\n")
        write(self.root, "entries/2026/2026-09-01 - for Leo only.md", "# Leo\nFor: Leo\n\nHis laugh.\n")
        write(self.root, "video/2026/2026-11-01 - first snow.md", "# First snow\n\nLook at it come down.\n")
        write(self.root, "video/2026/2026-11-01 - first snow.mp4", "video")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_letters_from_file_names_only(self):
        items = legacy.letters(os.path.join(self.root, "letters"))
        self.assertEqual([it["file"][:10] for it in items], ["2026-10-30", "2026-11-20", "2040-06-01"])
        self.assertEqual(items[1]["who"], "Ava")
        self.assertEqual(items[1]["what"], "first day of kindergarten")

    def test_sort_letters(self):
        b = legacy.sort_letters(legacy.letters(os.path.join(self.root, "letters")), TODAY)
        self.assertEqual([legacy.line_for(it) for it in b["due"]], ["3 days past: for Leo, his first bike (2026-10-30)"])
        self.assertEqual([legacy.line_for(it) for it in b["soon"]], ["in 18 days: for Ava, first day of kindergarten (2026-11-20)"])
        self.assertEqual(len(b["later"]), 1)

    def test_age(self):
        known = legacy.people(open(os.path.join(self.root, "people.md"), encoding="utf-8").read())
        self.assertEqual(legacy.turns(known["ava"][1], 18), dt.date(2040, 6, 1))
        self.assertEqual(legacy.turns(known["leo"][1], 18), dt.date(2042, 2, 28))
        self.assertEqual(legacy.turns(known["leo"][1], 4), dt.date(2028, 2, 29))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(legacy.main(["--root", self.root, "age", "ava", "18"]), 0)
        self.assertEqual(out.getvalue().strip(), "Ava turns 18 on 2040-06-01.")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(legacy.main(["--root", self.root, "age", "Sam", "18"]), 2)

    def test_book_for_one_child_in_date_order_without_letters(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(legacy.main(["--root", self.root, "--today", "2026-11-02", "book", "--for", "Ava", "--title", "For Ava"]), 0)
        path = out.getvalue().strip()
        self.assertEqual(path, os.path.join(self.root, "book", "ava-2026-11-02.md"))
        text = open(path, encoding="utf-8").read()
        self.assertTrue(text.startswith("# For Ava\n"))
        order = [text.index(t) for t in ("## Christmas", "## Your name", "## First snow", "## The kitchen on Elm Street")]
        self.assertEqual(order, sorted(order))
        self.assertIn("### The radio", text)
        self.assertIn("*From the video video/2026/2026-11-01 - first snow.mp4*", text)
        self.assertNotIn("## Leo", text)
        self.assertNotIn("For:", text)
        self.assertNotIn("SEALED", text)
        self.assertIn("from 4 entries", text)

    def test_book_year_and_everyone(self):
        items = legacy.entries(self.root, None, 2025)
        self.assertEqual([rel for rel, _, _ in items], ["entries/2025/2025-12-25 - Christmas.md"])
        self.assertEqual(len(legacy.entries(self.root)), 5)

    def test_letters_command_never_reads_text(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(legacy.main(["--root", self.root, "--today", "2026-11-02", "letters"]), 0)
        text = out.getvalue()
        self.assertIn("## Open date reached, give it\n\n- 3 days past: for Leo", text)
        self.assertIn("## Sealed for later\n\n- in ", text)
        self.assertNotIn("SEALED", text)
        self.assertNotIn("fourth birthday", text)

    def test_empty_folder(self):
        empty = tempfile.mkdtemp()
        try:
            self.assertEqual(legacy.letters(os.path.join(empty, "letters")), [])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(legacy.main(["--root", empty, "book"]), 2)
        finally:
            shutil.rmtree(empty, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
