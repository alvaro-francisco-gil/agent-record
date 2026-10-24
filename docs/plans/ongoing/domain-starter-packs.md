# Starter packs per domain

**Priority:** medium
**Gate:** blocked:first real bootstrap from a clean install (recheck 2026-11-15)
**Next:** in the same clean-install bootstrap, confirm a pack is offered after question 1, its rows are offered one at a time, and only justified skills are proposed

**Goal:** The bootstrap offers a starting routing table and set of questions per domain,
so the interview starts from a sensible shape instead of a blank page. A record stays
one skill; the pack is what changes.

## Context

Comparable "about me" repos ship templates, and adopters ask what goes where. The
convention is meant to fit very different records. A person's career, a newly
self-employed person's business, and a single physical asset such as a vehicle all
share the six rules, but their routing tables share almost nothing. AGENTS.md forbids
invented example records in this repo, so a pack can hold only **empty structure**:
directory names, routing rows and the questions to ask, never sample facts.

Question 1 also turns away records that need this most. "A record with no renderings is
a notebook" is right, but people don't recognise their renderings. An asset record
does produce documents: the bundle assembled for an inspection, an insurance claim, a
sale, a regulatory approval.

## Design

- **Location:** `skills/bootstrapping-a-system-of-record/assets/packs/<domain>.md`.
  Each holds a routing table with placeholder destinations, the domain's common
  sensitive categories (as prompts for question 3, never as the answer), its typical
  renderings, and 3–5 domain questions. No content.
- **First packs:**
  - `career`: profile and narrative, experience, credentials and diplomas,
    applications, CVs and letters.
  - `self-employed-business`: the business's identity and registrations, clients,
    invoices issued, expenses and receipts, tax filings and social contributions,
    suppliers, contracts. Categories only, never a country's form numbers: the
    jurisdiction comes from the interview.
  - `vehicle-or-asset`: identity and ownership papers, inspections, insurance,
    maintenance and repairs, modifications and their approvals, running costs.
- **Picked after question 1.** The bootstrap names the closest pack, or none. Question
  4 then starts from the pack's rows, and the human keeps, renames or drops each one.
  **Every row can be overridden**, and the "four to ten rows" rule still holds: a pack
  is a menu, not a layout to install whole.
- **Question 1 wording:** add that renderings include bundles assembled for a third
  party (inspector, insurer, buyer, accountant). Ask "who do you ever have to send
  documents to?" before concluding a record is a notebook.
- **No pack, no problem.** Anything unmatched runs the interview as today.
- **Skills to install, chosen by the agent and confirmed by the human.** Each pack lists
  the skills that commonly help its domain, from a small catalogue in
  `assets/skill-catalogue.md`. The catalogue names each skill's plugin, its install line
  and one line on when it helps: `plans-lifecycle` for a record with ongoing work,
  `obligations-register` once it exists, others as they ship. After question 4 the agent
  proposes only the skills the answers justify, one reason each, for example "you
  mentioned three renewal dates → the obligations register". It installs what the
  human accepts. Install at **project scope**, so the choice is committed with the repo
  and a second clone or collaborator gets the same skills. The routing table and the
  skill list grow the same way: add one the first time a need shows up, never
  speculatively.
  - **Anti-pattern: installing the whole catalogue.** Every loaded skill competes for
    attention. A skill nobody needs is noise in every session.
  - **Anti-pattern: catalogue entries for skills that don't exist yet.** Add an entry
    only when the plugin is installable.
- Mention the packs in `README.md`'s restatement of the bootstrap. Bump the version in
  all four manifests.

## Out of scope

- Jurisdiction-specific packs, such as one country's tax calendar. They need facts, not
  structure, and drift with the law. They belong in the adopter's own repo, or in a
  separate plugin maintained by someone who files those returns.
- Packs narrowing the interview too early. Resolved: the pack is offered after question
  1, and question 4 overrides every row.

## Handoff

Built in 1.3.0 (2026-10-24). Verified so far only by `validate.py`, the test suite and a
scratch run of the copied assets; this repo's bar for "verified" is a clean install with
the behaviour observed. Retire once that bootstrap is seen to work.
