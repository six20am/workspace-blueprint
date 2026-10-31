import json, os, sys, tempfile, unittest, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import build


def write(d, rel, text, newline=None):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline=newline) as fh:
        fh.write(text)


def make_repo(d, extra=None):
    write(d, "skills/a/SKILL.md", '---\nname: a\ndescription: "Does A. Use when A."\n---\n# a\n')
    write(d, "skills/a/TEST.md", "# test a\n")
    write(d, "adapters/claude-code/CLAUDE.md", "# map\n")
    write(d, "adapters/claude-code/setup.command", "#!/bin/bash\r\necho hi\r\n", newline="")
    write(d, "adapters/claude-code/platform.md", "# claude code platform\n")
    # maintainer notes name the public repo; they are never walked, so they never trip the scan
    write(d, "adapters/claude-code/publish.md", "# publish the six20am zip\n")
    write(d, "adapters/claude-code/skills/cc-only/SKILL.md", '---\nname: cc-only\ndescription: "Claude only. Use there."\n---\n')
    # the neutral path's file carries the public repo's download URL, so it may name the maintainer
    write(d, "ADAPT.md", "# Adapt\nDownload github.com/six20am/workspace-blueprint\n")
    write(d, "setup/setup.ps1", "# windows installer\n")
    write(d, "setup/setup.sh", "#!/bin/bash\n")
    write(d, "setup/tests/test-x.ps1", "# ps test\n")
    write(d, "setup/setup-report.md", "left over\n")
    write(d, "tests/test_me.py", "# root test\n")
    write(d, ".git/HEAD", "ref\n")
    write(d, "tools/sub/.git", "gitdir: ../.git/modules/sub\n")   # a submodule checkout keeps .git as a file
    write(d, ".pytest_cache/README.md", "cache\n")
    write(d, "build.py", "# me\n")
    write(d, "README.md", "# repo readme, names the maintainer\n")
    write(d, "docs/design.md", "# design spec\n")
    write(d, "tools/x/README.md", "# a tool readme, ships\n")
    for name, text in (extra or {}).items():
        write(d, name, text)


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

    def test_hard_rules_heading_is_fine(self):
        self.assertEqual(build.scan_text("## 8. Hard rules\n- never guess", []), [])


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
                self.assertIn("Top Folder/setup/setup.ps1", names)
                self.assertNotIn("Top Folder/tests/test_me.py", names)
                self.assertNotIn("Top Folder/setup/setup-report.md", names)
                self.assertNotIn("Top Folder/build.py", names)
                self.assertNotIn("Top Folder/README.md", names, "the repo readme is not part of the product")
                self.assertNotIn("Top Folder/docs/design.md", names, "the design spec is not part of the product")
                self.assertIn("Top Folder/tools/x/README.md", names, "tool readmes do ship")
                self.assertIn("Top Folder/ADAPT.md", names, "ADAPT.md ships at the root")
                self.assertFalse(any(n.endswith("/.git") or ".git/" in n or ".pytest_cache" in n for n in names))
                mode = z.getinfo("Top Folder/setup.command").external_attr >> 16
                self.assertEqual(mode & 0o111, 0o111)
                self.assertEqual(z.getinfo("Top Folder/setup.command").create_system, 3, "Unix creator, or a Mac ignores the mode bits")
                mode = z.getinfo("Top Folder/setup/setup.sh").external_attr >> 16
                self.assertEqual(mode & 0o111, 0o111)
                self.assertNotIn(b"\r\n", z.read("Top Folder/setup.command"))
                self.assertIn("Top Folder/setup/version.json", names)
            self.assertIn("CLAUDE.md", report)

    def test_claude_zip_maps_skills_and_overlays_adapter(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo)
            out = os.path.join(d, "x.zip")
            build.build(repo, out, names=[], adapter="claude-code", top="T")
            with zipfile.ZipFile(out) as z:
                names = z.namelist()
                for want in ("T/.claude/skills/a/SKILL.md", "T/.claude/skills/a/TEST.md", "T/.claude/skills/INDEX.md",
                             "T/CLAUDE.md", "T/setup.command", "T/setup/platform.md", "T/setup/adapter.json"):
                    self.assertIn(want, names)
                self.assertFalse(any(n.startswith("T/skills/") for n in names), "core skills/ must map to .claude/skills")
                self.assertFalse(any("/adapters/" in n for n in names))
                self.assertNotIn("T/install.sh", names)
                self.assertFalse(any(n.endswith("publish.md") for n in names), "maintainer publish notes stay in the repo")
                self.assertIn("T/.claude/skills/cc-only/SKILL.md", names, "an adapter skill lands in the adapter's skills folder")
                self.assertEqual(z.read("T/setup/platform.md").decode(), "# claude code platform\n")
                meta = json.loads(z.read("T/setup/adapter.json"))
                self.assertEqual(meta["adapter"], "claude-code")
                self.assertEqual(meta["skills_dir"], ".claude/skills")
                self.assertEqual(meta["map"], "CLAUDE.md")

    def test_other_adapter_json_shape(self):
        meta = json.loads(build.adapter_json("other"))
        self.assertEqual(meta, {"adapter": "other", "skills_dir": "skills", "map": "MAP.md",
                                "router": "ROUTER.md", "notes": "NOTES.md"})

    def test_other_adapter_has_no_build_output(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo)
            with self.assertRaises(ValueError):
                build.build(repo, os.path.join(d, "x.zip"), names=[], adapter="other", top="T")
            self.assertFalse(os.path.exists(os.path.join(d, "x.zip")))

    def test_index_lists_every_skill_one_line_each(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo")
            make_repo(repo, {"skills/b/SKILL.md": "---\nname: b\ndescription: >-\n  Folded text for B, e.g. this one.\n  Second sentence.\n---\n",
                             "skills/c/SKILL.md": "---\nname: c\ndescription: >\n  Plain folded C\n  over two lines.\n\n  NOT for: anything.\n---\n"})
            text = build.write_index(repo)
            with open(os.path.join(repo, "skills", "INDEX.md"), encoding="utf-8") as fh:
                self.assertEqual(fh.read(), text)
            lines = [l for l in text.splitlines() if l.startswith("- `")]
            self.assertEqual(lines, ["- `a`: Does A.",
                                     "- `b`: Folded text for B, e.g. this one.",
                                     "- `c`: Plain folded C over two lines."])
            self.assertNotIn("cc-only", text, "adapter-only skills are not in the core index")

    def test_refuses_on_leak(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"setup/SETUP.md": "call Zed first\n"})
            with self.assertRaises(build.LeakError) as cm:
                build.build(repo, os.path.join(d, "x.zip"), names=["zed"], top="T")
            self.assertIn("setup/SETUP.md", str(cm.exception).replace("\\", "/"))
            self.assertFalse(os.path.exists(os.path.join(d, "x.zip")))

    def test_refuses_leak_in_adapter_folder(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"adapters/claude-code/START-HERE.md": "call Zed first\n"})
            with self.assertRaises(build.LeakError) as cm:
                build.build(repo, os.path.join(d, "x.zip"), names=["zed"], adapter="claude-code", top="T")
            self.assertIn("adapters/claude-code/START-HERE.md", str(cm.exception).replace(os.sep, "/"))


    def test_refuses_agency_name_with_empty_names_list(self):
        # a public clone has no parent workspace names list; the gate must still know the agency's own name
        for word in ("Six20AM", "motus", "Machado", "ask Michael", "Hard Rule 10"):
            with tempfile.TemporaryDirectory() as d:
                repo = os.path.join(d, "repo"); make_repo(repo, {"setup/SETUP.md": "see %s here\n" % word})
                with self.assertRaises(build.LeakError, msg=word):
                    build.build(repo, os.path.join(d, "x.zip"), names=[], top="T")

    def test_refuses_secret_file(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"tools/a/accounts.json": "{}"})
            with self.assertRaises(build.LeakError):
                build.build(repo, os.path.join(d, "x.zip"), names=[], top="T")

    def test_version_json_carries_layout(self):
        repo = os.path.join(os.path.dirname(__file__), "..")
        self.assertEqual(json.loads(build.version_json(repo))["layout"], 2)


if __name__ == "__main__":
    unittest.main()
