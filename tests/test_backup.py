import contextlib
import datetime as dt
import importlib.util
import io
import os
import shutil
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("backup", os.path.join(HERE, "..", "tools", "backup", "backup.py"))
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


def put(root, rel, text="x"):
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class BackupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = os.path.join(self.tmp, "workspace")
        put(self.root, "clients/acme/notes.md", "notes")
        put(self.root, "money/ledger.csv", "a,b")
        put(self.root, ".git/HEAD", "ref: refs/heads/main")
        put(self.root, "site/node_modules/pkg/index.js", "never")
        put(self.root, "tools/x/__pycache__/x.pyc", "never")
        self.to = os.path.join(self.tmp, "drive", "my-workspace")
        os.makedirs(os.path.dirname(self.to))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_main(self, *argv, now=None):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = backup.main(list(argv), root=self.root, now=now)
        return rc, out.getvalue()

    def test_refuses_bad_targets(self):
        self.assertIn("inside the workspace", backup.check_target(self.root, os.path.join(self.root, "backup")))
        self.assertIn("inside the workspace", backup.check_target(self.root, self.root))
        self.assertIn("holds the workspace", backup.check_target(self.root, self.tmp))
        self.assertIn("plugged in", backup.check_target(self.root, os.path.join(self.tmp, "nodrive", "x")))
        self.assertIsNone(backup.check_target(self.root, self.to))
        rc, out = self.run_main("--to", os.path.join(self.root, "backup"))
        self.assertEqual(rc, 2)
        self.assertFalse(os.path.exists(os.path.join(self.root, "backup")))

    def test_no_place_yet(self):
        rc, out = self.run_main()
        self.assertEqual(rc, 2)
        self.assertIn("--to", out)

    def test_first_run_copies_logs_and_second_run_copies_only_changes(self):
        rc, out = self.run_main("--to", self.to, now=dt.datetime(2026, 10, 28, 9, 5))
        self.assertEqual(rc, 0, out)
        self.assertIn("3 files copied, 0 unchanged, to", out)
        self.assertEqual(open(os.path.join(self.to, "clients", "acme", "notes.md")).read(), "notes")
        self.assertTrue(os.path.isfile(os.path.join(self.to, ".git", "HEAD")))
        self.assertFalse(os.path.exists(os.path.join(self.to, "site", "node_modules")))
        self.assertFalse(os.path.exists(os.path.join(self.to, "tools", "x", "__pycache__")))
        log = open(os.path.join(self.root, "setup", "backup-log.md"), encoding="utf-8").read()
        self.assertIn("2026-10-28 09:05 | 3 copied, 0 unchanged | to " + os.path.abspath(self.to), log)
        # change one, add one, leave the rest; the log itself is new too
        time.sleep(0.05)
        put(self.root, "clients/acme/notes.md", "notes, more")
        put(self.root, "clients/acme/plan.md", "plan")
        rc, out = self.run_main(now=dt.datetime(2026, 11, 2, 9, 0))
        self.assertEqual(rc, 0, out)
        self.assertIn("3 files copied, 2 unchanged", out)
        self.assertEqual(open(os.path.join(self.to, "clients", "acme", "notes.md")).read(), "notes, more")
        self.assertEqual(backup.last_run(self.root), (dt.date(2026, 11, 2), os.path.abspath(self.to)))
        extra = put(self.to, "only-in-backup.md", "kept")
        rc, out = self.run_main("--dry-run")
        self.assertIn("Nothing done", out)
        self.assertTrue(os.path.isfile(extra))

    def test_status_line(self):
        self.assertEqual(backup.status_line(self.root, today=dt.date(2026, 11, 2)), "No backup yet. The backup skill sets one up.")
        self.run_main("--to", self.to, now=dt.datetime(2026, 10, 28, 9, 5))
        self.assertEqual(backup.status_line(self.root, today=dt.date(2026, 10, 31)),
                         "Last backup 3 days ago (2026-10-28), to %s." % os.path.abspath(self.to))
        self.assertTrue(backup.status_line(self.root, today=dt.date(2026, 11, 10)).endswith(" Run it."))
        self.assertTrue(backup.status_line(self.root, today=dt.date(2026, 10, 28)).startswith("Last backup today"))


if __name__ == "__main__":
    unittest.main()
