---
name: bootstrapping-a-system-of-record
description: "Use when setting up a repo, or a layer inside one, to hold the authoritative record of a real person, organisation, business or research project — \"I want my agent to know my business\", \"set up a repo for my career\", adopting the system-of-record convention. Interviews, declares the perimeter before anything is committed, then scaffolds."
---

# Bootstrapping a system of record

Sets up a repo — or a layer inside a code repo — to hold the authoritative record of
something real, so that an agent working in it can answer questions about the person,
business or project instead of inventing plausible answers. The convention it installs is
`maintaining-a-system-of-record`; **read that skill first.** Everything below is its six
rules made concrete in one repo.

Two phases, in order: **an interview of four questions, then a scaffold.** The interview is
the work. The scaffold is twenty minutes of writing files, and every file in it is worthless
if the answers were guessed on the human's behalf.

> **Layering.** This skill runs once. What the repo lives by afterwards is the convention
> skill plus the repo's own instructions — written here, owned by the repo from the first
> commit, and winning over both wherever they differ. Write the first version to be edited,
> not to be preserved.

## Question 3 is a gate, not a step

**Nothing is committed until question 3 is answered.** Create the directory, write files,
`git init`, run the interview — all fine. Do not run `git commit`, not once, not for an
empty skeleton, until the perimeter is declared and the hook that enforces it is installed
and verified.

Because **git history is permanent.** A file committed and later deleted stays in the
history, and a repo that is private today may not be later. This is the only cheap moment to
get the perimeter right. Every later moment costs a history rewrite — and for a credential
or an account number, not even that: a secret committed once is a secret to rotate, not a
secret to delete.

- **Anti-pattern: committing a skeleton first and "doing the perimeter properly in a
  minute".** The skeleton commit is harmless. The habit it establishes is not, and the next
  commit is the one with the tax document in it.
- **Anti-pattern: bootstrapping into an existing repo without asking what is already
  committed.** See *The repo already has a record* below; the answer changes what you can
  offer.

## The interview

**Ask one question at a time, and write the answer down before asking the next.** The
capture rule applies to the bootstrap itself: a wall of four questions gets one answer back,
and the session that ends early loses all of it.

Write into the file, not into notes. Copy `assets/AGENTS-sections.md` to the repo's agents
file path before question 1, uncommitted, and fill its placeholders as the answers arrive.
When the interview ends, the agents file is finished rather than waiting to be transcribed.

### Question 1 — What is this record about, and what documents come out of it?

Two halves, and the second is the one people skip. The subject — a career, a consultancy's
client book, an association's paperwork, a research project's methods — says what the
sources are. The outgoing documents say what the sources are *for*: CVs, proposals,
invoices, grant sections, reports, decks.

The answer fills "What this repo is" and names the entry source file, the one an agent reads
before anything else.

If they cannot name a single document that comes out of the repo, say so: a record with no
renderings is a notebook, and a notebook does not need this convention.

### Question 2 — Is it the whole repo, or a layer inside one? Where does that layer start?

The test for the boundary: **would this fact still be true if every line of code were
deleted and rewritten in another language?** If yes, it belongs to the record.

- **The whole repo.** Nothing ships; everything is a source or a rendering. The scaffold
  goes at the root.
- **A layer inside a code repo.** The code ships; the layer holds the facts about the real
  thing the code serves. **The boundary is a path, and it gets named in the agents file.**
  If the layer is large enough to have its own conventions, give it its own agents file in
  its own directory, so an agent working there loads the record rules without the whole
  engineering file — then run the checker as
  `python3 scripts/record-check.py --root <layer> --agents-file <its agents file>`.

### Question 3 — What is the sensitive material, and is this repo public?

**The gate.** Nothing is committed before this is answered. Four things have to come out of
it, because the hook is generated from them:

1. **Public or private** — and private is not the same as safe. Access widens over a repo's
   life and history never narrows.
2. **The categories that never enter, and where they live instead.** This is prose, not a
   directory listing. It becomes the perimeter section.
3. **Path patterns that must never be committed** — these fill `<FORBIDDEN_PATTERNS>` in the
   hook, as shell `case` patterns joined by `|`, for example
   `private/*|secrets/*|*.key|*.p12`.
4. **Content patterns that must never be committed** — these fill `<CONTENT_PATTERNS>`, one
   extended regex, for example an account-number shape, a national ID format, a key prefix.
   If there are genuinely none, leave the placeholder as an empty string and the check
   switches itself off.

People under-answer this question, so ask the concrete versions: what is in the directory
you would close before sharing your screen? Which documents contain nothing but identity and
tax data? Where do credentials live, and is the answer a password manager? What would you
not want read by whoever gains access to this repo in five years — not today's reader,
that one?

Then **say back to them, in plain words, what the hook will block and what it will not**,
and only then move on. A perimeter the human has not heard stated is a perimeter they have
not agreed to.

- **Anti-pattern: accepting "nothing really, it's all fine".** Everyone has a category.
  Offer the common ones — credentials, identity documents, figures where only the structure
  is needed, other people's data, large binaries — and let them rule each one in or out.

### Question 4 — What kinds of fact will arrive, and where does each go?

The routing table: fact type on the left, destination path on the right. **The rows are
theirs.** No generic row list survives contact with a real record.

Start from the facts already mentioned in questions 1 to 3 — those arrived unprompted, so
they are the ones the repo actually receives. Four to ten rows is a healthy first table.
Thirty speculative rows is a table nobody reads, and every row is a directory the scaffold
then has to create.

Tell them the rule that keeps it alive: **add a row the first time a fact arrives with
nowhere to go**, rather than inventing a one-off destination for it.

## The scaffold

In this order. The hook is installed and proven before the first commit, which is the entire
point of the ordering.

1. **The agents file.** The filled template, both anchors intact, in the repo's own voice.
2. **The directories.** One per routing destination, and nothing the table does not mention.
   Git does not track empty directories, so each gets a `.gitkeep`.
3. **`scripts/record-check.py`.** Copied unchanged from this skill's assets. It is the
   generic half of enforcement: it lints marker syntax and verifies both anchors, and it
   never guesses what is sensitive, so it cannot fire on content. Unresolved markers are the
   worklist, not a failure. Pass `--agents-file`, `--inferred-marker` and `--unknown-marker`
   if the repo's answers differ from the defaults.
4. **`.githooks/pre-commit`.** From `assets/pre-commit-perimeter.sh`, placeholders filled
   from question 3, then `chmod +x .githooks/pre-commit` and
   `git config core.hooksPath .githooks`. This is the repo-specific half, and it is
   generated rather than shipped because every perimeter rule depends on a layout only this
   repo has. A shipped generic version would have to guess, and a false positive teaches
   people to reach for `--no-verify`, which is worse than no hook at all.
5. **Verify the hook runs** — the next section, before anything is committed.
6. **The first source file.** If the interview surfaced a real fact, write it down: the
   claim, where it came from, and an `[unknown: ...]` marker wherever a specific is missing.
   One true, sourced fact with one honest gap in it demonstrates the evidence rule and the
   markers together, which is worth more than any amount of prose describing them.
7. **Run `python3 scripts/record-check.py`, then commit.**

- **Anti-pattern: filling the first source file with a worked example.** A plausible invented
  fact in a record is indistinguishable from a real one six months later. Either a fact from
  the interview or an empty file.
- **Anti-pattern: scaffolding directories the routing table does not mention.** An empty
  directory nobody routed to is a destination nobody will use and a row nobody wrote.

## Verify the hook before declaring the bootstrap done

The hook template ships broken on purpose. `<FORBIDDEN_PATTERNS>` unfilled is not valid
shell, so the script dies; filled carelessly, it runs and matches nothing. **A dead hook is
the worst outcome of this whole procedure** — the human believes they are protected and is
not, and they find out from the history.

So prove that it runs, and that each rule bites, before the first commit. Every placeholder
below is quoted, because a real one of them contains a space sooner or later:

```bash
# 1. It runs, and it lets an ordinary file through.
git add "<an ordinary file>"
sh .githooks/pre-commit && echo "pass path OK"

# 2. The path rule bites. Use a throwaway that matches one forbidden pattern.
mkdir -p "<forbidden dir>" && echo placeholder > "<forbidden dir>/probe file.txt"
git add -f "<forbidden dir>/probe file.txt"
sh .githooks/pre-commit || echo "block path OK"
git rm --cached -qf "<forbidden dir>/probe file.txt" && rm -r "<forbidden dir>"

# 3. The content rule bites. Fabricate the value; never probe with real material.
printf '<FABRICATED VALUE MATCHING THE DECLARED PATTERN>\n' > "probe doc.md"
git add "probe doc.md"
sh .githooks/pre-commit || echo "content block OK"
git rm --cached -qf "probe doc.md" && rm -f "probe doc.md"
```

**All three lines must print.** Silence on the first means the script is broken. Silence on
the second or third means that rule matches nothing — which looks exactly like a working
hook.

Step 3 is the one people skip, and it is the one that fails quietly. An unfilled
`<FORBIDDEN_PATTERNS>` is a syntax error and step 1 catches it; an unfilled
`<CONTENT_PATTERNS>` parses, is non-empty, and matches nothing for the rest of the repo's
life. **If the repo declared no content rules, check that the placeholder was replaced with
an empty string** rather than left as `<CONTENT_PATTERNS>`, and skip step 3.

**Build the probe value from the pattern this repo declared**, not from a generic one. A run
of sixteen digits proves nothing against a rule written for an IBAN or a key prefix: the
hook stays silent, and silence at step 3 is indistinguishable from the broken case it exists
to detect. A step that cries wolf is a step that gets skipped, and this is the step nobody
can afford to skip.

The probe names carry a space on purpose. Received documents are named
`Contract Signed 2024.pdf` and `Contrato Firmado Año.pdf`, and a hook that word-splits its
file list, or that lets git C-quote a non-ASCII path, waves through exactly the class of
file it exists to stop. The shipped version reads one path at a time and turns
`core.quotePath` off; if you rewrite the loops, keep these probes and add an accented one.

Then check the three ways an installed hook is still not installed:

- `git config core.hooksPath` prints `.githooks`.
- `ls -l .githooks/pre-commit` shows the executable bit. Git skips a non-executable hook
  without a word.
- `case` patterns match the whole path string, not a path segment. `private/*` catches
  `private/x` and misses `a/private/x`; `*private/*` catches both. `*.key` matches at any
  depth. A pattern that itself contains a space has to be quoted — `"personal notes/"*` —
  or the `case` arm is a syntax error, which is what step 1 above is for.

**Never probe a content pattern with real sensitive material.** Use a fabricated value of
the same shape. A probe file that matches is a file you then have to be certain never got
committed.

### A hook is not a guarantee

**Start with the way it is most often absent: `core.hooksPath` is local config, and local
config is never committed.** The hook script is in the repo; the setting that makes git run
it is not. A fresh clone — the same person's second machine, a collaborator, a CI checkout —
has no perimeter check at all until someone runs `git config core.hooksPath .githooks`
again. Say so in the agents file, where the next clone will read it, and treat it as part of
the setup rather than a footnote.

Beyond that, it catches the careless case: the file dragged into the wrong directory, the
paste that still has an account number in it, the binary nobody looked at. It does not catch
a determined one. `--no-verify` exists, pattern lists are never complete, and committing is
not the only way material leaves a machine — a file attached to an email or a directory
opened on a shared screen is outside its reach entirely.

**The perimeter is a decision the humans hold; the hook only reminds them of it.** Say that
out loud when you install it, so that installing it does not end the conversation about what
belongs in the repo.

## The repo already has a record

The common case. Most adopters have a repo with something in it already, and some of the
convention usually exists there under other names.

**Never overwrite an existing agents file.** Read it in full first — everything that repo
learned the hard way is in wording you would be deleting.

Then, in order:

1. **Map what is there onto the six rules.** Which of the four questions does the file
   already answer? Those are not asked again.
2. **Run the interview for the rest.** Question 3 is still the gate, even here — a repo with
   history has already made perimeter decisions, stated or not, and the job is to get them
   stated. **If material that should be outside the perimeter is already committed, say so
   plainly and do not offer a delete commit as a fix.** History is permanent: the honest
   options are to rotate or revoke what was exposed, or to rewrite the history *and* rotate
   it anyway.
3. **Add the anchors to the sections that already exist.** If the file already has a routing
   table or a perimeter section, put `<!-- record:routing -->` and `<!-- record:perimeter -->`
   above them and change nothing else. Only where a section is genuinely absent do you insert
   the template's.
4. **Add the missing sections in the file's own voice** — its heading style, its register,
   its level of formality. The template is a source of content, not of prose.
5. **Run the checker over the existing tree before the hook goes in.** Expect failures that
   pre-date you. Fix the malformed markers; leave the open ones alone, because they are the
   worklist. **Check `git config core.hooksPath` before assuming the hook is live**: an
   existing repo may already point somewhere else, and every other clone of it has no
   perimeter check until that setting is made there too. Tell whoever else works in the repo,
   in the same message that tells them the perimeter exists.
6. **Do not reorganise.** Existing files stay where they are. Write the routing table that
   describes where things actually live, and move things later, in their own commits, if at
   all.

- **Anti-pattern: pasting the template over a working agents file.** It replaces specific,
  earned rules with generic ones, and nobody will notice what was lost until it is needed.
- **Anti-pattern: a routing table describing the layout you wish the repo had.** The first
  fact routed by it lands somewhere that does not exist.

## Done when

- The agents file carries both anchors, and `python3 scripts/record-check.py` exits 0.
- The perimeter section names what never enters and where it lives instead.
- The hook is executable, `core.hooksPath` points at it, and it has been seen to pass one
  file and block another.
- Every routing destination exists.
- The human has heard, in plain words, what the perimeter covers and what the hook cannot do.
