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


def test_sympy_p1_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/section_iid_p1_pressure_expansion_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section II.D p1 pressure-expansion SymPy checks" in result.stdout
    assert "p1_thermodynamic_reconstruction" in result.stdout
    assert "expected_nonzero_replace_MnT_by_spatial_derivative" in result.stdout
    assert "expected_nonzero_omit_temperature_gradient_pressure_term" in result.stdout
    assert "appendix_b_b3_branch_deferred" in result.stdout
    assert "pressure_tensor_satisfies_reversible_condition_eq_244" in result.stdout


def test_section_contains_derivative_expansion_and_derivative_warning() -> None:
    text = _flat("sections/02d_hydrodynamic_equations.tex")
    required = [
        "Derivative Expansion of the Diagonal Gradient Pressure",
        "p_1=n\\hat\\mu-\\hat e+T\\hat S-p",
        "M_n|_T=(\\partial M/\\partial n)_T",
        "\\grad M = M_n|_T\\,\\grad n + M_T|_n\\,\\grad T",
        "\\frac{1}{2}\\left(nM_n|_T-M\\right)|\\grad n|^2",
        "Appendix B later rescales this tensor",
        "printed-B3 versus dimensional-source branch",
    ]
    for phrase in required:
        assert phrase in text


def test_p1_derivation_steps_record_statuses() -> None:
    with (ROOT / "research_notes/onuki_iid_p1_derivation_steps.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["P1-01"]["status"] == "VERIFIED"
    assert by_id["P1-05"]["status"] == "VERIFIED"
    assert by_id["P1-07"]["status"] == "VERIFIED"
    assert by_id["P1-09"]["status"] == "DEFERRED"


def test_p1_symbol_registry_separates_derivatives() -> None:
    with (ROOT / "research_notes/onuki_iid_p1_symbol_type_registry.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_symbol = {row["symbol"]: row for row in rows}
    assert by_symbol["M_n|T"]["role"] == "density derivative of M at fixed T"
    assert "not spatial grad M" in by_symbol["M_n|T"]["notes"]
    assert by_symbol["grad M"]["role"] == "spatial derivative"
    assert by_symbol["B3 branch"]["notes"] == "deferred in this pass"


def test_pressure_tensor_branch_audit_preserves_b3_deferral() -> None:
    text = _read("research_notes/onuki_iid_pressure_tensor_branch_audit.md")
    assert "Appendix-B scaling" in text
    assert "printed-B3 versus dimensional-source branch remains separate" in text
    assert "does not perform Appendix-B scaling" in text
    assert "do not prove" in text.lower()


def test_no_forbidden_p1_overclaims() -> None:
    combined = "\n".join(
        [
            _read("sections/02d_hydrodynamic_equations.tex"),
            _read("research_notes/SECTION_IID_P1_PRESSURE_EXPANSION.md"),
            _read("research_notes/onuki_iid_pressure_tensor_branch_audit.md"),
        ]
    )
    forbidden = [
        "Appendix-B B3 scaling is resolved",
        "printed-B3 branch is corrected",
        "official erratum",
        "simulation-code branch is inferred",
        "proves the PDE model",
        "proves thermodynamic consistency",
    ]
    for phrase in forbidden:
        assert phrase not in combined
