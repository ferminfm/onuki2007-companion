# Section II.D: Balances and Entropy Bookkeeping

`sections/02d_hydrodynamic_equations.tex` derives the local mass, momentum,
total/internal-energy, and entropy bookkeeping associated with Onuki
Eqs. (2.35)--(2.53). It separates balances, constitutive inputs, local fluxes,
and boundary-dependent integrated statements.

Run `python3 scripts/python/section_iid_hydrodynamic_balance_sympy.py` and the
matching Wolfram trace. Omitting the reversible entropy flux is the key negative
control. Passing finite checks does not prove the second law, a continuum PDE,
or the global wall-transfer map.
