#!/usr/bin/env python3
"""Scaffold integrity checks for the Onuki 2007 companion.

This script checks repository structure, source-ledger rows, bibliography keys,
and public-scope markers. It is a project-hygiene regression, not a scientific
verification layer.
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "README.md",
    "main.tex",
    "preamble.tex",
    "macros.tex",
    "research_notes/COPYRIGHT_SAFE_COMPANION_POLICY.md",
    "research_notes/ONUKI2007_SOURCE_EQUATION_LEDGER.csv",
    "research_notes/ONUKI2007_EQUATION_DEPENDENCY_GRAPH.md",
    "research_notes/ONUKI2007_VERIFICATION_PLAN.md",
    "research_notes/ONUKI2007_NOTATION_CROSSWALK.md",
    "research_notes/ONUKI2007_OPEN_ISSUES_FROM_FUKAGAWA_AUDIT.md",
    "references/onuki2007_companion.bib",
]

LEDGER_COLUMNS = [
    "equation_number",
    "section",
    "pdf_page",
    "printed_page",
    "object_type",
    "variables",
    "dependencies",
    "derivation_planned",
    "verification_planned",
    "related_fukagawa_audit_issue",
]

REQUIRED_LEDGER_ROWS = {
    "(2.12)--(2.15)",
    "(2.16)--(2.19)",
    "(2.35)",
    "(2.36)",
    "(2.38)",
    "(2.39)",
    "(2.40)",
    "(2.49)",
    "(2.50)",
    "(2.51)--(2.53)",
    "(B3)",
    "(B5)",
    "(B6)",
    "simulation_boundary_assumptions",
}


def test_required_files_exist() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    assert not missing, f"Missing required files: {missing}"


def test_ledger_schema_and_rows() -> None:
    ledger = ROOT / "research_notes/ONUKI2007_SOURCE_EQUATION_LEDGER.csv"
    with ledger.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, "ledger has no rows"
    assert rows[0].keys() == set(LEDGER_COLUMNS)
    seen = {row["equation_number"] for row in rows}
    missing = REQUIRED_LEDGER_ROWS - seen
    assert not missing, f"ledger missing required rows: {sorted(missing)}"


def test_no_source_pdfs_tracked_in_companion() -> None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.pdf"],
        text=True,
        capture_output=True,
        check=True,
    )
    tracked_pdfs = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() != "main.pdf"
    ]
    assert not tracked_pdfs, (
        "source or generated PDFs must remain untracked in the companion: "
        f"{tracked_pdfs}"
    )


def test_policy_declares_original_companion() -> None:
    text = " ".join((ROOT / "README.md").read_text().split())
    required = [
        "original guided-derivation companion",
        "does not reproduce the paper",
        "original paper is required reading",
    ]
    for phrase in required:
        assert phrase in text


def main() -> int:
    test_required_files_exist()
    test_ledger_schema_and_rows()
    test_no_source_pdfs_tracked_in_companion()
    test_policy_declares_original_companion()
    print("PASS: Onuki 2007 companion scaffold integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
