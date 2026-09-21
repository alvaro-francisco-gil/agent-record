#!/bin/sh
# Perimeter check. Generated at bootstrap; owned by this repo, edit it freely.
# Never bypass with --no-verify. If it blocks something legitimate, change the rule.
set -eu
fail=0

# Two things below are load-bearing, so change them only on purpose.
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
staged=$(mktemp)
trap 'rm -f "$staged"' EXIT
git -c core.quotePath=false diff --cached --name-only --diff-filter=ACM > "$staged"

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
while IFS= read -r f; do
  case "$f" in
    <FORBIDDEN_PATTERNS>) echo "perimeter: $f is outside the perimeter"; fail=1 ;;
  esac
done < "$staged"

# 3. Content patterns that must never be committed. Filled from question 3.
#    One extended regex: IBAN, national ID formats, API key prefixes.
#    No content rules? Replace the placeholder with an empty string, not nothing.
if [ -n "<CONTENT_PATTERNS>" ]; then
  while IFS= read -r f; do
    if git show ":0:$f" 2>/dev/null | grep -qEI "<CONTENT_PATTERNS>"; then
      echo "perimeter: $f matches a forbidden content pattern"; fail=1
    fi
  done < "$staged"
fi

exit $fail
