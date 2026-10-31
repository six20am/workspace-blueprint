import datetime as dt
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("events", os.path.join(HERE, "..", "tools", "local-events", "events.py"))
events = importlib.util.module_from_spec(spec)
spec.loader.exec_module(events)

ICS = """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART:20260205T190000
SUMMARY:Town council meeting
LOCATION:City Hall\\, Room 2
URL:https://example.org/council
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260207
SUMMARY:Farmers market
END:VEVENT
BEGIN:VEVENT
DTSTART:20260301T100000
SUMMARY:Too far out
END:VEVENT
BEGIN:VEVENT
DTSTART:20260205T190000
SUMMARY:Town council meeting
END:VEVENT
END:VCALENDAR
"""


class LocalEventsTest(unittest.TestCase):
    def test_collect_windows_dedupes_and_sorts(self):
        feeds = [("https://a.example/cal.ics", "City"), ("https://b.example/cal.ics", "Library")]
        found, errors = events.collect(feeds, 14, today=dt.datetime(2026, 2, 1),
                                       fetcher=lambda url: ICS if "a.example" in url else (_ for _ in ()).throw(OSError("down")))
        self.assertEqual([e["title"] for e in found], ["Town council meeting", "Farmers market"])
        self.assertEqual(found[0]["where"], "City Hall, Room 2")
        self.assertTrue(found[1]["all_day"])
        self.assertEqual(len(errors), 1)
        self.assertIn("Library", errors[0])

    def test_render_shape(self):
        found, errors = events.collect([("x", "City")], 14, today=dt.datetime(2026, 2, 1), fetcher=lambda u: ICS)
        text = events.render(found, errors, [("https://c.example/events", "Chamber")], 14, today=dt.datetime(2026, 2, 1))
        self.assertIn("## Thursday February 05", text)
        self.assertIn("- 7:00 PM: Town council meeting at City Hall, Room 2 (City) <https://example.org/council>", text)
        self.assertIn("- all day: Farmers market (City)", text)
        self.assertIn("## Check by hand (no feed)", text)
        self.assertNotIn("Too far out", text)
        self.assertNotIn("—", text)

    def test_read_sources(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write("# comment\nhttps://a.example/cal.ics City Hall\nhttps://c.example/events page: Chamber\n")
            path = fh.name
        try:
            feeds, pages = events.read_sources(path)
        finally:
            os.unlink(path)
        self.assertEqual(feeds, [("https://a.example/cal.ics", "City Hall")])
        self.assertEqual(pages, [("https://c.example/events", "Chamber")])


if __name__ == "__main__":
    unittest.main()
