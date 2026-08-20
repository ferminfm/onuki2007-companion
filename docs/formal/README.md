# Finite Lean and Mathlib Checks

This directory explains the target-local Lean project at
`formal/korteweg1901_mathlib/`. It checks finite algebraic or logical kernels
used in the Korteweg--Onuki tensor reconstruction. It is not a formalization of
a continuum field, balance law, boundary-value problem, constitutive law,
second law, PDE, or physical-model equivalence.

## Quick Start

The pinned compiler is declared in `formal/korteweg1901_mathlib/lean-toolchain`.
With Lean and Lake available, run either command from the repository root:

```bash
make verify-lean
bash scripts/verify_formal_project.sh
```

The second command builds the project and performs a source-level placeholder
and custom-axiom audit. The lockfile records the exact Mathlib revision used by
Lake.

## Reading the Theorems

`theorem-index.md` gives every public theorem's exact declaration, hypotheses in
mathematical language, a hand proof, companion anchor, and scope limit. Read it
with the displayed derivations in Appendices C and E. The code checks a finite
final step after the hand derivation has supplied field definitions, product
rules, boundary assumptions, and physical interpretation.

`theorem-to-paper-map.csv` supplies the same anchors and scope limits in a
portable machine-readable form.
