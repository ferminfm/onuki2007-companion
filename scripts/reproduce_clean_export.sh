#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="${TMPDIR:-/tmp}/onuki-clean-export-$$"
FIRST="$BASE/first"
SECOND="$BASE/second"
cleanup() { rm -rf "$BASE"; }
trap cleanup EXIT

mkdir -p "$BASE"
python3 "$ROOT/scripts/export_standalone.py" --output "$FIRST"
python3 "$ROOT/scripts/export_standalone.py" --output "$SECOND"
python3 "$ROOT/scripts/verify_standalone_export.py" --export "$FIRST"
python3 "$ROOT/scripts/verify_standalone_export.py" --export "$SECOND"

first_digest="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["tree_digest"])' "$FIRST/.standalone/export-metadata.json")"
second_digest="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["tree_digest"])' "$SECOND/.standalone/export-metadata.json")"
test "$first_digest" = "$second_digest"
printf '%s\n' "CLEAN_EXPORT_REPRODUCIBLE_OK digest=$first_digest"
