# Setup playbook

The names of the map file, the router file, the section notes file, the skills folder and the shell on this platform are in `setup/platform.md`. Read it before step 0.

You are setting up this workspace for a person who may never have used a tool like this. Keep every message short. Ask one question at a time. Never show them a file path unless they ask. Never type a credential.

## 0. Read the report

Open `setup/setup-report.md`. If it does not exist, the installer was not run; say so in one line and go to step 1 anyway. The tools can be installed later.

Tell the person, in three lines at most:
- what installed,
- what failed (just the count and the names),
- what needs them to sign in (just the names).

Then ask: "Want me to fix the failed ones now, or after we set up your folders?" Default is after. Do not re-run anything that is marked installed or present.

## 1. The four questions

Ask them one at a time. Wait for the answer before the next. Each has a "not sure" answer; if you get one, say what you picked and move on.

**Q1. "What do you do?"**
Free text. Use the answer to name things and to pick examples in the files you write. "Not sure" is not an option here; if they give one word, that is enough.

**Q2. "What are the two or three kinds of work you would hand to an assistant if you had one?"**
Free text. Each answer becomes a section of their one workspace: its own folder and its own section notes file, so you load only what that kind of work needs. Say "section" to the person, never "workspace", for these; to them the workspace is the whole folder. Two is fine, three is better, more than four means ask them to pick the top three. "Not sure": pick three from Q1 and say them back; let them correct you.

**Q3. "How do you like things filed?"**
Read `setup/filing-styles.md`. Show the six names, each with its one-line "suits" sentence. If they want to see one, show its sample tree with their own sections swapped in. If they pick two styles, combine them: the first sets the top level, the second sets the layout inside the folder where the work happens, and show the merged tree before building. "Not sure": by stage.

**Q4. "When I write for you, how should it sound?"**
Three choices: plain and direct, warm, formal. Or they can paste something they wrote. "Not sure": plain and direct.

## 2. Build

Do this without asking more questions. Tell them you are building and that it takes a minute.

1. **Folders.** Create the tree for the chosen style with their sections from Q2. Use the sample in `setup/filing-styles.md` as the pattern. Lowercase, hyphens, no spaces in folder names unless the style itself uses them (Numbered index does).
2. **The map file.** Overwrite the template version. It becomes the map: what this workspace is (one line from Q1), the folder tree, a quick navigation table (task from Q2, folder to go to), file naming rules (`[topic]-[status].md`, statuses `draft`, `review`, `final`), and where files land. Keep it under 150 lines. The shape is the map file in `_reference/example-workspace/`; the content is theirs. Delete the "not set up yet" block.
3. **The router file** at the top level. The router: a table with one row per section: the task, the folder, what else to load. Under 50 lines. Shape: the router file in `_reference/example-workspace/`.
4. **One section notes file per section.** Follow `_reference/03-context-md-anatomy.md` exactly: what this section is, a what-to-load table with a skip-these column, the folder layout, the process, where tools plug in, what not to do. Name the skills from the skills folder that fit this section in the "where tools plug in" section with a trigger, not just a mention.
5. **`voice.md`** in the reference folder of the chosen style (or `reference/` if the style has none). From Q4: three or four rules, a short sample paragraph in that voice, and three things never to do. If they pasted a sample, pull the rules from it.
6. **Keep `setup/`, the skills folder, `tools/` and `_reference/` where they are.** Do not move or delete them. The `update` skill replaces them in place later; the person's own files are never in its path.
7. **One line in the map file about updates:** "When `setup/version.json` is more than 30 days old, offer the `update` skill once." That is how the workspace keeps getting new skills and tools.
8. **Starting rows.** Match what the person said in Q1 and Q2 against this table. Write each skill it names as a row under "where tools plug in" in the section notes file it fits, with a trigger.

| The person said | Rows to write |
|---|---|
| photos, images, pictures | `media-tools`, `photo-organizer`, `image-search` |
| books, invoices, receipts, bookkeeping, money | `money-log`, `paperwork`, `document-builder` |
| writing, posts, newsletter, social | `writer`, `social-copywriter`, `voice-extractor` |
| research, reports, competitors | `deep-research`, `summarize`, `meeting-prep` |
| video, podcast, recordings | `video-watcher`, `channel-mine`, `media-tools` |
| letters, forms, mail, bills, notices | `paperwork`, `explain-this`, `writer` |
| travel, trips, bookings | `trip-plan`, `summarize` |
| job search, resume, applications | `resume-and-letter`, `meeting-prep` |
| meetings, clients, calls | `meeting-prep`, `summarize`, `weekly-brief` |
| anything else | `summarize`, `writer` |

A row for a skill that is not in the skills folder yet is still written; the skill lands with `update`.

## 3. Fix

If they said "now" in step 0, work through the failed tools one at a time. For each: say what it is for in one line, then re-run the installer for just that tool. Its `id` is in `setup/tools.json`:

- Windows: `powershell -ExecutionPolicy Bypass -File setup/setup.ps1 -Only <id> -Yes -NoLaunch`
- Mac: `bash setup/setup.sh --only <id> --no-launch`

On a Grok Bot: `bash install.sh --only <id>`.

Do not run the install commands from `tools.json` by hand; they use helpers that exist only inside the installer. Each run rewrites `setup/setup-report.md`, so read it again afterwards rather than editing it. Say whether it worked. If it fails twice, tell the person what you tried in one line and move on.

For anything under "Sign in yourself", tell them the one thing to do, in their words, and stop. You never sign in for them.

## 4. Test

Pick one real task from Q2. Say "Let me try one thing so we know it works." Do the task. Then check, yourself, that:
- you loaded the right section notes file and nothing else you did not need,
- the output file landed where the map file says it should.

If either is wrong, fix the routing file, not the task, and say what you changed.

## 5. Close

Run the `doctor` skill first. Until it ships, read `setup/setup-report.md` instead.

Then say, in this order:
1. "Your workspace is ready." One line on what it has: the sections by name.
2. The first-week card: five things to try this week, each one sentence, drawn from the four answers.
3. The sign-in list from doctor or the report, if any, as "Two things need you: ..."
4. "If you ask for something I have no tool for, I will say so and offer to build one."

Then stop. Do not keep going on your own.
