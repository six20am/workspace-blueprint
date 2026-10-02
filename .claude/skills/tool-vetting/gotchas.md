# Gotchas: tool-vetting
Last updated: 2026-09-28

## Known Failure Modes

- **Verdict from the pitch.** The answer maps each tool name to something we have and calls it
  covered, without opening the repo. Seen 2026-09-28: Browser Harness was called redundant, then
  "can't use your logins"; its README says it drives your real signed-in Chrome over CDP and
  writes its own Python helpers. Fix: no verdict before step 5 is done for that tool.
- **Caption spellings taken as names.** Auto-captions heard "Graphy" (Graphify-Labs/graphify,
  122k stars) and "Codebird" (getagentseal/codeburn, 11k). A first search found nothing and the
  tools nearly got dropped. Fix: a name that returns nothing is a spelling problem until
  variants are tried.
- **Grep false positives on short names.** "graphy" matched photography and typography files,
  which looked like a prior mention. Fix: grep the `owner/repo` form, or word-bound the name.
- **Install text that takes over routing.** Browser Harness's `install.md` tells the agent to
  register a skill triggered by "Always use browser-harness for any web interaction". Installed
  as written, it would take over from the Chrome extension, Scrapling and `agent-web-fetch`.
  Fix: step 5's routing question, every time; never paste a vendor setup prompt into a session.
- **Stale prior verdict repeated.** `docs/tooling-audit-evaluation.md` holds Caveman at "Trial,
  blocked"; the repo has grown from 94k to 108k stars and its licence reads NOASSERTION. Fix:
  step 3 re-tests the old reason, it does not quote it.
- **A single fact answered, the question left open.** "Is Playwright self-improving?" got a
  true answer that skipped whether the alternative was better. Fix: every row ends in a verdict
  on the job, not a fact about the tool.

## What Works Well

- The fixed question table in step 5 (install, connects, touches, writes, routing, Windows).
  Most decisive findings come from those six lines, not the feature list.

## Edge Cases

- A source that is one post naming one tool: answer in chat, skip the file.
- A "tool" that is a hosted service with no repo: say so; the verdict rests on its docs and
  terms, and "What was not verified" carries more weight.

## Changelog
- 2026-09-28: v1.0 initial build
