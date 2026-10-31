import contextlib, datetime, io, os, shutil, sys, tempfile, time, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "weekly-brief"))
import brief

TODAY = datetime.date(2026, 10, 31)


def stamp(day, hour=12):
    """Epoch seconds for local noon on a date."""
    return time.mktime(datetime.datetime(day.year, day.month, day.day, hour).timetuple())


class Workspace:
    def __init__(self):
        self.root = tempfile.mkdtemp()

    def file(self, rel, day, text="x"):
        p = os.path.join(self.root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.utime(p, (stamp(day), stamp(day)))
        return p

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def build():
    ws = Workspace()
    d = lambda n: TODAY - datetime.timedelta(days=n)
    ws.file("clients/acme/notes.md", d(1))
    ws.file("clients/acme/3-delivery/report.pdf", d(0))
    ws.file("money/Sent/invoice-12.pdf", d(3))
    ws.file("money/old-invoice.pdf", d(20))
    ws.file("setup/setup-report.md", d(2),
            "# Setup report\n\n## Needs attention\n\n- **Thing** (failed): nope\n\n"
            "## Sign in yourself\n\n- **GitHub CLI**: Run: gh auth login.\n"
            "- **NotebookLM**: Run: notebooklm login.\n\n## Already present\n\n- Git (base)\n")
    ws.file("setup/gap-log.md", d(1),
            "# Gap log\n\n`YYYY-MM-DD | what | built / found / by hand`\n\n"
            "2026-10-29 | turn a scan into text | found\n"
            "2026-10-10 | resize photos | built\n")
    ws.file("paperwork/dates.md", d(30),
            "# Dates\n\n2026-11-10 | water bill due | from money/water.pdf\n"
            "2026-12-25 | lease renewal | from home/lease.pdf\n"
            "2026-11-02 | car tag renewal | from car/tag.pdf\n")
    ws.file("waiting-on.md", d(30),
            "# Waiting on\n\n2026-10-19 | Harbor Plumbing | quote for the back bathroom | emailed\n"
            "2026-10-30 | Pat | the photos from Saturday | texted\n"
            "## Came back\n2026-10-10 | Harbor Plumbing | first visit date | emailed | came back 2026-10-12\n")
    ws.file("CONTEXT.md", d(30), "# Router\n\n| Task | Load |\n|---|---|\n| Weekly notes go in `notes/weekly` | here |\n")
    ws.file("tools/x/run.py", d(0))
    ws.file("_reference/a.md", d(0))
    ws.file("skills/s/SKILL.md", d(0))
    ws.file(".hidden/secret.md", d(0))
    ws.file("clients/.DS_Store", d(0))
    ws.file("clients/node_modules/pkg/index.js", d(0))
    ws.file("notes/weekly/weekly-brief-2026-10-24.md", d(0))
    return ws


class RepeatsTests(unittest.TestCase):
    def test_groups_by_shared_words_and_counts(self):
        saves = [
            "wrote Monday update email to clients",
            "renamed March invoices by date",
            "Monday client update email drafted",
            "sorted photos from the trip",
            "sent Monday update email again",
            "renamed April invoices by date",
            "drafted the monday client update",
        ]
        hits = brief.repeats(saves)
        self.assertEqual(hits, [(4, "wrote Monday update email to clients")])
        self.assertEqual(brief.repeats(saves, minimum=2)[1], (2, "renamed March invoices by date"))

    def test_short_or_filler_summaries_do_not_group(self):
        self.assertEqual(brief.repeats(["fixed it", "fixed it", "fixed it"]), [])

    def test_render_has_the_section(self):
        data = {"came_in": [], "went_out": [], "dates_due": [], "waiting": [], "gaps": [], "sign_ins": [],
                "repeats": ["4 times: wrote Monday update email"], "window": (datetime.date(2026, 10, 25), datetime.date(2026, 10, 31))}
        text = brief.render(data)
        self.assertIn("## Jobs that keep coming back (last 90 days)", text)
        self.assertIn("- 4 times: wrote Monday update email", text)


class WeeklyBriefTests(unittest.TestCase):
    def setUp(self):
        self.ws = build()
        self.data = brief.collect(self.ws.root, TODAY, 7)

    def tearDown(self):
        self.ws.close()

    def test_collect_window_and_exclusions(self):
        self.assertEqual(self.data["window"], (datetime.date(2026, 10, 25), TODAY))
        came = self.data["came_in"]
        self.assertEqual(came, ["clients/acme/3-delivery/report.pdf", "clients/acme/notes.md", "money/Sent/invoice-12.pdf"])

    def test_went_out_by_folder_name(self):
        self.assertEqual(self.data["went_out"], ["clients/acme/3-delivery/report.pdf", "money/Sent/invoice-12.pdf"])

    def test_dates_due_within_14_days(self):
        self.assertEqual(self.data["dates_due"], ["2026-11-02 | car tag renewal | from car/tag.pdf",
                                                  "2026-11-10 | water bill due | from money/water.pdf"])

    def test_waiting_on_overdue_only(self):
        self.assertEqual(self.data["waiting"], ["12 days: Harbor Plumbing, quote for the back bathroom (asked 2026-10-19, emailed)"])
        os.remove(os.path.join(self.ws.root, "waiting-on.md"))
        self.assertEqual(brief.collect(self.ws.root, TODAY, 7)["waiting"], [])

    def test_gaps_in_window_only(self):
        self.assertEqual(self.data["gaps"], ["2026-10-29 | turn a scan into text | found"])

    def test_sign_ins_parsed(self):
        self.assertEqual(self.data["sign_ins"], ["GitHub CLI: Run: gh auth login.", "NotebookLM: Run: notebooklm login."])

    def test_render_sections_and_nothing(self):
        text = brief.render(self.data)
        self.assertTrue(text.startswith("# Week of 2026-10-25 to 2026-10-31\n"))
        heads = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual(heads, ["## Came in", "## Went out", "## Dates coming up", "## Waiting on, overdue", "## Gaps logged",
                                 "## Jobs that keep coming back (last 90 days)", "## Sign-ins needed"])
        self.assertIn("- clients/acme/notes.md", text)
        self.assertIn("- 2026-11-10 | water bill due | from money/water.pdf", text)
        self.assertIn("- 12 days: Harbor Plumbing", text)
        empty = dict(self.data, came_in=[], went_out=[], dates_due=[], waiting=[], gaps=[], sign_ins=[])
        self.assertEqual(brief.render(empty).count("Nothing."), 7)

    def test_output_path_from_router_notes_line(self):
        out = brief.output_path(self.ws.root, TODAY, None)
        self.assertEqual(out, os.path.join(self.ws.root, "notes", "weekly", "weekly-brief-2026-10-31.md"))
        os.remove(os.path.join(self.ws.root, "CONTEXT.md"))
        self.assertEqual(brief.output_path(self.ws.root, TODAY, None), os.path.join(self.ws.root, "weekly-brief-2026-10-31.md"))
        self.assertEqual(brief.output_path(self.ws.root, TODAY, "x.md"), "x.md")
        saved, brief.ROOT = brief.ROOT, self.ws.root
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = brief.main(["--today", "2026-10-31"])
        finally:
            brief.ROOT = saved
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.ws.root, "weekly-brief-2026-10-31.md")))
        self.assertIn("weekly-brief-2026-10-31.md", out.getvalue())

    def test_cap_at_40_files(self):
        data = dict(self.data, came_in=["f%02d.md" % i for i in range(45)])
        text = brief.render(data)
        section = text.split("## Came in")[1].split("## Went out")[0]
        bullets = [l for l in section.splitlines() if l.startswith("- ")]
        self.assertEqual(len(bullets), 41)
        self.assertEqual(bullets[39], "- f39.md")
        self.assertEqual(bullets[40], "- and 5 more")


if __name__ == "__main__":
    unittest.main()
