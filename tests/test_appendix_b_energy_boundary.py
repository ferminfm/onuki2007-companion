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


def test_sympy_energy_boundary_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_energy_boundary_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B energy/boundary SymPy checks" in result.stdout
    assert "energy_density_b4_reconstruction" in result.stdout
    assert "expected_nonzero_missing_kinetic_density_factor" in result.stdout
    assert "expected_nonzero_wrong_gravity_power_sign" in result.stdout
    assert "expected_nonzero_mixed_dimensional_scaled_velocity" in result.stdout
    assert "expected_nonzero_omitted_global_wall_transfer" in result.stdout


def test_pint_energy_boundary_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/appendix_b_energy_boundary_units.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Appendix B energy/boundary Pint checks" in result.stdout
    assert "energy_density_scaled" in result.stdout
    assert "boundary_rhs_scaled" in result.stdout


def test_appendix_b_contains_energy_and_boundary_scaling() -> None:
    text = _flat("appendices/B_scaled_equations_plan.tex")
    required = [
        "Scaled Total-Energy Density",
        "E_T=\\phi\\Theta-\\phi^2+\\frac{\\sigma}{2}\\phi |V|^2",
        "\\nabla\\cdot(\\phi\\nabla\\Theta)-g^*\\phi V_z",
        "\\nu\\cdot\\nabla\\phi=\\frac{\\phi-5/6}{2\\sqrt{2}}",
        "does not by itself specify the heat boundary data",
    ]
    for phrase in required:
        assert phrase in text


def test_energy_boundary_map_statuses_are_bounded() -> None:
    with (ROOT / "research_notes/onuki_appendix_b_energy_boundary_map.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["row_id"]: row for row in rows}
    assert by_id["EB-01"]["status"] == "EXACT_UNDER_SCALING"
    assert by_id["EB-05"]["status"] == "EXACT_UNDER_SCALING"
    assert by_id["EB-06"]["status"] == "BOUNDARY_TRANSFER_REQUIRED"
    assert by_id["EB-07"]["status"] == "UNRESOLVED_SOURCE_DEPENDENT"


def test_source_target_rows_mark_b4_b5_b6_complete() -> None:
    with (ROOT / "research_notes/onuki_scaled_dynamics_source_targets.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["target_id"]: row for row in rows}
    assert by_id["APPB-B4"]["baseline_status"] == "COMPLETED_ENERGY_DENSITY_SCALING"
    assert by_id["APPB-B5"]["baseline_status"] == "COMPLETED_LOCAL_ENERGY_SCALING"
    assert by_id["APPB-B6"]["baseline_status"] == "COMPLETED_DENSITY_BOUNDARY_SCALING"
