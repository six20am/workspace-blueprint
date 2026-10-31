import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "doctor"))
import doctor


SAMPLE = """# Setup report

Run: 2026-10-31 10:52 on HOST

## Needs attention

- **LibreOffice (documents, 300 MB and more)** (failed): winget exited 1603
- **Tesseract (reads text in images)** (failed): installed but not found on PATH
- **whisper.cpp English model** (manual): Download the model from the whisper.cpp page

## Sign in yourself

- **NotebookLM (Google Notebook)**: Run: notebooklm login. It opens a browser.
- **Agent Reach (X, Reddit, LinkedIn, YouTube transcripts)**: Run: agent-reach setup.
- **GitHub CLI**: Run: gh auth login.

## Installed now

- ImageMagick (images) (programs)
- ExifTool (photo and video details) (programs)
- jq (reads and edits JSON) (programs)
- Pandoc (document converting) (programs)

## Already present

""" + "".join("- Tool %d (base)\n" % i for i in range(20))

CLEAN = """# Doctor report

Run: 2026-10-31 10:52 on HOST

## Already present

- Git (base)
- Python (3.12 or newer) (base)
"""


class SummaryTests(unittest.TestCase):
    def test_summary_from_report(self):
        out = doctor.summarize(SAMPLE).splitlines()
        self.assertEqual(out[0], "Present: 20")
        self.assertEqual(out[1], "Installed now: 4 (ImageMagick (images), ExifTool (photo and video details), jq (reads and edits JSON), Pandoc (document converting))")
        self.assertEqual(out[2], "Failed: 2")
        self.assertEqual(out[3], "  - LibreOffice (documents, 300 MB and more): winget exited 1603")
        self.assertEqual(out[4], "  - Tesseract (reads text in images): installed but not found on PATH")
        self.assertEqual(out[5], "")
        self.assertEqual(out[6], "Sign in yourself:")
        self.assertEqual(out[7:], [
            "  - NotebookLM (Google Notebook): Run: notebooklm login. It opens a browser.",
            "  - Agent Reach (X, Reddit, LinkedIn, YouTube transcripts): Run: agent-reach setup.",
            "  - GitHub CLI: Run: gh auth login.",
        ])

    def test_summary_clean_report(self):
        out = doctor.summarize(CLEAN)
        self.assertEqual(out.splitlines(), ["Present: 2", "Installed now: 0", "Failed: 0, nothing to fix"])
        self.assertNotIn("Sign in yourself", out)


class CommandTests(unittest.TestCase):
    def test_command_for_platform(self):
        root = os.path.join("x", "ws")
        win = os.path.join(root, "setup", "setup.ps1")
        self.assertEqual(doctor.installer_command(root, "claude-code", False, True),
                         ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", win, "-Yes", "-NoLaunch"])
        self.assertEqual(doctor.installer_command(root, "claude-code", True, True),
                         ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", win, "-Yes", "-NoLaunch", "-DryRun"])
        runner = os.path.join(root, "setup", "runner.py")
        self.assertEqual(doctor.installer_command(root, "grok-bot", False, False),
                         [sys.executable, runner, "--doctor", "--no-launch", "--adapter", "grok-bot"])
        self.assertEqual(doctor.installer_command(root, "grok-bot", True, False),
                         [sys.executable, runner, "--doctor", "--no-launch", "--adapter", "grok-bot", "--dry-run"])

    def test_read_adapter_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(doctor.read_adapter(d), "claude-code")
            os.makedirs(os.path.join(d, "setup"))
            with open(os.path.join(d, "setup", "adapter.json"), "w", encoding="utf-8") as fh:
                fh.write('{"adapter": "grok-bot", "skills_dir": "skills"}')
            self.assertEqual(doctor.read_adapter(d), "grok-bot")


if __name__ == "__main__":
    unittest.main()
