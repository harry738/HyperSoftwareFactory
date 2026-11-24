#!/usr/bin/env bash
# Every test file, stopping at the first failure. CI and the project's checks.sh run this.
set -euo pipefail
cd "$(dirname "$0")/.."
py=$(command -v python || command -v python3)

for t in scripts/test_*.py factory/test_*.py; do
  # factory/test_factory.py covers the Windows patches and exits 1 on any other system.
  if [[ $t == factory/test_factory.py && ! $(uname -s) =~ ^(MINGW|MSYS|CYGWIN) ]]; then
    echo "== $t skipped: Windows only"
    continue
  fi
  echo "== $t"
  "$py" "$t"
done
echo "all test files passed"
