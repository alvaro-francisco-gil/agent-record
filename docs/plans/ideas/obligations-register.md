# Obligations register: reaching people outside a session

**Priority:** medium

## Goal

A date in a record's obligations register reaches its owner before it closes, even when
nobody opens an agent session that week.

## Context

1.3.0 shipped the register itself: `assets/obligations.md` (a Markdown table, so the
script needs no YAML parser) and `assets/agenda.py`, which lists overdue and upcoming
rows and exits 1 when something is overdue. The bootstrap installs both when the
interview surfaces a dated obligation, and the agents file tells each session to run the
agenda first.

The gap is everything outside a session. In one adopter's record, a filing deadline that
was tracked in prose was still missed, because nothing reached out. That record now sends
itself chat alerts through its own server, which strangers won't have. The people this
convention now targets (a vehicle owner, someone newly self-employed) may open a session
once a month.

## Design / approach

Candidates, cheapest first:

- **`agenda.py --ics`**: export the open rows as an iCalendar file with alarms (say 7 and 2
  days before) that the human imports into the calendar they already use. No server. The
  cost is that a re-import is needed whenever a row changes.
- **A scheduled CI job** on the record's host that runs the agenda and opens an issue
  when something is due. The host then emails the owner. It needs no server, but needs
  the repo on a host with scheduled jobs.
- **Agent-side scheduling**, where the person's agent app supports scheduled tasks: a
  weekly task that runs the agenda and reports. Depends on the tool.

## Open questions

- Which of these works for someone who never opens a terminal? The `.ics` export looks
  like the best first step.
- Should alerts follow a fixed ladder (7 days, 2 days, the last day, then weekly while
  overdue) or be configurable per row?
