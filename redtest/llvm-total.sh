#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <instrumented-object> <profdata> <source-file> [source-file ...]" >&2
    exit 2
fi

OBJECT=$1
PROFDATA=$2
shift 2
SOURCES=("$@")

REPORT_OUTPUT="$(
    LC_ALL=C llvm-cov report \
        --instr-profile="${PROFDATA}" \
        "${OBJECT}" \
        "${SOURCES[@]}" 2>&1
)"
printf '%s\n' "${REPORT_OUTPUT}"

EXPORT_JSON="$(
    LC_ALL=C llvm-cov export \
        --summary-only \
        --format=text \
        --instr-profile="${PROFDATA}" \
        "${OBJECT}" \
        "${SOURCES[@]}"
)"

TOTAL="$(
    python3 -c '
import json
import sys

data = json.load(sys.stdin)
try:
    percent = data["data"][0]["totals"]["lines"]["percent"]
except (KeyError, IndexError, TypeError) as exc:
    raise SystemExit(f"unable to extract line coverage from llvm-cov JSON: {exc}")
print(f"{percent:.2f}%")
' <<<"${EXPORT_JSON}"
)"

printf 'Total coverage:|%s\n' "${TOTAL}"
