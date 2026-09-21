#!/usr/bin/env python3
# Generic checks for a system-of-record repo.
#
# Errors (exit 1): malformed uncertainty markers, and a missing anchor in the
# agents file. Unresolved markers are NOT errors - they are the worklist.
#
# What it does not cover, so nobody reads a pass as more than it is:
#   - Only *.md is scanned. A marker in a .txt, .csv, .html or .ipynb source is
#     invisible here. Keep the record in Markdown, or extend this glob.
#   - The agents file is read for its two anchors and then skipped by the marker
#     sweep, so a marker written in the agents file itself is never listed. It
#     is skipped because the template's own definitions of the two markers
#     would otherwise open every new repo's worklist with two phantom entries.
#   - Nothing here reads content for sensitivity, and nothing here can check the
#     evidence rule. A pass is not evidence that a document is honest.
import argparse, pathlib, re, sys

SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__"}
FENCE = re.compile(r"\s*(```|~~~)")
SPAN = re.compile(r"`[^`]*`")


def check(root, inferred="inferred", unknown="unknown", agents_file="AGENTS.md"):
    errors, worklist = [], []

    agents = root / agents_file
    if not agents.is_file():
        errors.append(f"{agents_file}: missing")
    else:
        text = agents.read_text(encoding="utf-8", errors="replace")
        for anchor in ("record:perimeter", "record:routing"):
            if f"<!-- {anchor} -->" not in text:
                errors.append(f"{agents_file}: missing the <!-- {anchor} --> anchor")

    good = re.compile(r"\[" + re.escape(unknown) + r": *([^\]]*)\]")
    bare = re.compile(r"\[" + re.escape(unknown) + r"\]")
    inf = re.compile(r"\[" + re.escape(inferred) + r"\]")

    for path in sorted(root.rglob("*.md")):
        if SKIP & set(path.relative_to(root).parts):
            continue
        # The agents file defines the two markers, so it matches them. It is
        # instructions, not a source: read above for the anchors, skipped here.
        if path == agents:
            continue
        rel = path.relative_to(root)
        # A received .md need not be UTF-8. An undecodable byte is not a marker
        # defect and must never be a traceback in somebody else's repo.
        body = path.read_text(encoding="utf-8", errors="replace")
        fenced = False
        for n, line in enumerate(body.splitlines(), 1):
            # A marker shown as an example is not a marker. Every repo that
            # documents this convention writes the two words in prose, so
            # counting them would fire the check on a healthy record - the one
            # thing it must never do. Fenced blocks and `code spans` are quoted
            # syntax, not open questions.
            if FENCE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            line = SPAN.sub("", line)
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
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
    # --list is the health check the agents-file template installs everywhere,
    # so it never exits non-zero - an open worklist is the normal state. It
    # still has to say when a marker is malformed, or the one mode people run
    # by habit is the one mode that can never report a defect.
    if a.list:
        return 0
    if errors:
        return 1
    print(f"OK - no malformed markers, anchors present ({len(worklist)} open marker(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
