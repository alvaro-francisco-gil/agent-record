# Check that GEMINI.md imports every skill

**Priority:** medium — the plugin once shipped to Gemini with half its skills (fixed in `538d153`), and AGENTS.md says nothing fails when it happens
**Gate:** decision:Should `validate.py` fail unless `GEMINI.md` carries exactly one `@` import per directory under `skills/`, each resolving to a real `SKILL.md`?

**Goal:** Make the second entry point impossible to forget: a skill added to, renamed in or removed from `skills/` without the matching `GEMINI.md` line fails the gate instead of silently not reaching Gemini users.

## Context

As of `6b1b5fd` (2026-10-16):

- `gemini-extension.json` names `GEMINI.md` as its `contextFileName`; `GEMINI.md` is two lines, one `@./skills/<name>/SKILL.md` import per skill.
- AGENTS.md `## Single source of truth`: "a skill added to `skills/` and not added there reaches no Gemini user, and nothing fails to tell anyone. It shipped that way once." That was `c6229bf feat: the bootstrapping-a-system-of-record skill and its assets`, which added the second skill without its import; `538d153 fix: the perimeter hook must see a rename, and --list must report errors` added the missing line ("GEMINI.md imported one skill of two, so a Gemini user never got the bootstrap skill the marketplace advertises").
- The rule is held only by prose. `scripts/validate.py` already walks `skills/*/SKILL.md` for frontmatter and reads `gemini-extension.json`, but never opens `GEMINI.md`.

## Design

A few lines in `scripts/validate.py`, beside the existing skill walk:

- Read `gemini-extension.json`'s `contextFileName` (rather than hard-coding `GEMINI.md`), parse every line starting with `@`, and resolve each relative to the repo root.
- Fail on: a skill directory with no import; an import whose path does not exist; an import that is not a `skills/<name>/SKILL.md`; a skill imported twice.
- Illustrative messages: `GEMINI.md: skills/<name> is not imported`, `GEMINI.md: @./skills/<name>/SKILL.md does not exist`.

**Alternatives considered:** generating `GEMINI.md` from `skills/` — adds a build step to a repo that has none, and a generated file still needs a check that it was regenerated; a pytest test instead of `validate.py` — `validate.py` is the documented home of "failures that only surface when an agent tries to load the plugin", which this is.

**Testing strategy:** cases for `validate.py` against a temporary tree (missing import, dangling import, duplicate, clean) in a new `tests/test_validate.py`; shares the module with `version-bump-check` if that lands first.

## Paths

As of 2026-10-17:

- `scripts/validate.py`
- `tests/test_validate.py` (new)
- `AGENTS.md` (the `GEMINI.md` paragraph can say the gate now checks it)

## Approval

**Needs your yes** — should `validate.py` fail on a `GEMINI.md` that does not import exactly the skills under `skills/`? Recommended answer: yes, because the defect already shipped once and AGENTS.md itself names the absence of a failing check as the problem.

## Out of scope

Verifying that Gemini actually resolves the `@` imports at install time (`verify-other-agents`); the version-bump check (`version-bump-check`).
