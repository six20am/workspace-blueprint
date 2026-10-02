---
name: voice-extractor
description: "Extracts a replicable voice profile from writing samples. Produces a style guide Claude can use to write in that voice. Use when: /voice-extractor is invoked."
---

# Voice Extractor
v1.1: 2026-08-07

## WHY THIS WORKS

Voice is not tone. Tone is a mood dial: formal, casual, warm. Voice is the sum of structural patterns that make one writer sound like themselves and no one else: sentence rhythm, vocabulary range, how ideas are sequenced, what gets said and what gets left out, how emphasis is created without formatting. Most AI-generated copy sounds identical because it mimics tone, not voice. The only way to capture a real voice is to analyze actual samples at the pattern level: not to describe the feeling, but to reverse-engineer the mechanics. A voice profile built from specific evidence produces writing that reads like the source, not like a vague approximation of their vibe.

---

## INPUTS NEEDED

- **Writing samples**: REQUIRED. Minimum 3 samples. More is better. Can be emails, posts, sales pages, transcripts, DMs, or any text written by the person. Paste directly or describe the source.
- **Subject of the voice**: REQUIRED. Who wrote this? (Client name, "me," personal brand, company founder, etc.)
- **Intended output use**: OPTIONAL. What will this voice profile be used to write? (Social posts, emails, sales copy, scripts.) Defaults to general-purpose if not specified.
- **Known voice notes**: OPTIONAL. Any self-description the person has given about their writing style, phrases they use often, or things they hate seeing in their copy.

If fewer than 3 samples are provided, flag it and ask for more before proceeding. A profile built from one sample will overfit to that sample's context, not the underlying voice.

**Reserve a holdout set before reading anything.** If 6 or more samples are available, set
aside 3 at random and do not read them during extraction: they are the validation set for
step 10. Ask for the extra samples if the person offered exactly 3: "six or more lets me
validate the profile against writing it has never seen, which is the difference between a
profile that looks right and one that is right."

With fewer than 6, proceed without a holdout and mark the profile `validated: no: sample
count too low`. Do not carve a holdout out of 3 samples; a profile built from 2 is worse
than an unvalidated profile built from 3.

---

## PROCESS

1. **Read all samples without analyzing yet.** Get a feel for the whole before pulling it apart. Note the first impression: does this person sound like anyone specific? What is the overall register?

2. **Analyze sentence structure.** Measure average sentence length. Identify the range (shortest to longest). Note whether sentences are compound-heavy, fragment-heavy, or declarative-dominant. Look for structural patterns that repeat: "short punch after a long setup," "list then land," "question then answer," etc.

3. **Catalog vocabulary patterns.** Flag words and phrases that appear more than once across samples: these are signature vocabulary. Note what the person never uses: jargon they avoid, filler words they skip, hedging language they omit or lean on. Identify the vocabulary ceiling: do they write at a 6th-grade level, a college level, or somewhere specific?

4. **Extract rhythm signature.** Read 3-5 sentences aloud mentally. Identify the cadence: punchy and staccato, long and flowing, clipped then expansive, or irregular. Note where the writer creates emphasis: through sentence length contrast, repetition, placement, or line breaks.

5. **Identify structural habits.** How does this person open? How do they close? Do they use callbacks? Do they front-load conclusions or bury them? Do they tell stories, give examples, make assertions, or ask questions as their default mode of developing an idea?

6. **Extract signature phrases and constructions.** Pull 5-10 actual phrases or sentence structures from the samples that could only have been written by this person. These are the fingerprints: they go into the profile verbatim.

7. **Identify what this voice does NOT do.** This is as important as what it does. Does this person never use em dashes? Never start with "I"? Never hedge? Never use passive voice? Never write more than 3 sentences in a row without a line break? These negative constraints prevent voice drift when the profile is used downstream.

8. **Build the voice profile.** Compile all analysis into the structured output below.

9. **Run a voice test.** Write 3-5 sentences in the extracted voice on a neutral topic (something not in the samples). Present them alongside the profile and flag any patterns that did not survive the transfer. Note those gaps in the profile's WATCH FOR section.

10. **Validate against the holdout: the only step with ground truth.** Step 9 grades its own homework: it produces writing in the voice and then judges whether it sounds right, with nothing to check against. This step has an answer key.

    For each of the 3 held-out samples, read only its *situation*: who it was written to, what prompted it, what it needed to accomplish. Draft what this person would have written, using the profile alone. Then open the real one and compare.

    Divergences are the finding, and they are almost always one of three things:
    - **A missing hard rule**: they never do something the draft did. Add it to what the voice does NOT do.
    - **A missing register distinction**: the profile collapsed two modes into one. They write differently to a client than to a friend, and the profile did not know that. Split it.
    - **An overfit pattern**: a "signature" construction that turned out to belong to the extraction samples' context, not the person. Demote or cut it.

    Tighten the profile, then re-draft that sample. A pattern that needed three passes to catch is worth noting in WATCH FOR: it is the one most likely to drift downstream.

    Stamp the result at the top of the profile: `validated: 2026-08-07: 3 holdout samples` once the drafts read as plausibly theirs, or `validated: no: <reason>` if they do not. An unvalidated profile is still usable; an unvalidated profile that *looks* validated is how voice drift ships to a client.

    Show the person the divergences you found. Their reaction is better evidence than your comparison: "I'd never say that" is a hard rule you cannot derive from samples alone, and it goes in verbatim.

---

## OUTPUT FORMAT

```
VOICE PROFILE: [Subject Name]
Built from: [number] samples: [brief description of sample types]
Built: [date]
Validated: [date: N holdout samples] / [no: reason]
Intended use: [general-purpose / specific output type]

---

FIRST IMPRESSION
[2-3 sentences. What this voice sounds like before you analyze it.
The gut-level read a stranger would have after one paragraph.]

---

SENTENCE STRUCTURE
Average length: [X words]
Range: [shortest type] to [longest type]
Dominant pattern: [describe the structural pattern that appears most often]
Signature construction: [specific sentence structure used repeatedly, with example]

---

VOCABULARY
Register: [conversational / professional / street / elevated / mixed]
Ceiling: [approximate reading level or description]
Signature words/phrases (use these):
- "[exact phrase from samples]"
- "[exact phrase from samples]"
- "[exact phrase from samples]"
- "[exact phrase from samples]"
- "[exact phrase from samples]"

Words/phrases this voice avoids:
- [word or construction]
- [word or construction]
- [word or construction]

---

RHYTHM SIGNATURE
[2-3 sentences describing the cadence. How does this voice create momentum?
Where does it pause? How does it land a point?]

---

STRUCTURAL HABITS
Opens with: [how this person typically starts a piece]
Develops ideas by: [assertion / story / example / question / list: which is dominant]
Closes with: [how they typically end: callback, directive, open loop, declarative]
Uses callbacks: [yes / no / sometimes]
Conclusion placement: [front-loaded / buried / earned at the end]

---

FINGERPRINTS (do not lose these)
[5-10 exact phrases or constructions pulled from the samples.
These are the hardest things to fake and the most important to preserve.]
1. "[exact quote or construction]"
2. "[exact quote or construction]"
3. "[exact quote or construction]"
4. "[exact quote or construction]"
5. "[exact quote or construction]"

---

WHAT THIS VOICE DOES NOT DO
[Negative constraints. Specific. Each one is a guardrail.]
- Never [specific construction or word choice]
- Never [specific construction or word choice]
- Never [specific construction or word choice]
- Never [specific construction or word choice]
- Never [specific construction or word choice]

---

VOICE TEST
Topic: [neutral topic used for the test]
Sample output:
[3-5 sentences written in the extracted voice]

Patterns that survived: [list what held]
Patterns at risk of drift: [what is hardest to maintain without more samples]

---

WATCH FOR
[2-4 specific failure modes when using this profile to write new content.
What is most likely to break first? What will make it sound generic?]
```

---

## SKILL CHAIN

Upstream: Raw writing samples (emails, posts, transcripts, sales pages: any text written by the subject)
Downstream: `voice.md` in the workspace reference folder, and any writing task
Handoff format: save the full Voice Profile as `voice.md`; a writing task reads it with the instruction "Write in this voice."

---

## NOTES

- More samples always beat fewer. If the user provides one sample, flag it and ask for at least two more before building. A single-sample profile overfits to that context.
- Transcripts of speech are valid input but flag them: spoken voice and written voice diverge. A profile built purely from transcripts may produce copy that reads like a talk, not like prose.
- If the subject has described their own voice in writing, treat that self-description as a data point, not ground truth. Writers consistently misidentify their own patterns. The samples are the evidence. The self-description is context.
- The voice profile is a reusable document in its own right. It can be handed to any writer, human or AI, to keep the voice consistent across everything written.
- The WHAT THIS VOICE DOES NOT DO section is where most profiles break down in practice. Spend extra time here. The negative constraints are the guardrails that prevent generic output.
- If samples span very different contexts (formal proposal vs. casual DM), note the range explicitly and identify which mode is appropriate for the intended output use.
