# update

Brings a workspace up to the latest Workspace Blueprint without touching the owner's files.

```
python tools/update/update.py            # check, then update if newer
python tools/update/update.py --check    # report only; exit 10 means an update exists
python tools/update/update.py --force    # update even when the version matches
```

Double-click `update.cmd` (Windows) or `update.command` (Mac) does the same thing.

**What it touches:** only the paths the template owns, listed in `OWNED` at the top of the
script: `.claude/skills/`, `tools/`, `_reference/`, the installer under `setup/`, `tools.json`
and the front-page files. A skill the owner built is never removed, because it does not exist
upstream. A template file the owner edited is copied to `setup/update-backup/<date>/` before
it is replaced.

**What it never touches:** `CLAUDE.md`, every `CONTEXT.md`, `voice.md`, the owner's folders,
`setup/setup-report.md`, `setup/gap-log.md`.

**How it knows:** `setup/version.json` holds the commit the workspace was built from. The
script asks GitHub for the latest commit on `main`. Same commit, nothing happens.

**After the copy:** it runs the installer with the no-launch flag, so any tool added to
`setup/tools.json` gets installed and everything already present is skipped. Then it writes
`setup/update-report.md`.

Standard library only. Needs github.com. The `update` skill in `.claude/skills/update/` is
how Claude runs it.
