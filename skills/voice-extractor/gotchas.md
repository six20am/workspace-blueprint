# Gotchas: Voice Extractor
Last updated: 2026-03-29

## Known Failure Modes

- **Profile built from a single sample** overfits to that sample's context (a sales email reads like all sales emails, a casual DM reads like all casual DMs). Fix: require minimum 3 samples before building. Flag and ask if fewer are provided.

- **Tone description passed off as voice analysis**: output says things like "warm and conversational" without identifying any structural evidence. Fix: every claim in the profile must trace back to a specific pattern observed in the samples. If it cannot be evidenced, it does not go in.

- **Fingerprints section filled with paraphrases** instead of exact phrases. Fix: fingerprints must be verbatim quotes or verbatim structural constructions from the samples. Paraphrase loses the voice.

- **WHAT THIS VOICE DOES NOT DO section left vague** ("avoids jargon," "keeps it simple") instead of specific. Fix: negative constraints must be executable guardrails. "Never uses em dashes" is a constraint. "Keeps it simple" is not.

- **Voice test topic too close to the samples**: tests using a topic already covered in the samples confirm pattern recognition but do not test transferability. Fix: always pick a neutral topic outside the sample content for the voice test.

- **Self-description overrides sample evidence**: user says "I write in a very formal tone" but samples are casual and punchy. Fix: always prioritize sample evidence over self-description. Note the discrepancy in the profile explicitly.

- **Transcript-only profiles** produce copy that sounds like a talk, not prose. Fix: flag when all samples are transcripts, note the limitation, and ask for any written samples before building.

- **Profile describes the subject's best writing** when samples include rough drafts or off-brand pieces. Fix: ask the user which samples best represent the voice they want to replicate before analyzing. Do not average in outliers.

## What Works Well

[Populate from real use]

## Edge Cases

[Populate from real use]

## Changelog
- 2026-03-29: v1.0 initial build
- 2026-08-07: v1.1: added step 10, holdout validation against 3 reserved samples,
  and a `Validated:` field in the profile header. Step 9's neutral-topic test grades
  its own output with no ground truth; step 10 compares drafts against what the person
  actually wrote. Intake now reserves 3 samples when 6+ are available and marks the
  profile unvalidated below that threshold. Method adapted from `yc-software/qm`'s
  `email-voice-profile` skill (MIT).
