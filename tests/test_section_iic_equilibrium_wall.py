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
        [sys.executable, "scripts/python/section_iic_equilibrium_wall_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section II.C SymPy checks" in result.stdout
    assert "expected_nonzero_omitted_wall_residual" in result.stdout
    assert "homogeneous_temperature_coefficient" in result.stdout
    assert "W_to_helmholtz_rewriting" in result.stdout
    assert "grand_potential_shifted_coexistence_zero" in result.stdout
    assert "Wtot_surface_term_source_convention" in result.stdout


def test_section_records_wall_derivation_and_scope() -> None:
    text = _flat("sections/02c_equilibrium_conditions.tex")
    required = [
        "Typed Objects and Assumptions",
        "Equilibrium and wall status",
        "source-stated constrained-equilibrium setup",
        "source-stated wall entropy/energy model objects",
        "unresolved later-source data",
        "generalized chemical potential is constant",
        "One-Dimensional Interface Branch",
        "Surface-Tension Identity",
        "delta_e W",
        "source rewriting",
        "source grand-potential density",
        r"W_{\mathrm{tot}}",
        "Beltrami identity",
        "boundary part of the first variation",
        "Natural Wall Density Boundary Condition",
        "global entropy or total-energy balance",
        "Appendix-B B3 scaling is not involved",
    ]
    for phrase in required:
        assert phrase in text


def test_source_badges_match_section_iic_source_page() -> None:
    text = _read("sections/02c_equilibrium_conditions.tex")
    required_badges = {
        "2.22": "eq:iic-homogeneous-temperature",
        "2.23": "eq:iic-W-helmholtz-conversion",
        "2.24": "eq:iic-F",
        "2.25": "eq:iic-muhat-constant",
        "2.26": "eq:iic-grand-potential-density",
        "2.27": "eq:iic-gamma-n",
        "2.29": "eq:iic-Wtot",
        "2.30": "eq:iic-natural-wall-condition",
        "2.31": "eq:iic-fs",
        "2.32": "eq:iic-Ftot",
        "2.33": "eq:iic-quadratic-fs",
        "2.34": "eq:iic-quadratic-wall-condition",
    }
    for source_no, label in required_badges.items():
        label_index = text.index(f"\\label{{{label}}}")
        window = text[max(0, label_index - 220): label_index + 80]
        assert f"\\sourceeqbadge{{{source_no}}}" in window

    raw_index = text.index("\\label{eq:iic-first-integral-raw}")
    integral_index = text.index("\\label{eq:iic-first-integral}")
    first_integral_window = text[raw_index - 260: integral_index + 120]
    assert "\\sourceeqbadge{2.24}" not in first_integral_window
    assert "\\sourceeqbadge{2.25}" not in first_integral_window


def test_derivation_steps_record_verified_rows() -> None:
    with (ROOT / "research_notes/onuki_iic_derivation_steps.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["IIC-08"]["status"] == "VERIFIED"
    assert by_id["IIC-09"]["status"] == "VERIFIED"
    assert by_id["IIC-11"]["status"] == "VERIFIED"
    assert by_id["IIC-13"]["status"] == "VERIFIED"
    assert by_id["IIC-14"]["expression_after"] == "global entropy transfer not closed"


def test_wall_boundary_audit_separates_branches() -> None:
    text = _read("research_notes/onuki_iic_wall_boundary_audit.md")
    assert "M nu.grad n + (partial f_s/partial n)_T" in text
    assert "EXACT_SOURCE_WALL_BRANCH" in text
    assert "EXPECTED_NONZERO_OMITTED_WALL_RESIDUAL" in text
    assert "UNRESOLVED_NOT_CLOSED_HERE" in text


def test_global_transfer_remains_unresolved() -> None:
    combined = "\n".join(
        [
            _read("sections/02c_equilibrium_conditions.tex"),
            _read("research_notes/SECTION_IIC_EQUILIBRIUM_WALL_DERIVATION.md"),
            _read("research_notes/onuki_iic_wall_boundary_audit.md"),
        ]
    )
    assert "global entropy transfer" in combined
    assert "not closed" in combined
    forbidden = [
        "hydrodynamic equations are derived here",
        "global entropy transfer is closed",
        "Appendix-B B3 is resolved here",
        "proves PDE well-posedness",
    ]
    for phrase in forbidden:
        assert phrase not in combined
