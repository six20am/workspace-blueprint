# Filing styles

Six ways to lay out folders. The person picks one in setup. The three routing files (map, router, one `CONTEXT.md` per workspace) work the same under all six. Only the folder names and nesting change.

Each sample below uses a photographer with three kinds of work: shoots, editing, and client delivery. Swap in the person's own workspaces.

## Military

Numbered sections, each with one fixed job. Everything has one home and a number. Suits people who think in chain of command and standing procedure.

```
workspace/
├── S1-admin/          contracts, invoices, calendar
├── S2-intel/          research, competitors, ideas
├── S3-operations/     shoots, editing, delivery (the work)
│   ├── shoots/
│   ├── editing/
│   └── delivery/
├── S4-supply/         gear lists, presets, templates
└── S6-comms/          email drafts, social posts
```

## By stage

Folders follow the work as it moves from start to finish. Suits anyone whose work runs as a pipeline. **This is the default when the person is not sure.**

```
workspace/
├── 01-intake/         what came in: briefs, requests
├── 02-shoots/         the raw work
├── 03-editing/        work in progress
├── 04-delivery/       finished, sent to the client
└── reference/         presets, templates, voice
```

## By client or project

One folder per client, the same sub-folders inside each. Suits agencies, freelancers, anyone whose work belongs to someone else.

```
workspace/
├── clients/
│   ├── smith-wedding/
│   │   ├── brief/
│   │   ├── shoots/
│   │   ├── editing/
│   │   └── delivery/
│   └── acme-headshots/
│       └── (same four)
├── templates/         the four folders, empty, to copy
└── reference/
```

## PARA

Four folders sorted by how active something is: Projects (has a deadline), Areas (ongoing), Resources (useful someday), Archive (done). Suits general knowledge work and personal use.

```
workspace/
├── projects/          smith-wedding, acme-headshots
├── areas/             editing, gear, bookkeeping
├── resources/         presets, lighting notes, contracts
└── archive/           finished projects, old areas
```

## Numbered index

Ten top-level ranges, numbered folders inside. Find anything by its number. Suits people with a lot of reference material.

```
workspace/
├── 10-19 Business/
│   ├── 11 Contracts/
│   ├── 12 Invoices/
│   └── 13 Taxes/
├── 20-29 Shoots/
│   ├── 21 Weddings/
│   └── 22 Headshots/
├── 30-39 Editing/
└── 40-49 Reference/
```

## By date

Year, then month, then the item. Suits journals, content calendars, anything driven by when it happened.

```
workspace/
├── 2026/
│   ├── 09/
│   │   ├── 2026-09-14-smith-wedding/
│   │   └── 2026-09-20-acme-headshots/
│   └── 10/
└── reference/
```
