# Test: getting-started

## The ask
"Hi, I just added you. Let's get started." (first message to a new Bot)

## The input
A Bot with no folder in `/workspace` that holds a `MAP.md`.

## Done looks like
The Bot asks the four questions one at a time, builds `/workspace/<bot-name>/` with `MAP.md`, `ROUTER.md`, a `NOTES.md` per section and `voice.md`, saves the memory rule and says so, runs `bash install.sh` and the `doctor` skill, then asks for a new chat and one real task to prove it.
