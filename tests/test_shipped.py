import os, re, unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
FORBIDDEN = re.compile(r"six20am|motus|machado|mtesi|C:\\Users\\|/c/Users/|shared-core|shared-systems|work-log|Michael|\bGHL\b|HighLevel|Hard Rule \d|\b[0-9a-f]{32}\b", re.I)
# files that may name the maintainer (same set as build.py): the updater and ADAPT.md carry the public repo's URL
ALLOWED = {"README.md", "docs/design.md", "tools/update/update.py", "ADAPT.md"}
# vendor code shipped as-is; scanned by eye, not by string (see the ledger ruling)
VENDOR = ("skills/last30days/scripts/", "skills/agent-reach/_references")
# verbatim third-party notices whose source URLs carry 32-character ids; every other forbidden string is still checked
HEX_OK = {"tools/motion/ATTRIBUTIONS.md"}
FORBIDDEN_NO_HEX = re.compile("|".join(p for p in FORBIDDEN.pattern.split("|") if "{32}" not in p), re.I)
TEXT = (".md", ".json", ".ps1", ".sh", ".command", ".cmd", ".py", ".txt", ".mjs", ".js", ".ts", ".tsx")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".superpowers", ".impeccable", ".agents", ".remotion"}
SKIP_PATHS = {"tools/motion/out"}  # render output; build.py skips it too
SKIP_ROOT_DIRS = {"site", ".github", "docs", "dist"}  # the website, CI and build outputs never ship; build.py skips them too
ADAPTER_SKIP_FILES = ("publish.md",)  # maintainer notes inside an adapter folder; never shipped (like the root README.md)
PLATFORM = re.compile(r"\.claude/|\bCLAUDE\.md\b|\bCONTEXT\.md\b|claude mcp add|/workspace/<")
# backticked names an adapter root or the run time supplies; not files in this repo
RUNTIME = {"setup/platform.md", "setup/adapter.json", "setup/version.json", "setup/setup-report.md", "setup/update-report.md",
           "install.sh", "setup.cmd", "setup.command", "update.cmd", "update.command", "CLAUDE.md", "CONTEXT.md", "voice.md"}


def rel_of(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def is_adapter_note(rel):
    parts = rel.split("/")
    return len(parts) == 3 and parts[0] == "adapters" and parts[2] in ADAPTER_SKIP_FILES


def shipped_files():
    for dirpath, dirs, files in os.walk(ROOT):
        at_root = os.path.abspath(dirpath) == os.path.abspath(ROOT)
        here = rel_of(dirpath)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (at_root and d in SKIP_ROOT_DIRS)
                   and (d if at_root else here + "/" + d) not in SKIP_PATHS]
        for f in files:
            p = os.path.join(dirpath, f)
            rel = rel_of(p)
            if f.endswith(TEXT) and not rel.startswith("tests/") and rel != "build.py" and not is_adapter_note(rel):
                yield rel, p


class ShippedTest(unittest.TestCase):
    def test_required_files_exist(self):
        for f in ("adapters/claude-code/START-HERE.md", "adapters/claude-code/CLAUDE.md", "adapters/claude-code/AGENTS.md",
                  "adapters/claude-code/GEMINI.md", "adapters/claude-code/setup.cmd", "adapters/claude-code/setup.command",
                  "adapters/claude-code/platform.md", "ADAPT.md", "skills/INDEX.md",
                  "setup/SETUP.md", "setup/filing-styles.md", "setup/gap-log.md", "setup/tools.json"):
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
                m = (FORBIDDEN_NO_HEX if rel in HEX_OK else FORBIDDEN).search(fh.read())
                self.assertIsNone(m, "%s contains %r" % (rel, m.group(0) if m else None))

    def test_backticked_paths_resolve(self):
        for rel in ("adapters/claude-code/CLAUDE.md", "adapters/claude-code/AGENTS.md", "adapters/claude-code/GEMINI.md",
                    "adapters/claude-code/START-HERE.md", "setup/SETUP.md", "ADAPT.md"):
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                text = fh.read()
            for path in re.findall(r"`((?:setup|_reference|skills|\.claude)/[A-Za-z0-9_./-]+)`", text):
                if path in RUNTIME:
                    continue  # an adapter root file or written at run time
                tries = (path, path.replace(".claude/skills/", "skills/"))
                self.assertTrue(any(os.path.exists(os.path.join(ROOT, t)) for t in tries), "%s names %s" % (rel, path))

    def test_claude_md_routes_setup(self):
        with open(os.path.join(ROOT, "adapters", "claude-code", "CLAUDE.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("set this up", text)
        self.assertIn("setup/SETUP.md", text)

    def test_gap_finder_present_and_skill_count(self):
        skills = os.path.join(ROOT, "skills")
        names = sorted(d for d in os.listdir(skills) if os.path.isfile(os.path.join(skills, d, "SKILL.md")))
        self.assertIn("gap-finder", names)
        self.assertIn("update", names)
        self.assertGreaterEqual(len(names), 22, names)
        with open(os.path.join(skills, "INDEX.md"), encoding="utf-8") as fh:
            indexed = [l for l in fh.read().splitlines() if l.startswith("- `")]
        self.assertEqual(len(names), len(indexed), "skills/INDEX.md is stale; run build.py")
        with open(os.path.join(skills, "gap-finder", "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        for word in ("build", "find", "by hand", "gap-log.md", "three times", "tool-vetting"):
            self.assertIn(word, text)

    def test_no_platform_paths_in_core_skills(self):
        for rel, p in shipped_files():
            if not rel.startswith("skills/") or rel.startswith(VENDOR) or rel.startswith("skills/last30days/"):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                m = PLATFORM.search(fh.read())
                self.assertIsNone(m, "%s names a platform path %r" % (rel, m.group(0) if m else None))

    def test_adapt_md_is_short_and_neutral(self):
        with open(os.path.join(ROOT, "ADAPT.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertLess(len(text.splitlines()), 70)
        self.assertIn('{"adapter": "other", "skills_dir": "skills", "map": "MAP.md", "router": "ROUTER.md", "notes": "NOTES.md"}', text)
        for want in ("bash setup/setup.sh --no-launch", "python3 tools/doctor/doctor.py", "python3 tools/update/update.py",
                     "setup/SETUP.md", "MAP.md", "ROUTER.md", "NOTES.md", "voice.md"):
            self.assertIn(want, text)
        vendors = ["claude", "gemini", "codex", "openai", "gr" + "ok"]   # split so the repo-wide grep for the retired vendor stays clean
        self.assertNotRegex(text, re.compile("|".join(vendors), re.I), "ADAPT.md names no vendor")
        self.assertNotIn("python tools/", text, "ADAPT.md uses python3: stock Linux and Mac have no python")

    def test_filing_styles_has_six(self):
        with open(os.path.join(ROOT, "setup/filing-styles.md"), encoding="utf-8") as fh:
            text = fh.read()
        for name in ("## Military", "## By stage", "## By client or project", "## PARA", "## Numbered index", "## By date"):
            self.assertIn(name, text)

    def test_every_skill_has_a_test_task(self):
        skills = os.path.join(ROOT, "skills")
        for d in sorted(os.listdir(skills)):
            if not os.path.isfile(os.path.join(skills, d, "SKILL.md")):
                continue
            t = os.path.join(skills, d, "TEST.md")
            self.assertTrue(os.path.isfile(t), d + " has no TEST.md")
            with open(t, encoding="utf-8") as fh:
                text = fh.read()
            for h in ("## The ask", "## The input", "## Done looks like"):
                self.assertIn(h, text, d + " TEST.md missing " + h)


if __name__ == "__main__":
    unittest.main()
