# Wolfram Suite Guide

This guide is a reader map for the committed Wolfram Language checks. It does
not replace the visible derivations in the companion. Each suite begins from
the stated finite expression, displays named intermediate transitions in its
terminal trace, and compares a residual with zero or with a deliberately
nonzero control. A successful run has the limited scope shown below.

| Suite | Source and companion anchor | Premise and assumptions | Trace and control | Expected result and scope |
|---|---|---|---|---|
| `IIA` | Onuki (2.1)--(2.11); Section II.A | Local free-energy variables; no gradient or boundary term | `section_iia_vdw_baseline_checks.wls`; altered derivative-sign control | Local algebraic thermodynamic identities only |
| `IIB` | Onuki (2.12)--(2.20); Section II.B | Smooth density and temperature fields; stated variational boundary branch | `section_iib_gradient_entropy_checks.wls`; suppressed gradient-term control | Functional-derivative components under the named variation |
| `IIC` | Onuki (2.21)--(2.34); Section II.C | One-dimensional equilibrium profile and declared wall branch | `section_iic_equilibrium_wall_checks.wls`; incompatible wall-data control | Stationary-profile and wall-term bookkeeping, not dynamics |
| `APPENDIX_A` | Appendix A; (2.47); Appendix A companion | Smooth virtual displacement and fixed boundary convention | `appendix_a_reversible_stress_checks.wls`; stress-sign control | Finite stress/virtual-work transition, not a continuum theorem |
| `IID_BALANCE` | Onuki (2.35)--(2.53); Section II.D | Smooth local fields and stated balance-law conventions | `section_iid_hydrodynamic_balance_checks.wls`; omitted reversible-flux control | Local balance bookkeeping only; global transfer is excluded |
| `IID_P1` | Onuki (2.48); Section II.D | Thermodynamic partial derivative at fixed temperature | `section_iid_p1_pressure_expansion_checks.wls`; total-versus-partial derivative control | Diagonal pressure expansion under explicit derivative conventions |
| `B_SCALING` | Appendix B; Appendix B companion | Declared scales, `K=0`, constant `C` where specified | `appendix_b_scaling_definitions_checks.wls`; dimensional-factor control | Nondimensional substitution identities only |
| `B_MOMENTUM` | Onuki (B3); Appendix B companion | Printed and dimensional-source branches kept distinct | `appendix_b_momentum_b3_checks.wls`; branch-difference control | Branch residual classification; no author-intent or code claim |
| `B_B3` | Onuki (B3); B3 factor note | Dimensional-source pressure term and Appendix-B scales | `appendix_b_b3_typo_candidate_checks.wls`; nontrivial polynomial force control | Missing-factor residual under the dimensional-source branch only |
| `B_ENERGY` | Onuki (B4)--(B6); Appendix B companion | Declared scaling and boundary hypotheses | `appendix_b_energy_boundary_checks.wls`; omitted-boundary control | Finite scaled energy/boundary identities, not global closure |
| `B_TRACE` | Onuki (B1)--(B6); Appendix B companion | The manifest's stated transition inputs | `appendix_b_transition_trace.wls`; branch-sensitive trace rows | Named intermediate Appendix-B transformations |
| `III` | Onuki (3.5)--(3.20); Section III guide | Published parameter symbols, not a numerical reproduction | `section_iii_simulation_estimates_checks.wls`; changed-scale control | Finite estimate arithmetic only |
| `KORTEWEG` | Korteweg (20); Korteweg appendix | The historical-source transcription and declared notation map | `korteweg1901_tensor_trace.wls`; sign/tensor-term control | Tensor reconstruction in the stated modern notation |
| `CROSSWALK` | Korteweg (20); Onuki (2.47)--(2.48) | Shared local tensor schema and declared coefficient map | `korteweg_onuki_crosswalk_checks.wls`; coefficient-map control | Local crosswalk components only, not historical influence or full equivalence |

## Reading a trace

The scripts print named transition IDs before their final residual. Start with
the manuscript or appendix calculation, then find the matching script in
[`../wolfram-suite-manifest.json`](../wolfram-suite-manifest.json). A
zero-residual row checks the exact finite identity stated by that transition. A
designed expected-nonzero row verifies that the named perturbation is visible;
it is not a discovery of a source error or a simulation result.

The notebook generator is deliberately small: it creates an uncached entry
point, while the committed scripts and this guide remain the canonical reader
documentation.
