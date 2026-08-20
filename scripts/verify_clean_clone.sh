#!/usr/bin/env bash
set -euo pipefail

# Run inside an exported staging tree or a fresh clone.  The commands use only
# files inside that tree; Wolfram is deliberately a separate local, licensed
# layer and is not required for the portable open gate.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .standalone/file-manifest.json ]]; then
  python3 scripts/verify_standalone_export.py --export "$ROOT"
  TREE_MODE=export_staging_tree
else
  git rev-parse --is-inside-work-tree >/dev/null
  TREE_MODE=fresh_git_clone
  printf '%s\n' 'CLEAN_CLONE_GIT_METADATA_OK export_metadata_intentionally_excluded'
fi
make verify-source-policy
make verify-open
make verify-formal
make manuscript
git status --short 2>/dev/null || true
printf '%s\n' "CLEAN_CLONE_VERIFY_OK mode=${TREE_MODE} scope=open_python_lean_latex"
