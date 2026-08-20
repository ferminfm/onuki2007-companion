#!/usr/bin/env python3
"""Pint checks for Section II.D stress, flux, production, and wall-transfer units.

These checks constrain finite dimensional statements only. They do not derive
constitutive laws, close the global boundary branch, or prove the second law.
"""

from __future__ import annotations

import csv
from pathlib import Path

from pint import UnitRegistry


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "section_iid_hydrodynamic_balance_units_summary.tsv"


def main() -> int:
    ureg = UnitRegistry()
    rows: list[dict[str, str]] = []

    length = 1 * ureg.meter
    time = 1 * ureg.second
    temperature = 1 * ureg.kelvin
    energy = 1 * ureg.joule
    pressure = 1 * ureg.pascal

    number_density = 1 / length**3
    density_gradient = number_density / length
    velocity = length / time
    velocity_gradient = 1 / time
    stress = pressure
    force_density = pressure / length
    power_density = energy / length**3 / time
    energy_flux = energy / length**2 / time
    entropy_flux = energy_flux / temperature
    entropy_production = power_density / temperature
    capillary_coefficient = pressure / density_gradient**2
    thermal_conductivity = energy / (time * length * temperature)
    temperature_gradient = temperature / length

    checks = {
        "stress_power_units": (stress * velocity_gradient, power_density),
        "stress_divergence_force_density_units": (stress / length, force_density),
        "stress_energy_flux_units": (stress * velocity, energy_flux),
        "reversible_entropy_flux_units": (
            capillary_coefficient
            / temperature
            * number_density
            * velocity_gradient
            * density_gradient,
            entropy_flux,
        ),
        "conductive_entropy_flux_units": (
            thermal_conductivity * temperature_gradient / temperature,
            entropy_flux,
        ),
        "thermal_entropy_production_units": (
            thermal_conductivity * temperature_gradient**2 / temperature**2,
            entropy_production,
        ),
        "wall_surface_energy_rate_over_temperature_units": (
            energy_flux / temperature,
            entropy_flux,
        ),
    }

    for check_id, (value, target) in checks.items():
        converted = value.to(target.units)
        rows.append(
            {
                "check_id": check_id,
                "status": "PASS_DIMENSIONAL",
                "result": str(converted.to_base_units().units),
                "note": "finite Section II.D dimensional compatibility",
            }
        )
        print(f"{check_id}\tPASS_DIMENSIONAL\t{converted.to_base_units().units}")

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_id", "status", "result", "note"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    print("PASS: Section II.D hydrodynamic-balance Pint checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
