# A fabrication evaluation

**Priority:** high

## Goal

Measure, with Claude Code's plugin evaluation runner, how often an agent invents facts in an outgoing
document with the plugin installed versus without it, and publish the numbers in the
README.

## Context

No memory or context tool publishes fabrication numbers, and the directory doesn't check
whether a plugin helps. A measured reduction would be this plugin's strongest claim. It
would also turn the README's "it makes invention refusable" from an argument into a
result.

## Design / approach

- A fixture record with deliberate gaps: a missing end date, an unmeasured outcome, an
  unheld responsibility. Invented and clearly synthetic, per AGENTS.md.
- Prompts that pull towards each named failure: round this up, add a metric, fill this gap.
- Score: claims with no source, gaps filled instead of asked, markers used correctly.

## Open questions

- The fixture must never look like a real record. Name it as synthetic in every file?
- Where do fixtures live so they don't ship in the plugin folder?
