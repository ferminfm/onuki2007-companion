"""Stable metadata for the public Python, SymPy, and Pint verification routes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    """A legacy script exposed by the portable command-line interface."""

    check_id: str
    topic: str
    script: str
    scope: str
    dimensional: bool = False
    public: bool = True


CHECKS: tuple[Check, ...] = (
    Check("scaffold", "repository", "scripts/python/check_companion_scaffold.py", "canonical repository layout and excluded source-audit ledgers", public=False),
    Check("iia-vdw", "section-iia", "scripts/python/section_iia_vdw_baseline_sympy.py", "finite local van der Waals identities"),
    Check("iib-gradient", "section-iib", "scripts/python/section_iib_gradient_entropy_sympy.py", "finite gradient-entropy and coefficient identities"),
    Check("iic-wall", "section-iic", "scripts/python/section_iic_equilibrium_wall_sympy.py", "equilibrium and declared wall-branch algebra"),
    Check("appendix-a-stress", "appendix-a", "scripts/python/appendix_a_reversible_stress_sympy.py", "finite reversible-stress component bookkeeping"),
    Check("iid-balance", "section-iid", "scripts/python/section_iid_hydrodynamic_balance_sympy.py", "local energy and entropy bookkeeping"),
    Check("iid-units", "section-iid", "scripts/python/section_iid_hydrodynamic_balance_units.py", "dimensions of Section II.D flux and production terms", True),
    Check("iid-p1", "section-iid", "scripts/python/section_iid_p1_pressure_expansion_sympy.py", "diagonal pressure expansion under fixed-temperature derivatives"),
    Check("b-scaling", "appendix-b", "scripts/python/appendix_b_scaling_definitions_sympy.py", "Appendix-B scale definitions and finite substitutions"),
    Check("b-scaling-units", "appendix-b", "scripts/python/appendix_b_scaling_definitions_units.py", "Appendix-B scale dimensions", True),
    Check("b-momentum", "appendix-b", "scripts/python/appendix_b_momentum_b3_sympy.py", "printed and dimensional-source B3 branch comparison"),
    Check("b-b3", "appendix-b", "scripts/python/appendix_b_b3_typo_candidate_sympy.py", "dimensional-source B3 factor residual and control"),
    Check("b-energy", "appendix-b", "scripts/python/appendix_b_energy_boundary_sympy.py", "scaled local energy and boundary bookkeeping"),
    Check("b-energy-units", "appendix-b", "scripts/python/appendix_b_energy_boundary_units.py", "scaled energy and boundary dimensions", True),
    Check("iii-estimates", "section-iii", "scripts/python/section_iii_simulation_estimates.py", "finite published-estimate arithmetic; no numerical reproduction"),
    Check("korteweg-tensor", "korteweg", "scripts/python/korteweg1901_tensor_sympy.py", "finite tensor reconstruction in the declared notation"),
    Check("korteweg-units", "korteweg", "scripts/python/korteweg1901_tensor_units.py", "tensor and force-density dimensions", True),
    Check("korteweg-crosswalk", "korteweg", "scripts/python/korteweg_onuki_crosswalk_sympy.py", "bounded local Korteweg--Onuki tensor crosswalk"),
)


def by_id(check_id: str) -> Check:
    """Return one check or raise a reader-facing key error."""

    for check in CHECKS:
        if check.check_id == check_id:
            return check
    raise KeyError(f"unknown check ID: {check_id}")
