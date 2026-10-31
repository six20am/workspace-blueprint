import contextlib, io, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "setup"))
import mac_runner


def tool(id, needs=(), install=("ok",), login=None):
    return {"id": id, "name": id, "area": "tools", "needs": list(needs),
            "install_mac": list(install), "check_mac": "check:" + id, "login": login}


class FakeMachine:
    def __init__(self):
        self.installed = {"check:git": True}
        self.ran = []

    def check(self, expr):
        return bool(self.installed.get(expr))

    def run(self, cmd):
        self.ran.append(cmd)
        if cmd == "boom":
            return 1
        if cmd.startswith("mark:"):
            self.installed["check:" + cmd[5:]] = True
        if cmd.startswith("markboom:"):
            self.installed["check:" + cmd[9:]] = True
            return 255
        return 0


class RunToolsTest(unittest.TestCase):
    def setUp(self):
        self.m = FakeMachine()

    def status(self, tools, **kw):
        with contextlib.redirect_stdout(io.StringIO()):
            res = mac_runner.run_tools(tools, self.m.run, self.m.check, **kw)
        return {r["id"]: r for r in res}

    def test_present_runs_nothing(self):
        s = self.status([tool("git")])
        self.assertEqual(s["git"]["status"], "present")
        self.assertEqual(self.m.ran, [])

    def test_install_then_recheck(self):
        s = self.status([tool("node", install=["mark:node"])])
        self.assertEqual(s["node"]["status"], "installed")

    def test_failed_command_keeps_going(self):
        s = self.status([tool("python", install=["boom"]), tool("node", install=["mark:node"])])
        self.assertEqual(s["python"]["status"], "failed")
        self.assertIn("exit code 1", s["python"]["detail"])
        self.assertEqual(s["node"]["status"], "installed")

    def test_skipped_when_need_failed(self):
        s = self.status([tool("python", install=["boom"]), tool("markitdown", needs=["python"], install=["mark:markitdown"])])
        self.assertEqual(s["markitdown"]["status"], "skipped")
        self.assertIn("python", s["markitdown"]["detail"])

    def test_no_mac_install_is_manual(self):
        t = {"id": "whisper", "name": "whisper", "area": "tools", "needs": [], "check": "x", "install": ["win only"]}
        s = self.status([t])
        self.assertEqual(s["whisper"]["status"], "manual")

    def test_noisy_exit_code_loses_to_passing_check(self):
        s = self.status([tool("noisy", install=["markboom:noisy"])])
        self.assertEqual(s["noisy"]["status"], "installed")
        self.assertIn("exit code 255", s["noisy"]["detail"])

    def test_install_ran_but_check_fails(self):
        s = self.status([tool("half", install=["ok"])])
        self.assertEqual(s["half"]["status"], "failed")
        self.assertIn("check still fails", s["half"]["detail"])

    def test_dry_run_plans_and_runs_nothing(self):
        s = self.status([tool("ffmpeg", install=["mark:ffmpeg"])], dry_run=True)
        self.assertEqual(s["ffmpeg"]["status"], "planned")
        self.assertEqual(self.m.ran, [])

    def test_second_run_sees_present(self):
        self.status([tool("node", install=["mark:node"])])
        self.m.ran.clear()
        s = self.status([tool("node", install=["mark:node"])])
        self.assertEqual(s["node"]["status"], "present")
        self.assertEqual(self.m.ran, [])


class SelectTest(unittest.TestCase):
    def test_only_pulls_the_tool_and_its_needs_in_order(self):
        tools = [tool("claude"), tool("plugin", needs=["claude"]), tool("node"), tool("mcp", needs=["node", "claude"])]
        self.assertEqual([t["id"] for t in mac_runner.select_tools(tools, "mcp")], ["node", "claude", "mcp"])
        self.assertEqual([t["id"] for t in mac_runner.select_tools(tools, None)], ["claude", "plugin", "node", "mcp"])
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            mac_runner.select_tools(tools, "nope")


class ReportTest(unittest.TestCase):
    def test_sections_match_the_windows_report(self):
        results = [
            {"id": "a", "name": "A", "area": "base", "status": "installed", "detail": "", "login": None},
            {"id": "b", "name": "B", "area": "base", "status": "present", "detail": "", "login": None},
            {"id": "c", "name": "C", "area": "tools", "status": "failed", "detail": "exit code 1", "login": None},
            {"id": "d", "name": "D", "area": "logins", "status": "manual", "detail": "", "login": "sign in"},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "setup-report.md")
            mac_runner.write_report(results, p, "mac")
            with open(p, encoding="utf-8") as fh:
                text = fh.read()
        for heading in ("# Setup report", "## Needs attention", "## Sign in yourself", "## Installed now", "## Already present"):
            self.assertIn(heading, text)
        self.assertIn("- **C** (failed): exit code 1", text)
        self.assertIn("- **D**: sign in", text)
        self.assertNotIn("\u2014", text)

    def test_report_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "setup-report.md")
            mac_runner.write_report([{"id": "a", "name": "A", "area": "base", "status": "failed", "detail": "x", "login": None}], p, "mac")
            mac_runner.write_report([], p, "mac")
            with open(p, encoding="utf-8") as fh:
                self.assertNotIn("Needs attention", fh.read())


class LoadTest(unittest.TestCase):
    def test_loads_real_manifest_and_root_with_space(self):
        here = os.path.dirname(__file__)
        tools = mac_runner.load_tools(os.path.join(here, "..", "setup", "tools.json"))
        self.assertGreaterEqual(len(tools), 20)
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, "My Stuff")
            os.makedirs(root)
            self.assertEqual(mac_runner.shell_quote(root), "'" + root + "'")


if __name__ == "__main__":
    unittest.main()
