#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Central companion verification runner.
#
# This script runs finite algebraic, dimensional, ledger, and prose-regression
# checks that correspond to Appendix C and the public code-to-paper map in
# research_notes/onuki_companion_code_to_paper_map.csv and research_notes/visible_derivation_code_to_equation_map.csv.  Legacy batch-internal
# maps are still regression-tested separately where useful.  The runner deliberately
# avoids numerical reproduction and does not claim to prove the PDE model,
# physical constitutive laws, the second law, or unpublished implementation
# behavior.

python3 scripts/python/check_companion_scaffold.py
python3 scripts/python/section_iia_vdw_baseline_sympy.py
python3 scripts/python/section_iib_gradient_entropy_sympy.py
python3 scripts/python/section_iic_equilibrium_wall_sympy.py
python3 scripts/python/appendix_a_reversible_stress_sympy.py
python3 scripts/python/section_iid_hydrodynamic_balance_sympy.py
python3 scripts/python/section_iid_hydrodynamic_balance_units.py
python3 scripts/python/section_iid_p1_pressure_expansion_sympy.py
python3 scripts/python/appendix_b_scaling_definitions_sympy.py
python3 scripts/python/appendix_b_scaling_definitions_units.py
python3 scripts/python/appendix_b_momentum_b3_sympy.py
python3 scripts/python/appendix_b_b3_typo_candidate_sympy.py
python3 scripts/python/appendix_b_energy_boundary_sympy.py
python3 scripts/python/appendix_b_energy_boundary_units.py
python3 scripts/python/section_iii_simulation_estimates.py
python3 scripts/python/korteweg1901_tensor_sympy.py
python3 scripts/python/korteweg1901_tensor_units.py
python3 scripts/python/korteweg_onuki_crosswalk_sympy.py
python3 scripts/python/build_coauthor_relation_audit.py
python3 scripts/python/build_coauthor_verification_map.py
python3 -m pytest -q \
  tests/test_coauthor_relation_audit.py \
  tests/test_coauthor_t03_derivation_closure.py \
  tests/test_coauthor_t04_derivation_closure.py \
  tests/test_coauthor_t05_derivation_closure.py \
  tests/test_coauthor_t06_public_editorial.py \
  tests/test_coauthor_t06_derivation_closure.py \
  tests/test_coauthor_t07_verification_audit.py \
  tests/test_reference_catalog.py \
  tests/test_derivation_proof_policy.py \
  tests/test_section_iia_vdw_baseline.py \
  tests/test_companion_scaffold.py \
  tests/test_section_iib_gradient_entropy.py \
  tests/test_section_iic_equilibrium_wall.py \
  tests/test_appendix_a_reversible_stress.py \
  tests/test_section_iid_hydrodynamic_balances.py \
  tests/test_section_iid_p1_pressure_expansion.py \
  tests/test_appendix_b_scaling_definitions.py \
  tests/test_appendix_b_momentum_b3.py \
  tests/test_appendix_b_b3_typo_candidate.py \
  tests/test_appendix_b_energy_boundary.py \
  tests/test_section_iii_simulation_guide.py \
  tests/test_companion_code_readability.py \
  tests/test_capillary_interstitial_context.py \
  tests/test_external_source_anchoring.py \
  tests/test_literature_source_anchoring.py \
  tests/test_bounded_discrepancy_source_page_audit.py \
  tests/test_provenance_readability_final_qa.py \
  tests/test_visible_derivation_code_gate.py \
  tests/test_korteweg1901_primary_source_inventory.py \
  tests/test_korteweg_historical_lineage_map.py \
  tests/test_korteweg1901_tensor_reconstruction.py \
  tests/test_korteweg_onuki_crosswalk.py \
  tests/test_korteweg_public_integration.py \
  tests/test_korteweg_provenance_formal_scope_audit.py \
  tests/test_korteweg_final_qa_handoff.py

if command -v WolframKernel >/dev/null 2>&1; then
  WolframKernel -script scripts/wolfram/section_iia_vdw_baseline_checks.wls
  WolframKernel -script scripts/wolfram/section_iib_gradient_entropy_checks.wls
  WolframKernel -script scripts/wolfram/section_iic_equilibrium_wall_checks.wls
  WolframKernel -script scripts/wolfram/appendix_a_reversible_stress_checks.wls
  WolframKernel -script scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls
  WolframKernel -script scripts/wolfram/section_iid_p1_pressure_expansion_checks.wls
  WolframKernel -script scripts/wolfram/appendix_b_scaling_definitions_checks.wls
  WolframKernel -script scripts/wolfram/appendix_b_momentum_b3_checks.wls
  WolframKernel -script scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls
  WolframKernel -script scripts/wolfram/appendix_b_energy_boundary_checks.wls
  WolframKernel -script scripts/wolfram/appendix_b_transition_trace.wls
  WolframKernel -script scripts/wolfram/section_iii_simulation_estimates_checks.wls
  WolframKernel -script scripts/wolfram/korteweg1901_tensor_trace.wls
  WolframKernel -script scripts/wolfram/korteweg_onuki_crosswalk_checks.wls
elif command -v wolframscript >/dev/null 2>&1; then
  wolframscript -file scripts/wolfram/section_iia_vdw_baseline_checks.wls
  wolframscript -file scripts/wolfram/section_iib_gradient_entropy_checks.wls
  wolframscript -file scripts/wolfram/section_iic_equilibrium_wall_checks.wls
  wolframscript -file scripts/wolfram/appendix_a_reversible_stress_checks.wls
  wolframscript -file scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls
  wolframscript -file scripts/wolfram/section_iid_p1_pressure_expansion_checks.wls
  wolframscript -file scripts/wolfram/appendix_b_scaling_definitions_checks.wls
  wolframscript -file scripts/wolfram/appendix_b_momentum_b3_checks.wls
  wolframscript -file scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls
  wolframscript -file scripts/wolfram/appendix_b_energy_boundary_checks.wls
  wolframscript -file scripts/wolfram/appendix_b_transition_trace.wls
  wolframscript -file scripts/wolfram/section_iii_simulation_estimates_checks.wls
  wolframscript -file scripts/wolfram/korteweg1901_tensor_trace.wls
  wolframscript -file scripts/wolfram/korteweg_onuki_crosswalk_checks.wls
else
  printf '%s\n' "Wolfram unavailable; symbolic companion checks skipped"
fi
