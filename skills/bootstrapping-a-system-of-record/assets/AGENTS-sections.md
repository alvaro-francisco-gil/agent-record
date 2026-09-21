<!--
TEMPLATE - the sections a system-of-record repo carries in its agents file
(AGENTS.md, CLAUDE.md, or whatever this repo already uses).

Fill every <ANGLE BRACKET> from the interview. Delete this comment block, delete
any section the repo genuinely does not need, and rewrite the prose in the
repo's own voice - it is owned by the repo from the first commit, not by the
skill that wrote it.

Two strings are not yours to edit: `<!-- record:routing -->` and
`<!-- record:perimeter -->`. scripts/record-check.py looks for them by exact
text, and a reworded anchor fails silently.

Retrofitting a repo that already has an agents file: do NOT paste this over it.
Read what is there, add the anchors and only the sections that are missing, and
keep the existing wording.
-->

## What this repo is

<ONE OR TWO SENTENCES from question 1: whose record this is, and what it is the
authoritative account of.>

It holds two layers, and the difference matters more than any other rule here:

- **Sources** — authored Markdown, kept current, written to be read by an agent.
  Chiefly <SOURCE DIRECTORIES>.
- **Renderings** — <THE OUTGOING DOCUMENTS: CVs, proposals, invoices, reports,
  decks> generated from the sources, plus documents received from outside and
  filed as received: <RECEIVED DOCUMENTS: signed contracts, certificates,
  statements>.

**A rendering that disagrees with its source is a bug in the rendering.** For a
received document the arrow reverses: the document is the evidence, so the bug
is in the source file.

<ONLY IF THE RECORD IS A LAYER INSIDE A CODE REPO — delete otherwise:>
**The record layer is `<PATH>`.** Everything outside it is code. The record layer
declares its own boundary here, and code never reaches into it for facts it
should be passed.

## Read `<ENTRY SOURCE FILE>` first

Before answering anything about <THE SUBJECT OF THE RECORD>, read
`<ENTRY SOURCE FILE>`. It is the entry point and it links out to everything else.
Do not reconstruct context from a rendering; a generated document was true on the
day it was generated, and it is not where the current truth lives.

<!-- record:routing -->

## Where a fact goes

When something durable surfaces, it goes here:

| Fact | Goes to |
|---|---|
| <FACT TYPE> | `<PATH>` |
| <FACT TYPE> | `<PATH>` |
| <FACT TYPE> | `<PATH>` |

Add a row the first time a fact arrives with nowhere to go. Never invent a
one-off destination instead of adding the row.

## The evidence rule

**Every claim in an outgoing document traces to a source file** — one under
<EVIDENCE DIRECTORIES>, by path, that a reader can open.

Never round a number up, never invent a metric, and never write plausible filler
where a specific is missing — surface the gap as a question instead, in a marker
or straight to <THE HUMAN>. If something new is stated mid-session, write the
source file **first**, then use it.

This is the rule the repo exists to enforce, and the one no script can check.

## The capture rule

**When a session surfaces a durable fact, write it to the right file in that
session.** A fact that stays in the transcript is lost the moment the session
ends; losing it is the problem this repo was built to solve.

Assume concurrent writers. Commit small and often, and re-read `git log` before
assuming the tree is as you left it.

## Uncertainty markers

Two markers, used literally so they stay greppable:

- `[inferred]` — derived from a document or from reasoning, not confirmed by
  <THE HUMAN>.
- `[unknown: <question>]` — could not be determined. The text is the question to
  ask.

Never silently drop a marker, and never guess past one. Unresolved markers are
the normal state, not a defect. The health check:

```bash
python3 scripts/record-check.py --list
```

<IF THE RECORD IS KEPT IN ANOTHER LANGUAGE: declare its two marker words here and
pass them to the checker with --inferred-marker and --unknown-marker. Always
exactly two; never a third.>

<!-- record:perimeter -->

## Perimeter

This repo is **<public|private>**. Some things stay out, deliberately:

- <CATEGORY THAT NEVER ENTERS> — <where it lives instead>.
- <CATEGORY THAT NEVER ENTERS> — <where it lives instead>.
- <CATEGORY THAT NEVER ENTERS> — <where it lives instead>.

`.githooks/pre-commit` enforces the mechanical part of this — forbidden paths,
forbidden content patterns, oversized files. **Never bypass it with
`--no-verify`.** If it blocks something legitimate, change the rule in its own
commit. It catches the careless case, not a determined one; the perimeter is a
decision, and the hook is only a reminder of it.

**Git history is permanent.** A file committed and later deleted remains in the
history, and a repo that is private today may not be later. Treat every commit as
publication to anyone who ever gains access.

Named third parties are described by role and observable behaviour, never
characterised personally. The same holds for anyone who cannot consent to being
written about: the role, the event and the date, not the person.

Inside the perimeter, be candid. <WHAT CANDOR MEANS HERE: rates, frank
self-assessment, what actually went wrong, real intent.> An agent that cannot see
what is actually wanted gives advice worth nothing.

## Repo health beats every rule above

If a rule here makes the repo worse for a specific change, break the rule and
update this file in the same commit. Rules exist to keep the repo coherent, not
to be obeyed mechanically.

**Except the perimeter.** It is an obligation to people who are not in the room.
If it is genuinely wrong it changes deliberately, in its own reviewed commit,
before the thing it would have blocked is committed.
