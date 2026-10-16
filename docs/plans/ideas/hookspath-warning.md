# Warn when the perimeter hook isn't active

**Priority:** low

## Goal

Have `record-check.py` warn when `git config core.hooksPath` doesn't point at `.githooks`
on the current clone, so a fresh clone isn't silently running with no perimeter check.

## Context

The bootstrap skill already says the hook is most often absent because `core.hooksPath`
is local config, and a fresh clone has no perimeter check until someone sets it. The
checker runs anyway, so it is the cheapest place to notice.

## Design / approach

One `git config --get core.hooksPath` call, a warning with the fix, and a test. No new
dependencies: the script must still run on a bare Python 3.
