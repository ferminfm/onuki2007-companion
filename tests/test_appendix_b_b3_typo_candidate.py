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


def test_sympy_typo_candidate_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_b3_typo_candidate_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B B3 typo-candidate SymPy checks" in result.stdout
    assert "diagonal_laplacian_scales_to_minus_two_theta_phi_lap_phi" in result.stdout
    assert "one_dimensional_force_residual_generically_nonzero" in result.stdout
    assert "NEGATIVE_CONTROL_NOT_SOURCE_GROUNDED" in result.stdout


def test_appendix_b_direct_proof_is_present_and_bounded() -> None:
    text = _flat("appendices/B_scaled_equations_plan.tex")
    required = [
        "Direct Check of the B3 Diagonal Laplacian Factor",
        "-2\\Theta\\phi\\Delta_{\\rm sc}\\phi",
        "high-confidence typographical-omission candidate in the printed Eq.~(B3) branch under the dimensional-source derivation",
        "not an official erratum",
        "not a statement of author intent",
        "not evidence about the unpublished simulation-code branch",
    ]
    for phrase in required:
        assert phrase in text


def test_article_facing_prose_uses_neutral_source_language() -> None:
    article_files = [
        "README.md",
        "main.tex",
        "sections/00_companion_scope.tex",
        "appendices/B_scaled_equations_plan.tex",
    ]
    for path in article_files:
        text = _read(path)
        assert "copyright-safe" not in text.lower()
        assert "without utilizing the original material" not in text.lower()
    assert "reconstructs the calculations independently" in _read("sections/00_companion_scope.tex")


def test_typo_candidate_steps_and_branch_map_statuses() -> None:
    with (ROOT / "research_notes/onuki_appendix_b_b3_typo_candidate_steps.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["B3TYPO-03"]["expected_result"] == "-2 Theta phi Delta_sc phi"
    assert by_id["B3TYPO-06"]["status"] == "SOURCE_BRANCH_DISCREPANCY"
    assert by_id["B3TYPO-08"]["status"] == "NEGATIVE_CONTROL_NOT_SOURCE_GROUNDED"
    assert by_id["B3TYPO-09"]["status"] == "UNRESOLVED_SOURCE_DEPENDENT"

    with (ROOT / "research_notes/onuki_appendix_b_b3_branch_map.csv").open(newline="") as handle:
        branch_rows = {row["row_id"]: row for row in csv.DictReader(handle)}
    assert branch_rows["B3-03"]["status"] == "SOURCE_BRANCH_DISCREPANCY"
    assert "Typographical omission under dimensional-source derivation" in branch_rows["B3-03"]["notes"]
    assert branch_rows["B3-06"]["status"] == "UNRESOLVED_SOURCE_DEPENDENT"


def test_proof_note_preserves_unresolved_boundaries() -> None:
    text = _flat("research_notes/APPENDIX_B_B3_TYPO_CANDIDATE_PROOF.md")
    assert "typographical omission under the dimensional-source derivation" in text
    assert "official author intent" in text
    assert "which branch, if any, was used in unpublished simulation code" in text
    forbidden = [
        "official erratum is established",
        "author intended",
        "simulation code used",
        "numerical impact is proven",
    ]
    for phrase in forbidden:
        assert phrase not in text
