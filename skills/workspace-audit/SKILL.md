---
name: workspace-audit
description: "Use when checking whether a workspace's map, router and notes still match the folders and files on disk. Reports drift with a one-line fix for each and moves nothing without a yes."
---

# Workspace audit

Check that a workspace still holds together, and report what drifted. Run it on request, or when a task went to the wrong folder or the AI loaded the wrong files.

## Check the three layers

1. **Map.** Every top-level folder in the map file exists, and every folder on disk appears in the map. Name the orphans in both directions.
2. **Router.** Every path named in the router file and in each section notes file actually resolves. A row pointing at a deleted file is the most common rot.
3. **Workspace notes.** Each section has a notes file, and it names what to read for the work that actually happens in that folder.

## Check the drift

- Files sitting in a folder the map says they don't belong in.
- Folders created by hand that never got a row anywhere.
- Two files that look like the same document, where only one is current.
- A router row whose files have not changed in months, which usually means the row is dead.

## Report

A short table: what was checked, what failed, and the one-line fix for each. Offer to apply the fixes. Never move or delete a file without the owner saying yes to that specific move.
