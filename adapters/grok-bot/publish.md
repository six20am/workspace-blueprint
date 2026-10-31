# Publishing the template

## Where the files come from

The GitHub Action in `six20am/workspace-blueprint` runs `build.py --adapter grok-bot` and pushes the output to `six20am/grokbot-blueprint` using the `GROKBOT_PUSH_TOKEN` secret. Without the secret, run `python build.py --adapter grok-bot --push` locally.

## Build the source Bot

A template is made from a Bot, so the Bot is what gets published. Steps follow xAI's docs, read 2026-10-31.

1. Create a new Bot named Workspace Blueprint.
2. Tell it its job: "If you have no folder in `/workspace` with a `MAP.md` in it, run `getting-started` before doing anything else."
3. Have it save each folder in `skills/` as a skill, word for word, with the description from the file's top lines.

## Publish

Open the Bot's details, choose **Share**, then **Create a copy**. Choose **Publish** on the template card, then **Copy link**.

## Test before sharing the link

The docs say a public template link exposes "its identity, description, skills, and routines." They do not say whether files or memory come with it. Check on a clean account:

1. Every folder in `skills/` arrived word for word, counted against `skills/INDEX.md`.
2. The new Bot starts `getting-started` on its first message. If not, the fallback in `START-HERE.md` is the only way in.
3. The saved memory rule loads `MAP.md` and `ROUTER.md` in a new chat.
4. A second Bot on the same account builds its own folder and leaves the first one alone.

Record the date and results in the README status line. After a skill changes, update the core repo first, then the skill in the source Bot, then publish again.
