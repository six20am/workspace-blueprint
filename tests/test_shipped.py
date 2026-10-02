import os, re, unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
FORBIDDEN = re.compile(r"six20am|motus|machado|mtesi|C:\\Users\\|/c/Users/|shared-core|shared-systems|work-log|Michael|Hard Rule \d|\b[0-9a-f]{32}\b", re.I)
ALLOWED = {"README.md", os.path.join("docs", "design.md")}
# vendor code shipped as-is; scanned by eye, not by string (see the ledger ruling)
VENDOR = (os.path.join(".claude", "skills", "last30days", "scripts"), os.path.join(".claude", "skills", "agent-reach", "_references"))
TEXT = (".md", ".json", ".ps1", ".sh", ".command", ".cmd", ".py", ".txt", ".mjs", ".js")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".superpowers"}


def shipped_files():
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, ROOT)
            if f.endswith(TEXT) and not rel.startswith("tests") and rel != "build.py":
                yield rel, p


class ShippedTest(unittest.TestCase):
    def test_required_files_exist(self):
        for f in ("START-HERE.md", "CLAUDE.md", "AGENTS.md", "GEMINI.md", "setup/SETUP.md", "setup/filing-styles.md", "setup/gap-log.md", "setup/tools.json"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, f)), f)

    def test_no_em_dashes(self):
        for rel, p in shipped_files():
            with open(p, encoding="utf-8", errors="replace") as fh:
                self.assertNotIn("\u2014", fh.read(), rel)

    def test_no_agency_or_personal_strings(self):
        for rel, p in shipped_files():
            if rel in ALLOWED or rel.startswith("_reference") or rel.startswith(VENDOR):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                m = FORBIDDEN.search(fh.read())
                self.assertIsNone(m, "%s contains %r" % (rel, m.group(0) if m else None))

    def test_backticked_paths_resolve(self):
        for rel in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "START-HERE.md", "setup/SETUP.md"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                text = fh.read()
            for path in re.findall(r"`((?:setup|_reference|\.claude)/[A-Za-z0-9_./-]+)`", text):
                if path.endswith("setup-report.md"):
                    continue  # written by the installer at run time, gitignored on purpose
                self.assertTrue(os.path.exists(os.path.join(ROOT, path)), "%s names %s" % (rel, path))

    def test_claude_md_routes_setup(self):
        with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("set this up", text)
        self.assertIn("setup/SETUP.md", text)

    def test_gap_finder_present_and_twenty_skills(self):
        skills = os.path.join(ROOT, ".claude", "skills")
        names = sorted(d for d in os.listdir(skills) if os.path.isfile(os.path.join(skills, d, "SKILL.md")))
        self.assertIn("gap-finder", names)
        self.assertEqual(len(names), 20, names)
        with open(os.path.join(skills, "gap-finder", "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        for word in ("build", "find", "by hand", "gap-log.md", "three times", "tool-vetting"):
            self.assertIn(word, text)

    def test_filing_styles_has_six(self):
        with open(os.path.join(ROOT, "setup/filing-styles.md"), encoding="utf-8") as fh:
            text = fh.read()
        for name in ("## Military", "## By stage", "## By client or project", "## PARA", "## Numbered index", "## By date"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
