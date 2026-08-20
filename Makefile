.PHONY: help setup-python verify-fast verify-python verify-lean verify-formal verify-wolfram verify-open verify-source-policy verify-clean-export verify-all manuscript links export clean python-list python-all python-dimensions

help:
	@printf '%s\n' 'Prerequisites: Python 3 with pytest/sympy/pint; PDFLaTeX/BibTeX for the PDF; Lean 4.29.0 for finite kernels.'
	@printf '%s\n' 'WolframKernel is a licensed local optional layer and is not executed by hosted CI.'
	@printf '%s\n' 'make verify-open       Run portable Python/SymPy/Pint/pytest checks (output: test status)'
	@printf '%s\n' 'make verify-wolfram    Run local Wolfram checks when WolframKernel exists (output: symbolic traces)'
	@printf '%s\n' 'make verify-lean       Build finite Mathlib kernels (output: Lake build status)'
	@printf '%s\n' 'make verify-formal     Audit formal placeholders and rebuild finite kernels'
	@printf '%s\n' 'make verify-source-policy  Scan tracked content for prohibited public artifacts and common secrets'
	@printf '%s\n' 'make verify-clean-export   Export twice and verify hash-stable portable staging trees'
	@printf '%s\n' 'make manuscript        Build the companion PDF (output: ignored main.pdf)'
	@printf '%s\n' 'make export OUT=/tmp/onuki-export  Create one deterministic standalone staging tree'
	@printf '%s\n' 'make python-list     List portable Python verification check IDs'
	@printf '%s\n' 'make python-all      Run portable Python verification check IDs'
	@printf '%s\n' 'make python-dimensions Run portable Pint dimensional checks'

setup-python:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -e '.[dev]'

verify-fast: verify-python

verify-python:
	PYTHONPATH=src python3 -m onuki2007_companion.cli python-all
	python3 -m pytest -q tests/test_python_package_cli.py tests/test_standalone_export.py tests/test_wolfram_literate_manifest.py tests/test_formal_reproducibility.py tests/test_clean_clone_reproducibility.py

verify-lean:
	cd formal/korteweg1901_mathlib && lake build

verify-formal:
	bash scripts/verify_formal_project.sh

verify-wolfram:
	@if command -v WolframKernel >/dev/null 2>&1; then bash scripts/run_verification.sh; else printf '%s\n' 'WolframKernel unavailable; run make verify-open instead.'; fi

verify-open: verify-python

verify-source-policy:
	python3 scripts/verify_public_source_policy.py

verify-clean-export:
	bash scripts/reproduce_clean_export.sh

python-list:
	PYTHONPATH=src python3 -m onuki2007_companion.cli list

python-all:
	PYTHONPATH=src python3 -m onuki2007_companion.cli python-all

python-dimensions:
	PYTHONPATH=src python3 -m onuki2007_companion.cli dimensions

verify-all:
	bash scripts/run_verification.sh

manuscript:
	bash scripts/build.sh

links:
	python3 scripts/verify_standalone_export.py --self-check

export:
	@test -n "$(OUT)" || (printf '%s\n' 'Set OUT to an external staging directory.'; exit 2)
	python3 scripts/export_standalone.py --output "$(OUT)"

clean:
	latexmk -C main.tex 2>/dev/null || true
	rm -rf .pytest_cache __pycache__ scripts/python/__pycache__ tests/__pycache__
