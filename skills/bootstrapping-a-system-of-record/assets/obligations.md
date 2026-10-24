# Obligations

Every dated obligation that costs something when missed: filings, renewals,
inspections, payment deadlines, expiries, claim windows. **This file holds the
date.** The why and the how stay in the file named under *explained in*, which
links here instead of restating the date. A date written in two places is two
dates sooner or later.

`python3 scripts/agenda.py` lists what is overdue and what closes soon. Run it
at the start of every session and raise what it lists before the task at hand.

Columns:

- **id:** unique and stable, e.g. `inspection-2027` or `insurance-renewal-2027`.
- **what:** one line, what has to be done.
- **opens:** first day it can be done, `YYYY-MM-DD`, or `-` if it can be done any time.
- **closes:** last day, `YYYY-MM-DD`. Keep the nominal date. If the real one moves
  for a weekend or holiday, this file errs early, never late.
- **if missed:** what it costs.
- **explained in:** the file that owns the reasoning, or `-`.
- **done:** empty while owed. Once done, the path to the proof (a receipt, an
  acknowledgement, a report), or `n/a: <why>` when it turned out not to be owed.
  Setting it is what takes the row off the agenda.

Recurring obligations get one row per occurrence, written out a year ahead.
When a row is done, add the next one in the same commit.

| id | what | opens | closes | if missed | explained in | done |
|---|---|---|---|---|---|---|
