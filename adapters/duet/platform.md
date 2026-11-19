# Platform: Claude Duet

| Fact | On this platform |
|---|---|
| The map | `MAP.md` at the top of the workspace. It says what each folder holds and where new files go. |
| The router | `ROUTER.md` at the top of the workspace. One row per kind of task, naming what to load. |
| Section notes | A `NOTES.md` in each section's folder. It says what to read for which job in that section. |
| The skills folder | `skills/` in the workspace holds the source. The ones the person uses every day are also saved as claude.ai skills from `skill-uploads/`, so every chat has them. |
| Workspace root | `/mnt/project-files/workspace`, the chat's own project folder. It lasts when the cloud computer is rebuilt. |
| Shell | bash, on a Linux cloud computer that is rebuilt every few hours. |
| How the map loads | Nothing loads it on its own. A standing rule in the chat's instructions or memory does it. The rule reads "Before any task, read MAP.md and ROUTER.md in /mnt/project-files/workspace, then load only the files the matching row names." |
| Installer | `bash setup/cloud-programs.sh`. Run it after each rebuild, or run `python3 tools/doctor/doctor.py`, which runs it. |
| Updates | `python3 tools/update/update.py`. It runs the doctor itself after the files land. |
| Cost view | None. |
| Shell output trimming | None. rtk is for Claude Code on a computer. |
| The web | The cloud computer's programs reach package stores and GitHub only. Duet's own web search and browser reach the rest, so save a page to a file and hand the file to a tool. |
