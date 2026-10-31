import contextlib, io, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "document-builder"))
import build_doc

FIXTURE = """# Weekly notes

A short paragraph about the week.

| Item | Owner |
|---|---|
| Order paper | Sam |
| Fix printer | Lee |
"""


class CommandTests(unittest.TestCase):
    def test_pandoc_command_shapes(self):
        docx = build_doc.pandoc_command("in.md", "out.docx", "docx")
        self.assertEqual(docx[0], "pandoc")
        self.assertEqual(docx[1:4], ["in.md", "-o", "out.docx"])
        self.assertNotIn("-t", docx)
        pptx = build_doc.pandoc_command("in.md", "out.pptx", "pptx")
        self.assertIn("-t", pptx)
        self.assertEqual(pptx[pptx.index("-t") + 1], "pptx")
        html = build_doc.pandoc_command("in.md", "out.html", "html")
        self.assertIn("-s", html)
        ref = build_doc.pandoc_command("in.md", "out.docx", "docx", reference="ref.docx")
        self.assertEqual(ref[ref.index("--reference-doc") + 1], "ref.docx")

    def test_soffice_command_shape(self):
        cmd = build_doc.soffice_command("soffice", "a.docx", "outdir")
        self.assertEqual(cmd, ["soffice", "--headless", "--convert-to", "pdf", "--outdir", "outdir", "a.docx"])


class CsvTests(unittest.TestCase):
    def test_markdown_table_to_csv(self):
        md = "Intro\n\n| Name | Note |\n|---|:---:|\n| Ann | Hello, world |\n| Bo | plain |\n\nAfter"
        out = build_doc.markdown_table_to_csv(md)
        self.assertEqual(out.splitlines(), ["Name,Note", 'Ann,"Hello, world"', "Bo,plain"])

    def test_no_table_returns_empty(self):
        self.assertEqual(build_doc.markdown_table_to_csv("# Title\n\nJust text, no table."), "")


class PathTests(unittest.TestCase):
    def test_default_out_path(self):
        src = os.path.join("notes", "week.md")
        self.assertEqual(build_doc.default_out(src, "docx"), os.path.join("notes", "week.docx"))
        self.assertEqual(build_doc.default_out(src, "csv"), os.path.join("notes", "week.csv"))


class MissingProgramTests(unittest.TestCase):
    def test_missing_program_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "n.md")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(FIXTURE)
            original = build_doc.find_pandoc
            build_doc.find_pandoc = lambda: None
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = build_doc.main([src, "--to", "docx"])
            finally:
                build_doc.find_pandoc = original
        self.assertEqual(rc, 3)
        self.assertIn("Missing: pandoc. Run: python tools/doctor/doctor.py (python3 on Mac and Linux)", buf.getvalue())


class RealConversionTests(unittest.TestCase):
    def _fixture(self, tmp):
        src = os.path.join(tmp, "notes.md")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(FIXTURE)
        return src

    @unittest.skipUnless(build_doc.find_pandoc(), "pandoc not installed")
    def test_real_docx_when_pandoc_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fixture(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = build_doc.main([src, "--to", "docx"])
            out = os.path.join(tmp, "notes.docx")
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))
            self.assertGreater(os.path.getsize(out), 1024)

    @unittest.skipUnless(build_doc.find_pandoc() and build_doc.find_soffice(), "pandoc or LibreOffice not installed")
    def test_real_pdf_when_both_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._fixture(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = build_doc.main([src, "--to", "pdf"])
            out = os.path.join(tmp, "notes.pdf")
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))
            with open(out, "rb") as fh:
                self.assertEqual(fh.read(4), b"%PDF")


if __name__ == "__main__":
    unittest.main()
