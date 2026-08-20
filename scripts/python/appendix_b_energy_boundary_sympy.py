#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Appendix B energy/boundary scaling.

These checks support the companion's Appendix B derivation of B4--B6 scale
bookkeeping. They verify local algebra and an expected omitted wall-transfer
residual only; they do not reproduce simulations or close global balances.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_energy_boundary_summary.tsv"


def _record(rows: list[dict[str, str]], check_id: str, status: str, residual: sp.Expr | str, note: str) -> None:
    rows.append({"check_id": check_id, "status": status, "residual": str(residual), "note": note})
    print(f"{check_id}\t{status}\t{residual}\t{note}")


def _assert_zero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr, note: str) -> None:
    residual = sp.factor(sp.simplify(expression))
    _record(rows, check_id, "PASS_ZERO", residual, note)
    if residual != 0:
        raise AssertionError(f"{check_id} residual is not zero: {residual}")


def _assert_expected_nonzero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr, expected: sp.Expr, note: str) -> None:
    residual = sp.factor(sp.simplify(expression))
    expected_residual = sp.factor(sp.simplify(expected))
    _record(rows, check_id, "PASS_EXPECTED_NONZERO", residual, note)
    if residual == 0:
        raise AssertionError(f"{check_id} unexpectedly vanished")
    if sp.simplify(residual - expected_residual) != 0:
        raise AssertionError(f"{check_id} residual {residual} != expected {expected_residual}")


def _write_summary(rows: list[dict[str, str]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "residual", "note"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    phi, theta, sigma, v_sq = sp.symbols("phi Theta sigma V_sq")
    e_scaled = phi * theta - phi**2 + sigma * phi * v_sq / 2
    _assert_zero(
        rows,
        "energy_density_b4_reconstruction",
        e_scaled - (phi * theta - phi**2 + sigma * phi * v_sq / 2),
        "B4 local energy density branch",
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_missing_kinetic_density_factor",
        (phi * theta - phi**2 + sigma * v_sq / 2) - e_scaled,
        sigma * v_sq * (1 - phi) / 2,
        "dropping phi from the kinetic-energy density changes B4",
    )

    m, ell, eps, t0, nu0 = sp.symbols("m ell eps t0 nu0", positive=True)
    kinetic_coeff = m * ell**2 / (eps * t0**2)
    sigma_from_nu = nu0**2 * m / (eps * ell**2)
    _assert_zero(
        rows,
        "kinetic_energy_coefficient_scales_to_sigma",
        kinetic_coeff.subs(t0, ell**2 / nu0) - sigma_from_nu,
        "kinetic term coefficient is sigma after t0=ell^2/nu0",
    )

    heat_coeff = t0 * nu0 / ell**2
    _assert_zero(
        rows,
        "heat_diffusion_coefficient_scales_to_one",
        heat_coeff.subs(t0, ell**2 / nu0) - 1,
        "lambda=kB*nu0*n gives div(phi grad Theta)",
    )

    g = sp.symbols("g")
    _assert_zero(
        rows,
        "gravity_power_coefficient",
        (m * g * ell / eps) - (m * g * ell / eps),
        "g*=m g ell/epsilon is the scaled gravity-power coefficient",
    )
    gstar, vz = sp.symbols("gstar V_z")
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_wrong_gravity_power_sign",
        gstar * phi * vz - (-gstar * phi * vz),
        2 * gstar * phi * vz,
        "reversing the B5 gravity-work sign leaves twice the source term",
    )

    stress_flux, v_dim, v_scaled = sp.symbols("Mdot stress_v_dim V_scaled")
    mixed_flux = stress_flux * (t0 / ell) * v_dim
    scaled_flux = stress_flux * v_scaled
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_mixed_dimensional_scaled_velocity",
        mixed_flux - scaled_flux,
        stress_flux * ((t0 / ell) * v_dim - v_scaled),
        "the B5 stress flux closes only after V=(t0/ell)v is substituted",
    )

    v0, n, nc, grad_phi = sp.symbols("v0 n nc grad_phi")
    boundary_rhs = v0 * (n - 5 * nc / 2)
    _assert_zero(
        rows,
        "boundary_rhs_phi_minus_five_six",
        boundary_rhs.subs({n: phi / v0, nc: 1 / (3 * v0)}) - (phi - sp.Rational(5, 6)),
        "Eq. (3.2) boundary RHS scales to phi-5/6",
    )

    boundary_heat, surface_rate = sp.symbols("boundary_heat surface_energy_rate")
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_omitted_global_wall_transfer",
        boundary_heat + surface_rate,
        boundary_heat + surface_rate,
        "local B5/B6 scaling does not remove global wall/surface transfer",
    )

    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Appendix B energy/boundary SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
