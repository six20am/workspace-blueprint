# Test: local-events

## The ask
"What's going on in town over the next two weeks?"

## The input
The town and state. Nothing else; the skill finds the public calendars.

## Done looks like
A `local-events/sources.txt` with at least four public feeds named (city, library, parks, one more), shown to the person for additions. Then `python tools/local-events/events.py --days 14` run and its output saved as `local-events/<date>-this-fortnight.md`: events by date with time, title, venue where given, the calendar it came from, and a link. No ticket bought, no sign-up, no event from behind a login, no event the feeds did not carry.
