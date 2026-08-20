#!/usr/bin/env python3
"""Independent finite-component checks for the Korteweg 1901 reconstruction.

The script verifies Cartesian product-rule and sign/variable-map identities.
It does not formalize the continuum PDE, infer constitutive coefficients, or
establish an Onuki equivalence.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "korteweg1901_tensor_sympy_summary.tsv"


def _zero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr) -> None:
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
    rows.append(
        {"check_id": check_id, "status": "PASS_EXPECTED_NONZERO", "residual": str(residual)}
    )


def run_checks() -> list[dict[str, str]]:
    x, y = sp.symbols("x y")
    rho = sp.Function("rho")(x, y)
    alpha = sp.Function("alpha")(x, y)
    beta = sp.Function("beta")(x, y)
    gamma = sp.Function("gamma")(x, y)
    delta_k = sp.Function("delta_K")(x, y)

    rx, ry = sp.diff(rho, x), sp.diff(rho, y)
    rxx, rxy, ryy = sp.diff(rho, x, 2), sp.diff(rho, x, y), sp.diff(rho, y, 2)
    q = rx**2 + ry**2
    lap = rxx + ryy
    hessian = sp.Matrix([[rxx, rxy], [rxy, ryy]])
    gradient = sp.Matrix([rx, ry])
    identity = sp.eye(2)

    compact = (alpha * q - gamma * lap) * identity + beta * (gradient * gradient.T) - delta_k * hessian
    source_components = sp.Matrix(
        [
            [alpha * q + beta * rx**2 - gamma * lap - delta_k * rxx,
             beta * rx * ry - delta_k * rxy],
            [beta * ry * rx - delta_k * rxy,
             alpha * q + beta * ry**2 - gamma * lap - delta_k * ryy],
        ]
    )

    rows: list[dict[str, str]] = []
    for i in range(2):
        for j in range(2):
            _zero(rows, f"compact_component_{i}{j}", compact[i, j] - source_components[i, j])

    direct = sp.Matrix(
        [
            sp.diff(source_components[0, 0], x) + sp.diff(source_components[0, 1], y),
            sp.diff(source_components[1, 0], x) + sp.diff(source_components[1, 1], y),
        ]
    )

    collected_x = (
        q * sp.diff(alpha, x)
        - lap * sp.diff(gamma, x)
        + rx * (sp.diff(beta, x) * rx + sp.diff(beta, y) * ry)
        - (sp.diff(delta_k, x) * rxx + sp.diff(delta_k, y) * rxy)
        + (2 * alpha + beta) * (rxx * rx + rxy * ry)
        + beta * rx * lap
        - (gamma + delta_k) * sp.diff(lap, x)
    )
    collected_y = (
        q * sp.diff(alpha, y)
        - lap * sp.diff(gamma, y)
        + ry * (sp.diff(beta, x) * rx + sp.diff(beta, y) * ry)
        - (sp.diff(delta_k, x) * rxy + sp.diff(delta_k, y) * ryy)
        + (2 * alpha + beta) * (rxy * rx + ryy * ry)
        + beta * ry * lap
        - (gamma + delta_k) * sp.diff(lap, y)
    )
    _zero(rows, "divergence_x_collected", direct[0] - collected_x)
    _zero(rows, "divergence_y_collected", direct[1] - collected_y)

    state_alpha = sp.Function("a")
    temperature = sp.Function("theta")(x, y)
    chain_actual = sp.diff(state_alpha(rho, temperature), x)
    chain_expected = (
        sp.Subs(sp.Derivative(state_alpha(sp.Symbol("r"), sp.Symbol("t")), sp.Symbol("r")),
                (sp.Symbol("r"), sp.Symbol("t")), (rho, temperature)) * rx
        + sp.Subs(sp.Derivative(state_alpha(sp.Symbol("r"), sp.Symbol("t")), sp.Symbol("t")),
                  (sp.Symbol("r"), sp.Symbol("t")), (rho, temperature)) * sp.diff(temperature, x)
    )
    _zero(rows, "coefficient_state_chain_rule", chain_actual - chain_expected)

    body, div_p, div_sigma = sp.symbols("body divP divSigma")
    _zero(rows, "pressure_to_cauchy_sign_bridge", (body - div_p) - (body + div_sigma).subs(div_sigma, -div_p))

    m0, gi, gj, hij, coeff = sp.symbols("m0 gi gj hij coeff")
    _zero(rows, "density_gradient_coefficient_map", coeff * (m0 * gi) * (m0 * gj) - coeff * m0**2 * gi * gj)
    _zero(rows, "density_hessian_coefficient_map", coeff * (m0 * hij) - coeff * m0 * hij)

    rho_poly = 1 + x**2 + x * y + y**3
    polynomial_rules = {
        rho: rho_poly,
        alpha: 1 + x,
        beta: 2 + y,
        gamma: 3 + x * y,
        delta_k: 4 + x**2,
    }
    direct_poly = sp.simplify(direct.subs(polynomial_rules).doit())

    coefficient_derivative_x = (
        q * sp.diff(alpha, x)
        - lap * sp.diff(gamma, x)
        + rx * (sp.diff(beta, x) * rx + sp.diff(beta, y) * ry)
        - (sp.diff(delta_k, x) * rxx + sp.diff(delta_k, y) * rxy)
    )
    omitted_coefficients = sp.simplify(coefficient_derivative_x.subs(polynomial_rules).doit())
    _nonzero(rows, "expected_nonzero_omitted_coefficient_derivatives", omitted_coefficients)
    _nonzero(rows, "expected_nonzero_wrong_sign_force", 2 * direct_poly[0])

    chi = x**2 * y**2
    scalar_gauge_div_x = sp.diff(chi, x)
    _nonzero(rows, "expected_nonzero_scalar_isotropic_gauge", scalar_gauge_div_x)

    airy = sp.Matrix(
        [[sp.diff(chi, y, 2), -sp.diff(chi, x, y)],
         [-sp.diff(chi, x, y), sp.diff(chi, x, 2)]]
    )
    airy_div = sp.Matrix(
        [sp.diff(airy[0, 0], x) + sp.diff(airy[0, 1], y),
         sp.diff(airy[1, 0], x) + sp.diff(airy[1, 1], y)]
    )
    _zero(rows, "divergence_free_airy_gauge_x", airy_div[0])
    _zero(rows, "divergence_free_airy_gauge_y", airy_div[1])
    _nonzero(rows, "airy_gauge_not_literal_zero", airy[0, 0])
    return rows


def main() -> int:
    rows = run_checks()
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "residual"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print("PASS: Korteweg 1901 tensor SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
