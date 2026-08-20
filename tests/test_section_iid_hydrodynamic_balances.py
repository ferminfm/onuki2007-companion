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
        [sys.executable, "scripts/python/section_iid_hydrodynamic_balance_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section II.D hydrodynamic-balance SymPy checks" in result.stdout
    assert "viscous_heat_production_decomposition_2d" in result.stdout
    assert "entropy_rate_eq_242_time_derivative_substitution" in result.stdout
    assert "reversible_residual_cancellation_eq_244" in result.stdout
    assert "symmetric_stress_power_dummy_index_swap" in result.stdout
    assert "thermal_heat_product_rule_eq_245" in result.stdout
    assert "gibbs_duhem_identity_eq_246" in result.stdout
    assert "expected_nonzero_wrong_reversible_stress_sign" in result.stdout
    assert "entropy_flux_reconstruction_eq_249" in result.stdout
    assert "entropy_flux_missing_mass_balance_residual_factor" in result.stdout
    assert "expected_nonzero_entropy_flux_without_number_balance" in result.stdout
    assert "expected_nonzero_added_flux_gauge" in result.stdout
    assert "expected_nonzero_omitted_reversible_entropy_flux" in result.stdout
    assert "expected_nonzero_omitted_boundary_transfer" in result.stdout
    assert "UNRESOLVED_BOUNDARY_TRANSFER_RECORDED" in result.stdout
    assert "static_gravity_stress_balance_eq_251" in result.stdout
    assert "gravity_modified_mu_hat_eq_252" in result.stdout
    assert "conductive_boundary_sign_eq_253" in result.stdout
    assert "wall_helmholtz_rate_identity_eq_253" in result.stdout


def test_section_iid_records_typed_balance_derivation() -> None:
    text = _flat("sections/02d_hydrodynamic_equations.tex")
    required = [
        "Typed Objects and Assumptions",
        "Number-Density Balance",
        "Balance-Law, Closure, and Local/Global Status Ledger",
        "Balance-law inputs",
        "Constitutive closures",
        "Bookkeeping identities",
        "Reversible residual choice",
        "Momentum Balance and Stress-Divergence Convention",
        "Total Energy Balance and Flux Terms",
        "Internal Energy from Total Energy and Kinetic Bookkeeping",
        "Viscous Heat Production",
        "Bulk Entropy Rate from the Section II.B Variation",
        "Substitution into the Bulk Entropy Rate",
        "Reversible-Stress Residual Cancellation",
        "Thermal Heat Production",
        "Gibbs--Duhem Identity Used for the Reversible Stress",
        "sourceeqbadge{2.41}",
        "sourceeqbadge{2.42}",
        "sourceeqbadge{2.43}",
        "sourceeqbadge{2.44}",
        "sourceeqbadge{2.45}",
        "sourceeqbadge{2.46}",
        "not a proof of the second law",
        "Reversible Entropy Flux",
        "Pointwise Assembly of the Entropy Flux",
        "eq:iid-local-entropy-time-variation",
        "eq:iid-entropy-flux-before-gradient-combination",
        "eq:iid-entropy-flux-mass-balance-combination",
        r"D_tn+n\grad\cdot v",
        "Local Capillary Energy-Flux Gauge",
        "Global Entropy Balance and Boundary Transfer",
        "One-Dimensional Gravity Equilibrium",
        "J_s^{\\mathrm{rev}}=-\\frac{1}{T}J_{\\mathrm{GA}}",
        "integrated entropy balance",
        "boundary- and wall-transfer issue",
    ]
    for phrase in required:
        assert phrase in text


def test_derivation_steps_have_expected_statuses() -> None:
    with (ROOT / "research_notes/onuki_iid_derivation_steps.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["IID-07"]["status"] == "VERIFIED"
    assert by_id["IID-08"]["status"] == "VERIFIED"
    assert by_id["IID-11"]["status"] == "VERIFIED"
    assert by_id["IID-12"]["status"] == "UNRESOLVED_BOUNDARY_TRANSFER"
    assert by_id["IID-23"]["status"] == "VERIFIED"
    assert by_id["IID-24"]["status"] == "VERIFIED"


def test_symbol_registry_separates_local_and_global_objects() -> None:
    with (ROOT / "research_notes/onuki_iid_symbol_type_registry.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_symbol = {row["symbol"]: row for row in rows}
    assert by_symbol["e_T"]["role"] == "total-energy density"
    assert by_symbol["J_s_rev"]["notes"] == "local flux contribution only"
    assert "blocks bulk-only integrated closure" in by_symbol["e_s_dot"]["notes"]


def test_global_entropy_transfer_remains_open() -> None:
    text = _read("research_notes/onuki_iid_entropy_production_audit.md")
    assert "This relation is local" in text
    assert "not an integrated entropy-balance closure" in text
    assert "Equation (2.53) contains boundary heat and surface-energy terms" in text


def test_flux_global_entropy_derivation_note_records_boundary_status() -> None:
    text = _read("research_notes/SECTION_IID_FLUX_GLOBAL_ENTROPY_DERIVATION.md")
    assert "J_s_rev = -J_GA/T" in text
    assert "not an integrated balance theorem" in text
    assert "boundary heat and surface-energy transfer" in text
    with (ROOT / "research_notes/onuki_iid_flux_derivation_steps.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["step_id"]: row for row in rows}
    assert by_id["FLUX-04"]["status"] == "VERIFIED"
    assert by_id["FLUX-06"]["status"] == "BOUNDARY_TRANSFER_REQUIRED"
    assert by_id["FLUX-07"]["status"] == "PASS_EXPECTED_NONZERO"


def test_no_forbidden_overclaims_in_iid_outputs() -> None:
    combined = "\n".join(
        [
            _read("sections/02d_hydrodynamic_equations.tex"),
            _read("research_notes/SECTION_IID_HYDRODYNAMIC_BALANCES_DERIVATION.md"),
            _read("research_notes/onuki_iid_entropy_production_audit.md"),
            _read("research_notes/onuki_iid_energy_balance_audit.md"),
        ]
    )
    forbidden = [
        "software proves the second law",
        "we prove the second law",
        "software proves PDE well-posedness",
        "we prove PDE well-posedness",
        "global entropy closure is complete",
        "Appendix-B B3 scaling is resolved",
        "simulation-code branch is inferred",
    ]
    for phrase in forbidden:
        assert phrase not in combined
