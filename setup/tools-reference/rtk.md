# rtk

Shortens the output of common commands (git, test runners, file listings) so an AI assistant reads less and spends fewer tokens.

```
rtk git status
rtk gain
```

**Gotcha:** The hook entry (`rtk-hook`) runs `rtk init -g --auto-patch` (without the flag a non-interactive run skips the settings file), which adds rtk to the Claude Code settings file (the old one is kept as `settings.json.bak`) and appends an `@RTK.md` line to the global `CLAUDE.md`; `rtk init -g --uninstall` reverses both. Its check reads that settings file for the word rtk, so a settings file that mentions rtk for any other reason also counts as installed.
