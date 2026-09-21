#!/usr/bin/env python3
# Generic checks for a system-of-record repo.
#
# Errors (exit 1): malformed uncertainty markers, and a missing anchor in the
# agents file. Unresolved markers are NOT errors - they are the worklist.
import argparse, pathlib, re, sys

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__"}


def check(root, inferred="inferred", unknown="unknown", agents_file="AGENTS.md"):
    errors, worklist = [], []

    agents = root / agents_file
    if not agents.is_file():
        errors.append(f"{agents_file}: missing")
    else:
        text = agents.read_text(encoding="utf-8")
        for anchor in ("record:perimeter", "record:routing"):
            if f"<!-- {anchor} -->" not in text:
                errors.append(f"{agents_file}: missing the <!-- {anchor} --> anchor")

    good = re.compile(r"\[" + re.escape(unknown) + r": *([^\]]*)\]")
    bare = re.compile(r"\[" + re.escape(unknown) + r"\]")
    inf = re.compile(r"\[" + re.escape(inferred) + r"\]")

    for path in sorted(root.rglob("*.md")):
        if SKIP & set(path.relative_to(root).parts):
            continue
        rel = path.relative_to(root)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if bare.search(line):
                errors.append(f"{rel}:{n}: [{unknown}] carries no question")
            for question in good.findall(line):
                if not question.strip():
                    errors.append(f"{rel}:{n}: [{unknown}:] has an empty question")
                else:
                    worklist.append(f"{rel}:{n}: {question.strip()}")
            if inf.search(line):
                worklist.append(f"{rel}:{n}: [{inferred}] {line.strip()[:90]}")

    return errors, worklist


def main():
    ap = argparse.ArgumentParser(description="Check a system-of-record repo.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--agents-file", default="AGENTS.md")
    ap.add_argument("--inferred-marker", default="inferred")
    ap.add_argument("--unknown-marker", default="unknown")
    ap.add_argument("--list", action="store_true", help="print the worklist and exit 0")
    a = ap.parse_args()

    errors, worklist = check(
        pathlib.Path(a.root).resolve(), a.inferred_marker, a.unknown_marker, a.agents_file
    )

    if a.list or worklist:
        print(f"worklist - {len(worklist)} open marker(s)")
        for w in worklist:
            print(f"  {w}")
    if a.list:
        return 0
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK - no malformed markers, anchors present ({len(worklist)} open marker(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
