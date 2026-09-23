---
name: maintaining-a-system-of-record
description: "Use when a repo holds the authoritative record of something real — a person's career, an organisation's accounts, a business's clients, a research project's methods — whether that is the whole repo or a layer inside a code repo. Defines the two layers (sources and renderings), the evidence rule, the capture rule, the [inferred]/[unknown:] markers, and the perimeter every adopting repo must declare."
---

# Maintaining a system of record

A **system of record** is a repo, or a layer inside one, that holds the authoritative
account of something real — a person's career, an organisation's accounts, a business's
clients and suppliers, a research project's methods — and from which outgoing documents
are generated.

It exists to prevent one specific failure. An agent that opens a repo knows the code and
knows nothing about the person, business or project the code serves. Asked to write a CV,
a proposal, an invoice, a grant section or a methods paragraph, it writes something
plausible: a number rounded to a rounder number, a metric nobody measured, a date that
fits the story. The output reads well and is false, and it goes out under a human's name.
**A record layer does not make that impossible — it makes it refusable**, by giving every
claim somewhere it has to come from, so an invented one has nowhere to hide.

Six rules:

1. Sources and renderings are different layers.
2. Every claim traces to a source file.
3. A durable fact surfaced in a session is written in that session.
4. Uncertainty is marked, literally and greppably.
5. Every fact type has one declared destination.
6. The perimeter says what never enters; inside it, be candid.

> **Layering.** This skill defines the *convention*. Everything specific to a repo — which
> directories are the record, which fact types route where, what the perimeter excludes,
> which words the uncertainty markers use — belongs in that repo's own agent instructions
> (`AGENTS.md`, `CLAUDE.md`, or equivalent), **which win over this file wherever they
> differ, except Rule 6** — a repo declares the perimeter's content, but cannot waive the
> obligation to have one. Referred to below as *the repo's instructions*.

## Locating the record layer

The convention fits two shapes, and a repo must know which one it is.

- **The record is the whole repo.** Nothing in it ships; everything in it is either a
  source or a rendering. A career repo, a household's or an association's paperwork, a
  consultancy's client book, a personal archive.
- **The record is a layer inside a code repo.** The code ships. The record layer holds the
  facts about the real thing the code serves. Examples of the shape: a research toolkit
  whose record layer is its context docs plus one directory per study; a mobile app whose
  business registry — funding calls, deadlines, potential collaborators — sits in its own
  top-level directory with its own agents file, read by an internal panel.

The test for drawing the boundary: **would this fact still be true if every line of code
were deleted and rewritten in another language?** If yes, it belongs to the record. A
study's field dates, a client's agreed rate, a grant's deadline, a person's degree — all
record. A module's interface, a query's shape, a build step — all code.

**The record layer declares its own boundary in the agents file, and code never reaches
into it for facts it should be passed.** When the layer is large enough to have its own
conventions, give it its own agents file in its own directory, so an agent working there
loads the record rules without loading the whole engineering file.

**It also declares where to start reading.** Name one source file as the entry point — the
current state, with links out to everything else — and say in the agents file that it is
read before anything else about the subject. Without it an agent reconstructs context from
whatever it opens first, and what it opens first is usually a rendering: a CV, last year's
report, a past proposal. Every rule below assumes the reader found the sources.

- **Anti-pattern: hard-coding a record fact into code.** A study's dates baked into a
  library function, a client's address inside a rendering script, a rate constant in a
  template. The fact now has two homes and they will disagree. Pass it in from the record.
- **Anti-pattern: a record layer with no declared boundary.** If the agents file does not
  say which directories are the record, every rule below is unenforceable, because nobody
  can tell what is covered.
- **Anti-pattern: no entry point.** A reader who has to guess where the current truth lives
  guesses wrong in the direction of whatever document looks most finished.

## Rule 1 — sources and renderings

The record has exactly two layers, and telling them apart matters more than any other
distinction here.

- **Sources.** Authored, kept current, written to be read by an agent. Usually Markdown.
  The current truth lives here and nowhere else.
- **Renderings.** Outgoing documents generated from the sources — CVs, letters, proposals,
  decks, invoices, reports — plus documents received from outside and filed as-is: signed
  contracts, diplomas, statements, certificates.

**A rendering that disagrees with its source is a bug in the rendering.**

That sentence decides every conflict. When a PDF says one thing and the source file says
another, the source is right by construction; the PDF is stale output. Never reconstruct
context by reading a rendering — a CV, a deck, a past proposal — because it was true on
the day it was generated and has been decaying since.

Received documents are the one asymmetry. A signed contract is a rendering nobody may
regenerate: what it establishes is read out into a source file, and the document itself is
filed unchanged as the proof. **For a received document the arrow reverses** — the document
is the evidence, so a disagreement is a bug in the source file, and reading it for what it
establishes is exactly the point. The warning above is about generated renderings, which
carry no authority of their own.

**When a source turns out to be wrong, correct it forward.** A rendering is regenerated,
but a source that was wrong is part of the record's history: add the correction with the
date and what changed, rather than quietly editing the original to match what is true now.
A record is trusted because its history can be read back; an entry rewritten in place makes
every other entry a question. A typo is a typo — but a changed *fact* is an event, and
events are appended.

- **Anti-pattern: hand-editing a rendering to fix a number.** The next regeneration
  silently reverts it, and in the meantime two documents make two different claims. Fix
  the source, regenerate.
- **Anti-pattern: a fact that exists only inside a rendering.** If the only place a date
  or a figure appears is a generated PDF, it is not in the record. Write the source file.
- **Anti-pattern: editing a past entry so the record looks like it was always right.** The
  outgoing documents built on the old figure still exist; now nothing explains them.

## Rule 2 — the evidence rule

**Every claim in an outgoing document traces to a source file.** Not to memory, not to the
session transcript, not to what is obviously true — to a file, by path, that a reader can
open.

The four ways this rule gets broken, named so they can be refused:

- **Rounding a number up.** "Just over three years" for two years and nine months. "Around
  a thousand users" for 840. The rounded figure is the one that gets quoted back.
- **Inventing a metric.** No source records an improvement, so a percentage appears that
  matches the shape of the sentence. It is fabrication whether or not it is flattering.
- **Fabricating the parts of a real total.** The aggregate is sourced — a headcount, a
  revenue figure, a member count — and the breakdown is not, so the parts are invented to
  sum correctly. This is the most tempting of the four, because the total is genuinely
  right and every part looks like arithmetic. It is also the worst, because a plausible
  decomposition *manufactures evidence*: each invented part now reads as sourced. The same
  move in reverse is plugging a gap — **never close a discrepancy by inventing the
  difference. Report the difference.**
- **Writing plausible filler where a specific is missing.** A responsibility nobody
  performed, a tool nobody used, a scope nobody had — inserted because the paragraph had a
  gap and prose abhors one. **Surface the gap as a question instead**, in the record's own
  uncertainty marker (Rule 4) or straight to the human.

**Ordering matters: when a human states something new mid-session, write the source file
first, then use it.** Not afterwards, not "I'll capture that once the letter is done" —
first. A claim used before it is recorded is a claim with no trail, and the letter is
already out the door by the time anyone notices.

**Where a fact came in is part of the fact.** The rule above governs claims going out; the
same discipline applies on the way in. When a fact is written, write its origin beside it —
the document, the message, the person, and the date. A record whose provenance nobody can
retrace is a record nobody trusts in three months, and re-verifying it costs far more than
the note would have.

**This is the one rule a script cannot check.** A tool can verify that a marker is
well-formed, that a routing table exists, that no forbidden file was committed. No tool
can look at the sentence "led a team of six" and know whether the team had six people.
Which is exactly why it is the reader's job, every time, and why a passing check suite is
never evidence that a document is honest. Mechanical checks cover the mechanical rules so
that attention is free for this one.

- **Anti-pattern: treating an earlier rendering as a source.** "The CV says it, so it's
  true" launders a fabrication into a fact. The CV is downstream.
- **Anti-pattern: softening rather than asking.** Replacing a missing specific with a
  vaguer claim that is still unsupported is the same violation with worse prose.

## Rule 3 — the capture rule

**When a session surfaces a durable fact, write it to the right file in that session.**

A fact left in the transcript is lost the moment the session ends. That loss is the
problem this convention exists to solve: the human already knew the fact, and now has to
say it again, and the next agent invents around the gap. A session that produced a good
document and captured nothing has left the record worse than it found it, because the
document now makes claims the record cannot support.

Durable means: still true, and still worth knowing, next month. A new client rate, a
changed deadline, a decision and its reason, a role that ended, an instrument's quirk. Not
durable: what was tried and abandoned in the current task.

**Assume concurrent writers.** More than one session may be editing the record at once,
human or agent. So: commit small and often rather than accumulating a large end-of-session
commit, and **re-read `git log` before assuming the tree is as you left it.**

- **Anti-pattern: batching capture to the end of the session.** Sessions end early, run out
  of context, or get abandoned mid-task. Write the fact when it appears.
- **Anti-pattern: capturing into the chat summary instead of a file.** A summary is a
  rendering of a session. It is not in the record.

## Rule 4 — uncertainty markers

Exactly two markers, used literally so they stay greppable:

```
[inferred]              derived from a document or from reasoning, not confirmed by a human
[unknown: <question>]   could not be determined; the text IS the question to ask
```

The rules on them:

- **Never silently drop a marker.** Removing `[inferred]` is a claim that someone confirmed
  it. Only a human's confirmation earns that edit.
- **Never guess past a marker.** An `[unknown:]` in a source must not become a specific in a
  rendering. It is a hole; a document with a hole is honest, a document with a guess is not.
- **The grep is both the health check and the intake worklist.** One command over the record
  directories lists everything unconfirmed:

  ```bash
  grep -rnE "\[inferred\]|\[unknown:" <record-dirs>
  ```

  `-E` is not optional. In a basic regular expression `\|` is a GNU extension: BSD and
  POSIX grep, which is what macOS ships, read the pattern as the literal text
  `[inferred]|[unknown:` and match nothing — a health check that reports a clean record
  because it is broken. Extended alternation is `|`, and it is portable.

  That command hard-codes the two words this file uses; a record kept in another language
  greps for its own pair.

**Unresolved markers are the normal state, not an error.** A record with none is a record
nobody has been honest in. Only a malformed marker — a bare `[unknown]` with no question, a
third marker word invented on the spot — is a defect worth failing a check over. A check
that fires on the normal state teaches people to bypass it.

**Marker words are per-repo. There are always exactly two.** A record kept in another
language uses that language's two words, declared in the repo's instructions. Never a
third: "probably", "TBC", "verify" and their friends fragment the grep, and a marker that
does not appear in one grep might as well not exist.

**One word may carry both states, if the repo declares it.** A record that writes a single
marker in two forms — bare for *unverified*, with a question for *here is the question* —
has the same two states under one word. Declaring that word as both of the repo's two
markers says so. What Rule 4 forbids is a third *state*, not a second spelling.

**A confidence grade is a different axis, and is not a third marker.** The two markers are a
confirmation *state*: a human has confirmed this, or nobody has. A record assembled from
historical sources of varying quality also needs a fidelity *grade* — how good the
underlying source is — and that is orthogonal. A repo that needs one declares it separately
(see *Three patterns*, below).

**Show the syntax in a fenced block, not in backticks.** Every record repo ends up writing
its own markers in prose in order to document them. A marker in backticks is still a marker
— backticking every marker is the house style in more than one record — so a grep counts it
and so should a checker. A fenced block is quoted syntax; backticks are only typography.

### The intake shape

Resolving markers is a conversation, and the shape of that conversation is the portable
part: **ask in small batches, write each answer immediately, and drive the batch from the
grep.** Five questions, answers written to their files as they arrive, commit, re-grep,
next five.

- **Anti-pattern: asking thirty questions at once.** The human answers three, the session
  ends, and all three are lost because nothing was written down. The long question list
  feels efficient and captures nothing.
- **Anti-pattern: resolving a marker from the model's own reasoning.** That produces
  `[inferred]` at best. Only a human turns `[inferred]` into a plain statement.

## Rule 5 — where a fact goes

**The repo declares a routing table: fact type on the left, destination path on the right.**
It lives in the repo's instructions, under the anchor:

```markdown
<!-- record:routing -->

| Fact | Goes to |
|---|---|
| … | … |
```

The anchor is a literal HTML comment on its own line, immediately above the table. It is
invisible when the file renders, and it lets a checker find the table without guessing at
heading wording — a heading regex breaks the first time someone writes "Routing" instead
of "Where a fact goes".

This skill mandates that the table exists. **The rows are the repo's own** — a career
record, a client book and a research toolkit route entirely different things, and no
generic row list would survive contact with any of them. Write the rows for the facts the
repo actually receives, and add a row the first time a fact arrives with nowhere to go.

- **Anti-pattern: a fact that lands in a plan document instead of the record.** Plans are
  temporary by design and get deleted when the work is done; the fact dies with the plan.
  Plans reference the record, never replace it.
- **Anti-pattern: inventing a destination rather than adding a row.** A one-off directory
  created to hold one fact is a fact nobody will find. Add the row, then file it.

## Rule 6 — the perimeter, and candor inside it

The perimeter and candor are a pair, and neither works alone. **The perimeter says what
never enters the repo. Candor says be frank about everything that does.** A record that
hedges is useless — an agent that cannot see what someone actually wants, actually earns,
or actually thinks went wrong gives advice worth nothing. That frankness is only safe
because the perimeter is real.

**Every adopting repo declares its perimeter explicitly**, in the repo's instructions,
under the anchor:

```markdown
<!-- record:perimeter -->

## Perimeter
```

Same form as the routing anchor: a literal HTML comment on its own line, immediately above
the section. The declaration itself is prose, not a directory listing — what never enters,
and where it lives instead. Three shapes it commonly takes:

- **Everything private.** The whole repo is private and the perimeter excludes categories
  rather than layers: credentials and recovery codes (a password manager), raw identity and
  tax documents, account balances and valuations where only the structure is needed, large
  binaries. Private is not the same as safe — access widens over a repo's life, and history
  never narrows.
- **Public repo, sensitive layer at an external root.** The repo is public and ships;
  the sensitive material sits outside the working tree entirely, at a path given by an
  environment variable, and a pre-commit hook plus a CI job rejects anything that looks
  like it. The layer is read from, distilled in the agent's own words, and never copied in.
  **Never bypass that hook.** If it blocks something legitimate, change the check in a
  reviewed commit.
- **Public repo, private sub-surface.** The repo is public and one bounded part of the
  record — a directory, a submodule, a paired private repo — is not. The boundary is named
  in the instructions, because a boundary nobody can state is a boundary nobody can hold.

Whichever shape: **git history is permanent. A file committed and later deleted stays in
the history, and a repo that is private today may not be later — treat every commit as
publication to anyone who ever gains access.** Adding something to a record is effectively
irreversible, which is why the perimeter is declared before the first commit rather than
after the first mistake.

**The third-party guardrail.** Named third parties are described by role and observable
behaviour, never characterised personally. "The counterparty took three weeks to return
the redline" is a fact worth keeping and belongs in the record. A judgement about who they
are as a person does not, however true it feels, and however private the repo is today.
The same holds for people who cannot consent to being written about — write the role, the
event and the date, not the person.

- **Anti-pattern: candor without a perimeter.** Frank notes in a repo whose boundary was
  never declared is how sensitive material ends up in permanent history.
- **Anti-pattern: a perimeter without candor.** A record sanitised for an audience that
  will never read it answers no real question. The record is not an outgoing document.
- **Anti-pattern: "I'll clean it up before it goes public."** History does not clean up.
  The decision is made at commit time or not at all.

## Three patterns, named but not mandated

None of these belongs in every record, and a repo that does not need one should not carry
it. They are named because each was re-derived from scratch by the second record that
needed it, which is a week that a paragraph saves. Each carries the test for whether it
applies.

**Graded fidelity** — *needed when the record is assembled from historical sources of
varying quality.* Declare a level per file (complete, documentary, summary-only, recalled)
and say what each one means. Two rules make it worth having: **no rendering may aggregate
across levels without saying so** — a total that mixes audited figures with recalled ones is
a fabricated total wearing a real one's clothes — and **fidelity only ever improves**, by
finding a better source, in its own commit. This is the axis Rule 4 does not cover.

**Stable identity** — *needed when the record is about many people or entities tracked over
time.* Give each one an id that is never reused and never renumbered, in an append-only
registry. The id is the person; a slot number, a row position and a filename are not.
**When in doubt, do not merge.** Merging two ids later is an afternoon. Splitting two people
who have been fused for years is close to impossible, and every document generated in
between was wrong about both.

**Readiness counted, not claimed** — *needed when outgoing documents are assembled from many
source files.* Before a bundle goes out, count the unresolved markers across everything it
draws on, and say the count rather than saying "ready". The failure this catches is not
forgetting a proposal; it is believing one is finished.

## Repo health beats every rule above

**If a rule here makes the repo worse for a specific change, break the rule and update the
repo's instructions in the same commit.** These rules exist to keep a record coherent, not
to be obeyed mechanically, and a convention that nobody may amend is one that gets quietly
worked around instead. The amendment is the price: break a rule silently and the next
agent restores it.

**Except the perimeter.** Rule 6 is an obligation to people who are not in the room: whoever
is named in the record, whoever's data was entrusted, whoever reads a permanent history
later. It is not a convention and it does not bend for convenience. If the perimeter is
genuinely wrong, it changes deliberately, in its own reviewed commit, before the thing it
would have blocked is committed — never by working around it in the moment.
