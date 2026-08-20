# Appendix E: Korteweg Crosswalk

The hand calculation in `appendices/E_korteweg_primary_source_crosswalk.tex`
reconstructs finite component relations from the inspected Korteweg source and
states the conditional local comparison with Onuki.

Run `python3 scripts/python/korteweg_onuki_crosswalk_sympy.py`; finite Lean
kernels are documented in `docs/formal/theorem-index.md`. The mixed-gradient
residual is the negative control. The crosswalk does not establish historical
influence, full tensor equality, a global balance, or model equivalence.
