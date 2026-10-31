---
name: backup
description: "Copies the whole workspace to a drive or synced folder the person names, and says on the weekly brief when it last ran. Undo protects against a mistake; this protects against a dead disk. Use when the person asks to back up, asks whether their files are safe, plugs in a drive for it, or when the brief shows the last backup is more than a week old."
---

# backup

Nothing to install. One command copies everything to a second place. It never deletes anything, on either side.

## Set up once

Ask one question: "Where should the copy live?" Two good answers:

- An external drive, plugged in for the run: `D:\backup` or `/Volumes/Backup`.
- A folder that another program already syncs to the cloud, on this computer: the cloud-drive folder in their home directory.

A folder inside the workspace is not a backup; the script refuses it. The first run names the place and remembers it in `setup/backup-log.md`; after that the command needs no argument.

```
python tools/backup/backup.py --to "D:\backup\my-workspace"   # python3 on Mac and Linux
```

## Each week

```
python tools/backup/backup.py
```

Run it after the brief, or whenever the brief says the last one is old. It copies files that are new or changed since the last run, leaves the rest, and prints one line: "412 files copied, 3,180 unchanged, to D:\backup\my-workspace." It adds the same line to `setup/backup-log.md`. If the drive is not there, it says so and stops; nothing is half-done.

The undo history (the `.git` folder) goes too, so a restored workspace keeps its past. `node_modules` and other installs are left out; setup puts those back.

## What to say

One line. "Backed up: 412 files copied to the drive, nothing else changed." On the brief: "Last backup was Tuesday, to the drive." Past seven days: "Last backup was 12 days ago. Plug the drive in and I will run it." Never ran: "No backup yet. Where should the copy live?"

## Getting a file back

Copy it from the backup folder by hand, or ask: "Bring back `clients/acme/notes.md` from the backup." That is one copy from the backup folder into the workspace, after saying which is newer. The backup side is never changed.

## Never

- Delete, move or overwrite anything in the backup folder except with a newer copy of the same file.
- Delete anything in the workspace, ever, as part of a backup.
- Back up to a folder inside the workspace, or to the workspace itself.
- Sign in to a cloud service, call a cloud API, or set up sync. A synced folder on this computer is fine; the syncing is the other program's job.
- Run it to a place the person did not name.
