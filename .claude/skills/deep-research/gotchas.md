# Gotchas: Deep Research
Last updated: 2026-03-31

## Known Failure Modes

- **Skipping Phase 1 decomposition** when the topic seems obvious. Leads to missing
  critical angles and producing a report that answers the wrong version of the question.
  Fix: Always map sub-questions before running the first search.

- **Treating single-source findings as confirmed facts.** Common with niche topics
  where only one article covers the subject. Fix: Flag all single-source claims as
  unverified in the output. Do not present them with the same confidence as cross-verified findings.

- **Summarizing instead of synthesizing.** Producing a list of "what each source said"
  instead of extracting patterns, conflicts, and conclusions. Fix: Phase 3 synthesis
  explicitly requires grouping, ranking, and insight extraction before writing output.

- **No action layer.** Delivering findings with no "so what." The output becomes
  interesting but not useful. Fix: Phase 4 is mandatory for STANDARD and BRIEF modes.
  Every report ends with specific recommended actions.

- **Hallucinating sources or citations.** Presenting training knowledge as a search
  result. Fix: Any finding not pulled from an actual search result in this session must
  be flagged as "from training knowledge, not verified by current search."

- **Scope creep mid-research.** User adds sub-questions after Phase 2 has started.
  Claude tacks on additional searches without re-mapping the territory, producing
  inconsistent depth across angles. Fix: If scope expands, restart Phase 1 before
  continuing.

- **Confidence washing.** Treating LOW confidence findings the same as HIGH confidence
  findings in the output. Fix: Confidence levels must be labeled explicitly on every
  major finding in STANDARD mode.

- **Wrong output mode.** Defaulting to STANDARD when the user just needs a quick
  answer, or using BRIEF when the decision is complex and stakes are high.
  Fix: Read the purpose statement to infer appropriate depth. When uncertain, ask.

## What Works Well

[Populate from real use.]

## Edge Cases

[Populate from real use.]

## Changelog

- 2026-03-31: v1.0 initial build
