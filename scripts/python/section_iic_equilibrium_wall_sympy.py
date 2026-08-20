#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Section II.C equilibrium wall identities.

These checks cover algebraic and one-dimensional variational bookkeeping only.
They do not prove the wall model, hydrodynamic equations, PDE well-posedness,
or simulation results.
"""

from __future__ import annotations

import sympy as sp


def _assert_zero(name: str, expression: sp.Expr) -> None:
    residual = sp.simplify(expression)
    print(f"{name}\t{residual}")
    if residual != 0:
        raise AssertionError(f"{name} residual is not zero: {residual}")


def _assert_expected_nonzero(name: str, expression: sp.Expr) -> None:
    residual = sp.simplify(expression)
    print(f"{name}\t{residual}")
    if residual == 0:
        raise AssertionError(f"{name} unexpectedly simplified to zero")


def run_checks() -> None:
    k_b, temp, beta = sp.symbols("k_B T beta", nonzero=True)
    _assert_zero(
        "homogeneous_temperature_coefficient",
        (1 / (k_b * temp) - beta).subs(beta, 1 / (k_b * temp)),
    )

    s_b, e_b, n_total, lambda_n, f_bulk = sp.symbols(
        "S_b E_b N lambda_N F"
    )
    w_rewritten = s_b / k_b + lambda_n * n_total - e_b / (k_b * temp)
    helmholtz_branch = (-f_bulk + k_b * temp * lambda_n * n_total) / (k_b * temp)
    _assert_zero(
        "W_to_helmholtz_rewriting",
        w_rewritten.subs(f_bulk, e_b - temp * s_b)
        - helmholtz_branch.subs(f_bulk, e_b - temp * s_b),
    )

    c_coeff, k_coeff, m_coeff = sp.symbols("C K M")
    _assert_zero(
        "helmholtz_gradient_coefficient_M",
        (k_coeff + temp * c_coeff - m_coeff).subs(m_coeff, k_coeff + temp * c_coeff),
    )

    mu_hat = sp.symbols("mu_hat")
    _assert_zero(
        "constant_muhat_stationarity_coefficient",
        (mu_hat - k_b * temp * lambda_n).subs(mu_hat, k_b * temp * lambda_n),
    )

    mu_cx, p_cx, n_phase, f_phase = sp.symbols("mu_cx p_cx n_phase f_phase")
    g_shifted = f_phase - mu_cx * n_phase + p_cx
    _assert_zero(
        "grand_potential_shifted_coexistence_zero",
        g_shifted.subs(f_phase, mu_cx * n_phase - p_cx),
    )

    sigma_s, e_s = sp.symbols("sigma_s e_s")
    _assert_zero("wall_helmholtz_density_transform", e_s - temp * sigma_s - (e_s - temp * sigma_s))
    _assert_zero(
        "Wtot_surface_term_source_convention",
        (sigma_s - beta * e_s) - (sigma_s - beta * e_s),
    )

    x = sp.symbols("x")
    m = sp.Function("M")(x)
    density = sp.Function("n")(x)
    variation = sp.Function("eta")(x)

    lhs = m * sp.diff(density, x) * sp.diff(variation, x)
    rhs = sp.diff(m * sp.diff(density, x) * variation, x) - sp.diff(
        m * sp.diff(density, x), x
    ) * variation
    _assert_zero("one_dimensional_equilibrium_gradient_ibp", lhs - rhs)

    m_b, q_b, fs_n = sp.symbols("M_b q_b fs_n", nonzero=True)
    boundary_residual = m_b * q_b + fs_n
    natural_q = -fs_n / m_b
    _assert_zero(
        "natural_wall_boundary_cancels_residual",
        boundary_residual.subs(q_b, natural_q),
    )

    n_b, a_s, b_s, n_c = sp.symbols("n_b a_s b_s n_c")
    f_s = -a_s * (n_b - n_c) + sp.Rational(1, 2) * b_s * (n_b - n_c) ** 2
    _assert_zero(
        "quadratic_wall_density_derivative",
        sp.diff(f_s, n_b) - (-a_s + b_s * (n_b - n_c)),
    )

    m_pos, n_x = sp.symbols("M n_x", positive=True)
    g_gp = sp.Rational(1, 2) * m_pos * n_x**2
    _assert_zero(
        "surface_tension_integrand_squared_consistency",
        (m_pos * n_x) ** 2 - 2 * m_pos * g_gp,
    )

    _assert_expected_nonzero(
        "expected_nonzero_omitted_wall_residual",
        m_b * q_b,
    )


def main() -> int:
    run_checks()
    print("PASS: Section II.C SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
