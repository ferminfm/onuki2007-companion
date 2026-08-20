#!/usr/bin/env bash
set -euo pipefail

# Run inside an exported staging tree or a fresh clone.  The commands use only
# files inside that tree; Wolfram is deliberately a separate local, licensed
# layer and is not required for the portable open gate.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/verify_standalone_export.py --export "$ROOT"
make verify-source-policy
make verify-open
make verify-formal
make manuscript
git status --short 2>/dev/null || true
printf '%s\n' 'CLEAN_CLONE_VERIFY_OK scope=exported_tree_open_python_lean_latex'
