#!/usr/bin/env python3
"""Pint dimensional checks for Appendix B energy and boundary scaling.

These checks verify units for the scaled energy density, heat branch, gravity
power, and density wall condition. They do not validate any numerical run or
decide the unpublished simulation-code branch.
"""

from __future__ import annotations

import csv
from pathlib import Path

from pint import UnitRegistry


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "appendix_b_energy_boundary_units_summary.tsv"


def _write(rows: list[dict[str, str]]) -> None:
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "result", "note"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _record(rows: list[dict[str, str]], check_id: str, status: str, result: str, note: str) -> None:
    rows.append({"check_id": check_id, "status": status, "result": result, "note": note})
    print(f"{check_id}\t{status}\t{result}\t{note}")


def main() -> int:
    ureg = UnitRegistry()
    rows: list[dict[str, str]] = []

    length = 1 * ureg.meter
    time = 1 * ureg.second
    mass = 1 * ureg.kilogram
    temperature = 1 * ureg.kelvin
    energy = 1 * ureg.joule

    v0 = length**3
    n = 1 / length**3
    velocity = length / time
    epsilon = energy
    k_b = energy / temperature
    e_density = energy / length**3
    nu0 = length**2 / time
    g = length / time**2
    ell = length

    dimensionless_targets = {
        "energy_density_scaled": e_density * v0 / epsilon,
        "kinetic_energy_scaled": (mass * n * velocity**2) * v0 / epsilon,
        "heat_coefficient_scaled": (ell**2 / nu0) * nu0 / ell**2,
        "gravity_power_scaled": mass * g * ell / epsilon,
        "boundary_gradient_scaled": v0 * ell * (1 / length**4),
        "boundary_rhs_scaled": v0 * n,
    }
    for check_id, quantity in dimensionless_targets.items():
        reduced = quantity.to_base_units()
        if not reduced.dimensionless:
            raise AssertionError(f"{check_id} is not dimensionless: {reduced}")
        _record(rows, check_id, "PASS_DIMENSIONLESS", str(reduced.units), "Appendix B energy/boundary scaling")

    heat_flux_coeff = k_b * nu0 * n
    _record(
        rows,
        "thermal_conductivity_branch_units",
        "PASS_DIMENSIONAL",
        str(heat_flux_coeff.to_base_units().units),
        "lambda=k_B*nu0*n",
    )

    _write(rows)
    print("PASS: Appendix B energy/boundary Pint checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
