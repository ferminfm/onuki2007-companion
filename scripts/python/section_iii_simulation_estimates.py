#!/usr/bin/env python3
"""Finite estimate checks for the Onuki Section III reading guide.

The checks are algebraic and dimensional only.  They do not reproduce source
simulations, figures, or unpublished implementation details.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pint
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "section_iii_simulation_estimates_summary.tsv"


def _record(rows: list[dict[str, str]], check_id: str, status: str, result: str, note: str) -> None:
    rows.append({"check_id": check_id, "status": status, "result": result, "note": note})
    print(f"{check_id}\t{status}\t{result}\t{note}")


def _assert_zero(rows: list[dict[str, str]], check_id: str, expression: sp.Expr, note: str) -> None:
    residual = sp.factor(sp.cancel(sp.simplify(expression)))
    _record(rows, check_id, "PASS_ZERO", str(residual), note)
    if residual != 0:
        raise AssertionError(f"{check_id} residual is not zero: {residual}")


def _is_dimensionless(quantity: pint.Quantity) -> bool:
    return quantity.to_base_units().dimensionless


def _assert_dimensionless(rows: list[dict[str, str]], check_id: str, quantity: pint.Quantity, note: str) -> None:
    reduced = quantity.to_base_units()
    status = "PASS_DIMENSIONLESS" if _is_dimensionless(reduced) else "FAIL_DIMENSIONAL"
    _record(rows, check_id, status, str(reduced.units), note)
    if status != "PASS_DIMENSIONLESS":
        raise AssertionError(f"{check_id} is not dimensionless: {reduced.units}")


def _assert_units(rows: list[dict[str, str]], check_id: str, quantity: pint.Quantity, target: pint.Unit, note: str) -> None:
    converted = quantity.to(target)
    _record(rows, check_id, "PASS_DIMENSIONAL", str(converted.units), note)


def _write_summary(rows: list[dict[str, str]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "result", "note"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    ell, nu0, t0, mass, eps, As, sigma, c, Q = sp.symbols(
        "ell nu0 t0 m epsilon A_s sigma c Q", positive=True
    )
    sigma_form_a = nu0**2 * mass / (eps * ell**2)
    sigma_form_b = mass * ell**2 / (eps * t0**2)
    _assert_zero(
        rows,
        "section_iii_sigma_forms",
        (sigma_form_a - sigma_form_b).subs(t0, ell**2 / nu0),
        "Eq. (3.6) forms agree after t0=ell^2/nu0",
    )
    _assert_zero(
        rows,
        "section_iii_sound_scale",
        (t0 * c / ell - As / sp.sqrt(sigma)).subs(c, As * ell / (t0 * sp.sqrt(sigma))),
        "Eq. (3.8) is equivalent to t0 c/ell=A_s sigma^{-1/2}",
    )

    density_ratio = sp.Rational(170, 100) / sp.Rational(27, 100)
    _assert_zero(
        rows,
        "transport_density_ratio_1p70_over_0p27",
        density_ratio - sp.Rational(170, 27),
        "Eqs. (3.3)--(3.4) make liquid/gas transport ratios follow n_l/n_g",
    )

    kB, T, Ts, v0, n, B = sp.symbols("k_B T T_s v_0 n B", positive=True)
    _assert_zero(
        rows,
        "sound_As_eq39_denominator",
        sp.sqrt(B / mass) * sp.sqrt(mass / eps) / (1 - v0 * n) - sp.sqrt(B / eps) / (1 - v0 * n),
        "Eq. (3.9) follows from A_s=c sqrt(m/epsilon) and the denominator branch of c",
    )

    L = sp.symbols("L", positive=True)
    c_from_eq38 = As * ell / (t0 * sp.sqrt(sigma))
    _assert_zero(
        rows,
        "acoustic_traversal_time_scale",
        L / c_from_eq38 - (L / ell) * t0 * sp.sqrt(sigma) / As,
        "L/c=(L/ell)t0 sigma^{1/2}/A_s from Eq. (3.8)",
    )

    gamma_s = sp.symbols("gamma_s", positive=True)
    gamma_attenuation = 2 * nu0 + (2 * nu0 / gamma_s) * (gamma_s - 1)
    _assert_zero(
        rows,
        "sound_damping_source_reduction",
        gamma_attenuation / (2 * nu0) - (2 - 1 / gamma_s),
        "Eq. (3.10) damping coefficient under the source attenuation convention",
    )

    tau = sp.symbols("tau", positive=True)
    capillary_left = t0 * sp.sqrt(eps * ell * tau ** sp.Rational(3, 2) * (Q / ell) ** 3 / mass)
    capillary_right = tau ** sp.Rational(3, 4) * Q ** sp.Rational(3, 2) / sp.sqrt(sigma)
    _assert_zero(
        rows,
        "capillary_wave_eq311_scaling",
        capillary_left.subs(sigma, mass * ell**2 / (eps * t0**2)) - capillary_right.subs(sigma, mass * ell**2 / (eps * t0**2)),
        "Eq. (3.11) follows from capillary-wave scaling and sigma definition",
    )

    p_vdw = n * kB * T / (1 - v0 * n) - eps * v0 * n**2
    Ts_expr = 2 * eps * v0 * n * (1 - v0 * n) ** 2 / kB
    _assert_zero(
        rows,
        "inverse_compressibility_eq312",
        n * sp.diff(p_vdw, n) - kB * n * (T - Ts_expr) / (1 - v0 * n) ** 2,
        "Eq. (3.12) follows from pressure derivative and spinodal temperature",
    )

    dim = sp.symbols("d", positive=True)
    Tn_s = 2 * T / (dim * n * (1 - v0 * n))
    pn_s = kB * T / (1 - v0 * n) ** 2 * (1 + sp.Rational(2, 1) / dim - Ts / T)
    As_d2 = (Tn_s / pn_s).subs(dim, 2)
    _assert_zero(
        rows,
        "adiabatic_coefficient_eq314_d2",
        As_d2 - (1 / n - v0) / (kB * (2 - Ts / T)),
        "Eq. (3.14) for d=2 from fixed-entropy derivative ratio",
    )

    delta_p, delta_T_b, As_l = sp.symbols("delta_p delta_T_b A_sl", positive=True)
    _assert_zero(
        rows,
        "pressure_estimate_eq313",
        (delta_p - delta_T_b / As_l).subs(delta_p, delta_T_b / As_l),
        "Eq. (3.13) reciprocal pressure-temperature estimate",
    )

    DeltaT, As_g = sp.symbols("DeltaT A_sg", positive=True)
    _assert_zero(
        rows,
        "phase_temperature_contrast_eq315",
        (DeltaT - (As_g - As_l) * delta_p).subs(DeltaT, (As_g - As_l) * delta_p),
        "Eq. (3.15) from subtracting two adiabatic temperature increments",
    )

    heat_flux, n_g, temperature, delta_s, v_c = sp.symbols("Q n_g T Delta_s v_c", positive=True)
    _assert_zero(
        rows,
        "latent_heat_velocity_definition",
        (v_c - heat_flux / (n_g * temperature * delta_s)).subs(v_c, heat_flux / (n_g * temperature * delta_s)),
        "Eq. (3.16) defines a finite velocity scale",
    )
    lambda_l, Tinf_prime = sp.symbols("lambda_l Tinf_prime", positive=True)
    _assert_zero(
        rows,
        "latent_heat_velocity_gradient_branch",
        (v_c + lambda_l * Tinf_prime / (n_g * temperature * delta_s)).subs(
            v_c, -lambda_l * Tinf_prime / (n_g * temperature * delta_s)
        ),
        "Eq. (3.16) far-field heat-flux branch Q=-lambda_l T'_infty",
    )

    lambda_eff, Nu = sp.symbols("lambda_eff Nu", positive=True)
    q_integral, delta_wall_temp = sp.symbols("Q_integral DeltaT_wall", positive=True)
    _assert_zero(
        rows,
        "effective_conductivity_eq317_definition",
        (lambda_eff - q_integral / delta_wall_temp).subs(
            lambda_eff, q_integral / delta_wall_temp
        ),
        "Eq. (3.17) defines lambda_eff from integrated bottom heat input",
    )
    bottom_flux, lambda_wall, grad_t_wall = sp.symbols(
        "Q_b lambda_wall gradT_wall", positive=True
    )
    _assert_zero(
        rows,
        "bottom_heat_flux_eq318_definition",
        (bottom_flux + lambda_wall * grad_t_wall).subs(
            bottom_flux, -lambda_wall * grad_t_wall
        ),
        "Eq. (3.18) is the conductive bottom-wall flux diagnostic",
    )
    _assert_zero(
        rows,
        "nusselt_ratio_definition",
        (Nu - lambda_eff / lambda_l).subs(Nu, lambda_eff / lambda_l),
        "Eq. (3.19) is a dimensionless ratio definition",
    )
    nc = sp.symbols("n_c", positive=True)
    _assert_zero(
        rows,
        "one_phase_nusselt_no_convection",
        (Nu - n / (sp.Rational(17, 10) * nc)).subs(Nu, n / (sp.Rational(17, 10) * nc)),
        "No-convection one-phase estimate Nu=n/(1.7 n_c)",
    )
    q0 = sp.symbols("Q_0", positive=True)
    _assert_zero(
        rows,
        "wetting_heat_flux_normalization",
        (q0 - eps * ell / (v0 * t0)).subs(q0, eps * ell / (v0 * t0)),
        "Section III.G plot-reading scale Q0=epsilon ell/(v0 t0)",
    )

    gravity, Tc, pc, gstar = sp.symbols("g T_c p_c gstar", positive=True)
    order_expr = (mass * n) * gravity * Tc / pc
    order_target = gstar * Tc / ell
    _assert_zero(
        rows,
        "adiabatic_gradient_order_eq320",
        order_expr.subs({n: 1 / v0, pc: eps / v0, gstar: mass * gravity * ell / eps})
        - order_target.subs(gstar, mass * gravity * ell / eps),
        "Eq. (3.20) order estimate gives g* T_c/ell under vdW scales",
    )

    _record(
        rows,
        "section_iii_no_numerical_reproduction_gate",
        "NOT_REPRODUCED",
        "not_applicable",
        "Section III guide checks finite estimates only",
    )
    _record(
        rows,
        "section_iii_b3_simulation_code_branch",
        "UNRESOLVED_SOURCE_DEPENDENT",
        "not_applicable",
        "Unpublished simulation-code branch is not inferred from Section III estimates",
    )

    ureg = pint.UnitRegistry()
    length = 1 * ureg.meter
    time = 1 * ureg.second
    mass_q = 1 * ureg.kilogram
    temp = 1 * ureg.kelvin
    energy = 1 * ureg.joule

    gravity_q = length / time**2
    _assert_dimensionless(rows, "section_iii_gstar_dimensionless", mass_q * gravity_q * length / energy, "g*=m g ell/epsilon")

    heat_flux_q = energy / (length**2 * time)
    entropy_per_particle = energy / temp
    number_density = 1 / length**3
    _assert_units(rows, "latent_heat_velocity_units", heat_flux_q / (number_density * temp * entropy_per_particle), length / time, "Q/(n_g T Delta s) has velocity units")

    thermal_conductivity = energy / (time * length * temp)
    integrated_bottom_heat = heat_flux_q * length
    _assert_units(
        rows,
        "effective_conductivity_eq317_units",
        integrated_bottom_heat / temp,
        thermal_conductivity.units,
        "integral Q_b dx divided by Delta T has two-dimensional conductivity units",
    )
    _assert_units(
        rows,
        "bottom_heat_flux_eq318_units",
        thermal_conductivity * temp / length,
        heat_flux_q.units,
        "lambda partial_y T has heat-flux units",
    )
    _assert_dimensionless(rows, "nusselt_dimensionless", thermal_conductivity / thermal_conductivity, "lambda_eff/lambda_l is dimensionless")

    pressure = energy / length**3
    dT_dp_at_s = temp / pressure
    _assert_units(rows, "adiabatic_gradient_units", (mass_q / length**3) * gravity_q * dT_dp_at_s, temp / length, "rho g (partial T/partial p)_s has temperature-gradient units")

    density = 1 / length**3
    density_gradient = density / length
    _assert_units(rows, "density_wall_condition_units", length * density_gradient, 1 / length**3, "ell nu.grad n has density units before scaling")

    v0_q = length**3
    t0_q = time
    ell_q = length
    _assert_units(rows, "heat_flux_normalization_q0_units", energy * ell_q / (v0_q * t0_q), heat_flux_q.units, "Q0=epsilon ell/(v0 t0) has heat-flux units")

    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Section III simulation-estimate checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
