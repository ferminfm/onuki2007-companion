#!/usr/bin/env python3
"""Pint dimensional checks for Onuki Appendix B scaling definitions.

The checks cover the scale definitions used before Appendix B equations are
read. They are dimensional sanity checks only, not a derivation of the scaled
PDEs or a validation of simulation parameters.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pint


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_scaling_definitions_units_summary.tsv"


def _is_dimensionless(quantity: pint.Quantity) -> bool:
    return quantity.to_base_units().dimensionless


def _record(rows: list[dict[str, str]], check_id: str, status: str, result: str, note: str) -> None:
    rows.append(
        {
            "check_id": check_id,
            "status": status,
            "result": result,
            "note": note,
        }
    )
    print(f"{check_id}\t{status}\t{result}\t{note}")


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
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_id", "status", "result", "note"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def run_checks() -> None:
    ureg = pint.UnitRegistry()
    rows: list[dict[str, str]] = []

    length_unit = ureg.meter
    time_unit = ureg.second
    mass_unit = ureg.kilogram
    temperature_unit = ureg.kelvin
    energy_unit = ureg.joule

    length = 1 * length_unit
    time = 1 * time_unit
    mass_quantity = 1 * mass_unit
    temperature = 1 * temperature_unit
    energy = 1 * energy_unit

    v0 = length**3
    n = 1 / length**3
    k_b = energy / temperature
    temp = temperature
    epsilon = energy
    velocity = length / time
    ell = length
    nu0 = length**2 / time
    particle_mass = mass_quantity
    gravity = length / time**2
    e_total = energy / length**3
    c_coeff = energy * length**5 / temperature

    _assert_units(
        rows,
        "length_scale_C_over_kB_v0",
        (c_coeff / (k_b * v0)) ** 0.5,
        length_unit,
        "sqrt(C/(k_B v0)) has length units",
    )
    _assert_units(rows, "time_scale_ell_squared_over_nu0", ell**2 / nu0, time_unit, "ell^2/nu0 has time units")
    _assert_dimensionless(rows, "phi_dimensionless", v0 * n, "phi=v0 n")
    _assert_dimensionless(rows, "theta_dimensionless", k_b * temp / epsilon, "Theta=k_B T/epsilon")
    _assert_dimensionless(rows, "velocity_dimensionless", (ell**2 / nu0) * velocity / ell, "V=t0 v/ell")
    _assert_dimensionless(rows, "energy_density_dimensionless", e_total * v0 / epsilon, "E_T=e_T v0/epsilon")
    _assert_dimensionless(rows, "sigma_dimensionless", nu0**2 * particle_mass / (epsilon * ell**2), "sigma=nu0^2 m/(epsilon ell^2)")
    _assert_dimensionless(rows, "gravity_dimensionless", particle_mass * gravity * ell / epsilon, "g*=m g ell/epsilon")
    _assert_units(rows, "viscosity_branch_units", nu0 * particle_mass * n, mass_unit / (length_unit * time_unit), "eta=zeta=nu0 m n")
    _assert_units(rows, "thermal_conductivity_branch_units", k_b * nu0 * n, energy_unit / (temperature_unit * length_unit * time_unit), "lambda=k_B nu0 n")
    _write_summary(rows)


def main() -> int:
    run_checks()
    print("PASS: Appendix B scaling-definition Pint checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
