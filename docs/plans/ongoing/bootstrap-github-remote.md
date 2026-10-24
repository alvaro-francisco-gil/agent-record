# The bootstrap ends with a remote, private by default

**Priority:** medium
**Gate:** blocked:first real bootstrap from a clean install (recheck 2026-11-15)
**Next:** install system-of-record 1.3.0 from the marketplace on a clean machine, bootstrap a record, and confirm the repo is created private and its visibility read back

**Goal:** A bootstrapped record ends up in a hosted repo the human owns, created by the
agent, private unless the human explicitly asks for public.

## Context

The bootstrap stops at a local first commit. Question 3 asks "public or private", but
nothing acts on the answer: no remote is created, and the person who most needs a backup
and a second machine, someone who has never used git, is left with a folder that exists
on one disk. Creating the repo is mechanical, and an agent can do it. The decision that
matters, its visibility, is already part of the gate.

## Design

- **Question 3 asks about hosting explicitly:** "This will live in a GitHub repo under
  your account. It will be private. Do you want it public instead?" **Private is the
  default**: silence, "I don't know" or "whatever" means private. Public only on an
  explicit yes. Before accepting it, restate that history is permanent and that every
  file ever committed will be readable by anyone.
- **The repo name** is proposed from question 1's subject (kebab-case) and confirmed.
- **A new scaffold step after the first commit** (and after hook verification step 4,
  which needs a committed file):
  1. `gh auth status`. If `gh` is missing or not logged in, guide the human through
     `gh auth login` and don't do it for them. A token never passes through the
     conversation.
  2. `gh repo create <name> --private --source . --remote origin --push` (or
     `--public` on the explicit yes).
  3. `gh repo view --json visibility` and say the visibility back to the human.
- **Fallback without `gh`:** the human creates an empty repo on github.com (no README,
  no licence, so the first push doesn't conflict). The agent then runs
  `git remote add origin <url>` and `git push -u origin HEAD`.
- **Other hosts:** if the human already uses GitLab or similar, do the equivalent. GitHub
  is the default, not a requirement.
- **Never push before the perimeter is verified.** The remote comes after the first
  commit, never as a way to "save progress" mid-interview.
- **Done when** gains a line: the remote exists, its visibility was read back, and the
  human heard it.
- The "hooks don't travel" paragraph already says a fresh clone has no perimeter check.
  Add that the remote makes a second clone likely, so the agents file's setup note is
  now load-bearing.

Release: bump the version in all four manifests. `GEMINI.md` is unchanged, since no
skill is added. Gate: `python3 scripts/validate.py && python3 -m pytest -q`.

## Out of scope

- Inviting collaborators. The human does that on the host, as an access decision.
- Organisation-owned repos. The bootstrap creates under the authenticated user; an
  org is the human's call, passed as `<org>/<name>`.

## Handoff

Built in 1.3.0 (2026-10-24). Verified so far only by `validate.py`, the test suite and a
scratch run of the copied assets; this repo's bar for "verified" is a clean install with
the behaviour observed. Retire once that bootstrap is seen to work.
