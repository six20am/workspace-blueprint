# Test: backup

## The ask
"Back everything up to the drive I just plugged in."

## The input
The drive letter or folder the person names. Nothing else.

## Done looks like
First run: `python tools/backup/backup.py --to <folder>` with the folder the person named, one line back with the counts and the place, and a matching line in `setup/backup-log.md`. Later runs: the same command with no argument, copying only what changed. The weekly brief says when it last ran and to where. Nothing deleted on either side; a folder inside the workspace refused; a missing drive reported and the run stopped.
