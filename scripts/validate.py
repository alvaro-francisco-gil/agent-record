#!/usr/bin/env python3
"""Validate every skill's frontmatter and every per-agent manifest.

Catches the failure modes that only surface once an agent tries to load the plugin:
unparseable YAML (an unquoted ': ' in a description is the classic), a missing name or
description, a name that disagrees with its directory, malformed JSON, and a version
that has drifted apart across the per-agent manifests.
"""
import json, pathlib, sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []

for skill in sorted((ROOT / "skills").iterdir()):
    f = skill / "SKILL.md"
    if not f.is_file():
        errors.append(f"{skill.name}: no SKILL.md")
        continue
    text = f.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{skill.name}: no YAML frontmatter")
        continue
    raw = text.split("---\n", 2)[1]
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        errors.append(f"{skill.name}: frontmatter is not valid YAML - {str(e).splitlines()[0]}")
        continue
    for key in ("name", "description"):
        if not meta.get(key):
            errors.append(f"{skill.name}: frontmatter is missing '{key}'")
    if meta.get("name") and meta["name"] != skill.name:
        errors.append(f"{skill.name}: frontmatter name '{meta['name']}' != directory name")

MANIFESTS = [
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]
versions = {}
for rel in MANIFESTS:
    p = ROOT / rel
    if not p.is_file():
        errors.append(f"{rel}: missing")
        continue
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{rel}: invalid JSON - {e}")
        continue
    if "version" in data:
        versions[rel] = data["version"]

if len(set(versions.values())) > 1:
    errors.append(f"version drift across manifests: {versions}")

if errors:
    print("FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"OK - {len(list((ROOT / 'skills').iterdir()))} skills, {len(MANIFESTS)} manifests, version {next(iter(set(versions.values())), 'n/a')}")
