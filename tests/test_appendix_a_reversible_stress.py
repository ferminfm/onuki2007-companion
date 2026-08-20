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
        [sys.executable, "scripts/python/appendix_a_reversible_stress_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix A reversible-stress SymPy checks" in result.stdout
    assert "expected_nonzero_omitted_offdiagonal_residual" in result.stdout
    assert "determinant_first_order_trace" in result.stdout
    assert "material_density_variation_A1" in result.stdout
    assert "gradient_square_variation_A3" in result.stdout
    assert "entropy_variation_A4_coefficients" in result.stdout
    assert "stress_identification_residual_A4" in result.stdout
    assert "p1_bridge_to_pressure_tensor" in result.stdout
    assert "material_gradient_variation_A3_substitution" in result.stdout
    assert "material_gradient_ibp_with_boundary_A3" in result.stdout
    assert "expected_nonzero_omitted_material_gradient_boundary" in result.stdout


def test_appendix_records_typed_derivation_and_signs() -> None:
    text = _flat("appendices/A_reversible_stress_plan.tex")
    required = [
        "Virtual Displacement and Density Variation",
        "delta_E n",
        "-\\grad\\cdot(nu)",
        "Coordinate Derivatives and the Gradient Term",
        "det F=1+",
        "material compression term",
        "partial_i' n'",
        "eq:app-a-material-density-gradient",
        "eq:app-a-material-gradient-variation",
        "eq:app-a-material-gradient-ibp",
        "eq:app-a-material-gradient-scalar-bulk",
        "C_c^2",
        "source Eq. (2.48)",
        "Entropy Variation and Identification of the Tensor",
        "entropy-density volume contribution",
        "Reversible Stress from Virtual Displacement",
        "f_i^{\\mathrm{rev}}",
        "-\\partial_j\\Pi_{ij}",
        "Appendix-B B3 printed/scaled branch remains unresolved here",
    ]
    for phrase in required:
        assert phrase in text


def test_appendix_a_source_badges_are_not_misused() -> None:
    text = _read("appendices/A_reversible_stress_plan.tex")
    required_badges = {
        "A1": "eq:app-a-material-density-variation",
        "A2": "eq:app-a-energy-work-convention",
        "A3": "eq:app-a-derivative-transform",
        "A4": "eq:app-a-entropy-variation-collected",
        "2.47": "eq:app-a-pi-pressure-form",
        "2.48": "eq:app-a-p1-thermo-form",
    }
    for source_no, label in required_badges.items():
        label_index = text.index(f"\\label{{{label}}}")
        window = text[max(0, label_index - 260): label_index + 80]
        assert f"\\sourceeqbadge{{{source_no}}}" in window

    eulerian_index = text.index("\\label{eq:app-a-eulerian-density-variation}")
    eulerian_window = text[max(0, eulerian_index - 220): eulerian_index + 80]
    assert "\\sourceeqbadge{A1}" not in eulerian_window

    pressure_index = text.index("\\label{eq:app-a-pi-pressure-form}")
    pressure_window = text[max(0, pressure_index - 220): pressure_index + 80]
    assert "\\sourceeqbadge{A3}" not in pressure_window
    assert "\\sourceeqbadge{A4}" not in pressure_window


def test_derivation_steps_record_verified_rows() -> None:
    with (ROOT / "research_notes/onuki_appendix_a_derivation_steps.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["APPA-04"]["status"] == "VERIFIED"
    assert by_id["APPA-14"]["status"] == "VERIFIED"
    assert by_id["APPA-15"]["status"] == "VERIFIED"
    assert by_id["APPA-16"]["expression_after"] == "deferred"
    assert by_id["APPA-26"]["status"] == "VERIFIED"
    assert by_id["APPA-27"]["status"] == "VERIFIED"
    assert by_id["APPA-28"]["status"] == "BOUNDARY_BRANCH_EXPLICIT"


def test_sign_convention_note_preserves_scope() -> None:
    text = _read("research_notes/onuki_appendix_a_stress_sign_conventions.md")
    assert "momentum force density from reversible stress = - partial_j Pi_ij" in text
    assert "internal-energy reversible stress power" in text
    assert "Appendix-B B3 printed/scaled branch is not resolved" in text
    assert "No unpublished simulation-code branch is inferred" in text


def test_iid_forward_reference_only() -> None:
    text = _flat("sections/02d_hydrodynamic_equations.tex")
    assert "Appendix~\\ref{app:reversible-stress-derivation}" in text
    assert "Internal Energy from Total Energy and Kinetic Bookkeeping" in text
    assert "Appendix-B B3 scaling is not used here" in text
    forbidden = [
        "Appendix-B B3 is resolved",
        "simulation-code branch is inferred",
        "global entropy closure is complete",
    ]
    for phrase in forbidden:
        assert phrase not in text
