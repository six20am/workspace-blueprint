---
name: update
description: "Brings the workspace up to the latest Workspace Blueprint: new and fixed skills, new tools, the installer. Never touches the owner's files. Use when the person says update, asks what is new, or when setup/version.json is more than 30 days old."
---

# update

Run this when the person asks to update, asks what is new, or when `setup/version.json` says the workspace was built or last updated more than 30 days ago. In that last case, offer once at the start of the session; do not run it unasked.

## Steps

1. Check first, change nothing:
   ```
   python tools/update/update.py --check   # python3 on Mac and Linux
   ```
   Exit 0 means up to date; say so and stop. Exit 10 means an update exists. Exit 2 means github.com could not be reached; say so and stop.
2. Tell the person in one line what will happen: skills and tools get replaced, their own files are not touched, anything they edited in a template file is backed up first.
3. Run it:
   ```
   python tools/update/update.py
   ```
   It downloads the latest version, copies the template-owned paths, then runs the installer in no-launch mode so new tools get installed. This can take a few minutes if a tool is new.
   On the neutral path (`ADAPT.md`) the same command runs, then `doctor`, because a reset of the agent's computer can lose installed programs.
4. Read `setup/update-report.md`. Say what was added, what changed, and whether the installer finished clean. If a file they had edited was replaced, name it and where the backup is.
5. If `setup/tools.json` gained a tool that needs a sign-in, `setup/setup-report.md` lists it. Pass that on.

## Never

- Run the update without saying first what it touches.
- Edit `tools/update/update.py` to add or remove paths. That list is the template's contract with the owner.
- Touch the map file, any router file or `voice.md` as part of an update. If a new skill needs a routing row, say so and add the one row with the person's yes.
