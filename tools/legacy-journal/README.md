# legacy-journal

Helps the `legacy-journal` skill keep `legacy/`, a journal a parent keeps for their kids. The weekly brief uses the same letter list.

```
python tools/legacy-journal/legacy.py letters                         # python3 on Mac and Linux
python tools/legacy-journal/legacy.py age Ava 18
python tools/legacy-journal/legacy.py book --for Ava --title "For Ava, from Dad"
```

`letters` lists sealed letters by their file names, `letters/YYYY-MM-DD - for <name> - <occasion>.md`: open date reached, within 30 days, and later. It never reads a letter's text; `letters/given/` is left out. `age` reads `people.md` (`Name | YYYY-MM-DD`) and prints the date that child turns that age. `book` gathers the `.md` files under `entries/` and `video/` in date order, the ones whose `For:` line says `everyone` or that name, into `book/<name>-YYYY-MM-DD.md` and prints the path; `--year` keeps one year. Sealed letters never go in a book. Standard library only; the book file is the only thing it writes.
