#!/bin/sh
# Perimeter check. Generated at bootstrap; owned by this repo, edit it freely.
# Never bypass with --no-verify. If it blocks something legitimate, change the rule.
set -eu
fail=0

# Staged paths go through a temp file, read one line at a time: a received
# document is often called "Contract Signed 2024.pdf", and word-splitting a
# space-containing path would wave through exactly the files this exists to stop.
# The loops read from the file rather than a pipe so that fail=1 survives.
# Residual limitation: a filename containing a NEWLINE still defeats this. Git
# quotes such paths by default (core.quotePath), so it is pathological, not likely.
staged=$(mktemp)
trap 'rm -f "$staged"' EXIT
git diff --cached --name-only --diff-filter=ACM > "$staged"

# 1. Size. Git stores every version of a binary in full.
while IFS= read -r f; do
  [ -f "$f" ] || continue
  size=$(wc -c < "$f")
  if [ "$size" -gt 1048576 ]; then
    echo "perimeter: $f is $((size / 1024)) KiB - over the 1 MiB limit"; fail=1
  fi
done < "$staged"

# 2. Paths that must never be committed. Filled from interview question 3.
#    Example: private/*  secrets/*  *.key  *.p12
while IFS= read -r f; do
  case "$f" in
    <FORBIDDEN_PATTERNS>) echo "perimeter: $f is outside the perimeter"; fail=1 ;;
  esac
done < "$staged"

# 3. Content patterns that must never be committed. Filled from question 3.
#    Example: IBAN, national ID formats, API keys.
if [ -n "<CONTENT_PATTERNS>" ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    if grep -nEI "<CONTENT_PATTERNS>" "$f" >/dev/null 2>&1; then
      echo "perimeter: $f matches a forbidden content pattern"; fail=1
    fi
  done < "$staged"
fi

exit $fail
