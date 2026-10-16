# Interop with a search layer

**Priority:** low

## Goal

Document how a record works alongside a search or memory tool (Basic Memory, memsearch)
for large records, instead of building one into the plugin.

## Context

The plugin has no search: an agent reads files. That is fine for a small record and slow
for a large one. Memory tools already index Markdown, and Basic Memory's `[question]`
category is the closest match to the `[unknown:]` marker.

## Design / approach

A README section: which tool, how to point it at the source layer only (never renderings),
and that the source file, not the index, stays authoritative.

## Open questions

- Does any indexing tool risk pulling perimeter-excluded files into its store?
