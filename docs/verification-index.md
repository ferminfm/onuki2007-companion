# Verification Index

Start with the hand derivation in the companion text. Then select a topic below
and run its executable mirror from the repository root.

| Topic | Primary scripts | Check scope |
|---|---|---|
| local van der Waals baseline | `scripts/python/section_iia_vdw_baseline_sympy.py`, `scripts/wolfram/section_iia_vdw_baseline_checks.wls` | finite thermodynamic algebra |
| portable Python command index | `pyproject.toml`, `src/onuki2007_companion/`, `docs/python-verification.md` | stable check IDs, topic runs, and finite scope descriptions |
| gradient entropy and energy | `scripts/python/section_iib_gradient_entropy_sympy.py`, `scripts/wolfram/section_iib_gradient_entropy_checks.wls` | variations and boundary-term signs |
| equilibrium and wall branch | `scripts/python/section_iic_equilibrium_wall_sympy.py`, `scripts/wolfram/section_iic_equilibrium_wall_checks.wls` | selected local and boundary identities |
| hydrodynamic bookkeeping | `scripts/python/section_iid_hydrodynamic_balance_sympy.py`, `scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls` | finite energy and entropy bookkeeping |
| scaled Appendix B | `scripts/python/appendix_b_b3_typo_candidate_sympy.py`, `scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls` | dimensional-source scaling and negative control |
| Korteweg comparison | `scripts/python/korteweg_onuki_crosswalk_sympy.py`, `formal/korteweg1901_mathlib/` | finite tensor kernels only; see `docs/formal/theorem-index.md` |

Run `make verify-open` for the open Python test layer, `make verify-wolfram`
for local symbolic traces, and `make verify-lean` for the finite formal layer.
`bash scripts/verify_formal_project.sh` additionally audits prohibited formal
placeholders before rebuilding the pinned project.
See `docs/hand-calculation-standard.md` and `docs/formal-scope.md` before
interpreting a passing result.
