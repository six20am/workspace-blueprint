# undo

Version history for the workspace folder, so "undo what you just did" works.

```
python tools/undo/undo.py init            # start history: git init, .gitignore, first save "workspace built" (python3 on Mac and Linux)
python tools/undo/undo.py save "<what>"   # save everything that changed; prints the short id and message
python tools/undo/undo.py list            # the last ten saves: id, date, message
python tools/undo/undo.py undo            # step back one save and print the files that came back
```

`init` is safe to run again: it adds every `gitignore-template` line `.gitignore` lacks, sets a local
name and email only when git has none, and marks the history as its own. `save`, `list` and `undo` refuse
a history without that mark, and `init` refuses a cloned copy of a repository (one with a remote).

`undo` reverts the newest save with a new commit, so the history is kept and nothing is lost.
Run it again and it steps back one more save, never putting the last undo back. Unsaved changes
are saved first as "before undo". With no history it says to run `init`; with only the first save
it says "Nothing to undo yet." Both exit 1.

The template keeps secrets, setup reports and large media out of history. Git cannot ignore by size,
so list any file over about 50 MB in `.gitignore` by name.

It never pushes anywhere and never deletes the `.git` folder. Standard library only; needs git.
