# Platform: Grok Bot

| Fact | On this platform |
|---|---|
| The map | `MAP.md` in the Bot's folder. It says what each folder holds and where new files go. |
| The router | `ROUTER.md` in the Bot's folder. One row per kind of task, naming what to load and what to skip. |
| Section notes | A `NOTES.md` in each section's folder. It says what to read for which job in that section. |
| The skills folder | `skills/` in the Bot's folder, one folder per skill. Each one is also saved as a Bot skill, word for word. |
| Workspace root | `/workspace/<bot-name>/`. `/workspace` is shared by all of the owner's Bots, so nothing goes at its top level. |
| Shell | bash on the Bot's cloud computer, usually as root. |
| How the map loads | Nothing loads it on its own. A lasting memory rule tells the Bot to read the map and router before every task; it counts only once a new chat proves it. |
| Installer | `bash install.sh` from the Bot's folder. Run it again, then the `doctor` skill, after the cloud computer resets. |
| Updates | The `update` skill, then the `doctor` skill. |
| Cost view | None. The Bot has no usage view to read. |
| Shell output trimming | RTK, called as `rtk <command>`. There is no hook to install. |
