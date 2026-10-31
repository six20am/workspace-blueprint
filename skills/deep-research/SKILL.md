---
name: deep-research
description: "Runs a structured multi-pass research process on any topic. Decomposes into sub-questions, searches multiple angles, cross-verifies claims, and delivers a sourced brief or full report with action layer. Use when: /deep-research is invoked."
---

# Deep Research
v1.1: 2026-06-05

## WHY THIS WORKS

Surface-level AI research fails because it treats "search and summarize" as the whole job.
Real research requires decomposing the question into distinct angles before searching,
verifying claims across multiple independent sources, and converting findings into
decisions or actions. The structured sub-question approach forces scope clarity upfront
so searches are targeted instead of broad. Multi-source cross-verification catches
contradictions and gaps that a single-pass answer never surfaces. Adding an action
layer at the end means the output drives next steps, not just reading.

---

## INPUTS NEEDED

REQUIRED: Research topic or question: one sentence minimum. The more specific the
better. "Who are the top competitors for a bakery in Austin"
produces better output than "competitor research."

REQUIRED: Purpose: what decision or action will this research inform? This shapes
depth, framing, and the action layer at the end.

OPTIONAL: Scope constraints: time period, geography, niche, platform, or angle to
focus on. Default: no constraint, the assistant infers from topic.

OPTIONAL: Output size: BRIEF (1-2 page summary), STANDARD (full structured report),
or RAW (findings only, no synthesis). Default: STANDARD.

OPTIONAL: Specific sub-questions: if the user already knows what they want answered,
list them. The assistant will add any missing angles.

If topic or purpose is missing, ask for both before proceeding. Do not start research
with incomplete inputs.

---

## PROCESS

### PHASE 1: DECOMPOSE

Before running a single search, map the research territory.

1. Restate the research question in one clear sentence.
2. Identify 3-6 sub-questions that fully cover the topic. Examples:
   - What exists in this space right now?
   - Who are the key players and what are they doing?
   - What are the gaps, weaknesses, or opportunities?
   - What does the target audience believe, feel, or need?
   - What data or proof points exist?
   - What has changed recently that matters?
3. Assign each sub-question a search angle: specific enough to return useful results.
4. Note which sub-questions are high-priority (answer the core purpose) vs. supporting.

Do not skip this phase. Research that starts with a search instead of a question map
produces unfocused output that misses the most important angles.

### PHASE 2: SEARCH AND GATHER

5. Execute searches per sub-question, using targeted 2-5 word queries.
6. Run minimum 3 searches per high-priority sub-question.
7. For claims that matter to the purpose, verify across at least 2 independent sources.
8. Flag any claims that appear in only one source as unverified.
9. Note source type for each finding: primary (official/direct), secondary (analysis),
   or tertiary (aggregator/forum). Weight primary and secondary sources higher.
10. If searches return conflicting data, note the conflict explicitly. Do not pick one
    and ignore the other.
11. If a key sub-question returns no useful results, note the gap and explain what
    that absence might mean.

### PHASE 3: SYNTHESIZE

12. Group findings by sub-question.
13. Identify the 3-5 most important insights: findings that directly inform the purpose.
14. Identify any surprises: things that contradict assumptions or change the picture.
15. Note confidence level for each major finding: HIGH (multiple verified sources),
    MEDIUM (single strong source or indirect evidence), LOW (inference or single weak source).
16. Do not present all findings as equal. Lead with what matters most to the purpose.

### PHASE 4: ACTION LAYER

17. Convert insights into specific next actions or decisions the user can take.
18. Structure as: IF [finding is true] THEN [recommended action].
19. Flag any findings that require further research before action is warranted.
20. If the research reveals the original question was the wrong question, say so.

---

## OUTPUT FORMAT

### BRIEF MODE (default for simple topics or time-constrained requests)

```
RESEARCH BRIEF: [Topic]
Purpose: [what decision this informs]
Date: [date]

KEY FINDINGS
[3-5 bullets. Each bullet is one verified insight with confidence level.]

GAPS AND UNCERTAINTIES
[What was not findable or confirmed. What still needs verification.]

RECOMMENDED ACTIONS
[2-4 specific next steps derived from the findings.]
```

### STANDARD MODE (default for strategy, market, or competitor research)

```
RESEARCH REPORT: [Topic]
Purpose: [what decision this informs]
Date: [date]
Scope: [constraints applied]

EXECUTIVE SUMMARY
[3-5 sentences. The most important insight and what to do about it.]

FINDINGS BY ANGLE

[Sub-question 1]
[Findings with source notes. Confidence level. Any conflicts flagged.]

[Sub-question 2]
...repeat for each angle...

KEY INSIGHTS
[The 3-5 findings that matter most. Why each one matters.]

SURPRISES
[What the research revealed that contradicts assumptions or changes the picture.]
[If nothing surprising, state "No significant surprises."]

GAPS
[What could not be verified. What is still unknown. What would change the picture.]

RECOMMENDED ACTIONS
[Specific next steps per finding. IF/THEN format where helpful.]
[Flag anything that needs more research before action.]
```

### RAW MODE (for users who want to do their own synthesis)

```
RAW FINDINGS: [Topic]
Date: [date]

[Sub-question 1]: [findings, sources, confidence]
[Sub-question 2]: [findings, sources, confidence]
...
```

---

## SKILL CHAIN

Upstream: direct invocation with a clear topic and purpose; `agent-web-fetch` or `notebooklm-research` when a source is gated or long
Downstream: whatever decision the research informs; `workspace-diff` when the topic is how to work; otherwise a standalone report filed under `research/`
Handoff format: STANDARD report or BRIEF, saved to `research/YYYY-MM-DD-<topic>.md`

---

## NOTES

Invocation: slash command only. Do not auto-trigger.

On source citation: When citing a web result, note the domain and general source type.
Full URL citation is not required but is helpful when the finding is contested or critical.

On DataForSEO MCP: When the research question requires data WebSearch cannot return (SERP composition, keyword volume/difficulty, backlink profile, LLM citation frequency,
content gap analysis), use the DataForSEO MCP tools if the person has that connector. Every call costs money, so cache every response.

Typical patterns:
- Competitor SEO research → `mcp__dataforseo__dataforseo_labs_google_ranked_keywords` +
  `mcp__dataforseo__backlinks_summary` for each named competitor
- Keyword landscape → `mcp__dataforseo__dataforseo_labs_google_keyword_ideas` +
  `mcp__dataforseo__dataforseo_labs_google_keyword_overview`
- "What is being said about brand X in AI" → `mcp__dataforseo__ai_opt_llm_ment_search` +
  `mcp__dataforseo__ai_opt_llm_ment_cross_agg_metrics`
- Live SERP for a query → `mcp__dataforseo__serp_organic_live_advanced`
- Content angle gap on a topic → `mcp__dataforseo__content_analysis_search` +
  `mcp__dataforseo__content_analysis_summary`

Cache every paid response to `research/cache/dataforseo/<topic>/` so nothing is fetched twice.

On hallucination risk: Do not synthesize conclusions that are not directly supported
by at least one search result. If the assistant's training knowledge is filling a gap where
no search result was found, flag it explicitly as "from training knowledge, not verified."

On scope creep: If the research question expands mid-process (the user adds more angles),
restart Phase 1 with the expanded scope before resuming Phase 2. Do not bolt on
additional searches without re-mapping the territory.

On use case range: This skill works for market research, competitor analysis, client
intelligence, niche validation, offer research, B2B targeting, regulatory landscape,
platform feature research, and strategic questions. It is not a substitute for primary
research (interviews, surveys, real customer data).

On output size: STANDARD reports for complex multi-angle topics typically run 600-1500
words. BRIEF mode runs 150-350 words. RAW mode has no target length.
