from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def _flat(path: str) -> str:
    return " ".join(_read(path).split())


def test_sympy_momentum_b3_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_momentum_b3_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B momentum/B3 SymPy checks" in result.stdout
    assert "printed_minus_dimensional_source_b3_residual" in result.stdout
    assert "b3_branch_status_regression" in result.stdout


def test_appendix_b_preserves_both_b3_branches() -> None:
    text = _flat("appendices/B_scaled_equations_plan.tex")
    required = [
        "dimensional-source-consistent scaled branch",
        "\\mathsf{M}^{\\mathrm{src}}_{ij}",
        "\\mathsf{M}^{\\mathrm{print}}_{ij}",
        "2\\Theta(\\phi-1)\\Delta\\phi\\,\\delta_{ij}",
        "high-confidence typographical-omission candidate in the printed formula",
        "not an official erratum",
        "not evidence about the unpublished numerical implementation",
    ]
    for phrase in required:
        assert phrase in text


def test_branch_map_statuses_are_bounded() -> None:
    with (ROOT / "research_notes/onuki_appendix_b_b3_branch_map.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["row_id"]: row for row in rows}
    assert by_id["B3-01"]["status"] == "EXACT_UNDER_SCALING"
    assert by_id["B3-03"]["status"] == "SOURCE_BRANCH_DISCREPANCY"
    assert by_id["B3-06"]["status"] == "UNRESOLVED_SOURCE_DEPENDENT"
    assert by_id["B3-07"]["status"] == "COVERED_SEPARATE_APPENDIX_B_ROWS"


def test_momentum_b3_note_does_not_infer_code_or_erratum() -> None:
    text = _flat("research_notes/APPENDIX_B_MOMENTUM_B3_BRANCH_DERIVATION.md")
    forbidden = [
        "official erratum is established",
        "simulation code branch inferred",
        "numerical reproduction is required",
        "silently correct",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "not an official erratum" in text
    assert "not an inference about the unpublished 2007 simulation code" in text
    assert "UNRESOLVED_SOURCE_DEPENDENT" in text
    assert "covered by the separate Appendix-B energy/boundary derivation" in text


def test_source_target_rows_mark_b2_b3_complete() -> None:
    with (ROOT / "research_notes/onuki_scaled_dynamics_source_targets.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["target_id"]: row for row in rows}
    assert by_id["APPB-B2"]["baseline_status"] == "COMPLETED_MOMENTUM_SCALING"
    assert by_id["APPB-B3"]["baseline_status"] == "COMPLETED_BRANCH_ANALYSIS"
