from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _flat(path: str) -> str:
    return " ".join(_read(path).split())


def test_sympy_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/section_iia_vdw_baseline_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section II.A van der Waals baseline SymPy checks" in result.stdout
    assert "sound_speed_units\tPASS_DIMENSIONAL" in result.stdout
    assert "bulk_pressure_from_n_mu_minus_f" in result.stdout
    assert "specific_heat_ratio_from_pressure_derivatives" in result.stdout
    assert "sound_speed_squared_with_excluded_volume_denominator" in result.stdout
    assert "eq_2_10_dp_equals_n_dmu_route" in result.stdout
    assert "surface_tension_grand_potential_reduction" in result.stdout
    assert "surface_tension_monotone_density_change" in result.stdout
    assert "surface_tension_wrong_orientation_negative_control\tPASS_EXPECTED_NONZERO" in result.stdout


def test_section_records_typed_derivation_and_limitations() -> None:
    text = _flat("sections/02a_vdw_baseline.tex")
    required = [
        "Typed Objects and Assumptions",
        "Bulk Free Energy and Derived State Functions",
        "Spinodal Temperature, Sound Speed, and Heat-Capacity Ratio",
        "Equilibrium Gradient Free Energy",
        "Coexistence Constants and Profile Terminology",
        "Fixed-Temperature Route to the Interface Pressure Relation",
        "companion derivation step, not an additional source equation",
        "The logarithmic terms cancel",
        "The fixed-entropy differential is",
        "c_{\\rm der}=\\frac{1}{1-v_0n}",
        "source-fidelity discrepancy",
        "Section III scaled coefficient",
        "not as a formal erratum",
        "\\dd p=n\\,\\dd\\mu",
        "first-order term is",
        "endpoint variations fixed",
        "not a mechanical stress law",
        "not a decision about the Appendix-B printed/scaled branch",
        "fixed-temperature pressure bridge",
        "eq:iia-interface-pressure-relation",
        "eq:iia-coexistence-bulk-conditions",
        "equilibrium density profile",
        "not a time trajectory",
        "eq:iia-grand-potential-first-integral",
        "square-gradient first-integral route",
        "eq:iia-surface-tension-density-change",
        "inspected Korteweg 1901 source provides historical and mechanical-stress context",
        "unpublished simulation-code branch remains unresolved",
    ]
    for phrase in required:
        assert phrase in text


def test_derivation_steps_record_statuses() -> None:
    with (ROOT / "research_notes/onuki_iia_derivation_steps.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["IIA-02"]["status"] == "VERIFIED"
    assert by_id["IIA-07"]["status"] == "VERIFIED"
    assert by_id["IIA-09"]["status"] == "VERIFIED"
    assert by_id["IIA-10"]["status"] == "VERIFIED"
    assert "fixed-temperature pressure bridge" in by_id["IIA-10"]["notes"]
    assert "no Appendix-B branch decision" in by_id["IIA-10"]["notes"]


def test_symbol_registry_has_core_objects() -> None:
    with (ROOT / "research_notes/onuki_iia_symbol_type_registry.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    seen = {row["symbol"] for row in rows}
    for symbol in ["n", "T", "f", "mu", "p", "s", "e", "T_s", "c", "gamma_s", "M", "gamma"]:
        assert symbol in seen


def test_section_does_not_overclaim_physics_or_b3_closure() -> None:
    combined = "\n".join(
        [
            _read("sections/02a_vdw_baseline.tex"),
            _read("research_notes/SECTION_IIA_THERMODYNAMIC_BASELINE_DERIVATION.md"),
        ]
    )
    forbidden = [
        "formal erratum is established",
        "simulation-code branch is known",
        "proves the physical equation of state",
        "proves the second law",
        "PDE well-posedness is proved",
    ]
    for phrase in forbidden:
        assert phrase not in combined
