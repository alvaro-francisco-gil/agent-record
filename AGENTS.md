# AGENTS.md

Instructions for anyone — human or agent — working in this repo.

## What this repo is

`agent-record` packages the system-of-record convention as a skill, for Claude Code, Codex,
Cursor, Gemini, and anything else that can read a `SKILL.md`. One plugin,
`system-of-record`, ships two skills:

- [skills/maintaining-a-system-of-record/SKILL.md](skills/maintaining-a-system-of-record/SKILL.md)
  — the convention. Six rules: sources and renderings, the evidence rule, the capture rule,
  greppable uncertainty markers, a fact-routing table, and a declared perimeter.
- [skills/bootstrapping-a-system-of-record/SKILL.md](skills/bootstrapping-a-system-of-record/SKILL.md)
  — the front door. Four interview questions, gated on the perimeter question, then a
  scaffold: the agents file, the routing destinations, and the checks (`record-check.py`,
  a pre-commit hook, `agenda.py` when there are deadlines), which the adopter's agent writes
  from `assets/checks.md` and proves against its acceptance tests.

**Read both before changing either.** They overlap on purpose — the bootstrap skill is the
convention made concrete in one repo — and a change to a rule in one that is not reflected
in the other is drift that ships.

## This repo is not itself a system of record

The sibling repo `agent-plans` can say "this repo uses the convention it ships". This one
cannot, and pretending otherwise in a repo about evidence would be the worst possible look.

`agent-record` holds no authoritative account of anything real. It has no sources and no
renderings, no routing table, no perimeter section and no `record-check.py` of its own — it
ships the convention rather than practising it. The records the convention was drawn from
are private, so they cannot be named here, quoted here, or pointed at.

Two consequences bind anyone writing in this repo:

- **Every example in the skills and the README is invented or category-level**, and must
  stay that way. No real client, employer, institution, project or person, and no detail
  from which one could be identified. This repo is public and its history is permanent.
- **Do not add record-style furniture here to make the repo look consistent** — no anchors
  in this file, no `identity/` directory, no worked "example record" committed as if it were
  one. A plausible invented record is indistinguishable from a real one six months later,
  which is precisely the failure the convention exists to prevent.

Because those records are private, this repo cannot show you the convention in use. Do not
substitute an invented example for the missing one.

## Per-repo policy

- **Plan documents** live in `docs/plans/{ideas,ready,ongoing}/`, with durable rationale in
  `docs/decisions/`, following the lifecycle convention from the sibling `agent-plans`
  marketplace. No `ongoing/soak/`, no `docs/incidents/`, no `docs/ops/` — nothing here
  deploys.
- **"Verified" means** the skill has been installed from this marketplace into a clean repo
  and the described behaviour observed — not that the Markdown reads correctly. The README
  says plainly that this has not yet happened in any tool; keep that note honest the moment
  it does.
- **No file in this repo may be anything but Markdown, plain text, JSON, YAML or a PNG,
  JPEG, GIF, WebP or ICO image, and no file may start with `#!`.** `LICENSE`, `.gitignore`,
  empty `.gitkeep` files and the two skill symlinks are the only exceptions. Anthropic's
  plugin directory unpacks the whole repo, dev tooling included, and refuses scripts,
  programs and package-manager configs from an account that is not a verified
  organisation; this one is personal and will stay so. **Never keep a script by pasting it
  into Markdown or YAML**: a program in a code fence still ships code, and it dodges the
  rule rather than meeting it. Describe behaviour and tests instead; a short command line in
  a test scenario is fine, a function body is not. CI enforces the file types and the `#!`
  rule.
- **The gate** is `.github/workflows/validate.yml`, which runs on every push and pull
  request: every JSON file parses, every skill's frontmatter loads and names its directory,
  `GEMINI.md` imports every skill, the four versions agree, a change under `skills/` or to
  `GEMINI.md` comes with a version bump, no file is outside the allowed types or starts with
  `#!`, and `claude plugin validate .` passes. Each step is a line or two of shell; run them
  by hand before a commit that touches a manifest or a skill's frontmatter (they need `jq`
  and mikefarah `yq`). Keep each step that short: a long program inside the YAML is the same
  dodge as a script in Markdown.
- **The checks are a specification, not code.**
  `skills/bootstrapping-a-system-of-record/assets/checks.md` specifies `record-check.py`,
  `agenda.py` and the perimeter hook, and lists the acceptance tests each must pass. The
  adopter's agent writes them; this repo never holds an implementation. A behaviour change
  is a change to the spec **and** a new or changed numbered test, in the same commit — the
  tests are the only thing every adopter's checks share, and a lesson not written as a test
  is a lesson the next freshly written checker will miss. Before releasing a change to
  `checks.md`, dry-run it: an agent that has not seen any earlier implementation writes the
  checks from the file alone, in a scratch repo outside this one, and runs every test.
- **Assets land in someone else's repo.** `obligations.md` and `AGENTS-sections.md` are
  copied and filled; the obligations register is a Markdown table, not YAML, so the agenda
  needs nothing beyond a standard library. `packs/` and `skill-catalogue.md` hold structure
  only, never an example fact.

## Single source of truth

`skills/` is the only copy of any skill. Every per-agent manifest (`.claude-plugin/`,
`.codex-plugin/`, `.cursor-plugin/`, `gemini-extension.json`) points at it rather than
holding its own copy. **Never duplicate a `SKILL.md`** — a second copy is drift waiting to
happen, which is the failure this packaging exists to prevent.

**`GEMINI.md` is the second entry point, and it is the one that silently ships half the
plugin.** `gemini-extension.json` names it as the context file, and it imports each skill by
path with an `@` line — so a skill added to `skills/` and not added there reaches no Gemini
user. It shipped that way once. **When the set of skills changes, `GEMINI.md` changes in
the same commit**, and it carries one `@` line per skill, always. CI now fails when a skill
directory has no `@./skills/<name>/SKILL.md` line.

The same applies to the rules themselves: they are stated in
`maintaining-a-system-of-record` and referenced elsewhere. `README.md` restates them for a
reader who has not installed anything, and that restatement is the one permitted copy — when
a rule changes, it changes in both, in the same commit.

## Releasing

Claude Code pins an installed plugin to the `version` in `.claude-plugin/plugin.json` and
auto-updates when it changes. **A content change that does not bump that version never
reaches existing users** — they stay on the cached copy, and the repo looks fixed while
every install is still broken. Bump it in the same commit as the content.

The version appears in exactly four files, and they must be identical:

```bash
grep -rn '"version"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json
```

`.claude-plugin/marketplace.json` carries no `version` key **by design** — it is a catalogue,
and the plugin it lists is versioned by `.claude-plugin/plugin.json`. CI compares exactly
the four files above, so it is not a fifth place to bump.

CI also fails a push or pull request that changes `skills/` or `GEMINI.md` without changing
the version in `.claude-plugin/plugin.json`. It looks at the whole pushed range, so one bump
anywhere in it is enough — which is what installed users actually receive.

Renames go in the `renames` map in `.claude-plugin/marketplace.json`, which is
**append-only** — old entries stay forever so migration chains keep resolving.

## Writing style for skills

Skills here are read by agents, in context, competing for attention with everything else
loaded. So:

- The `description` is the trigger. It decides whether the skill loads at all. Spend it on
  when to use the skill — the situations and the words a user actually types — not on
  caveats.
- State the rule, then the anti-pattern. Agents follow "never do X, because Y" better than
  prose that implies it.
- No repo-specific assumptions. If a line only makes sense in the author's repos, it is a
  bug — this ships to strangers, whose directory layout, language and threat model are not
  yours.
- Say what a rule cannot do. The convention makes invention refusable, not impossible; the
  checker covers markers and anchors only; the hook catches the careless case, not a
  determined one. A skill that overclaims gets trusted exactly once.

## Local agent discovery

Claude Code and Codex read `AGENTS.md` directly. Use Claude Code 2.1.281 or
newer; if a parent/local Claude instruction file shadows it, select
`claude-md-and-agents-md` in `/config`.

Published skill sources stay in `skills/`. `.agents/skills` points to that
directory and `.claude/skills` points to `.agents/skills`, so local discovery
and every plugin manifest use the same files. Preserve Git symlinks when
cloning on Windows. Do not put copied skills in either discovery directory.
