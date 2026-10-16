# A /capture command for durable facts

**Priority:** medium

## Goal

Make Rule 3 (a durable fact surfaced in a session is written in that session) one step:
`/capture` lists the durable facts that came up in the conversation and proposes where
each one routes.

## Context

The capture rule depends on the agent noticing a fact mid-task, which is exactly when its
attention is elsewhere. claude-md-management's `/revise-claude-md` does the same sweep for
codebase instructions. Memory tools capture automatically but without routing or
evidence.

## Design / approach

A command that reads the routing table, lists candidate facts with a proposed destination
each, and writes nothing until the human confirms. Possibly a session-end reminder later.

## Open questions

- Automatic capture would conflict with the perimeter. Keep it human-confirmed.
