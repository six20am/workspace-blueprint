import os, shutil, subprocess, sys, tempfile, unittest

UNDO_SRC = os.path.join(os.path.dirname(__file__), "..", "tools", "undo", "undo.py")
TEMPLATE_SRC = os.path.join(os.path.dirname(__file__), "..", "tools", "undo", "gitignore-template")


class UndoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        tool_dir = os.path.join(self.tmp, "tools", "undo")
        os.makedirs(tool_dir)
        self.undo_py = os.path.join(tool_dir, "undo.py")
        shutil.copy(UNDO_SRC, self.undo_py)
        if os.path.exists(TEMPLATE_SRC):
            shutil.copy(TEMPLATE_SRC, os.path.join(tool_dir, "gitignore-template"))
        self.cfg_dir = tempfile.mkdtemp()
        empty_cfg = os.path.join(self.cfg_dir, "gitconfig")
        open(empty_cfg, "w").close()
        self.env = dict(os.environ)
        self.env["GIT_CONFIG_GLOBAL"] = empty_cfg
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_DIR", "GIT_WORK_TREE"):
            self.env.pop(k, None)

    def tearDown(self):
        def onerr(func, path, exc):
            os.chmod(path, 0o700)
            func(path)
        shutil.rmtree(self.tmp, onerror=onerr)
        shutil.rmtree(self.cfg_dir, ignore_errors=True)

    def run_undo(self, *args):
        return subprocess.run([sys.executable, self.undo_py] + list(args), cwd=self.tmp,
                              env=self.env, capture_output=True, text=True)

    def git(self, *args):
        return subprocess.run(["git"] + list(args), cwd=self.tmp, env=self.env,
                              capture_output=True, text=True).stdout

    def write(self, name, text):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, name):
        with open(os.path.join(self.tmp, name), encoding="utf-8") as f:
            return f.read()

    def commit_count(self):
        return int(self.git("rev-list", "--count", "HEAD").strip())

    def test_init_creates_repo_and_gitignore(self):
        r = self.run_undo("init")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.tmp, ".git")))
        gi = self.read(".gitignore")
        for line in (".env", "*.pem", "*.key", "accounts.json", "setup/private-terms.txt", "*.mp4", "*.zip"):
            self.assertIn(line, gi.splitlines())
        self.assertEqual(self.commit_count(), 1)
        self.assertIn("workspace built", self.git("log", "-1", "--format=%s"))
        self.assertEqual(len(r.stdout.strip().splitlines()), 1)

    def test_save_then_undo_restores_file(self):
        self.run_undo("init")
        self.write("notes.md", "first\n")
        r = self.run_undo("save", "add notes")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("add notes", r.stdout)
        self.write("notes.md", "second\n")
        self.run_undo("save", "change notes")
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Undid: change notes", r.stdout)
        self.assertIn("notes.md", r.stdout)
        self.assertEqual(self.read("notes.md"), "first\n")
        # workspace built, add notes, change notes, and the revert on top
        self.assertEqual(self.commit_count(), 4)
        root = self.git("rev-list", "--max-parents=0", "HEAD").strip()
        self.assertEqual(self.git("rev-list", "--count", "HEAD", "^" + root).strip(), "3")
        log = self.git("log", "--format=%s")
        for msg in ("workspace built", "add notes", "change notes"):
            self.assertIn(msg, log)

    def test_save_with_nothing_changed(self):
        self.run_undo("init")
        r = self.run_undo("save", "nothing here")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nothing to save", r.stdout)

    def test_undo_without_history_is_refused(self):
        self.write("keep.md", "keep\n")
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 1)
        self.assertIn("No history yet. Run: python tools/undo/undo.py init", r.stdout + r.stderr)
        self.assertEqual(self.read("keep.md"), "keep\n")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, ".git")))

    def test_cloned_repo_is_refused(self):
        self.git("init", "-q")
        self.write("upstream.md", "from upstream\n")
        self.git("add", "-A")
        self.git("-c", "user.name=Up", "-c", "user.email=up@example.com", "commit", "-q", "-m", "upstream work")
        self.git("remote", "add", "origin", "https://example.com/blueprint.git")
        r = self.run_undo("init")
        self.assertEqual(r.returncode, 1)
        self.assertIn("This folder is a copy of a repository, not a workspace history.", r.stdout)
        self.assertEqual(self.git("config", "--local", "--get", "workspace.undo").strip(), "")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, ".gitignore")))
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 1)
        self.assertIn("This folder's history was not started by undo.", r.stdout)
        self.assertEqual(self.commit_count(), 1)

    def test_existing_gitignore_gains_missing_lines(self):
        self.write(".gitignore", "notes-private/\n.env\n")
        r = self.run_undo("init")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = self.read(".gitignore").splitlines()
        self.assertEqual(lines[0], "notes-private/")
        self.assertEqual(lines.count(".env"), 1)
        for line in ("*.pem", "accounts.json", "setup/setup-report.md", "*.mp4", "*.dmg"):
            self.assertIn(line, lines)
        self.assertEqual(self.git("config", "--local", "--get", "workspace.undo").strip(), "1")
        self.run_undo("init")
        self.assertEqual(self.read(".gitignore").splitlines(), lines)

    def test_undo_with_one_commit_is_refused(self):
        self.run_undo("init")
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Nothing to undo yet.", r.stdout + r.stderr)

    def test_second_undo_steps_back_again(self):
        self.run_undo("init")
        self.write("a.md", "one\n")
        self.run_undo("save", "add a")
        self.write("b.md", "two\n")
        self.run_undo("save", "add b")
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "b.md")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "a.md")))
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "b.md")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "a.md")))
        self.assertIn("Undid: add a", r.stdout)
        self.assertIn("a.md", r.stdout)
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Nothing to undo yet.", r.stdout)

    def test_undo_saves_dirty_tree_first(self):
        self.run_undo("init")
        self.write("a.md", "one\n")
        self.run_undo("save", "add a")
        self.write("draft.md", "unsaved work\n")
        r = self.run_undo("undo")
        self.assertEqual(r.returncode, 0, r.stderr)
        log = self.git("log", "--format=%s")
        self.assertIn("before undo", log)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "draft.md")))
        self.assertEqual(self.git("show", "HEAD~1:draft.md"), "unsaved work\n")
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "a.md")))

    def test_list_shows_recent_saves(self):
        self.run_undo("init")
        self.write("a.md", "one\n")
        self.run_undo("save", "add a")
        r = self.run_undo("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith("add a"))
        self.assertTrue(lines[1].endswith("workspace built"))


if __name__ == "__main__":
    unittest.main()
