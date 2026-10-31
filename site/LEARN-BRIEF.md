# Brief: the Learn page (how to use an AI well, and where the blueprint fits)

Format: web-page, the second page on the Workspace Blueprint site. Written 2026-10-31 for `/copywriter`. Every idea below carries its source. Nothing outside this file is a fact for this page.

## Who reads this

The same reader as `BRIEF.md`: one person who runs something small (a business, a practice, a side project, a household with too much paperwork). Not technical. They have tried an AI chat box and found it forgets everything and knows nothing about their files. They can copy and paste. They have heard "Claude" and may or may not have an account.

Awareness: they know the chat box is not enough. They do not know why it fails or what a good setup looks like. This page tells them.

## The one job this page does

Teach them, in plain words, how to use an AI well, and show that the blueprint already does the setup those lessons call for. Then send them to copy the prompt.

## The CTA

One: **Copy the prompt**, the prompt page's main action. This page links to it; it does not repeat the prompt box.

## Guardrails

Copied from `BRIEF.md`:

- No em dashes.
- Grade 8 or lower.
- No invented numbers, testimonials, logos or names of users. There are none.
- Never say "supercharge", "unlock", "seamless", "powerful". Say "AI service" or "your AI", not "AI agent".
- Name no AI vendor other than Claude.
- Do not name the agency's clients or the two agency brands.
- The download link is `https://github.com/six20am/workspace-blueprint/releases/latest/download/Six20AM-Workspace-Blueprint.zip`. The GitHub repo link is footer microcopy, not a second CTA.

Added for this page:

- Jake Van Clief is credited by name once, with a link to his YouTube channel. The channel handle in the source files is `@JEVanClief` (2026-10-14 and 2026-08-08 extracts), so the link is `https://www.youtube.com/@JEVanClief`. Not re-checked live for this brief; the builder confirms it resolves before the page ships.
- His ideas go in our own words. At most one direct quote, under 15 words, in quotation marks, with his name. Candidates, all from 6AzLk2-kWyY unless marked: "Every word in a prompt is a question, and something has to answer it." (14 words); "Put your eyes where your judgment matters." (7 words); "The machine does the volume, you make the call." (9 words, from his map, n1qE6NU7K_4). Pick one or none.
- Never phrase anything as his endorsement of this product. He has not seen it, has not mentioned it, and has no connection to it in any source. Every line about the blueprint is ours. Say "he teaches X; the blueprint does X", never "he recommends the blueprint" or "built his way".
- Do not say Jake wrote the teaching kit. The kit files in `_reference/` (01, 03, 04) carry no author name. `BRIEF.md` says only that the kit's author approved redistribution. The two are separate credits.
- The word "agent" may appear only where it is needed to explain his idea that you do not need one (idea 4 below), and once. Everywhere else: "your AI".
- His sources name Codex, ChatGPT, Gemini and others. The page names only Claude. Drop every other vendor name when retelling his examples.
- None of his self-reported figures go on the page. See § Not in the sources.

## Source key

| ID | What it is |
|---|---|
| 6AzLk2-kWyY | "How I'd Learn AI From Zero in 2026", 2026-10-06, 54 min, eleven lessons. Scripted and clean. The main source. |
| n1qE6NU7K_4 | "Isn't an AI Workspace Just a Folder Structure?", 2026-09-30, 9 min. Walks a real folder. Scripted and clean. |
| dZ8P7zevuGw | "ICM Explained (Folders Over Agents) in Five Minutes", 2026-09-21. |
| m7en7ugujlI | "Do You Actually Need AI Agents? (Why I Use Folders Instead)", 2026-10-10, 43 min. |
| iBPe14UitSk | "How to Build an AI Second Brain for Your Business", Short, 2026-10-09, 92 seconds. |
| bZSapJpCwuo | "How to Make AI Writing Stop Sounding Like AI (a 19-Line Check)", Short, 2026-10-04. |
| -CUsfao6m7E | "Your Second Brain Is Not a Notes App", live session, 2026-07-07, 56 min. Rough captions. |
| NWyTsKTKka8 | "Systems Thinking for People Who Build With AI", webinar, 90 min, read 2026-08-08. |
| ABeo1kKueRs | "I tested the big AI voice models", 2026-10-01. About voice cloning. Read; nothing in it for this page. |
| kit 01 | `_reference/01-how-to-adapt-this.md` |
| kit 03 | `_reference/03-context-md-anatomy.md` |
| kit 04 | `_reference/04-common-mistakes.md` |

Everything from the videos is the speaker's claim, retold from caption transcripts and NotebookLM reads. Everything about the blueprint is from `BRIEF.md` § Facts (binding).

## What Jake teaches, in plain words

Twelve ideas. Each one: the idea, its source, and the one line in the blueprint that already does it. Where the blueprint only partly does it, the gap is stated so the writer does not paper over it.

**1. The AI only sees what is on its desk.**
What it can see in this one conversation (what you typed, what you attached, a little memory) is the whole world to it. If a thing is not on the desk, it guesses. If everything is on the desk, it guesses which thing you meant. (6AzLk2-kWyY, lesson 1.1. Same idea as the webinar's rule that the AI reads the root file first and then only the files it needs, NWyTsKTKka8.)
Blueprint: a folder on the owner's own computer where the AI can find their files, with three routing files so it loads only what a task needs (`BRIEF.md`, What it is; What gets built).

**2. New job, new chat. And write down what has to survive the chat.**
An old chat drags the last job onto the desk. Every word in a prompt is a question, and something has to answer it: a file you wrote, a connection to your stuff, or you retyping it every morning. (6AzLk2-kWyY, lesson 1.1.)
Blueprint: files and rules persist between chats; the boundary list is written into the map and every section's notes so it holds in every chat (`BRIEF.md`, The boundary; the "it remembers" reason in § why).

**3. One short map file that the AI reads first.**
At the top of the folder sits one file that says what this place is, where things go, and what to read for each job. The AI reads it every time it opens the folder. Keep it short, about one screen. The most common mistake he sees is a giant map with everything crammed in, which puts the whole drawer back on the desk. (6AzLk2-kWyY lessons 1.3 and 2.2; n1qE6NU7K_4; dZ8P7zevuGw; iBPe14UitSk. Kit 04, Mistake 1, says the same: the map is a map only.)
Blueprint: three routing files so the AI loads only what a task needs (`BRIEF.md`, What gets built). Setup writes them from the owner's answers.

**4. You do not need a different AI for every job. You need folders.**
A "research AI", a "writing AI" and an "email AI" are the same model reading different instructions. A name on the door adds no instructions and no access. One good model plus a good set of folders does the work; the folder it opens decides what it becomes for that job. (6AzLk2-kWyY lessons 1.3 and 2.3; m7en7ugujlI; dZ8P7zevuGw.)
Blueprint: one AI, thirty-nine skills, each a folder the AI opens only when the request matches (`BRIEF.md`, What it can do, today). This is the one place the word "agent" may appear.

**5. When the work is written down, a short prompt is a button.**
His trigger for a whole weekly pipeline is one line: the recording is in, take it from here. Everything that line runs is written in the folders, so the prompt can be short. (n1qE6NU7K_4. The email example in 6AzLk2-kWyY lesson 1.3 is "check my email".)
Blueprint: the first-week asks are each one sentence ("paste a YouTube link and ask for the transcript") because a shipped skill already holds the steps; "set this up" is the whole setup prompt (`BRIEF.md`, Your first week; Paste-in prompts).

**6. A person checks the work at the cheap early stage.**
Nothing moves to the next step until somebody has looked at the last file. The check goes early, where a mistake costs a ten-second edit, not at the end, where it costs a rebuild. He does not watch every step; he puts his eyes where his judgment changes the result. (6AzLk2-kWyY lesson 3.1; n1qE6NU7K_4, where the pipeline stops at the transcript because that is where misheard names and private material show up first.)
Blueprint: setup shows the folder tree it picked and asks if it looks right before building; social posts and emails are drafts only, never posted or sent (`BRIEF.md`, Setup; What it can do, today).

**7. The things that must never happen without you get a hard stop, not just a sentence.**
A line in the map ("stop after each stage and wait for me") is a soft stop, and the AI almost always follows it. For sending, spending and deleting, he says to use the settings too, because the map is only something the AI reads. (6AzLk2-kWyY lessons 1.3 and 3.1; the webinar's draft-and-halt rule, NWyTsKTKka8.)
Blueprint: at setup the AI names the three things it will never do without asking (send anything, spend money, delete anything) and asks what else belongs on the list; the list is written into the map and every section's notes (`BRIEF.md`, The boundary). **Gap:** `BRIEF.md` describes the boundary as written into files, which is his soft stop. It says nothing about a setting or hook that blocks the action. Do not write that the blueprint "blocks" or "cannot" send, spend or delete. Write that it asks first, and that the rule is written where every chat reads it.

**8. Anything with one right answer becomes a small script. Anything that needs taste stays with you and the AI.**
If you have done a step the same way three or four times and the right answer does not depend on taste (renaming files, pulling numbers from a report, resizing images, finding every dash in a draft), ask the AI to write a script for it. Check it once against something you already did by hand. A script that is wrong is wrong the same way every time, which is why you check once and then trust it. (6AzLk2-kWyY lesson 3.2; n1qE6NU7K_4, the 20-line audit script; bZSapJpCwuo, the 19-line writing check.)
Blueprint: the skills that do one-answer work are already scripts (photos renamed by date taken, exact duplicates set aside, files converted, a bank export summarized by category); the gap finder notices when a task has no tool and offers to build one; the outbound check scans for secrets, account numbers and the owner's address before anything leaves (`BRIEF.md`, What it can do, today; Care of the workspace).

**9. A voice file: a few plain rules plus three or four things you actually wrote.**
AI writing sounds like AI because nobody gave it your voice. Fix: one file with plain rules the AI can check ("no em dashes", "no hype", "sign it with my first name") and real samples of your writing. Examples beat adjectives; the model copies a sample far better than it obeys a word like "punchy", bad habits included. Rules with one right answer move to a script; "does this sound like me" stays a judgment call. Then read the draft yourself. (bZSapJpCwuo; n1qE6NU7K_4, his voice.md; iBPe14UitSk, "how he talks" in the system folder.)
Blueprint: a voice file so anything the AI writes sounds like the owner; setup asks how you want it to sound; the `voice-extractor` skill builds the voice file from the owner's own writing, which is first-week ask number five (`BRIEF.md`, What gets built; Your first week).

**10. Write down every correction. The list is your first skill.**
Do one weekly job in a chat. Each time you correct it ("too formal", "never promise a date that is not confirmed", "sign it Jake"), write the correction down. That list becomes a short instruction file the AI opens whenever that kind of job comes up. When you catch yourself fixing the same thing twice, change the file that caused it, and every run after picks it up. Read what the AI writes into that file: it may invent a rule you never said, or turn one example into a law. (6AzLk2-kWyY lessons 1.1 and 1.2; n1qE6NU7K_4. Kit 01 step 4 says the same: add a doc when the AI repeats a mistake.)
Blueprint: the gap finder, which notices when a task has no tool and offers to build one (`BRIEF.md`, Care of the workspace; first-week ask seven). **Gap:** `BRIEF.md` does not describe a correction log or a "turn my corrections into a skill" skill. Say the owner can ask for one; do not say the blueprint keeps one.

**11. "Done" is not the test. Open the real file.**
His setup test: point the AI at a folder with one file, ask it to read it and save a one-page summary next to it, then open the summary outside the AI. If you can open it, read it and change it, the setup works. Finished work lands as plain files you can open in any editor before you send anything. (6AzLk2-kWyY lessons 1.3 and 1.4.)
Blueprint: everything the AI makes is a file in the owner's folder; setup writes `setup/setup-report.md` saying what installed, what failed and what needs a sign-in; drafts are files, never sent (`BRIEF.md`, Status; What it can do, today).

**12. Keep each fact in one place, and keep your method apart from your facts.**
Four kinds of file: how you do things (method), facts about one client or project, work in progress, and finished output. Method carries to the next client; facts stay with this one. Mix them and the AI starts promising every client the same date. Keep each fact in one file and have everything else point to it; two copies drift, and by week six the AI finds three prices for the same thing and picks the old one. Retired work goes in an archive folder the map tells the AI never to read. Never delete originals, sources or anything that belongs to someone else. (6AzLk2-kWyY lessons 1.2, 2.2 and 3.3; n1qE6NU7K_4, where his own files drifted.)
Blueprint: updates pull new skills and tools and never touch the owner's files, map, routing or voice file, which only works because method and the owner's facts live apart; the photo sorter deletes nothing; there is an undo history (`BRIEF.md`, Updates; What it can do, today; Care of the workspace).

Three more that fit if the page has room, each with the same shape:

**13. Start from a job that hurts, not from a plan to "have a second brain".**
Pick one job you repeat that has a person at the end (a weekly report, client onboarding, a newsletter). Ask: who is this for, what do they need to do next, where does the information come from now, what breaks and who feels it. Build the smallest thing that does today's job and add a folder only when the work asks for one. (6AzLk2-kWyY lesson 2.1 and 2.2; -CUsfao6m7E; n1qE6NU7K_4. Kit 04, Mistake 8: building everything before using anything.)
Blueprint: setup asks what you do and what work you want help with, one question at a time, and "not sure" is a fine answer (`BRIEF.md`, Setup).

**14. Skip the plumbing the first week.**
Connectors, custom skills and hooks all bolt on later. Much online setup advice comes from people whose favorite part is the setup. (iBPe14UitSk. Kit 04 Mistake 7 adds: the built-in skills and connections are the starting toolkit; audit what is already there before building.)
Blueprint: the skills arrive installed; the owner's week one is seven plain asks (`BRIEF.md`, Your first week). Careful: this is our claim that the blueprint does the plumbing, not his claim about the blueprint.

**15. The whole cost is more than the price.**
Subscription, setup time, keeping it running, time checking its work, time waiting. A cheaper tool that eats your whole Saturday costs you a Saturday. (6AzLk2-kWyY lesson 1.4.)
Blueprint: setup is fifteen to thirty minutes, most of it installs in a black window; the zip is free; Claude Code needs a Claude account and the page does not state Claude's prices (`BRIEF.md`, Setup; Cost).

## How to ask an AI for something

Practical habits, each with its source. The writer may group or cut; nothing here is invented.

| Habit | How it sounds | Source |
|---|---|---|
| Say the outcome and who it is for. | "A one-page summary of this contract for me, so I can decide whether to sign." | 6AzLk2-kWyY lesson 2.1 (who is this for, what do they need to do next); `BRIEF.md` Your first week ("say the outcome you want"). |
| Name the file or link that matters. | "Read the PDF in this folder named lease-2026.pdf." In a big folder, not every file reaches the desk, so name the one. | 6AzLk2-kWyY lesson 1.2; `BRIEF.md` Your first week ("name the file or link"). |
| Say where the result should land. | "Save it next to the original." "Put it in drafts with today's date and the client's name in the file name." | 6AzLk2-kWyY lessons 1.3 and 1.4; `BRIEF.md` Your first week ("say where the result should land"). |
| Keep the prompt short once the steps are written down. | "Check my email." "The recording's in, take it from here." The folder answers the rest. | 6AzLk2-kWyY lesson 1.3; n1qE6NU7K_4. |
| New job, new chat. | Start fresh for each unrelated job so the last one does not leak in. | 6AzLk2-kWyY lesson 1.1. |
| Correct it in plain words, in the chat. | "Too formal. I'd never say that. And don't promise the room yet." Each correction is a decision: your voice, what is actually known, who you are to the reader. | 6AzLk2-kWyY lesson 1.1. |
| Then write the correction down. | After the job, put the corrections in a file so you never retype them. When the same fix comes up twice, change the file, not the prompt. | 6AzLk2-kWyY lessons 1.1 and 1.2; n1qE6NU7K_4. |
| Let it interview you, one question at a time. | "I want help with my weekly report. Ask me one question at a time: what comes in, what I decide, what goes out, who gets it, where I stop to check." | n1qE6NU7K_4 (build your first one); 6AzLk2-kWyY lesson 1.2 (skill interview). |
| Tell it to stop and wait. | "Stop after each stage and wait for me." He says the AI almost always follows it. | 6AzLk2-kWyY lesson 3.1. |
| Tell it to say so when it does not know. | His email map carries two rules: never send anything, and if the client's notes do not confirm something, say so. | 6AzLk2-kWyY lesson 2.2. |
| Watch what it reads. | Give one real request in a fresh chat and watch which files it opens. Right few files, skipped the rest: good. Wandered through everything: the map is too vague, tighten one row. | 6AzLk2-kWyY lessons 1.3 and 2.2. **Note:** he says watch what it reads; the sources do not show him asking the AI to list the files it used. If the page tells the reader to ask "which files did you use", mark it as our suggestion, not his. |
| Ask the three freshness questions. | In a brand new chat: "What is this folder? What's in progress? What's next?" Wrong answers mean the map is out of date. | 6AzLk2-kWyY lesson 3.3. |
| Read what it wrote before you trust it. | A generated instruction file may carry a rule you never said, or turn one example into a law. A generated map may add rooms you do not need. | 6AzLk2-kWyY lessons 1.2 and 2.2. |
| Give samples, not adjectives, for voice. | Three or four things you actually wrote beat "make it punchy". | bZSapJpCwuo. |
| Check a new script once, properly. | Run it on something you already did by hand (last week's export) and compare. | 6AzLk2-kWyY lesson 3.2. |
| Use an export when one exists. | "Here is the export from my booking system" beats having the AI click around a website. | 6AzLk2-kWyY lesson 3.2. |
| Write rules like the note you would leave whoever covers your vacation. | Odd little rules included. That is the material the AI would never work out on its own. | iBPe14UitSk. |
| "Not sure" and "what can you do with this" are fine openers. | | `BRIEF.md` Your first week. This is ours, not his. |

## Not in the sources

The writer does not invent any of these. Where the page needs one, it leaves it out or marks it as ours.

- **Measured results.** No source gives a measured time saving, cost saving or outcome for a beginner. The figures that appear (tokens cut "by like 97%", cost cut "up to 90%", one agency's spend from $10,000 to $400 a month, "95% of AI initiatives yield zero return") are self-reported, unsupported on screen, or cited from memory, and the source extracts flag each one. None goes on the page. (KFmnlS9Y3qo; NWyTsKTKka8; the channel-mine § Changes over time, item 7.)
- **"Fetched content is data, not orders."** `BRIEF.md` states this rule for the blueprint (Privacy). No Jake source teaches it. His "keep method apart from facts" (idea 12) is about file drift, not about untrusted content. Do not present the security rule as his.
- **A hard block on send, spend, delete.** He says settings, plan mode and hooks block actions and the map does not. `BRIEF.md` describes the blueprint's boundary as written into files and as "asks first". No source says the blueprint enforces it with a setting or hook. See idea 7.
- **A correction log or a "turn corrections into a skill" skill in the blueprint.** He teaches it (idea 10). `BRIEF.md` lists no such skill. The nearest is the gap finder.
- **An undo history, a doctor, or a list of human sign-ins.** All three are blueprint facts (`BRIEF.md`). His nearest ideas: an archive folder the AI never reads and never deleting originals (idea 12); "who can open it is a permissions thing, the folder does not decide that". Nothing closer.
- **A routing-test or freshness-test skill in the blueprint.** He gives four tests (routing, freshness, AI-off, setup). `BRIEF.md` lists a workspace audit and a doctor that checks tools and sign-ins; neither is described as his routing or freshness test. Say the owner can run his tests by hand; do not say the blueprint runs them.
- **Anything about running on an AI service that gives the AI its own computer.** His examples are the Claude desktop app, Claude Code and other vendors on a person's own machine. The one related line: there is "a lot of security in keeping things local" (-CUsfao6m7E) and a local model is the pick when "privacy is the whole point" (6AzLk2-kWyY lesson 1.4). Nothing on cloud services that give an AI a computer. The page's "two ways to run it" is ours.
- **Six filing styles, three routing files, thirty-nine skills, the gap finder, the outbound check.** All blueprint facts. He names three folder shapes (stages, records, wiki) and says his skill knows six; the blueprint's six styles are a different list (military, by stage, by client or project, PARA, numbered index, by date). Do not line them up as the same six.
- **Jake and the teaching kit.** The kit files (01, 03, 04) carry no author name. Do not credit the kit to him and do not credit him with the kit's "What to Load / Skip These" table. The kit's routing table and his map's routing table are the same idea from two sources; the page may say the idea appears in both without saying one came from the other.
- **Jake's opinion of this blueprint, Six20AM, or Claude Code as a product.** None in any source.
- **His own product, community or courses.** He runs a paid community, a hosted app in alpha, and a 12-week cohort. None of it is on the page. Credit him once by name and channel link, nothing more.
- **Privacy of a cloud chat.** Not in his sources beyond the two lines above.
- **Mac or Windows setup, installers, sign-ins.** Blueprint only.
- **Jake's channel link, verified live.** Taken from the handle in two source files, not fetched for this brief.
- **The voice-model video (ABeo1kKueRs).** Read as instructed. It is about cloned narration voices and cloud versus local models; nothing in it teaches a beginner how to use an AI. Not used.
