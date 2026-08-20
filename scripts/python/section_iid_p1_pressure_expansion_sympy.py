#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Section II.D diagonal pressure p1.

These checks verify algebraic reconstruction of the local scalar p1 only.
They do not prove the PDE model, thermodynamic consistency, Appendix-B
scaling, or numerical simulations.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "section_iid_p1_pressure_expansion_summary.tsv"


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


def _check_b3_deferred(rows: list[dict[str, str]]) -> None:
    note = ROOT / "research_notes" / "onuki_iid_pressure_tensor_branch_audit.md"
    if not note.is_file():
        _record(
            rows,
            "appendix_b_b3_branch_deferred",
            "SKIPPED_CANONICAL_LEDGER",
            "not_exported",
            "canonical B3-deferral note is excluded from the standalone export; local p1 checks completed",
        )
        return
    text = note.read_text()
    required = [
        "Appendix-B scaling",
        "printed-B3 versus dimensional-source branch remains separate",
        "deferred",
    ]
    for phrase in required:
        if phrase not in text:
            raise AssertionError(f"Missing B3 deferral phrase: {phrase}")
    _record(
        rows,
        "appendix_b_b3_branch_deferred",
        "DEFERRED",
        "not_algebraic",
        "pressure expansion does not resolve Appendix-B B3",
    )


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    n, mu, e, temp, s, c_coeff, k_coeff, m_coeff, mn_fixed_t = sp.symbols(
        "n mu e T s C K M MnT"
    )
    grad_n_sq, lap_n, grad_a_dot_grad_n = sp.symbols("grad_n_sq lap_n gradA_dot_gradn")

    p_local = n * mu - e + temp * n * s
    ehat = e + k_coeff * grad_n_sq / 2
    shat = n * s - c_coeff * grad_n_sq / 2
    div_term = (m_coeff / temp) * lap_n + grad_a_dot_grad_n
    muhat = mu - temp * div_term + mn_fixed_t * grad_n_sq / 2

    p1_from_thermo = n * muhat - ehat + temp * shat - p_local
    p1_before_m_substitution = (
        -n * temp * div_term
        + (n * mn_fixed_t - k_coeff - temp * c_coeff) * grad_n_sq / 2
    )
    p1_after_m_substitution = (
        -n * temp * div_term + (n * mn_fixed_t - m_coeff) * grad_n_sq / 2
    )
    p1_derivative_expanded = (
        (n * mn_fixed_t - m_coeff) * grad_n_sq / 2
        - m_coeff * n * lap_n
        - temp * n * grad_a_dot_grad_n
    )

    _assert_zero(
        rows,
        "p1_thermodynamic_reconstruction",
        p1_from_thermo - p1_before_m_substitution,
        "reconstruct p1 from n*muhat-ehat+T*Shat-p",
    )
    _assert_zero(
        rows,
        "p1_M_equals_CT_plus_K_substitution",
        (n * mn_fixed_t - k_coeff - temp * c_coeff) * grad_n_sq / 2
        - ((n * mn_fixed_t - m_coeff) * grad_n_sq / 2).subs(
            m_coeff, temp * c_coeff + k_coeff
        ),
        "substitute M=CT+K in the gradient-square coefficient",
    )
    _assert_zero(
        rows,
        "p1_divergence_product_rule",
        p1_after_m_substitution - p1_derivative_expanded,
        "T div((M/T) grad n)=M laplacian n+T grad(M/T).grad n",
    )

    nx, nxx, ax = sp.symbols("nx nxx A_x")
    p1_1d = p1_derivative_expanded.subs(
        {grad_n_sq: nx**2, lap_n: nxx, grad_a_dot_grad_n: ax * nx}
    )
    p1_1d_expected = (
        (n * mn_fixed_t - m_coeff) * nx**2 / 2
        - m_coeff * n * nxx
        - temp * n * ax * nx
    )
    _assert_zero(
        rows,
        "p1_one_dimensional_component_form",
        p1_1d - p1_1d_expected,
        "one-dimensional component form of the derivative-expanded p1",
    )

    tensor_grad_piece, n_grad_muhat_over_t, ehat_grad_inv_t = sp.symbols(
        "tensor_grad_piece n_grad_muhat_over_t ehat_grad_inv_t"
    )
    dq_over_t = (
        n_grad_muhat_over_t
        - ehat_grad_inv_t
        - tensor_grad_piece
    )
    tensor_condition_lhs = dq_over_t + tensor_grad_piece
    tensor_condition_rhs = n_grad_muhat_over_t - ehat_grad_inv_t
    _assert_zero(
        rows,
        "pressure_tensor_satisfies_reversible_condition_eq_244",
        tensor_condition_lhs - tensor_condition_rhs,
        "Section II.B pointwise identity cancels the gradient tensor term in Eq. (2.44)",
    )

    mt_fixed_n, tx = sp.symbols("MTn T_x")
    spatial_mx = mn_fixed_t * nx + mt_fixed_n * tx
    wrong_mn = spatial_mx / nx
    p1_wrong_derivative = (
        (n * wrong_mn - m_coeff) * nx**2 / 2
        - m_coeff * n * nxx
        - temp * n * ax * nx
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_replace_MnT_by_spatial_derivative",
        p1_wrong_derivative - p1_1d_expected,
        n * mt_fixed_n * tx * nx / 2,
        "non-isothermal M_x/n_x replacement adds the M_T|n T_x contribution",
    )

    p1_without_temperature_gradient = (
        (n * mn_fixed_t - m_coeff) * nx**2 / 2
        - m_coeff * n * nxx
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_omit_temperature_gradient_pressure_term",
        p1_without_temperature_gradient - p1_1d_expected,
        temp * n * ax * nx,
        "omitting -T n grad(n).grad(M/T) leaves its opposite as the residual",
    )

    _check_b3_deferred(rows)
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Section II.D p1 pressure-expansion SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
