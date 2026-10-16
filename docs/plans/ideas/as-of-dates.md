# "As of" dates on facts that go stale

**Priority:** low

## Goal

Let a source fact carry the date it was last confirmed, so an agent can tell a current
headcount from a two-year-old one, and let `record-check.py` warn about facts past a
staleness threshold.

## Context

The record today says what is true, not when it was last checked. Graphiti is the only
compared tool that models facts expiring. Some fact types never go stale (a degree), and
others do within months (a team size, a rate).

## Design / approach

An optional inline form such as `(as of 2026-10)`, a per-repo list of fact types that
expire, and a checker warning, never an error.

## Open questions

- Is a new syntax worth it, or does git blame answer "when was this confirmed" well
  enough?
