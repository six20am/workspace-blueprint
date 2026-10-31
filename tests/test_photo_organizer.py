import datetime, os, shutil, struct, subprocess, sys, tempfile, time, unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "tools", "photo-organizer", "organize.py")


def tiff_with_date(date_text):
    """A little-endian TIFF block: IFD0 holds an Exif pointer; the Exif IFD holds DateTimeOriginal."""
    dt = date_text.encode() + b"\x00"                    # 20 bytes
    ifd0 = struct.pack("<H", 1) + struct.pack("<HHII", 0x8769, 4, 1, 26) + struct.pack("<I", 0)
    exif = struct.pack("<H", 1) + struct.pack("<HHII", 0x9003, 2, len(dt), 44) + struct.pack("<I", 0)
    return b"II*\x00" + struct.pack("<I", 8) + ifd0 + exif + dt


def jpeg_with_date(date_text):
    app1 = b"Exif\x00\x00" + tiff_with_date(date_text)
    return b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1 + b"\xff\xd9"


def heic_with_date(date_text):
    return b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00mif1heic" + b"\x00" * 16 + b"Exif\x00\x00" + tiff_with_date(date_text)


class PhotoOrganizerTests(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.root = os.path.join(self.base, "My Photos 2024")     # a folder name with spaces
        os.makedirs(os.path.join(self.root, "From Phone"))
        self.files = {}
        same = b"\xff\xd8" + b"same picture bytes" * 50 + b"\xff\xd9"
        self.put("beach.jpg", same, (2021, 7, 4))
        self.put("From Phone/beach copy.jpg", same, (2022, 1, 1))
        self.put("From Phone/IMG_0042.jpg", jpeg_with_date("2019:05:01 12:34:56"), (2023, 3, 3))
        self.put("moving shot.HEIC", heic_with_date("2020:12:25 08:00:00"), (2023, 3, 3))
        self.put("clip one.MOV", b"\x00\x00\x00\x08free" + b"no metadata here" * 10, (2018, 2, 14))

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def put(self, rel, data, ymd):
        p = os.path.join(self.root, *rel.split("/"))
        with open(p, "wb") as fh:
            fh.write(data)
        t = time.mktime(datetime.datetime(*ymd, 10, 15, 0).timetuple())
        os.utime(p, (t, t))
        self.files[rel] = data

    def run_tool(self, *args):
        r = subprocess.run([sys.executable, SCRIPT] + list(args), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout

    def snapshot(self):
        out = {}
        for dp, _, fs in os.walk(self.base):
            for fn in fs:
                p = os.path.join(dp, fn)
                if fn.endswith(".csv"):
                    continue
                with open(p, "rb") as fh:
                    out[os.path.relpath(p, self.root).replace(os.sep, "/")] = fh.read()
        return out

    def undo_csv(self):
        found = [f for f in os.listdir(self.base) if f.endswith(".csv")]
        self.assertEqual(len(found), 1, found)
        return os.path.join(self.base, found[0])

    def test_dry_run_moves_nothing_and_prints_plan(self):
        before = self.snapshot()
        out = self.run_tool("--root", self.root)
        self.assertEqual(self.snapshot(), before)
        self.assertIn("DRY RUN", out)
        self.assertIn("2019-05-01_123456.jpg", out)
        self.assertIn("--apply", out)
        self.assertEqual([f for f in os.listdir(self.base) if f.endswith(".csv")], [])

    def test_apply_renames_sorts_and_sets_duplicate_aside(self):
        self.run_tool("--root", self.root, "--apply")
        after = self.snapshot()
        self.assertEqual(after["2019/05/2019-05-01_123456.jpg"], self.files["From Phone/IMG_0042.jpg"])
        self.assertEqual(after["2020/12/2020-12-25_080000.HEIC"], self.files["moving shot.HEIC"])
        self.assertEqual(after["duplicates/From Phone/beach copy.jpg"], self.files["beach.jpg"])
        self.assertEqual(after["2021/07/2021-07-04_101500.jpg"], self.files["beach.jpg"])

    def test_mov_without_exif_uses_mtime_and_says_so(self):
        out = self.run_tool("--root", self.root)
        line = [l for l in out.splitlines() if "clip one.MOV" in l][0]
        self.assertIn("2018-02-14_101500.MOV", line)
        self.assertIn("file modified time", line)
        heic = [l for l in out.splitlines() if "moving shot.HEIC" in l][0]
        self.assertIn("photo EXIF", heic)
        self.run_tool("--root", self.root, "--apply")
        self.assertIn("2018/02/2018-02-14_101500.MOV", self.snapshot())

    def test_undo_restores_every_file_and_nothing_is_deleted(self):
        before = self.snapshot()
        self.run_tool("--root", self.root, "--apply")
        self.assertEqual(sorted(self.snapshot().values()), sorted(before.values()))
        preview = self.run_tool("--undo", self.undo_csv())
        self.assertIn("UNDO PREVIEW", preview)
        self.assertNotEqual(self.snapshot(), before)
        self.run_tool("--undo", self.undo_csv(), "--apply")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(os.path.exists(os.path.join(self.root, "duplicates")))

    def test_second_run_finds_nothing_to_do(self):
        self.run_tool("--root", self.root, "--apply")
        os.remove(self.undo_csv())
        out = self.run_tool("--root", self.root)
        self.assertIn("Nothing to do", out)

    def test_undo_refuses_paths_outside_the_folder(self):
        self.run_tool("--root", self.root, "--apply")
        log = self.undo_csv()
        with open(log, encoding="utf-8-sig") as fh:
            text = fh.read()
        outside = os.path.join(self.base, "elsewhere")
        with open(log, "w", encoding="utf-8-sig") as fh:
            fh.write(text.replace(os.path.join(self.root, "beach.jpg"), os.path.join(outside, "beach.jpg")))
        out = self.run_tool("--undo", log, "--apply")
        self.assertIn("outside the organized folder", out)
        self.assertFalse(os.path.exists(outside))


if __name__ == "__main__":
    unittest.main()
