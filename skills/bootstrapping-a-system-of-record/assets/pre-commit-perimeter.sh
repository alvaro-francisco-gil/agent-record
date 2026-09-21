#!/bin/sh
# Perimeter check. Generated at bootstrap; owned by this repo, edit it freely.
# Never bypass with --no-verify. If it blocks something legitimate, change the rule.
set -eu
fail=0
staged=$(git diff --cached --name-only --diff-filter=ACM)

# 1. Size. Git stores every version of a binary in full.
for f in $staged; do
  [ -f "$f" ] || continue
  size=$(wc -c < "$f")
  if [ "$size" -gt 1048576 ]; then
    echo "perimeter: $f is $((size / 1024)) KiB - over the 1 MiB limit"; fail=1
  fi
done

# 2. Paths that must never be committed. Filled from interview question 3.
#    Example: private/  secrets/  *.key  *.p12
for f in $staged; do
  case "$f" in
    <FORBIDDEN_PATTERNS>) echo "perimeter: $f is outside the perimeter"; fail=1 ;;
  esac
done

# 3. Content patterns that must never be committed. Filled from question 3.
#    Example: IBAN, national ID formats, API keys.
if [ -n "<CONTENT_PATTERNS>" ]; then
  for f in $staged; do
    [ -f "$f" ] || continue
    if grep -nEI "<CONTENT_PATTERNS>" "$f" >/dev/null 2>&1; then
      echo "perimeter: $f matches a forbidden content pattern"; fail=1
    fi
  done
fi

exit $fail
