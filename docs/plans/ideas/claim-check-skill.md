# A claim-check skill for outgoing documents

**Priority:** high

## Goal

Add a third skill that checks a draft before it goes out: every factual claim maps to a
source file by path, or to an `[inferred]` / `[unknown:]` marker, and anything that maps
to neither is reported.

## Context

Rule 2 (every claim in an outgoing document traces to a source file) is the core of the
convention, and today it is enforced only by the drafting agent's own discipline. The
agent that wrote a plausible sentence is the one least able to notice it invented it. The
nearest competitors check one document type each (resume-only fact-checkers) or check
citation pointers rather than claims (the Citations API). Nothing general exists.

## Design / approach

- Run the check in a fresh context (a subagent where the tool supports one), given only
  the draft and the record, not the drafting conversation.
- Output a table: claim, source path (with line), or "no source". Rounded numbers,
  metrics and filler are the three named failure modes, so flag them by name.
- Optional: `<!-- src: path#L12 -->` pointers in renderings that `record-check.py` can
  verify still resolve.

## Open questions

- Claim extraction is fuzzy. How strict before it becomes noise?
- Does this belong in `maintaining-a-system-of-record` as a step, or as its own skill with
  its own trigger ("check this draft against my record")?
