import json, os, shutil, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "update"))
import update


def put(base, rel, text):
    p = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def read(base, rel):
    with open(os.path.join(base, *rel.split("/")), encoding="utf-8") as fh:
        return fh.read()


def exists(base, rel):
    return os.path.exists(os.path.join(base, *rel.split("/")))


def make_upstream(base):
    """A raw repo tree as codeload delivers it: core skills, the claude-code adapter folder, ADAPT.md, core setup and tools."""
    put(base, "skills/web-read/SKILL.md", "web-read new\n")
    put(base, "skills/web-read/TEST.md", "web-read test\n")
    put(base, "skills/summarize/SKILL.md", "summarize template\n")
    put(base, "skills/INDEX.md", "# Skills index\n")
    put(base, "adapters/claude-code/CLAUDE.md", "template map\n")
    put(base, "adapters/claude-code/setup.cmd", "@echo off\n")
    put(base, "adapters/claude-code/platform.md", "# Platform: Claude Code\n")
    put(base, "adapters/claude-code/publish.md", "maintainer notes\n")
    put(base, "adapters/claude-code/skills/.keep", "")
    put(base, "ADAPT.md", "# Adapt\n")
    put(base, "README.md", "repo front page\n")
    put(base, "setup/tools.json", '{"tools": ["new"]}\n')
    put(base, "setup/setup.ps1", "# windows installer\n")
    put(base, "setup/lib/planner.ps1", "# planner\n")
    put(base, "setup/tests/run-tests.ps1", "# tests\n")
    put(base, "tools/update/update.py", "# updater\n")


def make_old_install(root):
    """A claude-code install from before the adapters existed: no setup/adapter.json."""
    put(root, ".claude/skills/web-read/SKILL.md", "web-read old\n")
    put(root, ".claude/skills/web-read/SKILL.md.orig-zh.bak", "stale backup\n")
    put(root, ".claude/skills/mine/SKILL.md", "owner built\n")
    put(root, ".claude/skills/summarize/SKILL.md", "owner summarize\n")
    put(root, "CLAUDE.md", "owner map\n")
    put(root, "setup/tools.json", '{"tools": []}\n')
    put(root, "voice.md", "owner voice\n")


OTHER_CFG = {"adapter": "other", "skills_dir": "skills", "map": "MAP.md", "router": "ROUTER.md", "notes": "NOTES.md"}


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wb-test-update-")
        self.src = os.path.join(self.tmp, "upstream")
        self.root = os.path.join(self.tmp, "owner")
        self.backup = os.path.join(self.root, "setup", "update-backup", "today")
        os.makedirs(self.root)
        make_upstream(self.src)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sync(self, adapter):
        log = []
        counts = update.sync(self.src, self.root, adapter, self.backup, log)
        return counts, log

    def test_old_layout_without_adapter_json(self):
        make_old_install(self.root)
        adapter = update.read_adapter(self.root)
        self.assertEqual(adapter["adapter"], "claude-code")
        self.assertEqual(adapter["skills_dir"], ".claude/skills")
        (added, changed, removed), log = self.sync(adapter)
        r = self.root
        self.assertEqual(read(r, ".claude/skills/web-read/SKILL.md"), "web-read new\n")
        self.assertEqual(read(r, ".claude/skills/web-read/TEST.md"), "web-read test\n")
        self.assertTrue(exists(r, ".claude/skills/INDEX.md"))
        self.assertFalse(exists(r, ".claude/skills/web-read/SKILL.md.orig-zh.bak"))
        self.assertEqual(read(self.backup, ".claude/skills/web-read/SKILL.md.orig-zh.bak"), "stale backup\n")
        self.assertIn("removed  .claude/skills/web-read/SKILL.md.orig-zh.bak", log)
        self.assertEqual(removed, 1)
        self.assertEqual(read(r, ".claude/skills/mine/SKILL.md"), "owner built\n")
        self.assertEqual(read(r, "CLAUDE.md"), "owner map\n")
        self.assertEqual(read(r, "voice.md"), "owner voice\n")
        self.assertEqual(read(r, "setup/platform.md"), "# Platform: Claude Code\n")
        self.assertEqual(read(r, "setup.cmd"), "@echo off\n")
        self.assertEqual(read(r, "setup/tools.json"), '{"tools": ["new"]}\n')
        self.assertTrue(exists(r, "setup/setup.ps1"))
        self.assertTrue(exists(r, "setup/lib/planner.ps1"))
        self.assertFalse(exists(r, "publish.md"))
        self.assertFalse(exists(r, "README.md"))
        self.assertFalse(exists(r, "install.sh"))
        self.assertFalse(exists(r, ".claude/skills/getting-started"))
        self.assertFalse(exists(r, "setup/adapter.json"))
        self.assertGreater(added, 0)
        self.assertGreater(changed, 0)

    def test_owner_skill_same_name_is_backed_up(self):
        make_old_install(self.root)
        _, log = self.sync(update.read_adapter(self.root))
        self.assertEqual(read(self.root, ".claude/skills/summarize/SKILL.md"), "summarize template\n")
        self.assertEqual(read(self.backup, ".claude/skills/summarize/SKILL.md"), "owner summarize\n")
        self.assertIn("changed  .claude/skills/summarize/SKILL.md", log)

    def test_other_layout_syncs_into_skills(self):
        put(self.root, "setup/adapter.json", json.dumps(OTHER_CFG))
        put(self.root, "skills/web-read/SKILL.md", "web-read old\n")
        put(self.root, "skills/web-read/old-helper.md", "stale\n")
        put(self.root, "skills/mine/SKILL.md", "owner built\n")
        adapter = update.read_adapter(self.root)
        self.assertEqual(adapter["adapter"], "other")
        (added, changed, removed), log = self.sync(adapter)
        r = self.root
        self.assertEqual(read(r, "skills/web-read/SKILL.md"), "web-read new\n")
        self.assertEqual(read(r, "skills/INDEX.md"), "# Skills index\n")
        self.assertEqual(read(r, "skills/mine/SKILL.md"), "owner built\n")
        self.assertFalse(exists(r, "skills/web-read/old-helper.md"))
        self.assertEqual(removed, 1)
        self.assertEqual(read(r, "ADAPT.md"), "# Adapt\n", "ADAPT.md lands at the root")
        self.assertEqual(read(r, "setup/tools.json"), '{"tools": ["new"]}\n')
        self.assertEqual(read(r, "tools/update/update.py"), "# updater\n")
        self.assertFalse(exists(r, "CLAUDE.md"))
        self.assertFalse(exists(r, "setup.cmd"))
        self.assertFalse(exists(r, ".claude"))
        self.assertFalse(exists(r, "publish.md"))
        self.assertFalse(exists(r, "README.md"), "the repo readme never ships")
        self.assertFalse(exists(r, "setup/platform.md"), "the neutral path has no adapter folder")
        self.assertEqual(json.loads(read(r, "setup/adapter.json")), OTHER_CFG)
        self.assertEqual(update.owned_pairs(adapter, self.src)[:2], [("skills", "skills"), ("ADAPT.md", "ADAPT.md")])
        self.assertFalse(any(src.startswith("adapters/") for src, _ in update.owned_pairs(adapter, self.src)))

    def test_never_list_follows_the_adapter(self):
        for rel in ("MAP.md", "ROUTER.md", "CLAUDE.md", "CONTEXT.md", "voice.md"):
            put(self.src, rel, "upstream " + rel + "\n")
        for rel in ("MAP.md", "ROUTER.md", "voice.md", "setup/adapter.json"):
            put(self.src, "adapters/other/" + rel, "upstream " + rel + "\n")
        for rel in ("CONTEXT.md", "voice.md", "setup/adapter.json"):
            put(self.src, "adapters/claude-code/" + rel, "upstream " + rel + "\n")
        put(self.src, "setup/adapter.json", "upstream adapter.json\n")

        other = os.path.join(self.tmp, "other")
        put(other, "setup/adapter.json", json.dumps(OTHER_CFG))
        put(other, "ROUTER.md", "owner router\n")
        update.sync(self.src, other, update.read_adapter(other), os.path.join(other, "bk"), [])
        self.assertFalse(exists(other, "MAP.md"))
        self.assertEqual(read(other, "ROUTER.md"), "owner router\n")
        self.assertFalse(exists(other, "voice.md"))
        self.assertEqual(json.loads(read(other, "setup/adapter.json")), OTHER_CFG)
        for rel in ("MAP.md", "ROUTER.md", "NOTES.md", "voice.md", "setup/adapter.json", "setup/setup-report.md", "setup/update-report.md"):
            self.assertIn(rel, update.never_paths(OTHER_CFG))

        claude = os.path.join(self.tmp, "claude")
        os.makedirs(claude)
        adapter = update.read_adapter(claude)
        self.assertNotIn("MAP.md", update.never_paths(adapter))
        update.sync(self.src, claude, adapter, os.path.join(claude, "bk"), [])
        self.assertFalse(exists(claude, "CLAUDE.md"))
        self.assertFalse(exists(claude, "CONTEXT.md"))
        self.assertFalse(exists(claude, "voice.md"))
        self.assertFalse(exists(claude, "setup/adapter.json"))
        self.assertTrue(exists(claude, "setup.cmd"))

    def test_unknown_adapter_name_falls_back_to_claude_code(self):
        put(self.root, "setup/adapter.json", json.dumps({"adapter": "../..", "skills_dir": "skills", "map": "MAP.md"}))
        adapter = update.read_adapter(self.root)
        self.assertEqual(adapter, update.ADAPTERS["claude-code"])
        self.assertEqual(update.owned_pairs(adapter, self.src)[0], ("skills", ".claude/skills"))

    def test_old_install_with_stamped_version_still_migrates(self):
        make_old_install(self.root)
        remote = "a" * 40
        # the old updater copied tools/ and stamped the remote commit, but never saw the new layout
        put(self.root, "setup/version.json", json.dumps({"commit": remote, "date": "2026-10-31", "updated": "2026-10-31"}))
        local = json.loads(read(self.root, "setup/version.json"))
        self.assertEqual(update.needs_update(local, remote, False), "migrate")
        log = []
        adapter, (added, changed, removed) = update.apply_update(self.src, self.root, self.backup, log, remote, "2026-10-31")
        self.assertEqual(adapter["adapter"], "claude-code")
        self.assertEqual(read(self.root, ".claude/skills/web-read/SKILL.md"), "web-read new\n")
        self.assertEqual(removed, 1)
        self.assertEqual(json.loads(read(self.root, "setup/adapter.json")), update.ADAPTERS["claude-code"])
        version = json.loads(read(self.root, "setup/version.json"))
        self.assertEqual(version["layout"], 2)
        self.assertEqual(version["commit"], remote)
        self.assertEqual(update.needs_update(version, remote, False), "up-to-date")

    def test_layout_2_and_matching_commit_is_up_to_date(self):
        remote = "b" * 40
        local = {"commit": remote, "date": "2026-10-31", "layout": 2}
        self.assertEqual(update.needs_update(local, remote, False), "up-to-date")
        self.assertEqual(update.needs_update(local, remote, True), "update")
        self.assertEqual(update.needs_update(local, "c" * 40, False), "update")
        self.assertEqual(update.needs_update({"commit": remote, "layout": 1}, remote, False), "migrate")
        self.assertEqual(update.needs_update({"commit": None, "date": None}, remote, False), "migrate")

    def test_existing_adapter_json_is_never_overwritten(self):
        put(self.root, "setup/adapter.json", json.dumps(OTHER_CFG))
        update.apply_update(self.src, self.root, self.backup, [], "d" * 40, "2026-10-31")
        self.assertEqual(json.loads(read(self.root, "setup/adapter.json")), OTHER_CFG)

    def test_other_runs_the_doctor_then_the_runner(self):
        put(self.root, "tools/doctor/doctor.py", "# doctor\n")
        put(self.root, "setup/runner.py", "# runner\n")
        self.assertEqual(update.doctor_command(self.root)[1:], [os.path.join(self.root, "tools", "doctor", "doctor.py")])
        os.remove(os.path.join(self.root, "tools", "doctor", "doctor.py"))
        self.assertEqual(update.doctor_command(self.root)[1:],
                         [os.path.join(self.root, "setup", "runner.py"), "--doctor", "--no-launch"])


if __name__ == "__main__":
    unittest.main()
