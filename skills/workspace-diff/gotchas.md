# workspace-diff: gotchas

Failure modes observed in real runs. Every item here cost something.

---

## NotebookLM CLI

**`source list` rejects partial notebook IDs.** Most `notebooklm` subcommands accept a 6-char
prefix. `source list --notebook <partial>` does not: it exits non-zero with no JSON, and a
downstream `json.load` dies with `Expecting value: line 1 column 1`. Always pass the full
UUID to `source list`. Observed 2026-07-25.

**Long `ask` output gets truncated by `tail`.** Piping a long extraction through `tail -120`
silently drops the first sections. The pilot lost groups A and B this way and needed a second
call. Redirect the whole answer to a file (`> out.md`) and read it, or request groups
explicitly in batches.

**`ask` continues the previous conversation.** A second `ask` against the same notebook
resumes the prior thread ("Resumed conversation: …"), so it may answer in the context of the
earlier question rather than fresh. For a clean second pass, state the scope explicitly
("ONLY output these two groups, nothing else") rather than assuming a blank slate.

**Sources in `preparing` produce false GAPs.** A claim that exists only in a still-indexing
source reads as absent from the notebook, and the run then reports the workspace as lacking
something the source never got to say. Gate on every source being `ready` before extracting.

**NotebookLM ends answers with an upsell.** ("Would you like me to compile these into a
PDF?") Strip it: it is not source content and must never reach the extract.

---

## The comparison itself

**`ALREADY` from memory is the primary failure mode.** It is genuinely tempting to verdict
"we already do that" from familiarity with the workspace. Every such verdict that is wrong
converts a real gap into a silent pass. Open the file. If the cited file does not contain the
practice, the verdict is `GAP` and the citation was a hallucination.

**Grep proves absence better than reading proves it.** For a `GAP`, a negative
`grep -rl` across the plausible directories is stronger evidence than "I didn't see it."
The pilot's headline finding (no `PROGRESS.md` pattern) rests on a zero-hit grep across
every folder that holds rules: the map file, the router files and the skills folder.

**Zero CONFLICT and zero AHEAD means the run failed.** Not "the source agreed with us" , 
it means the pass imported instead of comparing. Ask explicitly, per claim: *does anything
here already contradict this, and was that deliberate?*

**Watch for contradictions the source exposes inside the workspace.** The pilot's most
valuable finding was not a gap at all: `naming-rules.md` L16 bans `-final`/`-v2` suffixes
absolutely while L36–37 recommends that exact progression: a contradiction introduced by the
*previous* ingestion of the same source family. A claim can be `CONFLICT` against one part of
a file and `ALREADY` against another. When that happens, the finding is the contradiction.

**Scope clashes look like conflicts but aren't.** The source says "borrow from existing
repos"; the workspace says "never read other client builds to scaffold." Those target
different things (external OSS vs our own client work). Verdict `N/A`, and say why: do not
record a conflict that isn't one.

**Not every claim has a workspace surface.** Mobile voice-input technique, Remote Control
power settings, session naming: these are operator habits or product features with nothing
to wire. `N/A` with one line is the correct output, not a stretch to make them actionable.

---

## Wiring

**Cite the extract; never restate it.** No rule in two places. A wire that
copies the extract's wording creates a second source of truth that will drift.

**Check `INTEGRATION-LOG.md` before writing anything.** If the source family was integrated
before, new findings extend the existing living reference. A parallel v3 file next to a v2
covering the same ground is the exact duplication this process exists to prevent.

**A claim can be right and still be wrong for us.** The tool ladder (L1–L4) is sound advice
and strictly less developed than our 60/30/10 triage. Adopting it would be a downgrade.
That is what `AHEAD` is for.

---

## Cross-skill

Two lessons here generalise beyond this skill and belong in `global-lessons.md`:

1. **Verify absence with a negative grep, not with recall.** Applies to any audit skill.
2. **Redirect long CLI output to a file before filtering.** `tail`/`head` on an unbounded
   response silently loses content, and the loss is invisible in the transcript.
