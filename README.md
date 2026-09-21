# agent-record

An agent that opens your repo knows your code. It knows nothing about the person, the
business or the research project that code serves.

So when you ask it for a CV bullet, a client proposal, an invoice line, a grant section or
a methods paragraph, it writes something plausible. Two years and nine months becomes "just
over three years". A migration nobody measured acquires a 40% improvement. A responsibility
nobody held appears because the paragraph had a gap and prose abhors one. The output reads
well, it is false, and it goes out under a human's name.

A **system of record** is a repo — or a layer inside one — that holds the authoritative
account of the real thing, so that every claim in an outgoing document has somewhere it has
to come from. It does not make invention impossible. **It makes invention refusable**, which
is the most any convention can offer and considerably more than nothing.

This marketplace packages that convention as a skill, for Claude Code, Codex, Cursor, Gemini
and anything else that can read a `SKILL.md`.

## The six rules

**1. Sources and renderings are different layers.** Sources are authored Markdown, kept
current, written to be read by an agent; the current truth lives there and nowhere else.
Renderings are what comes out — CVs, letters, proposals, decks, invoices, reports — plus
documents received from outside and filed as-is. A rendering that disagrees with its source
is a bug in the rendering, which decides every conflict between a PDF and a source file. The
one asymmetry is the received document: a signed contract is evidence, so there the arrow
reverses and a disagreement is a bug in the source file.

**2. Every claim in an outgoing document traces to a source file.** Not to memory, not to
the session transcript, not to what is obviously true — to a file, by path, that a reader
can open. Three ways this rule gets broken, named so they can be refused: rounding a number
up, inventing a metric, and writing plausible filler where a specific is missing. The third
is the common one, and the fix is to surface the gap as a question rather than to fill it.
When a human states something new mid-session, the source file is written **first**, then
used.

**3. A durable fact surfaced in a session is written in that session.** A fact left in the
transcript dies when the session ends, and the next agent invents around the hole it left.
Durable means still true and still worth knowing next month. The rule also assumes
concurrent writers: commit small and often, and re-read `git log` before assuming the tree
is as you left it.

**4. Uncertainty is marked, literally and greppably.** Exactly two markers — `[inferred]`
for something derived rather than confirmed, and `[unknown: <question>]` where the text is
the question to ask. Never silently drop one, and never guess past one: an `[unknown:]` in a
source must not become a specific in a rendering. One grep over the record lists everything
unconfirmed, which is both the health check and the interview worklist. Unresolved markers
are the normal state, not a failure — a record with none is a record nobody has been honest
in.

**5. Every fact type has one declared destination.** The repo carries a routing table — fact
type on the left, path on the right — under a literal `<!-- record:routing -->` anchor, so a
checker can find it without guessing at heading wording. The rows are the repo's own: a
career record, a client book and a research project route entirely different things. Add a
row the first time a fact arrives with nowhere to go, rather than inventing a one-off
destination for it.

**6. The perimeter says what never enters; inside it, be candid.** The two are a pair.
A record that hedges is useless, because an agent that cannot see what someone actually
wants, earns or thinks went wrong gives advice worth nothing — and that frankness is only
safe because a boundary was declared first, under a `<!-- record:perimeter -->` anchor.
Git history is permanent: a file committed and later deleted stays in the history, and a
repo that is private today may not be later. Named third parties are described by role and
observable behaviour, never characterised personally.

Rule 6 is the one the convention will not let a repo waive. A repo decides what its
perimeter contains; it does not get to skip having one.

## What ships

| Skill | Purpose |
|---|---|
| `maintaining-a-system-of-record` | The convention. The six rules, how to tell a record layer from code, and what belongs to the adopting repo rather than to the skill. |
| `bootstrapping-a-system-of-record` | The front door. Four interview questions, then a scaffold: the agents file, the routing destinations, the checker and a generated pre-commit hook. |

Both ship in one install. The bootstrap skill runs once; the convention skill is what the
repo lives by afterwards.

**If you cannot name a document that comes out of your repo, stop here.** A record with no
renderings is a notebook, and a notebook does not need this convention.

The bootstrap interview is four questions, asked one at a time, each answer written down
before the next is asked. **Question 3 — what is sensitive, and is this repo public — is a
gate: nothing is committed until it is answered**, because the first commit is the only
cheap moment to get the perimeter right and every later one costs a history rewrite.

## Install

**Claude Code**

```
/plugin marketplace add alvaro-francisco-gil/agent-record
/plugin install system-of-record
```

**Codex / Cursor** — the repo ships `.codex-plugin/` and `.cursor-plugin/` manifests that
point at the same `skills/` directory.

**Any other agent** — clone the repo and point your agent at `skills/`, or copy a skill
directory into wherever your tool keeps skills. Each skill is a single Markdown file with
YAML frontmatter; the bootstrap skill's assets are one Python script, one shell script and
one Markdown template, none with third-party dependencies.

> **Verified in Claude Code; inferred elsewhere.** This marketplace has been added from
> GitHub and the plugin installed from it, and `claude plugin details` reports both skills
> in the component inventory. That is one tool. The Codex, Cursor and Gemini manifests
> follow the shape a published plugin uses and `scripts/validate.py` checks that each one
> parses as JSON, that every skill's frontmatter is loadable and names its own directory,
> and that the version has not drifted across the four manifests that carry one — but it
> does not check a manifest against any schema, and **no Codex, Cursor or Gemini install
> has been observed.** If one misbehaves, open an issue.

## What the tooling covers, and what it cannot

The bootstrap scaffolds two checks, and both are deliberately narrow.

`scripts/record-check.py` — copied into the adopting repo, generic — lints marker syntax and
verifies that both anchors are present in the agents file. It never guesses what is
sensitive, so it cannot fire on content, and it treats unresolved markers as the worklist
rather than as failures. A bare `[unknown]` with no question is an error; forty open
questions are not. **It scans `*.md` and nothing else**, and it skips the agents file in the
marker sweep because that file is where the two markers are defined — so a marker in a
`.txt`, a `.csv`, a notebook or the agents file itself is invisible to it. Keep the record in
Markdown, or widen the glob in your copy.

`.githooks/pre-commit` — generated at bootstrap from the perimeter answers, because every
perimeter rule depends on a layout only that repo has — refuses oversized files, forbidden
paths and forbidden content patterns in the staged blobs, including a file that arrives at a
forbidden path by being renamed into it. It catches the careless case, not
a determined one. **The content rule only ever applies to text**: `grep -I` discards a blob
at its first NUL byte, so a UTF-16 document, or a `.md` carrying a pasted binary run, passes
that rule unexamined — reported clean because the check could not see it, rather than
because it was. `core.hooksPath` is local config and is never committed, so a fresh clone
has no perimeter check until someone sets it again on that machine.

**The evidence rule is the one no script can check.** No tool can read "led a team of six"
and know whether the team had six people. That is why a passing check suite is never
evidence that a document is honest — the mechanical checks exist to cover the mechanical
rules, so that attention is free for the one that matters.

## A worked example

Invented, deliberately — a small consultancy's record, where `clients/` holds the sources
and proposals are the renderings.

A proposal needs one paragraph about a past engagement. With no record in the repo, an agent
writes this, and it is fluent:

> Over an eighteen-month engagement we cut their nightly batch runtime by around 40% and
> trained a team of six on the new pipeline.

Three numbers, none of them from anywhere. Eighteen months is a guess shaped like a fact,
40% is a percentage that fits the sentence, and six is the size a team usually is.

With a record, the same request starts by reading the source:

```markdown
<!-- clients/orchard/engagement.md -->

- Ran 4 March – 30 May 2025. Evidence: `contracts/orchard/sow-signed.pdf`.
- Nightly batch: 51 min → 34 min on the same input volume.
  Evidence: `evidence/orchard-batch-runtime.md`.
- Handover sessions: two, delivered on site.
  [unknown: how many people attended the handover sessions?]
```

So the paragraph becomes:

> In an engagement running from March to May 2025 we took the nightly batch from 51 to 34
> minutes on the same input volume, and delivered two on-site handover sessions.

Shorter, duller, and every clause in it is openable — including the dates, which stay as
months rather than rounding up to the "three months" that 4 March to 30 May is not quite.
The team size is simply absent, because Rule 4 says a marker does not become a specific,
and the `[unknown:]` stays in the file until the human answers it — at which point it
becomes a fact the next proposal can use.

Note what the record bought that is not visible in the paragraph: the next agent, in six
months, does not have to ask again.

## Layering

The skill defines the convention and nothing else. Everything specific to your repo — which
directories are the record, which fact types route where, what the perimeter excludes, which
two words your markers use if you keep the record in another language — belongs in your own
agent instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent), **which win wherever they
differ.**

The one exception is Rule 6. Your instructions declare what the perimeter contains; they
cannot declare that the repo does not need one.

## Licence

MIT. See [LICENSE](LICENSE).
