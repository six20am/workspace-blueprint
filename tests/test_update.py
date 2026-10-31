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
    """A raw repo tree as codeload delivers it: core skills, both adapter folders, core setup and tools."""
    put(base, "skills/web-read/SKILL.md", "web-read new\n")
    put(base, "skills/web-read/TEST.md", "web-read test\n")
    put(base, "skills/summarize/SKILL.md", "summarize template\n")
    put(base, "skills/INDEX.md", "# Skills index\n")
    put(base, "adapters/claude-code/CLAUDE.md", "template map\n")
    put(base, "adapters/claude-code/setup.cmd", "@echo off\n")
    put(base, "adapters/claude-code/platform.md", "# Platform: Claude Code\n")
    put(base, "adapters/claude-code/publish.md", "maintainer notes\n")
    put(base, "adapters/claude-code/skills/.keep", "")
    put(base, "adapters/grok-bot/README.md", "mirror front page\n")
    put(base, "adapters/grok-bot/install.sh", "#!/bin/sh\n")
    put(base, "adapters/grok-bot/platform.md", "# Platform: Grok Bot\n")
    put(base, "adapters/grok-bot/publish.md", "maintainer notes\n")
    put(base, "adapters/grok-bot/skills/getting-started/SKILL.md", "getting started\n")
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


GROK_CFG = {"adapter": "grok-bot", "skills_dir": "skills", "map": "MAP.md", "router": "ROUTER.md", "notes": "NOTES.md"}


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

    def test_grok_layout_syncs_into_skills(self):
        put(self.root, "setup/adapter.json", json.dumps(GROK_CFG))
        put(self.root, "skills/web-read/SKILL.md", "web-read old\n")
        put(self.root, "skills/web-read/old-helper.md", "stale\n")
        put(self.root, "skills/mine/SKILL.md", "owner built\n")
        adapter = update.read_adapter(self.root)
        self.assertEqual(adapter["adapter"], "grok-bot")
        (added, changed, removed), log = self.sync(adapter)
        r = self.root
        self.assertEqual(read(r, "skills/web-read/SKILL.md"), "web-read new\n")
        self.assertEqual(read(r, "skills/getting-started/SKILL.md"), "getting started\n")
        self.assertEqual(read(r, "skills/mine/SKILL.md"), "owner built\n")
        self.assertFalse(exists(r, "skills/web-read/old-helper.md"))
        self.assertEqual(removed, 1)
        self.assertEqual(read(r, "install.sh"), "#!/bin/sh\n")
        self.assertEqual(read(r, "README.md"), "mirror front page\n")
        self.assertEqual(read(r, "setup/platform.md"), "# Platform: Grok Bot\n")
        self.assertFalse(exists(r, "CLAUDE.md"))
        self.assertFalse(exists(r, "setup.cmd"))
        self.assertFalse(exists(r, ".claude"))
        self.assertFalse(exists(r, "publish.md"))
        self.assertFalse(exists(r, "setup/setup.ps1"))
        self.assertFalse(exists(r, "setup/lib"))
        self.assertFalse(exists(r, "setup/tests"))
        self.assertEqual(json.loads(read(r, "setup/adapter.json")), GROK_CFG)

    def test_never_list_follows_the_adapter(self):
        for rel in ("MAP.md", "ROUTER.md", "CLAUDE.md", "CONTEXT.md", "voice.md"):
            put(self.src, rel, "upstream " + rel + "\n")
        for rel in ("MAP.md", "ROUTER.md", "voice.md", "setup/adapter.json"):
            put(self.src, "adapters/grok-bot/" + rel, "upstream " + rel + "\n")
        for rel in ("CONTEXT.md", "voice.md", "setup/adapter.json"):
            put(self.src, "adapters/claude-code/" + rel, "upstream " + rel + "\n")
        put(self.src, "setup/adapter.json", "upstream adapter.json\n")

        grok = os.path.join(self.tmp, "grok")
        put(grok, "setup/adapter.json", json.dumps(GROK_CFG))
        put(grok, "ROUTER.md", "owner router\n")
        update.sync(self.src, grok, update.read_adapter(grok), os.path.join(grok, "bk"), [])
        self.assertFalse(exists(grok, "MAP.md"))
        self.assertEqual(read(grok, "ROUTER.md"), "owner router\n")
        self.assertFalse(exists(grok, "voice.md"))
        self.assertEqual(json.loads(read(grok, "setup/adapter.json")), GROK_CFG)
        self.assertIn("MAP.md", update.never_paths(GROK_CFG))
        self.assertIn("ROUTER.md", update.never_paths(GROK_CFG))

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


if __name__ == "__main__":
    unittest.main()
