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


def test_sympy_scaling_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_scaling_definitions_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B scaling-definition SymPy checks" in result.stdout
    assert "sigma_two_forms_equivalent" in result.stdout
    assert "b2_continuity_common_prefactor" in result.stdout
    assert "expected_nonzero_wrong_coordinate_derivative_scale" in result.stdout
    assert "b4_b5_b6_covered_by_energy_boundary_mirrors" in result.stdout


def test_pint_scaling_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_scaling_definitions_units.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B scaling-definition Pint checks" in result.stdout
    assert "phi_dimensionless" in result.stdout
    assert "thermal_conductivity_branch_units" in result.stdout


def test_appendix_b_contains_typed_scale_definitions() -> None:
    text = _flat("appendices/B_scaled_equations_plan.tex")
    required = [
        "Purpose and Scope",
        "\\ell=\\left(\\frac{C}{2k_Bv_0}\\right)^{1/2}",
        "t_0=\\frac{\\ell^2}{\\nu_0}",
        "\\phi=v_0 n",
        "\\Theta=\\frac{k_B T}{\\epsilon}",
        "V=\\frac{t_0}{\\ell}v",
        "Branchwise Scaled Pressure Tensor",
        "dimensional-source-consistent scaled branch",
        "scaled energy equation or validate any numerical run",
    ]
    for phrase in required:
        assert phrase in text


def test_scaling_registry_preserves_bounded_branches_and_coverage() -> None:
    with (ROOT / "research_notes/onuki_appendix_b_scaling_registry.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_symbol = {row["symbol"]: row for row in rows}
    assert by_symbol["phi"]["status"] == "VERIFIED_DIMENSIONLESS"
    assert by_symbol["sigma"]["status"] == "VERIFIED_DIMENSIONLESS"
    assert by_symbol["B3_branch"]["status"] == "COMPLETED_BRANCH_ANALYSIS"
    assert by_symbol["simulation_code_branch"]["status"] == "UNRESOLVED_SOURCE_DEPENDENT"


def test_scaling_note_does_not_derive_later_equations() -> None:
    text = _flat("research_notes/APPENDIX_B_SCALING_DEFINITIONS.md")
    forbidden = [
        "B3 branch resolved",
        "simulation code branch inferred",
        "numerical reproduction",
        "scaled total-energy equation is derived by the scaling-definition pass",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "records definitions and points to the separate mirrors for B2--B6" in text
    assert "B3 branch analysis is covered by the momentum/B3 mirrors" in text
    assert "B4--B6 are covered by the energy/boundary mirrors" in text
