# local-events

Reads the public calendar feeds listed in `local-events/sources.txt` and prints what is on in the next N days as Markdown, by date. Used by the `local-events` skill.

```
python tools/local-events/events.py --days 14
```

Standard library only. One line per calendar in the sources file: the feed URL, a space, a short name. A name that starts with `page` marks a web page with no feed; it is listed at the end for reading by hand. A dead feed is reported at the bottom and never stops the list. Events are the organizer's claim; the link is there to check.
