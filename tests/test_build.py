import os, sys, tempfile, unittest, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import build


def make_repo(d, extra=None):
    os.makedirs(os.path.join(d, "setup", "tests"))
    os.makedirs(os.path.join(d, "tests"))
    os.makedirs(os.path.join(d, ".git"))
    open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8").write("# map\n")
    open(os.path.join(d, "setup.command"), "w", encoding="utf-8", newline="").write("#!/bin/bash\r\necho hi\r\n")
    open(os.path.join(d, "setup", "setup.sh"), "w", encoding="utf-8").write("#!/bin/bash\n")
    open(os.path.join(d, "setup", "tests", "test-x.ps1"), "w", encoding="utf-8").write("# ps test\n")
    open(os.path.join(d, "setup", "setup-report.md"), "w", encoding="utf-8").write("left over\n")
    open(os.path.join(d, "tests", "test_me.py"), "w", encoding="utf-8").write("# root test\n")
    open(os.path.join(d, ".git", "HEAD"), "w").write("ref\n")
    open(os.path.join(d, "build.py"), "w").write("# me\n")
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write("# repo readme, names the maintainer\n")
    os.makedirs(os.path.join(d, "docs"))
    open(os.path.join(d, "docs", "design.md"), "w", encoding="utf-8").write("# design spec\n")
    os.makedirs(os.path.join(d, "tools", "x"))
    open(os.path.join(d, "tools", "x", "README.md"), "w", encoding="utf-8").write("# a tool readme, ships\n")
    for name, text in (extra or {}).items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)


class ScanTest(unittest.TestCase):
    def test_em_dash_is_a_problem(self):
        self.assertTrue(build.scan_text("a \u2014 b", ["zed"]))

    def test_name_is_a_problem_case_insensitive(self):
        self.assertTrue(build.scan_text("Hello ZED here", ["zed"]))

    def test_hex_id_is_a_problem(self):
        self.assertTrue(build.scan_text("id 3f3fd31a96f30afb6878d8a3dae68780 ok", []))

    def test_clean_text_passes(self):
        self.assertEqual(build.scan_text("plain words, a dash - here", ["zed"]), [])

    def test_secret_shaped_filename(self):
        self.assertTrue(build.is_secret("tools/x/accounts.json"))
        self.assertTrue(build.is_secret(".env"))
        self.assertFalse(build.is_secret("tools/x/accounts.example.json"))


class BuildTest(unittest.TestCase):
    def test_builds_zip_with_exec_bits_and_skips(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo)
            out = os.path.join(d, "Out Dir", "X.zip")
            report = build.build(repo, out, names=["zed"], top="Top Folder")
            with zipfile.ZipFile(out) as z:
                names = z.namelist()
                self.assertIn("Top Folder/CLAUDE.md", names)
                self.assertIn("Top Folder/setup.command", names)
                self.assertIn("Top Folder/setup/tests/test-x.ps1", names)
                self.assertNotIn("Top Folder/tests/test_me.py", names)
                self.assertNotIn("Top Folder/setup/setup-report.md", names)
                self.assertNotIn("Top Folder/build.py", names)
                self.assertNotIn("Top Folder/README.md", names, "the repo readme is not part of the product")
                self.assertNotIn("Top Folder/docs/design.md", names, "the design spec is not part of the product")
                self.assertIn("Top Folder/tools/x/README.md", names, "tool readmes do ship")
                self.assertFalse(any(".git/" in n for n in names))
                mode = z.getinfo("Top Folder/setup.command").external_attr >> 16
                self.assertEqual(mode & 0o111, 0o111)
                self.assertEqual(z.getinfo("Top Folder/setup.command").create_system, 3, "Unix creator, or a Mac ignores the mode bits")
                mode = z.getinfo("Top Folder/setup/setup.sh").external_attr >> 16
                self.assertEqual(mode & 0o111, 0o111)
                self.assertNotIn(b"\r\n", z.read("Top Folder/setup.command"))
            self.assertIn("CLAUDE.md", report)

    def test_refuses_on_leak(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"setup/SETUP.md": "call Zed first\n"})
            with self.assertRaises(build.LeakError) as cm:
                build.build(repo, os.path.join(d, "x.zip"), names=["zed"], top="T")
            self.assertIn("setup/SETUP.md", str(cm.exception).replace("\\", "/"))
            self.assertFalse(os.path.exists(os.path.join(d, "x.zip")))

    def test_refuses_agency_name_with_empty_names_list(self):
        # a public clone has no parent workspace names list; the gate must still know the agency's own name
        for word in ("Six20AM", "motus", "Machado", "ask Michael", "Hard Rule 10"):
            with tempfile.TemporaryDirectory() as d:
                repo = os.path.join(d, "repo"); make_repo(repo, {"setup/SETUP.md": "see %s here\n" % word})
                with self.assertRaises(build.LeakError, msg=word):
                    build.build(repo, os.path.join(d, "x.zip"), names=[], top="T")

    def test_hard_rules_heading_is_fine(self):
        self.assertEqual(build.scan_text("## 8. Hard rules\n- never guess", []), [])

    def test_refuses_secret_file(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"tools/a/accounts.json": "{}"})
            with self.assertRaises(build.LeakError):
                build.build(repo, os.path.join(d, "x.zip"), names=[], top="T")


if __name__ == "__main__":
    unittest.main()
