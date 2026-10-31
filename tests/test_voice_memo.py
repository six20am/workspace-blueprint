import importlib.util
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("memo", os.path.join(HERE, "..", "tools", "voice-memo", "memo.py"))
memo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memo)

RAW = """ uh so the Hendersons want the fence done before the fourth,
 I need to call the lumber yard about the posts
[BLANK_AUDIO]

 and remind me we're out of the brown stain
"""


def fake_convert(src, wav):
    with open(wav, "wb") as fh:
        fh.write(b"RIFF")


def fake_transcribe(wav, cli, model):
    assert os.path.isfile(wav)
    return RAW


def fake_paths():
    return "whisper-cli", "model.bin"


class VoiceMemoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.src = os.path.join(self.tmp, "Truck Memo 3.m4a")
        with open(self.src, "wb") as fh:
            fh.write(b"audio")
        self.into = os.path.join(self.tmp, "voice-memos")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_clean_joins_lines_and_drops_noise_markers(self):
        self.assertEqual(memo.clean(RAW),
                         "uh so the Hendersons want the fence done before the fourth, I need to call the lumber yard about the posts\n\n"
                         "and remind me we're out of the brown stain")

    def test_slug_and_output_path(self):
        self.assertEqual(memo.slug("Truck Memo 3.m4a"), "truck-memo-3")
        self.assertEqual(memo.slug("###.mp3"), "memo")
        os.makedirs(self.into)
        first = memo.output_path(self.into, "2026-11-02", self.src)
        self.assertTrue(first.endswith("2026-11-02-truck-memo-3.md"))
        open(first, "w").close()
        self.assertTrue(memo.output_path(self.into, "2026-11-02", self.src).endswith("2026-11-02-truck-memo-3 (2).md"))

    def test_run_writes_memo_and_leaves_recording(self):
        code, msg = memo.run(self.src, self.into, day="2026-11-02", converter=fake_convert, transcriber=fake_transcribe, paths=fake_paths)
        self.assertEqual(code, 0, msg)
        out = os.path.join(self.into, "2026-11-02-truck-memo-3.md")
        self.assertIn(out, msg)
        self.assertIn("(30 words)", msg)
        text = open(out, encoding="utf-8").read()
        self.assertTrue(text.startswith("# Voice memo, 2026-11-02\n"))
        for h in ("## Transcript", "## Notes", "## To do", "- [ ]"):
            self.assertIn(h, text)
        self.assertIn("call the lumber yard about the posts", text)
        self.assertNotIn("BLANK_AUDIO", text)
        self.assertNotIn("—", text)
        self.assertTrue(os.path.isfile(self.src))
        self.assertEqual(open(self.src, "rb").read(), b"audio")

    def test_refuses_non_audio_and_missing_file(self):
        code, msg = memo.run(os.path.join(self.tmp, "notes.txt"), self.into, converter=fake_convert, transcriber=fake_transcribe, paths=fake_paths)
        self.assertEqual(code, 2)
        self.assertIn("No recording", msg)
        other = os.path.join(self.tmp, "notes.txt")
        open(other, "w").close()
        code, msg = memo.run(other, self.into, converter=fake_convert, transcriber=fake_transcribe, paths=fake_paths)
        self.assertEqual(code, 2)
        self.assertIn("does not look like a recording", msg)

    def test_missing_whisper_is_exit_3(self):
        code, msg = memo.run(self.src, self.into, converter=fake_convert, paths=lambda: (None, None))
        self.assertEqual(code, 3)
        self.assertEqual(msg, "Missing: whisper-cli. Run: python tools/doctor/doctor.py")
        code, msg = memo.run(self.src, self.into, converter=fake_convert, paths=lambda: ("cli", None))
        self.assertEqual(code, 3)
        self.assertIn("English model", msg)


if __name__ == "__main__":
    unittest.main()
