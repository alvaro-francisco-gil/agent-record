# A register for dated obligations

**Priority:** medium

## Goal

Ship an optional register of every dated obligation that costs something when missed,
plus a dependency-free script that lists what is overdue or closing soon, so a deadline
in a record stops depending on someone rereading the right file.

## Context

Records hold dates with penalties attached: tax filings, insurance renewals, inspection
due dates, certificate and domain expiries, claim windows. The convention routes each
fact to one place, but a date written in prose is only seen when someone opens that
file. In one adopter's record, a filing deadline that a plan tracked in prose was still
missed. That record now keeps one machine-readable register that a script reads at the
start of every session, and the prose links to it instead of restating the date.

This is the convention's own single-source rule applied to time. It generalises to
every pack in `domain-starter-packs`: a vehicle has inspections and renewals, a business
has filings, a career has certificate expiries.

## Design / approach

- `assets/obligations.yaml`: a header documenting the fields (`id`, `what`, `opens`,
  `closes`, `if_missed`, `how`, `explained_in`, `done`, optional `only_if`, `group`),
  with no entries.
- `assets/agenda.py`: copied unchanged, bare Python 3, no dependencies. It reads the
  register and prints overdue items and items closing within N days. It exits non-zero
  when something is overdue, so a hook or CI can use it.
- The bootstrap asks, during question 4, "what in this record has a date that costs you
  if you miss it?" A yes installs the register and adds a line to the agents file: run
  the agenda at the start of every session and raise what it lists before the task.
- Recurring obligations are written out one occurrence per period, a year ahead. Simple
  to read, and the script stays trivial.

## Open questions

- **Alerts outside a session.** The agenda only helps when a session starts. Should push
  delivery (chat bot, email, calendar feed) be in scope, and which channel works for
  someone who never opens a terminal? An `.ics` export is the most portable.
- Does `agenda.py` need tests in `tests/` like `record-check.py`? It ships to strangers,
  so it probably does.
- Does it belong in the bootstrap or in a separate skill a record adopts later?
