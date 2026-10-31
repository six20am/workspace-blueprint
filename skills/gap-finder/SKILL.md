---
name: gap-finder
description: "Notices when a task has no tool or skill, says so, and offers to build a skill, find an outside tool, or do it by hand once. Fires on any task that matches no routing row and no skill. Also invoked by name."
---

# gap-finder

## When this fires

Before starting any task, check two places:

1. The routing tables: the top-level router file and the router file of the section the task belongs to.
2. The skills: the `description:` line of every `<skills folder>/*/SKILL.md`.

If neither names a tool, a skill or a process for this kind of task, this skill fires. If one does, use it and stop reading.

## What to say

One line, then wait:

> "I do not have a tool for that. I can **build** one (about ten minutes, and it is there next time), **find** one made by someone else, or just do it **by hand** this once. Which?"

Before you say that line, read `setup/gap-log.md`. If the same kind of task appears there three times as "by hand", say instead:

> "This is the third time you have asked for this. I should build a tool for it. Want me to?"

## The three paths

### Build

1. Run the interview in `build-interview.md`. Four questions, one at a time.
2. Write `<skills folder>/<name>/SKILL.md` with: frontmatter (`name`, `description` under 250 characters), when it fires, inputs needed, the steps, what it must never do, and where output goes.
3. Add one row to the router file for the section's "where tools plug in" table: the trigger and the skill name.
4. Run the task with the new skill. Show the result.
5. Log it: append `YYYY-MM-DD | <task in a few words> | built` to `setup/gap-log.md`.

### Find

1. Run the `tool-vetting` skill on whatever the person names, or on the top result of a web search for the job.
2. Nothing installs unless the verdict is **ADOPT**. Say the verdict and why in two lines.
3. On ADOPT: add an entry to `setup/tools.json` with its check and install commands for both platforms, install it, and write a wrapper skill as in step 2 of Build.
4. Log it: `... | found`.

### By hand

1. Do the task.
2. Log it: `... | by hand`.

## Never

- Build without the person saying yes.
- Install anything that `tool-vetting` did not mark ADOPT.
- Edit the map file, or any router file beyond adding the one routing row.
- Type a credential.
