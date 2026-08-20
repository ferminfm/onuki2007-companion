#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Appendix A reversible-stress bookkeeping.

These checks verify component algebra and integration-by-parts identities only.
They do not prove the hydrodynamic PDEs, thermodynamic consistency, boundary
closure, or simulation results.
"""

from __future__ import annotations

import sympy as sp


def _assert_zero(name: str, expression: sp.Expr) -> None:
    residual = sp.simplify(expression)
    print(f"{name}\t{residual}")
    if residual != 0:
        raise AssertionError(f"{name} residual is not zero: {residual}")


def _assert_expected_nonzero(name: str, expression: sp.Expr) -> None:
    residual = sp.factor(sp.simplify(expression))
    print(f"{name}\t{residual}")
    if residual == 0:
        raise AssertionError(f"{name} unexpectedly vanished")


def run_checks() -> None:
    eps = sp.symbols("eps")
    a11, a12, a21, a22 = sp.symbols("a11 a12 a21 a22")
    deformation = sp.Matrix([[1 + eps * a11, eps * a12], [eps * a21, 1 + eps * a22]])
    det_series = sp.series(deformation.det(), eps, 0, 2).removeO()
    _assert_zero("determinant_first_order_trace", det_series - (1 + eps * (a11 + a22)))

    n0, div_u = sp.symbols("n div_u")
    density_series = sp.series(n0 / (1 + eps * div_u), eps, 0, 2).removeO()
    _assert_zero("material_density_variation_A1", density_series - (n0 - eps * n0 * div_u))

    dnx, dny, uxx, uxy, uyx, uyy = sp.symbols("dnx dny uxx uxy uyx uyy")
    nx0, ny0 = sp.symbols("nx ny")
    grad_x_prime = nx0 + eps * (dnx - uxx * nx0 - uyx * ny0)
    grad_y_prime = ny0 + eps * (dny - uxy * nx0 - uyy * ny0)
    grad_square_prime = sp.Rational(1, 2) * (grad_x_prime**2 + grad_y_prime**2)
    grad_square_base = sp.Rational(1, 2) * (nx0**2 + ny0**2)
    grad_square_delta = sp.expand(grad_square_prime - grad_square_base).coeff(eps, 1)
    grad_square_target = nx0 * dnx + ny0 * dny - (
        nx0**2 * uxx + nx0 * ny0 * uyx + ny0 * nx0 * uxy + ny0**2 * uyy
    )
    _assert_zero("gradient_square_variation_A3", grad_square_delta - grad_square_target)

    theta_u, theta_x, theta_y = sp.symbols("theta_u theta_x theta_y")
    delta_nx_material = -nx0 * theta_u - n0 * theta_x
    delta_ny_material = -ny0 * theta_u - n0 * theta_y
    material_gradient_change = (
        nx0 * delta_nx_material
        + ny0 * delta_ny_material
        - (nx0**2 * uxx + nx0 * ny0 * uyx + ny0 * nx0 * uxy + ny0**2 * uyy)
    )
    material_gradient_target = (
        -(nx0**2 + ny0**2) * theta_u
        - n0 * (nx0 * theta_x + ny0 * theta_y)
        - (nx0**2 * uxx + nx0 * ny0 * uyx + ny0 * nx0 * uxy + ny0**2 * uyy)
    )
    _assert_zero(
        "material_gradient_variation_A3_substitution",
        material_gradient_change - material_gradient_target,
    )

    temp, shat, ehat, nhat, muhat, mcoef = sp.symbols("T Shat ehat n muhat M")
    pixx, pixy, piyx, piyy = sp.symbols("Pi_xx Pi_xy Pi_yx Pi_yy")
    coeff_xx = temp * shat - ehat + nhat * muhat - pixx + mcoef * nx0**2
    coeff_xy = -pixy + mcoef * nx0 * ny0
    coeff_yx = -piyx + mcoef * ny0 * nx0
    coeff_yy = temp * shat - ehat + nhat * muhat - piyy + mcoef * ny0**2
    _assert_zero(
        "entropy_variation_A4_coefficients",
        coeff_xx
        - ((temp * shat - ehat + nhat * muhat) - pixx + mcoef * nx0**2),
    )

    stress_diag = temp * shat - ehat + nhat * muhat
    _assert_zero(
        "stress_identification_residual_A4",
        coeff_xx.subs(pixx, stress_diag + mcoef * nx0**2),
    )
    _assert_zero(
        "offdiagonal_stress_identification_residual_A4",
        coeff_xy.subs(pixy, mcoef * nx0 * ny0),
    )

    p_local, p1 = sp.symbols("p p1")
    _assert_zero(
        "p1_bridge_to_pressure_tensor",
        (p_local + p1).subs(p1, nhat * muhat - ehat + temp * shat - p_local)
        - stress_diag,
    )

    x, y = sp.symbols("x y")
    n = sp.Function("n")(x, y)
    ux = sp.Function("u_x")(x, y)
    uy = sp.Function("u_y")(x, y)

    div_nu = sp.diff(n * ux, x) + sp.diff(n * uy, y)
    product_rule = (
        ux * sp.diff(n, x)
        + uy * sp.diff(n, y)
        + n * (sp.diff(ux, x) + sp.diff(uy, y))
    )
    _assert_zero("density_variation_product_rule", div_nu - product_rule)
    _assert_zero(
        "eulerian_density_variation",
        (-div_nu) - (-product_rule),
    )

    x1 = sp.symbols("x1")
    m = sp.Function("M")(x1)
    density = sp.Function("n")(x1)
    eta = sp.Function("eta")(x1)
    lhs = m * sp.diff(density, x1) * sp.diff(eta, x1)
    rhs = sp.diff(m * sp.diff(density, x1) * eta, x1) - sp.diff(
        m * sp.diff(density, x1), x1
    ) * eta
    _assert_zero("one_dimensional_gradient_ibp", lhs - rhs)

    theta_function = sp.Function("theta")(x1)
    retained_boundary_density = m * density * sp.diff(density, x1) * theta_function
    material_middle_term = m * density * sp.diff(density, x1) * sp.diff(
        theta_function, x1
    )
    material_bulk_term = -theta_function * sp.diff(
        m * density * sp.diff(density, x1), x1
    )
    _assert_zero(
        "material_gradient_ibp_with_boundary_A3",
        material_middle_term
        - (sp.diff(retained_boundary_density, x1) + material_bulk_term),
    )

    m_poly = 1 + x1
    n_poly = 1 + x1**2
    theta_poly = x1**2
    omitted_boundary_residual = sp.diff(
        m_poly * n_poly * sp.diff(n_poly, x1) * theta_poly, x1
    )
    _assert_expected_nonzero(
        "expected_nonzero_omitted_material_gradient_boundary",
        omitted_boundary_residual,
    )

    M, nx, ny, pdiag = sp.symbols("M nx ny pdiag")
    uxx, uxy, uyx, uyy = sp.symbols("uxx uxy uyx uyy")

    pi_xx = pdiag + M * nx**2
    pi_xy = M * nx * ny
    pi_yx = M * ny * nx
    pi_yy = pdiag + M * ny**2

    _assert_zero("off_diagonal_stress_symmetry", pi_xy - pi_yx)

    stress_power = pi_xx * uxx + pi_xy * uxy + pi_yx * uyx + pi_yy * uyy
    target = pdiag * (uxx + uyy) + M * (
        nx**2 * uxx + nx * ny * uxy + ny * nx * uyx + ny**2 * uyy
    )
    _assert_zero("component_stress_power_contraction", stress_power - target)

    diagonal_only_power = pi_xx * uxx + pi_yy * uyy
    _assert_expected_nonzero(
        "expected_nonzero_omitted_offdiagonal_residual",
        stress_power - diagonal_only_power,
    )


def main() -> int:
    run_checks()
    print("PASS: Appendix A reversible-stress SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
