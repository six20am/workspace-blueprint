---
name: workspace-diff
description: "Compares an outside source about how to work (a NotebookLM notebook, course, toolkit, blueprint) against this workspace and returns a claim-by-claim diff: ALREADY / GAP / CONFLICT / AHEAD / N/A, plus a scored, ranked change list. Diagnose-only: writes nothing to CLAUDE.md or any CONTEXT.md without approval. Use when asked to compare a course, notebook or blueprint against the workspace, mine a source for improvements, or check what a new method would change."
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Workspace Diff

## PURPOSE

Turn an outside source about *how to work* into a decision list about *this* workspace, without importing things it deliberately rejected and without writing the same rule in two places.

**Diagnose-only by default.** Emits a diff and a change list. Writes to `research/source-extracts/` (the extract) and `research/workspace-diffs/` (the diff) and nowhere else, unless the person approves specific changes.

## INPUT

One of:
- A NotebookLM notebook name or full UUID
- A local path to a source document or folder
- A URL to a course, blueprint or repo

Optional: `--scope <path>` to restrict the comparison to one area of the workspace.

If given a notebook name rather than an ID, resolve it with `notebooklm list --json`.

## PROCESS

### 1. Source

Confirm the source is readable and complete.

```bash
notebooklm source list --notebook <FULL-UUID> --json
```

Use the **full UUID**; partial IDs fail on `source list`. Every source must report `"status": "ready"`. If any are `preparing`, wait. A partial extract produces false `GAP` verdicts.

### 2. Prior run check

Look in `research/workspace-diffs/` for an earlier diff of the same source or source family.

- **Found:** new findings extend that file; they do not get a parallel one. Claims already recorded there are `ALREADY`, citing it.
- **Not found:** this is the first run; proceed.

### 3. Extract

One `notebooklm ask` per notebook. Demand atomic claims with citations:

```
Extract every distinct, actionable claim this source makes about how to structure a
workspace, run an AI-assisted process, organize context, or operate tooling.

Rules:
- One claim per line, stated as a single declarative sentence.
- Each claim carries its [n] citation.
- Split compound claims. "Write a spec and keep code out of it" is two claims.
- Include claims about what NOT to do; those are as load-bearing as the positive ones.
- Include stated rationale where the source gives one (the "why" decides CONFLICT vs GAP).
- If the source does not establish something, do not infer it. Write NOT IN SOURCE.
- Ignore course scaffolding: lesson navigation, "next up", community prompts, upsells.
```

Save to `research/source-extracts/<source-slug>.md` with a provenance line at the top (source, date, notebook ID).

### 4. Compare

For each claim, read only the files it plausibly touches: start from `CLAUDE.md`, follow the routing to the workspace `CONTEXT.md` that owns the claim's area, then the one or two reference docs or skills that would carry the practice. Assign one verdict:

| Verdict | Test |
|---|---|
| `ALREADY` | A workspace file contains this practice. **Open it and confirm**; never verdict from memory. |
| `GAP` | No workspace file covers it, and it would improve the workspace |
| `CONFLICT` | A workspace rule says the opposite, on purpose |
| `AHEAD` | The workspace has a more developed version of the same idea |
| `N/A` | The source's context does not transfer here |

Every row needs a source citation **and** a workspace evidence path. A verdict without an evidence path is rejected; re-derive it or drop the row.

**Actively hunt for `CONFLICT` and `AHEAD`.** They are the reason this is a comparison. Ask, per claim: *does anything in the workspace already contradict this, and was that deliberate?* A matrix with none is a failed run. Say so and re-run.

### 5. Triage

Score every `GAP` on five factors, 1 to 5 each: how often the situation comes up, how complex the fix is (lower is better), how much value it adds to the work, how much drift it prevents, and how well it composes with what exists. Create if the sum is 12 or more, or any factor is 5 with frequency 3 or more.

Route each: **do-now** (high score, additive, touches no standing rule), **later** (real but not urgent), **reject** (fails the bar; say why).

### 6. Emit

Write `research/workspace-diffs/<source-slug>.md`:

```markdown
# <Source>: Workspace Diff

**Source:** <name> (<id>) · <n> sources · **Run:** <date> · **Extract:** <path>
**Run:** 1 | 2 (extends <prior file>)

## Matrix
| # | Claim | Verdict | Source | Workspace evidence | Note |

## Ranked changes (GAP only)
| Rank | Change | Score | Target path | Route |

## Decisions recorded (CONFLICT / AHEAD)
| Claim | Verdict | Why the workspace differs |

## Counts
ALREADY n · GAP n · CONFLICT n · AHEAD n · N/A n
```

Then **stop**. Present the ranked list and ask which to apply. Do not edit `CLAUDE.md`, any `CONTEXT.md`, or any skill before approval.

### 7. Apply (only after approval)

- Applied changes **cite** the extract; never restate it (no rule in two places).
- After any `CONTEXT.md` edit, re-read it and confirm every path it names still exists.
- A change that adds a new capability is a `gap-finder` build, not an edit to a router.

## OUTPUT FORMAT

The diff file at the path above, plus a chat summary: the counts line, the top 3 ranked changes, and every `CONFLICT` row (those are the ones the person most needs to see).

## RULES

1. Diagnose-only until the person approves a specific change.
2. `ALREADY` requires an opened, confirmed file, never a remembered one.
3. Never sweep the workspace. Anchor reads only; if a claim needs twenty files it is too coarse.
4. Anything the source does not establish is **NOT IN SOURCE**. Never fill gaps with plausible method lore.
5. Applied changes cite the extract; they never duplicate it.
6. A claim contradicting a recorded `CONFLICT` halts and is surfaced, not adopted.
7. Idempotent: re-running after applying should report the applied items as `ALREADY` with their new citations.

## REFUSALS

- Source has `preparing` items: halt. Partial extracts fabricate gaps.
- A verdict with no evidence path: reject the row.
- Zero `CONFLICT` and zero `AHEAD`: report the run as failed; it imported instead of comparing.
- The person asks to apply something that reverses a recorded decision: surface the decision, get explicit confirmation, do not proceed silently.

## SKILL CHAIN

**Upstream:** `notebooklm` (creates and populates the source notebook). Manual sources need no upstream.

**Downstream:** `gap-finder` when a `GAP` row is a missing capability rather than a missing rule.

**Handoff format:** file-based. This skill writes `research/source-extracts/<slug>.md` (extract) and `research/workspace-diffs/<slug>.md` (matrix and ranked changes). Downstream steps read those paths; nothing is passed in context.

**Near neighbours, not duplicates:**
- `tool-vetting` judges software (a repo, a tool roundup). This compares a method. Its `MINE` rows are this skill's input.
- `gap-finder` notices a missing tool at task time. This finds missing rules from a source.

## RELATED

`gotchas.md` (failure modes seen in real runs)
