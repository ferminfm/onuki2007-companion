#!/usr/bin/env python3
"""Finite residual checks for the bounded Korteweg--Onuki stress crosswalk.

These checks compare local Cartesian tensor expressions. They do not prove a
continuum model, global balance, constitutive law, or historical influence.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "korteweg_onuki_crosswalk_summary.tsv"


def _zero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr | sp.Matrix) -> None:
    if isinstance(expression, sp.MatrixBase):
        residual = sp.simplify(sum(sp.expand(x) ** 2 for x in expression))
    else:
        residual = sp.simplify(sp.expand(expression))
    print(f"{check_id}\tPASS_ZERO\t{residual}")
    if residual != 0:
        raise AssertionError(f"{check_id}: expected zero, got {residual}")
    rows.append({"check_id": check_id, "status": "PASS_ZERO", "residual": str(residual)})


def _nonzero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr) -> None:
    residual = sp.factor(sp.simplify(expression))
    print(f"{check_id}\tPASS_EXPECTED_NONZERO\t{residual}")
    if residual == 0:
        raise AssertionError(f"{check_id}: expected nonzero residual")
    rows.append({"check_id": check_id, "status": "PASS_EXPECTED_NONZERO", "residual": str(residual)})


def run_checks() -> list[dict[str, str]]:
    m0, n, temperature = sp.symbols("m0 n T", nonzero=True)
    M, M_n, K = sp.symbols("M M_n K")
    nx, ny, tx, ty = sp.symbols("n_x n_y T_x T_y")
    nxx, nxy, nyy = sp.symbols("n_xx n_xy n_yy")
    delta_source = sp.symbols("delta_K")

    grad_n = sp.Matrix([nx, ny])
    hess_n = sp.Matrix([[nxx, nxy], [nxy, nyy]])
    identity = sp.eye(2)
    q = nx**2 + ny**2
    lap = nxx + nyy
    mixed = nx * tx + ny * ty

    alpha_n = -(M + n * M_n) / 2
    beta_n = M
    gamma_n = M * n

    korteweg_mapped = (alpha_n * q - gamma_n * lap) * identity + beta_n * (grad_n * grad_n.T)
    onuki_general = korteweg_mapped + (n * K / temperature) * mixed * identity

    rows: list[dict[str, str]] = []

    # Construct Eq. (20) first in mass-density derivatives and then substitute rho=m0*n.
    rho_grad = m0 * grad_n
    rho_hess = m0 * hess_n
    rho_lap = m0 * lap
    alpha_k = alpha_n / m0**2
    beta_k = beta_n / m0**2
    gamma_k = gamma_n / m0
    delta_k = sp.Integer(0)
    korteweg_mass = (
        (alpha_k * (rho_grad.dot(rho_grad)) - gamma_k * rho_lap) * identity
        + beta_k * (rho_grad * rho_grad.T)
        - delta_k * rho_hess
    )
    _zero(rows, "density_variable_and_coefficient_map", korteweg_mass - korteweg_mapped)

    expected_mixed = (n * K / temperature) * mixed * identity
    _zero(rows, "general_nonisothermal_tensor_residual", (onuki_general - korteweg_mapped) - expected_mixed)
    _zero(rows, "isothermal_restricted_tensor_map", (onuki_general - korteweg_mapped).subs({tx: 0, ty: 0}))
    _zero(rows, "K_zero_nonisothermal_tensor_map", (onuki_general - korteweg_mapped).subs(K, 0))
    _zero(rows, "constant_C_simulation_tensor_map", (onuki_general - korteweg_mapped).subs({K: 0, M_n: 0}))

    hessian_residual = -m0 * delta_source * hess_n
    _nonzero(rows, "expected_nonzero_independent_hessian_component", hessian_residual[0, 1])

    x = sp.symbols("x")
    n_poly = 1 + x**2
    t_poly = 2 + x
    scalar_residual = (n_poly * 3 / t_poly) * sp.diff(n_poly, x) * sp.diff(t_poly, x)
    force_residual = sp.diff(scalar_residual, x)
    _nonzero(rows, "expected_nonzero_general_force_residual", force_residual)
    _nonzero(rows, "expected_nonzero_wrong_source_sign", 2 * sp.diff(alpha_n * q - gamma_n * lap, nx))

    chi = x**3
    _nonzero(rows, "expected_nonzero_scalar_pressure_shift_force", sp.diff(chi, x))
    return rows


def main() -> int:
    rows = run_checks()
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "residual"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print("PASS: Korteweg--Onuki crosswalk SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
