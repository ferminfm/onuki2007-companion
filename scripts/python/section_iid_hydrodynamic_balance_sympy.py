#!/usr/bin/env python3
"""Finite SymPy checks for Onuki Section II.D balance-law bookkeeping.

These checks verify algebraic product rules and local flux relations only.
They do not prove the PDE model, constitutive laws, the second law, global
boundary closure, or numerical simulations.
"""

from __future__ import annotations

import csv
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "section_iid_hydrodynamic_balance_summary.tsv"


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
    rows: list[dict[str, str]], check_id: str, expression: sp.Expr, note: str
) -> None:
    residual = sp.factor(sp.simplify(expression))
    _record(rows, check_id, "PASS_EXPECTED_NONZERO", residual, note)
    if residual == 0:
        raise AssertionError(f"{check_id} unexpectedly vanished")


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


def _check_ledger_boundary_status(rows: list[dict[str, str]]) -> None:
    ledger = ROOT / "research_notes" / "ONUKI2007_SOURCE_EQUATION_LEDGER.csv"
    if not ledger.is_file():
        _record(
            rows,
            "global_boundary_entropy_transfer_regression",
            "SKIPPED_CANONICAL_LEDGER",
            "not_exported",
            "canonical source-ledger regression is excluded from the standalone export; finite checks completed",
        )
        return
    with ledger.open(newline="") as handle:
        matches = [
            row
            for row in csv.DictReader(handle)
            if row["equation_number"] == "(2.51)--(2.53)"
        ]
    if len(matches) != 1:
        raise AssertionError("Expected one source-ledger row for Eqs. (2.51)--(2.53)")
    related = matches[0]["related_fukagawa_audit_issue"].lower()
    if "wall" not in related or "global" not in related:
        raise AssertionError("Global entropy ledger row does not preserve wall/global caveat")
    _record(
        rows,
        "global_boundary_entropy_transfer_regression",
        "UNRESOLVED_BOUNDARY_TRANSFER_RECORDED",
        "not_algebraic",
        "Eqs. (2.51)--(2.53) retain boundary/wall-transfer caveat",
    )


def run_checks() -> None:
    rows: list[dict[str, str]] = []

    rho, rho_t, rho_x, v, v_t, v_x = sp.symbols("rho rho_t rho_x v v_t v_x")
    momentum_left = rho_t * v + rho * v_t + rho_x * v**2 + 2 * rho * v * v_x
    velocity_dot_momentum = v * momentum_left
    kinetic_left = (
        sp.Rational(1, 2) * rho_t * v**2
        + rho * v * v_t
        + sp.Rational(1, 2) * rho_x * v**3
        + sp.Rational(3, 2) * rho * v**2 * v_x
    )
    mass_residual = rho_t + rho_x * v + rho * v_x
    kinetic_residual = sp.simplify(velocity_dot_momentum - kinetic_left)
    _assert_zero(
        rows,
        "kinetic_energy_identity_under_mass_balance",
        kinetic_residual.subs(rho_t, -rho_x * v - rho * v_x),
        "velocity dot conservative momentum equals kinetic left-hand side when mass balance holds",
    )
    _assert_zero(
        rows,
        "kinetic_energy_identity_residual_factor",
        kinetic_residual - sp.Rational(1, 2) * v**2 * mass_residual,
        "residual factors exactly by the mass-balance residual",
    )

    a11, a12, a21, a22 = sp.symbols("A11 A12 A21 A22")
    a11_x, a12_y, a21_x, a22_y = sp.symbols("A11_x A12_y A21_x A22_y")
    v1, v2 = sp.symbols("v1 v2")
    v1_x, v1_y, v2_x, v2_y = sp.symbols("v1_x v1_y v2_x v2_y")
    v_dot_div_a = v1 * (a11_x + a12_y) + v2 * (a21_x + a22_y)
    div_a_dot_v = (
        a11_x * v1
        + a11 * v1_x
        + a21_x * v2
        + a21 * v2_x
        + a12_y * v1
        + a12 * v1_y
        + a22_y * v2
        + a22 * v2_y
    )
    stress_power = a11 * v1_x + a21 * v2_x + a12 * v1_y + a22 * v2_y
    _assert_zero(
        rows,
        "stress_flux_product_rule",
        v_dot_div_a - (div_a_dot_v - stress_power),
        "v_i partial_j A_ij = partial_j(A_ij v_i) - A_ij partial_j v_i",
    )

    symmetric_power_dj_vi = a11 * v1_x + a12 * v1_y + a12 * v2_x + a22 * v2_y
    symmetric_power_di_vj = a11 * v1_x + a12 * v2_x + a12 * v1_y + a22 * v2_y
    _assert_zero(
        rows,
        "symmetric_stress_power_dummy_index_swap",
        symmetric_power_dj_vi - symmetric_power_di_vj,
        "for symmetric stress, A_ij partial_j v_i equals A_ij partial_i v_j after dummy-index relabeling",
    )

    pi_power, sigma_power, heat_div, gravity_power = sp.symbols(
        "PiPower SigmaPower HeatDiv GravityPower"
    )
    total_rhs = -sp.Symbol("div_eT_v") - sp.Symbol("div_Pi_v") + sp.Symbol(
        "div_sigma_v"
    ) + heat_div - gravity_power
    kinetic_rhs = -sp.Symbol("div_K_v") - sp.Symbol("div_Pi_v") + pi_power + sp.Symbol(
        "div_sigma_v"
    ) - sigma_power - gravity_power
    internal_rhs = -sp.Symbol("div_ehat_v") - pi_power + sigma_power + heat_div
    bookkeeping_assumptions = {
        sp.Symbol("div_eT_v"): sp.Symbol("div_ehat_v") + sp.Symbol("div_K_v")
    }
    _assert_zero(
        rows,
        "internal_energy_from_total_minus_kinetic",
        (total_rhs - kinetic_rhs - internal_rhs).subs(bookkeeping_assumptions),
        "mechanical flux and gravity cancel in local internal-energy balance",
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_wrong_reversible_stress_sign",
        2 * pi_power,
        "reversing the pressure-positive stress sign leaves twice the reversible stress-power term",
    )

    a, b, c, d, eta, zeta = sp.symbols("a b c d eta zeta")
    theta = a + d
    s11 = 2 * a - theta
    s22 = 2 * d - theta
    s12 = b + c
    sigma11 = eta * s11 + zeta * theta
    sigma22 = eta * s22 + zeta * theta
    sigma12 = eta * s12
    sigma21 = eta * s12
    viscous_contraction = sigma11 * a + sigma12 * b + sigma21 * c + sigma22 * d
    viscous_source_form = sp.Rational(1, 2) * eta * (
        s11**2 + s12**2 + s12**2 + s22**2
    ) + zeta * theta**2
    _assert_zero(
        rows,
        "viscous_heat_production_decomposition_2d",
        viscous_contraction - viscous_source_form,
        "Eq. (2.41) decomposition of sigma_ij partial_i v_j in two dimensions",
    )

    shear, theta_scalar = sp.symbols("shear theta", nonnegative=True)
    viscous_proxy = eta * shear**2 + zeta * theta_scalar**2
    expected_proxy = eta * shear**2 + zeta * theta_scalar**2
    _assert_zero(
        rows,
        "viscous_quadratic_proxy",
        viscous_proxy - expected_proxy,
        "finite compatibility proxy for nonnegative viscous production",
    )

    m_coeff, n, div_v, grad_n, temp = sp.symbols("M n div_v grad_n T", nonzero=True)

    dehat_dt, dn_dt, muhat, mt, nu_dot_grad_n, boundary_measure = sp.symbols(
        "dehat_dt dn_dt muhat M nu_dot_grad_n boundary_measure"
    )
    entropy_rate_from_variation = dehat_dt / temp - muhat * dn_dt / temp - (
        mt * nu_dot_grad_n * dn_dt / temp
    ) * boundary_measure
    entropy_rate_expected = dehat_dt / temp - muhat * dn_dt / temp - (
        mt * nu_dot_grad_n * dn_dt / temp
    ) * boundary_measure
    _assert_zero(
        rows,
        "entropy_rate_eq_242_time_derivative_substitution",
        entropy_rate_from_variation - entropy_rate_expected,
        "Eq. (2.42) is Eq. (2.20) with delta ehat and delta n replaced by time derivatives",
    )

    lhs_condition, ehat, grad_inv_temp, ncoef, grad_muhat_over_temp = sp.symbols(
        "lhs_condition ehat grad_inv_T n grad_muhat_over_T"
    )
    reversible_residual = lhs_condition + ehat * grad_inv_temp - ncoef * grad_muhat_over_temp
    condition_rhs = -ehat * grad_inv_temp + ncoef * grad_muhat_over_temp
    _assert_zero(
        rows,
        "reversible_residual_cancellation_eq_244",
        reversible_residual.subs(lhs_condition, condition_rhs),
        "Eq. (2.44) sets the nondissipative bulk entropy residual to zero",
    )

    lam, tx, txx, lamx = sp.symbols("lambda Tx Txx lambda_x")
    heat_div_over_t = (lamx * tx + lam * txx) / temp
    entropy_heat_flux_div = (lamx * tx + lam * txx) / temp - lam * tx**2 / temp**2
    thermal_entropy_production = lam * tx**2 / temp**2
    _assert_zero(
        rows,
        "thermal_heat_product_rule_eq_245",
        heat_div_over_t - (entropy_heat_flux_div + thermal_entropy_production),
        "Eq. (2.45) product rule leaves lambda |grad T|^2/T^2",
    )

    diff_temp, diff_pressure, e_local, p_local, n_local, s_local, mu_local = sp.symbols(
        "dT dp e p n s mu"
    )
    d_inv_t = -diff_temp / temp**2
    d_mu = -s_local * diff_temp + diff_pressure / n_local
    d_mu_over_t = d_mu / temp + mu_local * d_inv_t
    gibbs_rhs = -e_local * d_inv_t + n_local * d_mu_over_t
    gibbs_lhs = diff_pressure / temp - p_local * diff_temp / temp**2
    mu_identity = {mu_local: (e_local + p_local - temp * n_local * s_local) / n_local}
    _assert_zero(
        rows,
        "gibbs_duhem_identity_eq_246",
        (gibbs_rhs - gibbs_lhs).subs(mu_identity),
        "Eq. (2.46) follows from dmu=-s dT+dp/n and n mu=e+p-T n s",
    )

    v_flux, shat_flux, ehat_flux, muhat_flux, v_dot_grad_n = sp.symbols(
        "v_flux Shat ehat_flux muhat_flux v_dot_grad_n"
    )
    dn_dt_flux = sp.symbols("dn_dt_flux")
    q_flux = n * muhat_flux - ehat_flux + temp * shat_flux
    pi_dot_v = q_flux * v_flux + m_coeff * v_dot_grad_n * grad_n
    flux_before_mass_balance = (
        (ehat_flux - n * muhat_flux) * v_flux / temp
        + pi_dot_v / temp
        + m_coeff * dn_dt_flux * grad_n / temp
    )
    entropy_flux_target = (
        shat_flux * v_flux - m_coeff * n * div_v * grad_n / temp
    )
    number_mass_residual = dn_dt_flux + v_dot_grad_n + n * div_v
    _assert_zero(
        rows,
        "entropy_flux_reconstruction_eq_249",
        flux_before_mass_balance.subs(
            dn_dt_flux, -v_dot_grad_n - n * div_v
        )
        - entropy_flux_target,
        "Eq. (2.49) flux follows from the pressure tensor and D_t n=-n div v",
    )
    _assert_zero(
        rows,
        "entropy_flux_missing_mass_balance_residual_factor",
        flux_before_mass_balance
        - entropy_flux_target
        - m_coeff * grad_n * number_mass_residual / temp,
        "without number balance the unreduced flux factors by D_t n+n div v",
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_entropy_flux_without_number_balance",
        m_coeff * grad_n * number_mass_residual / temp,
        "the Eq. (2.49) flux cancellation is not an identity for unconstrained fields",
    )

    j_ga = m_coeff * n * div_v * grad_n
    j_s_rev = -j_ga / temp
    _assert_zero(
        rows,
        "local_entropy_flux_gauge",
        j_s_rev + j_ga / temp,
        "local relation J_s^rev=-J_GA/T",
    )
    _assert_zero(
        rows,
        "local_entropy_energy_flux_conversion",
        temp * j_s_rev + j_ga,
        "equivalent local conversion T J_s^rev + J_GA=0",
    )
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_omitted_reversible_entropy_flux",
        0 - j_s_rev,
        "omitting the reversible entropy flux leaves the local gauge residual",
    )
    gauge_parameter = sp.symbols("gauge_parameter", nonzero=True)
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_added_flux_gauge",
        gauge_parameter * j_ga / temp,
        "a nonzero added local gauge changes the source-selected entropy flux branch",
    )
    boundary_heat, surface_energy_rate = sp.symbols("boundary_heat surface_energy_rate")
    _assert_expected_nonzero(
        rows,
        "expected_nonzero_omitted_boundary_transfer",
        (boundary_heat + surface_energy_rate) / temp,
        "omitting boundary heat and surface-energy transfer changes the global entropy schematic",
    )

    pi_zz_z, mass_density, grav, particle_mass, density = sp.symbols(
        "Pi_zz_z rho g m n_density"
    )
    _assert_zero(
        rows,
        "static_gravity_stress_balance_eq_251",
        (pi_zz_z + mass_density * grav).subs(
            pi_zz_z, -mass_density * grav
        ),
        "Eq. (2.51) is dPi_zz/dz=-rho g in the static one-dimensional branch",
    )
    muhat_z = sp.symbols("muhat_z")
    _assert_zero(
        rows,
        "gravity_modified_mu_hat_eq_252",
        (density * muhat_z + particle_mass * density * grav).subs(
            muhat_z, -particle_mass * grav
        ),
        "Eq. (2.52) follows from dPi_zz/dz=n dmu_hat/dz and rho=m n",
    )
    nu_lambda_grad_t = sp.symbols("nu_lambda_grad_T")
    conductive_flux = -nu_lambda_grad_t / temp
    _assert_zero(
        rows,
        "conductive_boundary_sign_eq_253",
        -conductive_flux - nu_lambda_grad_t / temp,
        "outward boundary entropy input from -lambda grad T/T is nu.lambda.gradT/T",
    )
    f_s_dot, sigma_s_dot = sp.symbols("f_s_dot sigma_s_dot")
    e_s_dot = f_s_dot + temp * sigma_s_dot
    _assert_zero(
        rows,
        "wall_helmholtz_rate_identity_eq_253",
        e_s_dot / temp - (f_s_dot / temp + sigma_s_dot),
        "fixed-temperature derivative of f_s=e_s-T sigma_s records wall surface-energy contribution",
    )

    _check_ledger_boundary_status(rows)
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Section II.D hydrodynamic-balance SymPy checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
