#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

python3 scripts/generate_manuscript_link_macros.py

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -file-line-error -halt-on-error main.tex
else
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -file-line-error -halt-on-error main.tex
fi
