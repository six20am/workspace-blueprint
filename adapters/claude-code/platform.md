# Platform: Claude Code

| Fact | On this platform |
|---|---|
| The map | `CLAUDE.md` at the top of the workspace. It says what each folder holds and where new files go. |
| The router | `CONTEXT.md` at the top of the workspace. One row per kind of task, naming what to load. |
| Section notes | A `CONTEXT.md` in each section's folder. It says what to read for which job in that section. |
| The skills folder | `.claude/skills/`, one folder per skill. Claude Code finds them there on its own. |
| Workspace root | The folder the zip made, wherever the person moved it. |
| Shell | PowerShell on Windows, bash on a Mac. |
| How the map loads | Claude Code reads `CLAUDE.md` automatically at the start of every chat. Nothing to save. |
| Installer | `setup.cmd` on Windows, `setup.command` on a Mac. Run the `doctor` skill to check or repair it later. |
| Updates | `update.cmd` on Windows, `update.command` on a Mac, or the `update` skill. |
| Cost view | `npx ccusage@latest` shows what the chats have used. |
| Shell output trimming | RTK. `rtk init -g --auto-patch` writes a hook into `~/.claude/settings.json` so long output is trimmed, saves the previous settings as `settings.json.bak`, and appends an `@RTK.md` line to `~/.claude/CLAUDE.md`. `rtk init -g --uninstall` reverses all of it. |
