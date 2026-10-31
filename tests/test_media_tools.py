import contextlib, io, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL_DIR = os.path.join(HERE, "..", "tools", "media-tools")
sys.path.insert(0, TOOL_DIR)
import _common, audio, container, exif, transcode

CLIP = os.path.join("media", "clip.mp4")


class ExifTests(unittest.TestCase):
    def test_show(self):
        self.assertEqual(exif.command("show", "photo.jpg"), ["exiftool", "-s", "photo.jpg"])

    def test_strip_writes_clean_copy(self):
        argv = exif.command("strip", "photo.jpg")
        self.assertEqual(argv, ["exiftool", "-all=", "-o", "photo-clean.jpg", "photo.jpg"])
        self.assertNotIn("-overwrite_original", argv)


class AudioTests(unittest.TestCase):
    def test_trim_absolute_end(self):
        self.assertEqual(audio.command("trim", "talk.wav", start="5", end="20"),
                         ["sox", "talk.wav", "talk-trim.wav", "trim", "5", "=20"])

    def test_trim_needs_start(self):
        with self.assertRaises(ValueError):
            audio.command("trim", "talk.wav")

    def test_convert_changes_extension(self):
        self.assertEqual(audio.command("convert", "talk.wav", to="mp3"), ["sox", "talk.wav", "talk.mp3"])

    def test_convert_same_format_never_overwrites(self):
        argv = audio.command("convert", "talk.flac", to="flac")
        self.assertEqual(argv[2], "talk-converted.flac")

    def test_normalize(self):
        self.assertEqual(audio.command("normalize", "talk.mp3", to="wav"),
                         ["sox", "--norm", "talk.mp3", "talk-normalized.wav"])


class TranscodeTests(unittest.TestCase):
    def test_default_preset_and_name(self):
        self.assertEqual(transcode.command(CLIP),
                         ["HandBrakeCLI", "-i", CLIP, "-o", os.path.join("media", "clip-handbrake.mp4"),
                          "--preset", "Fast 1080p30"])

    def test_custom_preset_and_out(self):
        argv = transcode.command("in.mov", preset="Very Fast 720p30", out="small.mp4")
        self.assertEqual(argv[3:], ["-o", "small.mp4", "--preset", "Very Fast 720p30"])


class ContainerTests(unittest.TestCase):
    def test_info(self):
        self.assertEqual(container.command("info", "movie.mkv"), ["mkvmerge", "-i", "movie.mkv"])

    def test_mux_all_tracks(self):
        self.assertEqual(container.command("mux", "movie.mp4", audio="dub.m4a", subs="en.srt"),
                         ["mkvmerge", "-o", "movie.mkv", "movie.mp4", "dub.m4a", "en.srt"])

    def test_mux_mkv_input_gets_new_name(self):
        self.assertEqual(container.command("mux", "movie.mkv")[2], "movie-muxed.mkv")


class SafetyTests(unittest.TestCase):
    def test_missing_program_exits_3(self):
        for mod, args in ((exif, ["show", "a.jpg"]), (audio, ["normalize", "a.wav"]),
                          (transcode, ["a.mp4"]), (container, ["info", "a.mkv"])):
            saved = mod.find
            mod.find = lambda: None
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = mod.main(args)
            finally:
                mod.find = saved
            self.assertEqual(code, 3, mod.__name__)
            self.assertIn("Missing: %s. Run: python tools/doctor/doctor.py" % mod.PROGRAM, err.getvalue())

    def test_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "a.jpg")
            out = os.path.join(d, "a-clean.jpg")
            for p in (src, out):
                open(p, "w").close()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(_common.refuse_unsafe([src], out), 1)
                self.assertEqual(_common.refuse_unsafe([src], src), 1)
            self.assertIsNone(_common.refuse_unsafe([src], os.path.join(d, "new.jpg")))


if __name__ == "__main__":
    unittest.main()
