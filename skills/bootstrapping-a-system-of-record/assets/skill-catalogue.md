# Skill catalogue

What the bootstrap may offer to install, after the interview. Propose an entry only
when the answers justify it, with the one-line reason from the interview. Install only
what the human accepts.

**An entry exists only when the thing is installable today.** Never add one for a
skill that is planned.

## Entries

### `system-of-record`: this convention, for every clone

- **Offer when:** always. The human installed it for their own machine. Installing it at
  project scope means a second machine, a collaborator or a fresh clone loads the
  convention too.
- **Marketplace:** `agent-record`, from GitHub `alvaro-francisco-gil/agent-record`.

### `plans-lifecycle`: work in progress, in files

- **Offer when:** the interview surfaced work that runs over weeks: a conversion, an
  application process, a dispute, a registration. Plans live in
  `docs/plans/{ideas,ready,ongoing}/` and the next session starts from them.
- **Marketplace:** `agent-plans`, from GitHub `alvaro-francisco-gil/agent-plans`.

### The obligations register: not a plugin, an asset of this skill

- **Offer when:** the interview surfaced a date that costs something when missed: a
  filing, a renewal, an inspection, an expiry.
- **Install:** scaffold step *The obligations register* in `SKILL.md`. Nothing to
  install, two files to copy.

## How to install a plugin entry

**Claude Code**, from the repo root:

```bash
claude plugin install <plugin> --marketplace <owner>/<repo> --scope project
```

That writes `enabledPlugins` to `.claude/settings.json`, and nothing else. A fresh
clone on another machine doesn't know where the marketplace lives, so add it in the
same file:

```json
{
  "enabledPlugins": { "<plugin>@<marketplace>": true },
  "extraKnownMarketplaces": {
    "<marketplace>": { "source": { "source": "github", "repo": "<owner>/<repo>" } }
  }
}
```

Commit `.claude/settings.json`. It holds no secrets.

**Other agents:** use the tool's own install for the same marketplace (see each
marketplace's README), or tell the human the plugin name and where it lives. Never
copy a skill's files into the repo by hand when a plugin install exists. The copy
stops receiving fixes.
