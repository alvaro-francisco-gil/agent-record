# Ship the plugin without scripts, so the Anthropic directory can list it

**Priority:** high — System of Record cannot be listed in Anthropic's plugin directory until no script is left in this repo
**Next:** write `assets/checks.md` (below), then remove the scripts, rewrite the gate, bump to 1.4.0 and push

**Goal:** One repo and one plugin, with no file in it that the directory refuses. The setup
skill keeps installing the same three checks, but the adopter's agent writes them from a
precise description and must prove them against a fixed list of tests before the first
commit. Decided by Álvaro on 2026-11-11.

## Context

- The directory refused v1.3.0 (`158ed7a`) on 2026-11-06: *"The directory accepts scripts,
  programs, and files outside the allowed types only from Verified organizations."*
  Allowed: Markdown, text, JSON, YAML, PNG/JPEG/GIF/WebP/ICO. Also refused, whatever the
  name: any file starting with `#!`, and package-manager config files. Text must be UTF-8
  with no NUL bytes. A license, readme, `.gitignore` and the icon may stay.
- "Verified" there means Anthropic knows the organization is a real company. A personal
  account will not become one, so the files have to go. (This is not the "Verified" of this
  repo's AGENTS.md, which means "installed into a clean repo and observed".)
- The directory unpacks the whole repo (69 files for v1.3.0, symlinked skill folders
  resolved), not only the plugin's files. Dev tooling counts too.
- Cross-repo history and the portal's own wording:
  `~/githubs/_workspace/docs/plans/ongoing/plugin-directory-listing.md`.

Files that must leave: `skills/bootstrapping-a-system-of-record/assets/record-check.py`,
`assets/agenda.py`, `assets/pre-commit-perimeter.sh`, `scripts/validate.py`,
`tests/test_agenda.py`, `tests/test_perimeter_hook.py`, `tests/test_record_check.py`.

**Never paste a script into a Markdown file to keep it.** The rule is about shipping code
from an unverified account. A script wrapped in a code fence still ships code, so it dodges
the rule rather than meeting it, and a reviewer will see it. The descriptions below state
behaviour and tests. They are not a program to copy out.

## Design

### `skills/bootstrapping-a-system-of-record/assets/checks.md`

One reference file, not a new skill. For each check: what it is for, the exact behaviour
(inputs, flags, exit codes, output), what it does not cover, and **the acceptance tests**.
The bootstrap's scaffold steps 3–5 change from "copy unchanged" to "write it from
`assets/checks.md` in the repo's language of choice (default: Python 3 standard library
for the two checkers, POSIX `sh` for the hook), run every acceptance test, and do not
commit until all pass".

Take the behaviour from the scripts as they stand at `158ed7a` before deleting them. Every
hardening comment in them becomes a numbered acceptance test, because those are the
lessons a freshly written version will miss. At least:

- **record-check:** a malformed marker fails, an unresolved one is listed but passes;
  both anchors are verified in the agents file; `--glob` widens the sweep beyond `*.md`
  (the 4% case: 44 markers in Markdown, 534 in ledger and YAML files); files named like the
  agents file are read for anchors and skipped by the sweep at any depth; dot-directories
  are skipped; fenced blocks are ignored; a marker inside a code span still counts unless
  it can never be a real marker (bare word, empty question, `<placeholder>`); an unclosed
  bracket ends at a blank line instead of swallowing the document; the same word given
  twice makes the bare form mean "unverified"; `--list` never exits non-zero but still
  reports malformed markers.
- **agenda:** the register is the Markdown table in `obligations.md` with the fixed
  columns; overdue first, then what closes within 45 days (`--within N`); `--check`
  validates only; exit 1 when malformed or something is overdue; a row with an
  `[unknown:]` date fails `--check`; `done` rows drop off; no dependencies beyond the
  language's standard library.
- **perimeter hook:** reads staged blobs (`git show ":0:$f"`), not the working tree; a
  `git mv` into a forbidden path plus an edit in the same commit is blocked (no rename
  detection, filter `ACMRT`); paths with spaces and non-ASCII names are checked
  (`core.quotePath=false`, one path per read, no pipe into the loop); submodule entries are
  skipped; placeholders left unfilled make it fail loudly, never match nothing; it is
  installed with `core.hooksPath .githooks` and proven to block before the first commit.

Each test is written as a scenario the agent can run in a scratch repo: the setup, the
command, the expected exit code and output.

### Everything else that names the scripts

- `skills/bootstrapping-a-system-of-record/SKILL.md`: scaffold steps 3, 4, 5 and 9 and the
  done-criteria (`record-check.py exits 0`, `agenda.py --check` passes). The checker keeps
  its name and its path in the adopter's repo (`scripts/record-check.py`,
  `scripts/agenda.py`, `.githooks/pre-commit`), so agents files and habits don't change.
- `assets/AGENTS-sections.md` and `assets/obligations.md` mention the commands; they stay
  valid if the names stay.
- `skills/maintaining-a-system-of-record/SKILL.md`: check for any "copied unchanged" claim.
- `README.md` (lines ~139–264 at `158ed7a`), `START.md`, `START.es.md`: "copied unchanged"
  becomes "written from a spec and tested". Say plainly what that costs: two adopters'
  checkers will not be byte-identical, and the tests are what they share.
- `AGENTS.md`: `## Per-repo policy` ("The gate before every commit", "Assets are shipped as
  they are copied") and the description of the bootstrap skill. New policy: **no file in
  this repo may be anything but Markdown, text, JSON, YAML or an allowed image, and none may
  start with `#!`**, with the reason. Keep the rule that every example is invented.

### The repo's own gate

`scripts/validate.py` and `tests/` go. `.github/workflows/validate.yml` keeps the checks
that matter, as short steps in the YAML: `claude plugin validate .` if the CLI can run in
CI (check first), otherwise `jq`/`yq` lines for JSON validity, frontmatter `name` matching
its directory, and the four `version` keys agreeing. Keep each step a line or two; a long
program inside the YAML is the same dodge as a script in Markdown.

This changes three `ready/` plans: `version-bump-check.md` and `gemini-imports-check.md`
were going to extend `validate.py`, so they become CI steps or move back to `ideas/`;
`ci-portability-matrix.md` tested shipped assets that no longer exist, so retire it and
say why in the commit.

### Release

Bump to **1.4.0** in all four manifests in the same commit as the content. Push to `main`.
The directory picks it up within about 6 hours. Then read System of Record's page at
claude.ai/directory/manage: expect "Validación" and "Directory policy" to pass and the
version to go to a person for review. Record the outcome in the workspace plan above.

## Acceptance

- `git ls-files` lists nothing outside the allowed types except `LICENSE` and
  `.gitignore`, and `git grep -l '^#!'` finds nothing.
- An agent bootstrapping a scratch repo from the new skill writes the three checks, runs
  every acceptance test in `checks.md`, and they pass.
- The directory's check of 1.4.0 passes Directory policy.
