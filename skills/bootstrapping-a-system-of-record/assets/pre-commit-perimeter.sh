#!/bin/sh
# Perimeter check. Generated at bootstrap; owned by this repo, edit it freely.
# Never bypass with --no-verify. If it blocks something legitimate, change the rule.
set -eu
fail=0

# Three things below are load-bearing, so change them only on purpose. Each one
# answers a different question about the list of staged files, and each was a
# real hole before it was closed.
#
# Which entries the diff lists. --diff-filter decides what git even mentions.
# ACM alone omits R (rename) and T (typechange), and rename detection is on by
# default - so `git mv notes/x.md private/x.md` plus an edit in the same commit
# listed nothing at all, and the file dragged into the wrong directory, the
# careless case this hook exists for, sailed into permanent history in silence.
# So: --no-renames, which reports the move as the add it really is, and ACMRT.
#
# The path list. A received document is called "Contract Signed 2024.pdf" or
# "Contrato Firmado Año.pdf", and either a space or a non-ASCII byte used to hide
# it from every check here: word-splitting broke the first, and git's default
# core.quotePath=true C-quotes the second into "private/A\303\261o.md", which
# matches no pattern and names no file. So: quotePath=false, one path per read,
# and a redirect rather than a pipe, which keeps fail=1 out of a subshell.
# Residual limitation: git quotes a path containing a newline, a double quote or
# a backslash whatever quotePath says, and such a path goes unchecked here.
#
# The bytes. Every check reads the staged blob (git show ":0:$f"), not the file
# in the working tree. The index is what enters permanent history; a worktree
# edited clean after `git add` would otherwise pass while the staged blob still
# carries what it carried. A submodule entry has no blob here, so it is skipped:
# what it points at is governed by that repo's own perimeter, not this one.
# Residual limitation: rule 3 below only ever applies to text, because grep -I
# discards a blob at its first NUL byte and says nothing - so a UTF-16 document,
# or a .md carrying a pasted binary run, passes the content rule unexamined. A
# clean report because the check could not see, which is the shape of a hole
# already closed here once. -I stays: regexing a 900 KiB PDF helps nobody, and
# this hook's honest scope is the careless case, not a determined one.
staged=$(mktemp)
trap 'rm -f "$staged"' EXIT
git -c core.quotePath=false diff --cached --no-renames --name-only --diff-filter=ACMRT > "$staged"

# 1. Size. Git stores every version of a binary in full.
while IFS= read -r f; do
  size=$(git show ":0:$f" 2>/dev/null | wc -c)
  if [ "$size" -gt 1048576 ]; then
    echo "perimeter: $f is $((size / 1024)) KiB - over the 1 MiB limit"; fail=1
  fi
done < "$staged"

# 2. Paths that must never be committed. Filled from interview question 3.
#    Example: private/*|secrets/*|*.key|*.p12
#    Quote any pattern containing a space: "personal notes/"*|*.key
#    No path rules at all? An empty placeholder is a syntax error, so either
#    delete this whole block, or leave one pattern that can never match a real
#    file, such as .perimeter-no-path-rules - and say in the agents file which.
while IFS= read -r f; do
  case "$f" in
    <FORBIDDEN_PATTERNS>) echo "perimeter: $f is outside the perimeter"; fail=1 ;;
  esac
done < "$staged"

# 3. Content patterns that must never be committed. Filled from question 3.
#    One extended regex: IBAN, national ID formats, API key prefixes.
#    No content rules? Replace the placeholder with an empty string, not nothing.
#    A double quote inside the value ends this string and changes what runs -
#    key="[A-Z]*" degrades to the unquoted word key=[A-Z]*, so the quotes that
#    were meant as literal characters become a zero-or-more and the rule fires
#    on the bare prefix key=, blocking a commit that holds no secret at all.
#    That false positive is the bad outcome here - it is what teaches people to
#    reach for --no-verify - and whether the word also globs against real
#    filenames, handing grep extra file operands, depends on the cwd.
#    ERE has no \d, \w or \s: write [0-9], [A-Za-z0-9_], [[:space:]] instead.
if [ -n "<CONTENT_PATTERNS>" ]; then
  while IFS= read -r f; do
    if git show ":0:$f" 2>/dev/null | grep -qEI "<CONTENT_PATTERNS>"; then
      echo "perimeter: $f matches a forbidden content pattern"; fail=1
    fi
  done < "$staged"
fi

exit $fail
