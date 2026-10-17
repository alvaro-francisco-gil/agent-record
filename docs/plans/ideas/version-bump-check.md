# Fail validation when shipped content changes without a version bump

**Priority:** medium — two content fixes have already landed unbumped after a release, and the rule that catches this today is a sentence in AGENTS.md
**Gate:** decision:Should `validate.py` (and CI) fail when a change under `skills/` or `GEMINI.md` lands without a new `version` in `.claude-plugin/plugin.json`?

**Goal:** Turn AGENTS.md's releasing rule ("a content change that does not bump that version never reaches existing users") from a convention into a check, so an installed user is never left on a cached copy while the repo looks fixed.

## Context

As of `6b1b5fd` (2026-10-16):

- AGENTS.md `## Releasing` says Claude Code pins an installed plugin to the `version` in `.claude-plugin/plugin.json`, and that a content change without a bump "never reaches existing users". Nothing enforces it. `scripts/validate.py` checks only that the four manifests that carry a `version` agree with each other, not that it moved.
- It has already been missed. `ec14c0c docs: README and AGENTS.md; release 1.0.0` released 1.0.0; two of the next four commits changed shipped skill content without a bump: `538d153 fix: the perimeter hook must see a rename, and --list must report errors` (four files under `skills/` plus `GEMINI.md`, the commit that added the bootstrap skill's import for Gemini) and `800aa80 fix: the guards guard, and three comments say the true thing` (the bootstrap `SKILL.md` and `pre-commit-perimeter.sh`). Neither touched `.claude-plugin/plugin.json`; they reached installed users only because `57ca524 docs: verified in Claude Code; release 1.0.1` bumped for an unrelated reason the same day.
- Every release since (`d39c37a`, `1ac6160`, `d6699ca`, `ad29ef8`, and `167a84c` to 1.2.1) bumped by hand, and the evidence shows the four manifests co-changing 8 times in 90 days — the bump is the hottest co-change in the repo.
- Commits go straight to `main`; CI (`.github/workflows/validate.yml`) runs `validate.py` and pytest on every push and PR.

## Design

`validate.py` gains a release check, run from the repo's existing gate:

- **Shipped paths:** a short list at the top of `validate.py` — `skills/` and `GEMINI.md` to start. README.md is left out: its public copy is the GitHub page the manifests' `documentationUrl` points at, and `57ca524` shows the author may still choose to bump for it.
- **Local (default):** compare the working tree and index against `HEAD` (`git diff HEAD --name-only`). If a shipped path changed and `.claude-plugin/plugin.json`'s `version` equals the one in `git show HEAD:.claude-plugin/plugin.json`, fail with the fix: "bump the version in all four manifests". This is the moment the AGENTS.md gate already runs, before the commit.
- **CI:** `python3 scripts/validate.py --base <ref>` compares `<ref>..HEAD` the same way. The workflow passes `github.event.before` on push and the PR base SHA on pull_request; an all-zero `before` (a new branch) skips the check. `actions/checkout@v4` fetches only the tip commit by default, so the workflow's checkout needs `fetch-depth: 0` for `<ref>` to exist. One bump anywhere in a pushed range satisfies it, which matches what installed users actually receive.
- Illustrative failure line (shape only): `release: skills/… changed since <ref> but .claude-plugin/plugin.json is still 1.2.1`.

`validate.py` is repo tooling, not a shipped asset, so calling `git` from it adds no constraint on adopters.

**Alternatives considered:** a pre-commit hook in this repo — a local hook is not committed config (the same `core.hooksPath` gap the bootstrap skill warns adopters about), so CI must carry the check anyway; a CI-only workflow step in shell — splits the rule from the gate AGENTS.md names, so a local run would stay silent; auto-bumping in CI — writes commits on `main` and picks the semver level for the author.

**Testing strategy:** a test module for `validate.py`'s release check against a throwaway git repo built the way `tests/test_perimeter_hook.py` builds one (clean env, no inherited config): a shipped change with no bump fails, the same change with a bump passes, a change only under `tests/` or `docs/` passes, an all-zero base is skipped.

## Paths

As of 2026-10-17:

- `scripts/validate.py`
- `.github/workflows/validate.yml`
- `tests/test_validate.py` (new)
- `AGENTS.md` (`## Releasing` names the check)

## Approval

**Needs your yes** — should a shipped change without a version bump fail `validate.py` and CI? Recommended answer: yes, because the rule is already binding in AGENTS.md, it has been missed twice, and the only cost is a failure message that names the fix.

## Out of scope

Choosing the semver level; tagging or GitHub releases; checking that the four manifests agree (already done); the GEMINI.md import check (`gemini-imports-check`).
