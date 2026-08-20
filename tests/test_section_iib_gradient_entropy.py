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


def test_sympy_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/section_iib_gradient_entropy_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section II.B SymPy checks" in result.stdout
    assert "source_eq_2_17_factor_n" in result.stdout
    assert "section_iia_consistency_s_e_ratio" in result.stdout
    assert "local_differential_identity_coefficients" in result.stdout
    assert "diagnostic_term_removal_leaves_C_grad_T" in result.stdout
    assert "diagnostic_term_removal_is_generically_nonzero" in result.stdout
    assert "PASS_EXPECTED_NONZERO" in result.stdout


def test_section_records_typed_derivation_and_boundaries() -> None:
    text = _flat("sections/02b_gradient_entropy_energy.tex")
    required = [
        "Typed Objects and Regularity Assumptions",
        "Definition and relation status",
        "source-stated model functionals",
        "derived coefficient identity",
        "not yet a force density",
        "M=CT+K",
        "n\\left(\\frac{\\partial s}{\\partial e}\\right)_n",
        "local equilibrium premise",
        "entropy per particle",
        "Section II.A van der Waals formulas",
        "\\left(\\frac{\\partial s}{\\partial e}\\right)_n",
        "pointwise local equilibrium identity",
        "generalized chemical potential",
        "n_\\varepsilon=n+\\varepsilon\\eta",
        "first-order",
        "fixed-temperature derivative used by the source",
        "pointwise product-rule",
        "outward-normal convention",
        "diagnostic term-removal test expression",
        "not a source equation",
        "B3 printed-source branch",
        "reversible stress tensor",
    ]
    for phrase in required:
        assert phrase in text
    assert "written thermodynamically" not in text


def test_derivation_step_registry_contains_required_rows() -> None:
    with (ROOT / "research_notes/onuki_iib_derivation_steps.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["IIB-10"]["status"] == "DONE"
    assert by_id["IIB-02"]["operation"] == "local temperature definition"
    assert "1/T=n(partial s/partial e)_n" in by_id["IIB-02"]["expression_after"]
    assert by_id["IIB-13"]["status"] == "VERIFIED"
    assert by_id["IIB-14"]["status"] == "VERIFIED"
    assert by_id["IIB-15"]["status"] == "VERIFIED"
    assert by_id["IIB-16"]["status"] == "VERIFIED"
    assert "Diagnostic term-removal" in by_id["IIB-16"]["notes"]


def test_boundary_audit_has_correct_sign_and_scope() -> None:
    text = _read("research_notes/onuki_iib_boundary_term_audit.md")
    assert "- int_boundary (M/T)(nu . grad n) delta n da" in text
    assert "outward-normal convention" in text
    assert "not the physical wall model" in text
    assert "B3 issue is unrelated" in text


def test_diagnostic_test_is_not_source_attributed() -> None:
    combined = "\n".join(
        [
            _read("sections/02b_gradient_entropy_energy.tex"),
            _read("research_notes/SECTION_IIB_GRADIENT_ENTROPY_DERIVATION.md"),
            _read("research_notes/onuki_iib_derivation_steps.csv"),
        ]
    )
    forbidden = [
        "counterfactual ablation",
        "Onuki uses the grad-M-only",
        "Fukagawa uses the grad-M-only",
        "source discrepancy for the grad-M-only",
        "corrected Onuki",
    ]
    for phrase in forbidden:
        assert phrase not in combined
    assert "not a source equation" in combined
