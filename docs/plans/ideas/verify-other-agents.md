# Verify the Cursor and Gemini installs

**Priority:** medium

## Goal

Install the plugin in Cursor and Gemini and observe both skills load and fire, so
the README's cross-agent claim is tested rather than inferred.

## Context

The README says plainly that only Claude Code and Codex have been verified. The sibling `agent-plans`
repo has the same gap and a ready plan for it. Doing both together halves the setup.

Codex was verified on 2026-10-20 (codex-cli 0.153.0): install, both skills listed, the
bootstrap fired unprompted and installed a working hook. Its one quirk, the sandbox's
read-only `.git/config`, is documented in the README.

## Design / approach

Follow `agent-plans`' verify plan. For each tool, confirm both skills are discovered and
that the bootstrap fires on "set up a repo for my career record". Narrow the README for
anything that doesn't work.
