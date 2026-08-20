#!/usr/bin/env python3
"""Focused symbolic checks for the Appendix-B B3 diagonal factor.

These checks support the dimensional-source branch calculation only. They do
not establish an official erratum, author intent, unpublished simulation-code
behavior, or numerical impact.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_b3_typo_candidate_summary.tsv"


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
        raise AssertionError(f"{check_id} residual {residual} does not match expected {expected_residual}")


def _write_summary(rows: list[dict[str, str]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "residual", "note"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _check_status_files(rows: list[dict[str, str]]) -> None:
    branch_map = ROOT / "research_notes" / "onuki_appendix_b_b3_branch_map.csv"
    if not branch_map.is_file():
        _record(
            rows,
            "unpublished_simulation_code_branch_regression",
            "SKIPPED_CANONICAL_LEDGER",
            "not_exported",
            "canonical B3 branch-status ledger is excluded from the standalone export; finite scaling checks completed",
        )
        return
    with branch_map.open(newline="") as handle:
        by_id = {row["row_id"]: row for row in csv.DictReader(handle)}
    if by_id["B3-03"]["status"] != "SOURCE_BRANCH_DISCREPANCY":
        raise AssertionError("B3 branch discrepancy status changed unexpectedly")
    if "Typographical omission under dimensional-source derivation" not in by_id["B3-03"]["notes"]:
        raise AssertionError(
            "B3-03 note must record the bounded typographical-omission classification"
        )
    if by_id["B3-06"]["status"] != "UNRESOLVED_SOURCE_DEPENDENT":
        raise AssertionError("Unpublished simulation-code branch must remain unresolved")
    _record(
        rows,
        "unpublished_simulation_code_branch_regression",
        "PASS_LOGICAL",
        "UNRESOLVED_SOURCE_DEPENDENT",
        "unpublished implementation branch is not inferred",
    )


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    C, kB, v0, ell, eps = sp.symbols("C kB v0 ell eps", nonzero=True)
    theta, phi, lap_phi, grad_phi_sq, phi_i, phi_j = sp.symbols(
        "Theta phi lap_phi grad_phi_sq phi_i phi_j"
    )

    M = C * eps * theta / kB
    ell_relation = C / (2 * kB * v0)

    _assert_zero(
        rows,
        "M_scales_to_two_epsilon_v0_ell_squared_theta",
        M.subs(C, 2 * kB * v0 * ell**2) - 2 * eps * v0 * ell**2 * theta,
        "M=CT with Theta=kB T/epsilon and ell^2=C/(2 kB v0)",
    )

    lap_x_n = lap_phi / (v0 * ell**2)
    grad_x_n_sq = grad_phi_sq / (v0**2 * ell**2)
    grad_i_n = phi_i / (v0 * ell)
    grad_j_n = phi_j / (v0 * ell)
    n = phi / v0

    scaled_lap_term = (v0 / eps) * (-M * n * lap_x_n)
    _assert_zero(
        rows,
        "diagonal_laplacian_scales_to_minus_two_theta_phi_lap_phi",
        scaled_lap_term.subs(ell**2, ell_relation) + 2 * theta * phi * lap_phi,
        "scaling of -M n Delta_x n retains the phi factor",
    )

    scaled_grad_square = (v0 / eps) * (-(M / 2) * grad_x_n_sq)
    _assert_zero(
        rows,
        "gradient_square_scales_to_minus_theta_grad_phi_squared",
        scaled_grad_square.subs(ell**2, ell_relation) + theta * grad_phi_sq,
        "scaling of -(M/2)|grad_x n|^2",
    )

    scaled_offdiag = (v0 / eps) * M * grad_i_n * grad_j_n
    _assert_zero(
        rows,
        "offdiagonal_gradient_stress_scales_to_two_theta_phi_i_phi_j",
        scaled_offdiag.subs(ell**2, ell_relation) - 2 * theta * phi_i * phi_j,
        "scaling of M partial_i n partial_j n",
    )

    source_diag_lap = -2 * theta * phi * lap_phi
    printed_diag_lap = -2 * theta * lap_phi
    expected_stress_residual = 2 * theta * (phi - 1) * lap_phi
    _assert_expected_nonzero(
        rows,
        "printed_minus_source_diagonal_laplacian_residual",
        printed_diag_lap - source_diag_lap,
        expected_stress_residual,
        "printed branch lacks the dimensional-source phi factor",
    )

    x = sp.symbols("x")
    phi_x = 1 + x**2
    theta0 = sp.symbols("Theta0", nonzero=True)
    stress_residual_1d = 2 * theta0 * (phi_x - 1) * sp.diff(phi_x, x, 2)
    force_residual_1d = -sp.diff(stress_residual_1d, x)
    _assert_expected_nonzero(
        rows,
        "one_dimensional_force_residual_generically_nonzero",
        force_residual_1d,
        -8 * theta0 * x,
        "for phi(x)=1+x^2, -d_x[2 Theta (phi-1) phi_xx] is nonzero",
    )

    wrong_scaled_lap = (v0 / eps) * (-M * lap_x_n)
    wrong_result = sp.factor(sp.simplify(wrong_scaled_lap.subs(ell**2, ell_relation)))
    _record(
        rows,
        "negative_control_replace_n_lap_n_by_lap_n",
        "NEGATIVE_CONTROL_NOT_SOURCE_GROUNDED",
        wrong_result,
        "replacing n Delta n by Delta n leaves a v0-dependent object and is not the source term",
    )
    if sp.simplify(wrong_result + 2 * theta * lap_phi) == 0:
        raise AssertionError("negative control unexpectedly matched the printed branch")

    _check_status_files(rows)
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Appendix B B3 typo-candidate SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
