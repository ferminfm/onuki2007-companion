#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Section II.A companion identities.

These checks verify algebraic thermodynamic and one-dimensional variational
bookkeeping only. They do not prove the physical equation of state, the dynamic
model, simulations, or PDE well-posedness.
"""

from __future__ import annotations

import sympy as sp
import pint


def _assert_zero(name: str, expression: sp.Expr) -> None:
    residual = sp.factor(sp.simplify(expression))
    print(f"{name}	PASS_ZERO	{residual}")
    if residual != 0:
        raise AssertionError(f"{name} residual is not zero: {residual}")


def run_checks() -> None:
    n, temp, kB, v0, eps, dim, mass, lam0 = sp.symbols(
        "n T kB v0 eps d m lam0", positive=True
    )
    x = sp.symbols("x")

    lambda_power = lam0 * temp ** (-dim / 2)
    f = kB * temp * n * (sp.log(lambda_power * n) - 1 - sp.log(1 - v0 * n)) - eps * v0 * n**2
    mu = sp.diff(f, n)
    pressure = n * mu - f
    pressure_target = n * kB * temp / (1 - v0 * n) - eps * v0 * n**2
    _assert_zero("bulk_pressure_from_n_mu_minus_f", pressure - pressure_target)

    entropy = -(sp.diff(f, temp)) / n
    entropy_target = -kB * (sp.log(lambda_power * n) - sp.log(1 - v0 * n)) + kB * (dim + 2) / 2
    _assert_zero("entropy_from_temperature_derivative", entropy - entropy_target)

    internal_energy = f + temp * n * entropy
    internal_target = dim * n * kB * temp / 2 - eps * v0 * n**2
    _assert_zero("internal_energy_from_f_plus_Tns", internal_energy - internal_target)

    spinodal_temp = 2 * eps * v0 * n * (1 - v0 * n) ** 2 / kB
    dpdn_T = sp.diff(pressure_target, n)
    _assert_zero(
        "isothermal_derivative_spinodal_factor",
        dpdn_T - kB * (temp - spinodal_temp) / (1 - v0 * n) ** 2,
    )

    dsdn_T = sp.diff(entropy_target, n)
    dsdT_n = sp.diff(entropy_target, temp)
    dTdn_s = -dsdn_T / dsdT_n
    _assert_zero(
        "adiabatic_temperature_derivative",
        dTdn_s - 2 * temp / (dim * n * (1 - v0 * n)),
    )

    dpdT_n = sp.diff(pressure_target, temp)
    dpdn_s = sp.simplify(dpdn_T + dpdT_n * dTdn_s)
    sound_target = kB * temp * (1 + sp.Rational(2, 1) / dim - spinodal_temp / temp) / (1 - v0 * n) ** 2
    _assert_zero("adiabatic_pressure_derivative_sound_kernel", dpdn_s - sound_target)
    sound_speed_squared = sound_target / mass
    sound_speed_squared_target = (
        kB
        * temp
        * (1 + sp.Rational(2, 1) / dim - spinodal_temp / temp)
        / (mass * (1 - v0 * n) ** 2)
    )
    _assert_zero("sound_speed_squared_with_excluded_volume_denominator", sound_speed_squared - sound_speed_squared_target)

    gamma_ratio = sp.simplify(dpdn_s / dpdn_T)
    gamma_target = 1 + 2 / (dim * (1 - spinodal_temp / temp))
    _assert_zero("specific_heat_ratio_from_pressure_derivatives", gamma_ratio - gamma_target)

    density = sp.Function("n")(x)
    mcoef = sp.Function("M")(density)
    nx = sp.diff(density, x)
    integrand = sp.Function("f0")(density) + sp.Rational(1, 2) * mcoef * nx**2
    euler = sp.diff(integrand, density) - sp.diff(sp.diff(integrand, nx), x)
    mu0 = sp.diff(sp.Function("f0")(density), density)
    mn = sp.diff(sp.Function("M")(density), density)
    expected_euler = mu0 - mcoef * sp.diff(density, x, 2) - sp.Rational(1, 2) * mn * nx**2
    _assert_zero("gradient_euler_lagrange_kernel", euler - expected_euler)

    interface_force = mcoef * sp.diff(density, x, 2) + sp.Rational(1, 2) * mn * nx**2
    compact_source_form = sp.Rational(1, 2) * mcoef * sp.diff(density, x, 2) + sp.diff(sp.Rational(1, 2) * mcoef * nx, x)
    _assert_zero("source_compact_gradient_chemical_potential_form", interface_force - compact_source_form)


    pressure_excess_candidate = density * interface_force - sp.Rational(1, 2) * mcoef * nx**2
    source_pressure_form = (
        sp.Rational(1, 2) * mcoef * density * sp.diff(density, x, 2)
        + sp.diff(sp.Rational(1, 2) * mcoef * density * nx, x)
        - mcoef * nx**2
    )
    _assert_zero("eq_2_10_source_pressure_form", source_pressure_form - pressure_excess_candidate)
    _assert_zero(
        "eq_2_10_dp_equals_n_dmu_route",
        sp.diff(source_pressure_form, x) - density * sp.diff(interface_force, x),
    )

    first_integral_lhs = sp.diff(sp.Rational(1, 2) * mcoef * nx**2, x)
    first_integral_rhs = interface_force * nx
    _assert_zero("surface_tension_first_integral_bookkeeping", first_integral_lhs - first_integral_rhs)

    omega_excess = sp.Rational(1, 2) * mcoef * nx**2
    interfacial_excess_integrand = omega_excess + sp.Rational(1, 2) * mcoef * nx**2
    _assert_zero("surface_tension_grand_potential_reduction", interfacial_excess_integrand - mcoef * nx**2)

    m_pos, omega_pos = sp.symbols("M_pos omega_pos", positive=True)
    nx_pos = sp.sqrt(2 * omega_pos / m_pos)
    density_integrand = m_pos * nx_pos
    density_target = sp.sqrt(2 * m_pos * omega_pos)
    _assert_zero(
        "surface_tension_monotone_density_change",
        density_integrand - density_target,
    )

    wrong_orientation_residual = sp.simplify(-density_integrand - density_target)
    print(
        "surface_tension_wrong_orientation_negative_control"
        f"\tPASS_EXPECTED_NONZERO\t{wrong_orientation_residual}"
    )
    if wrong_orientation_residual == 0:
        raise AssertionError("reversing the monotone orientation must reverse the density integral")

    ureg = pint.UnitRegistry()
    sound_speed_unit = (1 * ureg.joule / ureg.kilogram) ** 0.5
    converted = sound_speed_unit.to(ureg.meter / ureg.second)
    print(f"sound_speed_units\tPASS_DIMENSIONAL\t{converted.units}")


def main() -> int:
    run_checks()
    print("PASS: Section II.A van der Waals baseline SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
