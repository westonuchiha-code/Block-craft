#!/bin/bash
# Build the rebuild and run its browser tests. Each prints its own result; the script exits non-zero if any failed.
cd "$(dirname "$0")/.." && node tools/build.mjs || exit 1
cd tests2
fail=0
for t in smoke play ui4k; do
  out=$(timeout 600 python3 -u $t.py 2>&1); rc=$?
  echo "$t rc=$rc | $(echo "$out" | tail -1 | cut -c1-120)"
  [ $rc -ne 0 ] && fail=1
done
exit $fail
