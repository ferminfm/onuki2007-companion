#!/usr/bin/env python3
"""Pint dimensional checks for the Korteweg 1901 capillary tensor."""

from __future__ import annotations

import csv
from pathlib import Path

from pint import UnitRegistry


ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "generated" / "python" / "korteweg1901_tensor_units_summary.tsv"


def main() -> int:
    ureg = UnitRegistry()
    length = 1 * ureg.meter
    mass = 1 * ureg.kilogram
    time = 1 * ureg.second
    density = mass / length**3
    pressure = mass / (length * time**2)
    grad_density = density / length
    hess_density = density / length**2

    alpha = pressure / grad_density**2
    beta = alpha
    gamma = pressure / hess_density
    delta_k = gamma

    checks = {
        "alpha_gradient_square_pressure": alpha * grad_density**2,
        "beta_dyadic_pressure": beta * grad_density**2,
        "gamma_laplacian_pressure": gamma * hess_density,
        "delta_hessian_pressure": delta_k * hess_density,
    }
    rows: list[dict[str, str]] = []
    for check_id, value in checks.items():
        value.to(pressure.units)
        rows.append({"check_id": check_id, "status": "PASS_DIMENSIONAL", "result": str(value.to_base_units().units)})
        print(f"{check_id}\tPASS_DIMENSIONAL\t{value.to_base_units().units}")

    force_density = pressure / length
    divergence = (alpha * grad_density**2) / length
    divergence.to(force_density.units)
    rows.append({"check_id": "stress_divergence_force_density", "status": "PASS_DIMENSIONAL", "result": str(divergence.to_base_units().units)})
    print(f"stress_divergence_force_density\tPASS_DIMENSIONAL\t{divergence.to_base_units().units}")

    m0 = mass
    number_density = 1 / length**3
    (m0 * number_density).to(density.units)
    rows.append({"check_id": "mass_number_density_map", "status": "PASS_DIMENSIONAL", "result": str((m0 * number_density).to_base_units().units)})
    print(f"mass_number_density_map\tPASS_DIMENSIONAL\t{(m0 * number_density).to_base_units().units}")

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "result"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print("PASS: Korteweg 1901 tensor Pint checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
