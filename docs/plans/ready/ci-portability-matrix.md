# Run the shipped assets' tests on macOS and an old Python

**Priority:** medium — the assets ship to strangers' machines, a BSD-vs-GNU defect has already reached the documented health check unnoticed, and CI runs one OS and one Python

**Goal:** Back the claims that `record-check.py` "must run on a bare Python 3" and that the perimeter hook (`#!/bin/sh`, installed and run as `sh .githooks/pre-commit`) works on adopters' machines, with evidence a build can fail on, instead of the author's single Linux machine.

## Context

As of `6b1b5fd` (2026-10-16):

- `.github/workflows/validate.yml` runs one job: `ubuntu-latest`, `python-version: '3.12'`, then `validate.py` and `pytest -q`.
- AGENTS.md: `record-check.py` "is copied unchanged, so it must run on a bare Python 3 with no dependencies". No minimum version is stated anywhere in the README or the bootstrap skill, and no build runs anything older than 3.12.
- The hook (`skills/bootstrapping-a-system-of-record/assets/pre-commit-perimeter.sh`) runs under `sh` and calls `mktemp`, `wc -c`, `grep -qEI`, `git show` — tools whose BSD and GNU versions differ. `tests/test_perimeter_hook.py` runs it exactly as adopters do (`sh .githooks/pre-commit`), but only on Ubuntu, where `sh` is dash and the tools are GNU.
- That difference has bitten once already: `538d153 fix: the perimeter hook must see a rename, and --list must report errors` records that the documented health-check grep used `\|`, a GNU BRE extension, which on macOS "matched the literal string and reported a clean record". It was caught by reading, not by a build. That defect sat in the grep documented in `skills/maintaining-a-system-of-record/SKILL.md`, not in either asset, so this matrix would not itself have caught it; it shows the class of defect (BSD vs GNU tools) is real for this repo's users, and the hook calls exactly such tools.
- The two assets are the hottest source files in the 90-day window: `record-check.py` churn 6 with 4 fixes, `pre-commit-perimeter.sh` churn 5 with 4 fixes.

## Design

Turn the single job into a small matrix, keeping one `validate.py` run:

- `os: [ubuntu-latest, macos-latest]` × `python: [<floor>, '3.12']` for `pytest -q`; `validate.py` stays on one cell (it is repo tooling, not shipped).
- **The floor:** the oldest Python 3 that both `actions/setup-python` offers on the runner and the test toolchain (pytest) still supports, chosen and checked when this is built — likely 3.9. The README's install or "what ships" section then states it in one line: "`record-check.py` needs Python 3.<floor>+ and nothing else". `record-check.py` itself uses nothing newer than f-strings today, so no code change is expected.
- If a macOS cell fails, that is a real adopter defect: fix the asset in its own commit (with its release bump), not the test.

**Alternatives considered:** pin an old Python only, no macOS — misses the class of defect that has actually occurred; add Windows (Git Bash) too — worth it later, but the hook's tests depend on `sh` and git's Windows quoting, and it would likely start as a pile of skips; vendor a POSIX-shell linter (shellcheck) instead — catches syntax, not BSD-vs-GNU behaviour of `wc`/`grep`.

**Testing strategy:** no new tests; the existing 47 run in more environments. Any skip a macOS cell needs is written with a reason, as `tests/test_perimeter_hook.py` already does for missing `git`/`sh`.

## Paths

As of 2026-10-17:

- `.github/workflows/validate.yml`
- `README.md` (one line stating the Python floor)
- `skills/bootstrapping-a-system-of-record/SKILL.md` (only if it should state the floor where it copies `record-check.py`)

## Approval

Decided 2026-10-17 (Álvaro): yes — Should CI run the test suite on macOS as well as Ubuntu, and on a declared minimum Python 3 as well as 3.12, with that minimum stated in the README?

## Out of scope

Windows support; verifying the plugin in Codex, Cursor or Gemini (`verify-other-agents`); changing either asset unless a new cell finds a defect.
