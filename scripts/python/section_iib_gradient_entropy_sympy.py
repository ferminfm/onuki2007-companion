#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Section II.B companion identities.

These checks verify algebraic and one-dimensional integration-by-parts
bookkeeping only.  They do not prove the physical model, thermodynamics,
boundary theory, or PDE well-posedness.
"""

from __future__ import annotations

import sympy as sp


def _assert_zero(name: str, expression: sp.Expr) -> None:
    residual = sp.simplify(expression)
    print(f"{name}\t{residual}")
    if residual != 0:
        raise AssertionError(f"{name} residual is not zero: {residual}")


def _assert_expected_nonzero(
    name: str, expression: sp.Expr, expected: sp.Expr
) -> None:
    residual = sp.factor(sp.simplify(expression))
    expected_residual = sp.factor(sp.simplify(expected))
    print(f"{name}\tPASS_EXPECTED_NONZERO\t{residual}")
    if residual == 0 or sp.simplify(residual - expected_residual) != 0:
        raise AssertionError(
            f"{name} residual {residual} does not match {expected_residual}"
        )


def run_checks() -> None:
    x = sp.symbols("x")
    c = sp.Function("C")(x)
    temp = sp.Function("T")(x)
    k = sp.Function("K")(x)
    m = sp.Function("M")(x)

    m_expr = c * temp + k

    density_symbol, entropy_e, inv_temp = sp.symbols("n s_e invT")
    dim, kB, temperature = sp.symbols("d kB T", positive=True)
    _assert_zero(
        "source_eq_2_17_factor_n",
        (inv_temp - density_symbol * entropy_e).subs(
            inv_temp, density_symbol * entropy_e
        ),
    )
    _assert_zero(
        "entropy_density_variation_energy_coefficient",
        (density_symbol * entropy_e - inv_temp).subs(
            inv_temp, density_symbol * entropy_e
        ),
    )
    entropy_temperature_derivative = dim * kB / (2 * temperature)
    energy_temperature_derivative = dim * density_symbol * kB / 2
    _assert_zero(
        "section_iia_consistency_s_e_ratio",
        entropy_temperature_derivative / energy_temperature_derivative
        - 1 / (density_symbol * temperature),
    )

    delta_sigma, delta_e, delta_n, mu_symbol = sp.symbols(
        "delta_sigma delta_e delta_n mu"
    )
    local_differential = delta_sigma - (inv_temp * delta_e - mu_symbol * inv_temp * delta_n)
    _assert_zero(
        "local_differential_identity_coefficients",
        local_differential.subs(delta_sigma, inv_temp * delta_e - mu_symbol * inv_temp * delta_n),
    )

    _assert_zero("M_equals_CT_plus_K", m_expr - (c * temp + k))

    temperature_identity = temp * sp.diff(m / temp, x) - (
        sp.diff(m, x) - (m / temp) * sp.diff(temp, x)
    )
    _assert_zero("T_grad_M_over_T_identity", temperature_identity)

    complete_coefficient = sp.diff(m_expr, x) - (m_expr / temp) * sp.diff(temp, x)
    substituted_target = (
        temp * sp.diff(c, x) + sp.diff(k, x) - (k / temp) * sp.diff(temp, x)
    )
    _assert_zero(
        "M_equals_CT_plus_K_temperature_correction",
        complete_coefficient - substituted_target,
    )

    simulation_branch = complete_coefficient.subs(
        {
            k: 0,
            sp.diff(k, x): 0,
            sp.diff(c, x): 0,
        }
    )
    _assert_zero("K_zero_constant_C_complete_coefficient", simulation_branch)

    diagnostic_test = sp.diff(m_expr, x).subs(
        {
            k: 0,
            sp.diff(k, x): 0,
            sp.diff(c, x): 0,
        }
    )
    _assert_zero(
        "diagnostic_term_removal_leaves_C_grad_T",
        diagnostic_test - c * sp.diff(temp, x),
    )
    _assert_expected_nonzero(
        "diagnostic_term_removal_is_generically_nonzero",
        diagnostic_test,
        c * sp.diff(temp, x),
    )

    a = sp.Function("A")(x)
    density = sp.Function("n")(x)
    variation = sp.Function("eta")(x)
    lhs = -a * sp.diff(density, x) * sp.diff(variation, x)
    rhs = sp.diff(-a * sp.diff(density, x) * variation, x) + sp.diff(
        a * sp.diff(density, x), x
    ) * variation
    _assert_zero("one_dimensional_integration_by_parts", lhs - rhs)


def main() -> int:
    run_checks()
    print("PASS: Section II.B SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
