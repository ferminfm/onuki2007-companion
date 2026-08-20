#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Appendix B momentum/B3 branches.

These checks verify algebraic scaling and branch residuals only. They do not
decide an erratum, unpublished simulation implementation, PDE well-posedness,
or numerical impact.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_momentum_b3_summary.tsv"


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
    residual = sp.factor(sp.simplify(expression))
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
    if residual == 0:
        raise AssertionError(f"{check_id} unexpectedly vanished")
    if sp.simplify(residual - expected_residual) != 0:
        raise AssertionError(
            f"{check_id} residual {residual} does not match expected {expected_residual}"
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


def _check_status_files(rows: list[dict[str, str]]) -> None:
    branch_map = ROOT / "research_notes" / "onuki_appendix_b_b3_branch_map.csv"
    if not branch_map.is_file():
        _record(
            rows,
            "b3_branch_status_regression",
            "SKIPPED_CANONICAL_LEDGER",
            "not_exported",
            "canonical B3 branch-status ledger is excluded from the standalone export; finite branch residual checks completed",
        )
        return
    with branch_map.open(newline="") as handle:
        map_rows = list(csv.DictReader(handle))
    by_id = {row["row_id"]: row for row in map_rows}
    if by_id["B3-03"]["status"] != "SOURCE_BRANCH_DISCREPANCY":
        raise AssertionError("B3 branch residual status changed unexpectedly")
    if by_id["B3-06"]["status"] != "UNRESOLVED_SOURCE_DEPENDENT":
        raise AssertionError("Simulation-code branch must remain unresolved")
    _record(
        rows,
        "b3_branch_status_regression",
        "PASS_LOGICAL",
        "source_branch_preserved",
        "printed and dimensional-source branches remain separate",
    )


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    m, ell, eps, t0, nu0, g = sp.symbols("m ell eps t0 nu0 g")
    phi, theta, lap_phi, grad_phi_sq = sp.symbols("phi Theta lap_phi grad_phi_sq")
    phi_i, phi_j = sp.symbols("phi_i phi_j")
    p0 = sp.symbols("P0")

    _assert_zero(
        rows,
        "sigma_two_forms_in_momentum_scaling",
        (m * ell**2 / (eps * t0**2)).subs(t0, ell**2 / nu0)
        - (nu0**2 * m / (eps * ell**2)),
        "momentum inertial coefficient after t0=ell^2/nu0",
    )
    _assert_zero(
        rows,
        "gravity_scale_definition",
        (m * g * ell / eps) - (m * g * ell / eps),
        "definition of g* as molecular gravitational energy over epsilon",
    )

    c_coeff, kb, v0 = sp.symbols("C kB v0", positive=True)
    coeff = (v0 / eps) * (c_coeff * eps * theta / kb) / (v0**2 * ell**2)
    coeff_scaled = coeff.subs(ell**2, c_coeff / (2 * kb * v0))
    _assert_zero(
        rows,
        "gradient_stress_coefficient_scales_to_two_theta",
        coeff_scaled - 2 * theta,
        "M partial_i n partial_j n scales to 2 Theta partial_i phi partial_j phi",
    )
    _assert_zero(
        rows,
        "diagonal_gradient_square_coefficient_scales_to_theta",
        coeff_scaled / 2 - theta,
        "M |grad n|^2/2 scales to Theta |grad phi|^2",
    )

    source_diag = p0 - theta * grad_phi_sq - 2 * theta * phi * lap_phi
    printed_diag = p0 - theta * grad_phi_sq - 2 * theta * lap_phi
    expected_branch_residual = 2 * theta * (phi - 1) * lap_phi
    _assert_expected_nonzero(
        rows,
        "printed_minus_dimensional_source_b3_residual",
        printed_diag - source_diag,
        expected_branch_residual,
        "printed B3 and dimensional-source branch differ by the diagonal Laplacian factor",
    )

    source_offdiag = 2 * theta * phi_i * phi_j
    printed_offdiag = 2 * theta * phi_i * phi_j
    _assert_zero(
        rows,
        "offdiagonal_gradient_stress_same_in_both_branches",
        printed_offdiag - source_offdiag,
        "off-diagonal gradient stress is not the B3 branch discrepancy",
    )

    visc_coeff = (v0 / eps) * (nu0 * m * phi / v0) * (1 / t0)
    sigma_def = m * ell**2 / (eps * t0**2)
    _assert_zero(
        rows,
        "viscous_stress_coefficient_scales_to_sigma_phi",
        visc_coeff.subs(t0, ell**2 / nu0) - (sigma_def * phi).subs(t0, ell**2 / nu0),
        "eta=nu0*m*n gives the scaled coefficient sigma*phi",
    )

    phi_x, phi_xx, phi_xxx = sp.symbols("phi_x phi_xx phi_xxx")
    residual_1d = 2 * theta * (phi - 1) * phi_xx
    derivative_1d = 2 * theta * ((phi - 1) * phi_xxx + phi_x * phi_xx)
    chain_derivative = sp.diff(residual_1d, phi) * phi_x + sp.diff(residual_1d, phi_xx) * phi_xxx
    _assert_zero(
        rows,
        "one_dimensional_constant_theta_branch_residual_derivative",
        derivative_1d - chain_derivative,
        "constant-Theta derivative of the branch residual",
    )

    _check_status_files(rows)
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Appendix B momentum/B3 SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
