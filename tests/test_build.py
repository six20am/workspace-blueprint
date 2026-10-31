import base64, json, os, sys, tempfile, unittest, zipfile
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
    write(d, "adapters/grok-bot/README.md", "# grok readme, names the maintainer\n")
    write(d, "adapters/grok-bot/install.sh", "#!/bin/bash\r\necho grok\r\n", newline="")
    write(d, "adapters/grok-bot/platform.md", "# grok bot platform\n")
    # maintainer notes name the public repos; they are never walked, so they never trip the scan
    write(d, "adapters/claude-code/publish.md", "# publish the six20am zip\n")
    write(d, "adapters/grok-bot/publish.md", "# publish the six20am mirror\n")
    write(d, "adapters/grok-bot/skills/getting-started/SKILL.md", '---\nname: getting-started\ndescription: "Starts. Use first."\n---\n')
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
                self.assertFalse(any("getting-started" in n for n in names), "the grok adapter skill never reaches the zip")
                self.assertEqual(z.read("T/setup/platform.md").decode(), "# claude code platform\n")
                meta = json.loads(z.read("T/setup/adapter.json"))
                self.assertEqual(meta["adapter"], "claude-code")
                self.assertEqual(meta["skills_dir"], ".claude/skills")
                self.assertEqual(meta["map"], "CLAUDE.md")

    def test_grok_folder_keeps_skills_dir_and_adds_adapter_skill(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo)
            out = os.path.join(d, "grok")
            write(out, ".git/HEAD", "keep me\n")
            write(out, "stale.md", "from a previous build\n")
            build.build_folder(repo, out, names=[], adapter="grok-bot")
            for want in ("skills/a/SKILL.md", "skills/getting-started/SKILL.md", "skills/INDEX.md", "install.sh",
                         "README.md", "setup/setup.sh", "setup/platform.md", "setup/version.json", "tools/x/README.md"):
                self.assertTrue(os.path.isfile(os.path.join(out, want)), want)
            for gone in ("CLAUDE.md", "setup.command", "setup/setup.ps1", "setup/tests", ".claude", "adapters", "stale.md", "build.py", "publish.md", "setup/publish.md"):
                self.assertFalse(os.path.exists(os.path.join(out, gone)), gone)
            self.assertTrue(os.path.isfile(os.path.join(out, ".git", "HEAD")), "the mirror's .git survives a rebuild")
            with open(os.path.join(out, "README.md"), encoding="utf-8") as fh:
                self.assertIn("grok readme", fh.read())
            with open(os.path.join(out, "setup", "platform.md"), encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "# grok bot platform\n")
            with open(os.path.join(out, "install.sh"), "rb") as fh:
                self.assertNotIn(b"\r\n", fh.read())
            with open(os.path.join(out, "setup", "adapter.json"), encoding="utf-8") as fh:
                meta = json.load(fh)
            self.assertEqual(meta["adapter"], "grok-bot")
            self.assertEqual(meta["map"], "MAP.md")
            self.assertEqual(meta["skills_dir"], "skills")

    def test_build_folder_refuses_repo_and_ancestors_and_inside_tree(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo)
            for bad in (repo, d, os.path.join(repo, "tools", "out"), os.path.join(repo, "dist")):
                with self.assertRaises(ValueError, msg=bad):
                    build.build_folder(repo, bad, names=[], adapter="grok-bot")
            self.assertTrue(os.path.isfile(os.path.join(repo, "skills", "a", "SKILL.md")), "a refused build deletes nothing")
            self.assertFalse(os.path.exists(os.path.join(repo, "tools", "out")))
            ok = os.path.join(repo, "dist", "x")
            build.build_folder(repo, ok, names=[], adapter="grok-bot")
            self.assertTrue(os.path.isfile(os.path.join(ok, "skills", "a", "SKILL.md")))

    def test_push_env_carries_token_as_header_not_url(self):
        token = "ghs_testtoken123"
        url = "https://github.com/six20am/grokbot-blueprint.git"
        argv, env = build.push_command(url, token)
        self.assertEqual(argv, ["git", "push", "--force", url, "HEAD:main"])
        self.assertFalse(any(token in a for a in argv), "the token is never in the argv")
        self.assertNotIn("@", argv[3])
        basic = base64.b64encode(("x-access-token:" + token).encode()).decode()
        self.assertEqual(env["GIT_CONFIG_COUNT"], "2")
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "http.https://github.com/.extraHeader")
        self.assertEqual(env["GIT_CONFIG_VALUE_0"], "Authorization: Basic " + basic)
        self.assertEqual(env["GIT_CONFIG_KEY_1"], "credential.helper")
        self.assertEqual(env["GIT_CONFIG_VALUE_1"], "", "credential helpers are switched off so the token is never stored")
        self.assertFalse(any(token in v for v in env.values()), "the raw token appears only inside the base64 header")
        self.assertEqual(build.push_command(url, None), (argv, {}), "no token: the user's own credentials, no overrides")

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
            self.assertNotIn("getting-started", text, "adapter-only skills are not in the core index")

    def test_refuses_on_leak(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"setup/SETUP.md": "call Zed first\n"})
            with self.assertRaises(build.LeakError) as cm:
                build.build(repo, os.path.join(d, "x.zip"), names=["zed"], top="T")
            self.assertIn("setup/SETUP.md", str(cm.exception).replace("\\", "/"))
            self.assertFalse(os.path.exists(os.path.join(d, "x.zip")))

    def test_refuses_leak_in_own_adapter_only(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo"); make_repo(repo, {"adapters/grok-bot/START-HERE.md": "call Zed first\n"})
            build.build(repo, os.path.join(d, "x.zip"), names=["zed"], adapter="claude-code", top="T")
            with self.assertRaises(build.LeakError) as cm:
                build.build_folder(repo, os.path.join(d, "grok"), names=["zed"], adapter="grok-bot")
            self.assertIn("adapters/grok-bot/START-HERE.md", str(cm.exception).replace("\\", "/"))

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


if __name__ == "__main__":
    unittest.main()
