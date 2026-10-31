# Publishing the Claude Code zip

## Every push

The GitHub Action in `six20am/workspace-blueprint` runs `build.py --adapter claude-code` on every push to `main`, zips the output, and uploads it to the release tagged `latest`. Nothing is built by hand.

## After each release

Check the zip a new owner would download:

1. Download the `latest` zip from the release page.
2. Extract it to an empty folder outside the repo.
3. Run the installer as a dry run from that folder: `powershell -ExecutionPolicy Bypass -File setup\setup.ps1 -DryRun` on Windows, or `bash setup/setup.sh --dry-run` on a Mac.
4. Confirm `.claude/skills/INDEX.md` and `adapter.json` are in the extracted folder.

If any check fails, fix the repo and push again. The old zip stays up until a new one passes.
