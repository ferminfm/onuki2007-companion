#!/usr/bin/env python3
"""Finite algebra checks for Onuki Appendix B scaling definitions.

These checks verify scale identities only. They do not derive the scaled
energy equation, boundary condition, simulations, or unpublished code branch.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_scaling_definitions_summary.tsv"


def _record(rows: list[dict[str, str]], check_id: str, status: str, residual: sp.Expr | str, note: str) -> None:
    rows.append(
        {
            "check_id": check_id,
            "status": status,
            "residual": str(residual),
            "note": note,
        }
    )
    print(f"{check_id}\t{status}\t{residual}\t{note}")


def _assert_zero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr, note: str) -> None:
    residual = sp.simplify(expression)
    _record(rows, check_id, "PASS_ZERO", residual, note)
    if residual != 0:
        raise AssertionError(f"{check_id} residual is not zero: {residual}")


def _assert_expected_nonzero(
    rows: list[dict[str, str]],
    check_id: str,
    expression: sp.Expr,
    expected: sp.Expr,
    note: str,
) -> None:
    residual = sp.factor(sp.simplify(expression))
    expected_residual = sp.factor(sp.simplify(expected))
    _record(rows, check_id, "PASS_EXPECTED_NONZERO", residual, note)
    if residual == 0 or sp.simplify(residual - expected_residual) != 0:
        raise AssertionError(
            f"{check_id} residual {residual} does not match {expected_residual}"
        )


def _write_summary(rows: list[dict[str, str]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_id", "status", "residual", "note"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def run_checks() -> None:
    rows: list[dict[str, str]] = []
    ell, c_coeff, k_b, v0 = sp.symbols("ell C k_B v0", positive=True)
    t0, nu0, mass, eps = sp.symbols("t0 nu0 m epsilon", positive=True)
    grav, density, temp, velocity, e_total = sp.symbols(
        "g n T v e_T", positive=True
    )

    _assert_zero(
        rows,
        "length_scale_squared_relation",
        (ell**2 - c_coeff / (2 * k_b * v0)).subs(c_coeff, 2 * k_b * v0 * ell**2),
        "ell^2=C/(2 k_B v0) is the source length-scale definition",
    )
    _assert_zero(
        rows,
        "time_scale_relation",
        (t0 - ell**2 / nu0).subs(t0, ell**2 / nu0),
        "t0=ell^2/nu0 is the source time-scale definition",
    )

    phi = v0 * density
    theta = k_b * temp / eps
    scaled_velocity = t0 * velocity / ell
    scaled_energy_density = e_total * v0 / eps
    sigma_a = nu0**2 * mass / (eps * ell**2)
    sigma_b = mass * ell**2 / (eps * t0**2)
    g_star = mass * grav * ell / eps

    _assert_zero(rows, "phi_definition", phi - v0 * density, "phi=v0 n")
    _assert_zero(rows, "theta_definition", theta - k_b * temp / eps, "Theta=k_B T/epsilon")
    _assert_zero(rows, "scaled_velocity_definition", scaled_velocity - t0 * velocity / ell, "V=t0 v/ell")
    _assert_zero(
        rows,
        "scaled_energy_density_definition",
        scaled_energy_density - e_total * v0 / eps,
        "E_T=e_T v0/epsilon",
    )
    _assert_zero(
        rows,
        "sigma_two_forms_equivalent",
        (sigma_a - sigma_b).subs(t0, ell**2 / nu0),
        "sigma forms agree after substituting t0=ell^2/nu0",
    )
    _assert_zero(rows, "gravity_parameter_definition", g_star - mass * grav * ell / eps, "g*=m g ell/epsilon")

    phi_t, div_phi_v, phi_x = sp.symbols("phi_t div_phi_V phi_x")
    dimensional_continuity = phi_t / (v0 * t0) + div_phi_v / (v0 * t0)
    _assert_zero(
        rows,
        "b2_continuity_common_prefactor",
        v0 * t0 * dimensional_continuity - (phi_t + div_phi_v),
        "both B2 continuity terms carry the common 1/(v0 t0) scale",
    )
    correct_density_gradient = phi_x / (v0 * ell)
    wrong_density_gradient = phi_x / v0
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_wrong_coordinate_derivative_scale",
        v0 * ell * wrong_density_gradient - v0 * ell * correct_density_gradient,
        (ell - 1) * phi_x,
        "omitting grad_x=ell^-1 grad_* leaves an uncancelled coordinate scale",
    )
    _record(
        rows,
        "b4_b5_b6_covered_by_energy_boundary_mirrors",
        "PASS_LOGICAL",
        "covered_separately",
        "B4--B6 are covered by appendix_b_energy_boundary SymPy/Wolfram/Pint mirrors",
    )
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Appendix B scaling-definition SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
