# backup

Copies the workspace to a folder the person named, new and changed files only, and logs the run in `setup/backup-log.md`. Used by the `backup` skill; the weekly brief reads the log to say when it last ran.

```
python tools/backup/backup.py --to "D:\backup\my-workspace"   # the first time (python3 on Mac and Linux)
python tools/backup/backup.py                                 # after that: the last place used
python tools/backup/backup.py --dry-run
```

A file is copied when the backup has no copy, or its copy differs in size or is older. Nothing is deleted or replaced with something older, on either side. The undo history (`.git`) is copied; `node_modules`, `__pycache__`, `.venv` and the like are not. A target inside the workspace, one that holds the workspace, or one whose parent folder is missing (the drive is not in) is refused before anything is touched. Exit 1 lists files that could not be copied; the rest were. Standard library only.
