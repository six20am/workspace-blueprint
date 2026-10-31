# update

Brings a workspace up to the latest Workspace Blueprint without touching the owner's files.

```
python tools/update/update.py               # check, then update if newer
python tools/update/update.py --check       # report only; exit 10 means an update exists
python tools/update/update.py --force       # update even when the version matches
python tools/update/update.py --no-install  # copy files only, skip the installer or doctor
```

**Which platform:** `setup/adapter.json`, written by the build, names the adapter. No file, or a name not listed below, means claude-code.

| Adapter | Skills folder | Map | Router |
|---|---|---|---|
| claude-code | `.claude/skills` | `CLAUDE.md` | `CONTEXT.md` |
| other (the neutral path, `ADAPT.md`) | `skills` | `MAP.md` | `ROUTER.md` (notes: `NOTES.md`) |

**What it copies:** the download is the raw repo, so the script maps it the way the build does. `skills/` goes to the skills folder. For claude-code, `adapters/claude-code/skills/` goes there too, `adapters/claude-code/platform.md` goes to `setup/platform.md`, and every other file directly in that folder goes to the top of the workspace, except `publish.md`. The neutral path has no adapter folder. The core `tools/`, `_reference/`, `ADAPT.md` and installer files under `setup/` are copied for both.

**What it never touches:** the adapter's map, router and notes files, `voice.md`, `setup/adapter.json` (it is created only when missing), `setup/setup-report.md`, `setup/gap-log.md`, and every folder the owner made.

**Backups and stale files:** a template file the owner edited is copied to `setup/update-backup/<date>/` before it is replaced. A file in a skill folder that also exists upstream, but that upstream no longer has, is backed up the same way and then removed. A skill folder the owner built is never touched.

**How it knows:** `setup/version.json` holds the commit the workspace was built from, plus `"layout": 2` once this script has run. Same commit and layout 2: nothing happens. No layout key means the old updater stamped the file without seeing the new layout, so the next run syncs everything once, even when the commit matches.

**After the copy:** claude-code runs the installer in no-launch mode, so a new tool in `setup/tools.json` gets installed. The neutral path runs the doctor instead (`tools/doctor/doctor.py`, falling back to `setup/runner.py --doctor --no-launch`), because a reset of the agent's computer can lose installed programs. Then it writes `setup/update-report.md`.

Standard library only. Needs github.com. The `update` skill is how the assistant runs it.
