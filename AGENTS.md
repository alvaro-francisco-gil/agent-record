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
  scaffold: the agents file, the routing destinations, `record-check.py` and a generated
  pre-commit hook.

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
- **The gate before every commit** is `python3 scripts/validate.py && python3 -m pytest -q`.
  `validate.py` catches the failures that only surface when an agent tries to load the
  plugin — unparseable frontmatter, a name that disagrees with its directory, version drift
  across manifests. The tests cover `record-check.py`, which ships to strangers and is the
  only Python that does.
- **Assets are shipped as they are copied.** `skills/bootstrapping-a-system-of-record/assets/`
  holds files that land verbatim in someone else's repo. `record-check.py` is copied
  unchanged, so it must run on a bare Python 3 with no dependencies;
  `pre-commit-perimeter.sh` ships with `<FORBIDDEN_PATTERNS>` and `<CONTENT_PATTERNS>`
  unfilled, which is deliberate — an unfilled path list is a syntax error, and a hook that
  dies loudly beats one that silently matches nothing.

## Single source of truth

`skills/` is the only copy of any skill. Every per-agent manifest (`.claude-plugin/`,
`.codex-plugin/`, `.cursor-plugin/`, `gemini-extension.json`) points at it rather than
holding its own copy. **Never duplicate a `SKILL.md`** — a second copy is drift waiting to
happen, which is the failure this packaging exists to prevent.

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
and the plugin it lists is versioned by `.claude-plugin/plugin.json`. `validate.py` reads all
five manifests but compares only the versions it finds, so its `5 manifests` count is
correct and is not a fifth place to bump.

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
