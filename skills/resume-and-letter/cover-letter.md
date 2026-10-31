# Writing the cover letter

One page that answers the three questions every reader of an application is asking: Why this job? What have you done that fits? Do you have the skills? The truth rules in `SKILL.md` come first.

## The profile

The person's standing facts live in `profile.md`, in the folder the router file names for notes. If the router names none, ask where it goes. Read it at the start of every cover letter.

If there is no profile yet, build one before the first letter, in a few minutes: read the resume, fill in what it answers, ask only for the rest (name check, a one-line summary of their edge, how they like to work), and show the result. Save it only on the person's yes. After that, each letter is: paste the posting, answer two or three questions, approve the outline, get the letter.

Update the profile only when the person agrees, at the end of a letter: a phrasing they corrected, a sharper skills line, a note on what this application led with. The profile is a plain file in their workspace; nothing copies it anywhere else.

## The flow

1. **Read** the posting against the resume and the profile. Note which of the person's main threads (see the profile) fits each thing the posting stresses.
2. **Ask for the why.** The opening cannot be written from a resume. Ask only what is still unknown, each answerable in a sentence or a yes or no:
   - Do you know their product or service? Have you used it?
   - Is there something about this job's problems or stage that draws you?
   - Do you know anyone there, or did someone point you to it?
   - Are you, or someone close to you, the kind of customer they serve?
   - Have you noticed anything they did recently?
   If the answers are thin, write a softer, honest opening. Never write enthusiasm the person did not express.
3. **Outline one part at a time.** Confirm each before the next; write no letter until the outline is approved. If the person says "the rest looks fine", do the rest in one go.
   - **The opening angle,** from what the person actually said in step 2.
   - **Three experience bullets,** each with a bold lead-in, each tied to one thing the posting stresses, each a specific result from the resume or the profile's list of proven claims.
   - **The skills part:** who the person is at work, one short line per skill area from the profile, reordered for this posting. A skills line is a way of working ("I plan for what can go wrong first"), never a retold result from the bullets. Name any thin area honestly or leave it out.
4. **Check against the resume.** Do not repeat what the resume already says in the same words. Each thread lives in the letter or the resume, not both.
5. **Phrasing pass** (below).
6. **Draft in Markdown,** then offer the Word file or PDF through `document-builder`.

## Shape

```
Dear [first name, only if the posting or the person gives one; otherwise "[Company] team"],

[Opening: why this job, why now. Two or three sentences.]

**[Bold lead-in 1].** [A result that answers the posting's first priority.]
**[Bold lead-in 2].** [A result that answers the second.]
**[Bold lead-in 3].** [A result that answers the third.]

[Skills: three to five short lines, strongest first for this posting.]

[One warm closing line.]

[Name]
```

Never look up a hiring manager's name to put in the greeting. A wrong name on the first line is worse than "Dear [Company] team".

## Tone

- **Warm and specific.** Not stiff, not chatty.
- **No inflation.** Understate when unsure. Strip "extensive", "deep", "significant", "proven"; let the numbers carry it.
- **Borrow the posting's words only where the record backs them.**
- **Do not claim familiarity the person did not claim.** Avoid "I have followed you for years." Prefer "The mix of [X] and [Y] is the kind of place I do my best work."
- **Do not write the job as a stretch** if the person has already worked at that level or above.
- **Keep each employer's language with that employer.** Words from a retail job do not describe the work at a software firm.

## Phrasing pass

Read the draft once for:

1. The same claim in more than one bullet. Vary it or cut it.
2. Bullets that start the same way. Vary the openings.
3. Inflated adjectives. Cut them.
4. A noun used five times. Vary it or cut it.
5. A skills line that repeats a bullet. Recast it or drop it.
6. A thread that is in both the letter and the resume. Keep it in one.

## Profile template

Copy this into `profile.md` on the first run and fill it from the resume and the person's answers. Every bracket gets replaced or deleted.

```
# Profile

## About me
- Name: [name]
- Current or target level: [for example, shift supervisor]
- One-line edge: [the sentence that sums up what I bring]

## Main threads
The two to four stories that carry most of my applications.
- [Thread 1]: [for example, cut costs, turned a team around]
- [Thread 2]: [for example, trained new staff, built a process]
- [Thread 3]: [for example, first hire in a new role]

## Skills
One line per area, a way of working, not a single result. Strength: strong, solid or thin.
| Area | Strength | Line |
|---|---|---|
| [area] | [strong] | [I plan for what can go wrong first.] |
| [area] | [solid] | [I set the goal, then let the team own the how.] |

## Proven claims
Results the resume can back. Letters draw only from this list; anything else gets a [placeholder].
- [result with its number, as it appears on the resume]

## Employer language
| Employer | Kind of place | Its words | Do not borrow |
|---|---|---|---|
| [employer] | [kind] | [terms used there] | [terms from elsewhere] |

## Look
- Font: [the resume's font, or a plain default]
- Accent color: [the resume's accent, or none]
- Page: [Letter or A4]

## Phrasing log
| Avoid | Prefer |
|---|---|
| [responsible for the schedule] | [ran the schedule] |

## Past letters
One entry per letter: employer and role, what the posting stressed, the three bullet lead-ins and which thread each used, the skills order, and any correction that stuck.
```
