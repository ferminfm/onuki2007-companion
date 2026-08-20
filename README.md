# Onuki 2007 Guided Derivation Companion

This directory is an original guided-derivation companion for Akira Onuki's 2007
Physical Review E paper on dynamic van der Waals theory.

The original paper is required reading. This companion does not reproduce the
paper and does not replace it. It uses Onuki's section order and equation
numbers as navigation aids, then provides original derivations, notation
crosswalks, assumptions, boundary branches, and finite verification checks.

Companion coverage: Section II.A derives the local van der Waals thermodynamic
baseline, coexistence conditions, interface profile, and surface-tension
identity used by the later sections. Section II.B contains an original
derivation guide for the gradient entropy/energy functionals, the relation
`M=CT+K`, the generalized chemical-potential variation, and the entropy
variation boundary term. Section II.C covers equilibrium conditions,
the one-dimensional interface branch, surface tension, and the natural wall
density boundary condition. Section II.D covers the local hydrodynamic
balance-law, energy, entropy-production, pressure-tensor, diagonal
gradient-pressure, local flux-gauge, and boundary-dependent global-entropy
bookkeeping. Appendix A derives the reversible stress tensor from virtual
displacement and records the stress-divergence sign convention. Appendix B
now records the scaling definitions, the scaled continuity and momentum
bookkeeping, and the printed-versus-dimensional-source B3 pressure-tensor
branches. It also derives the scaled total-energy density, local energy
equation, and density boundary condition in Appendix B, while keeping global
wall/surface transfer separate. The unpublished simulation-code branch remains
unresolved.
Section III now gives a simulation reading guide for method assumptions, finite estimates, and scenario boundaries without numerical reproduction. Later final-summary material remains navigational.
Appendix E records an inspected-primary-source reconstruction of Korteweg's
1901 capillary stress and a conditional local tensor crosswalk to Onuki.  It
keeps the source transcription, modern notation, constitutive assumptions,
nonisothermal residual, and non-equivalent energy/entropy/wall objects separate.

## Source-Use Policy

* Equations are cited by source number, not copied as a substitute for the
  source.
* Quotations are avoided except for minimal bibliographic or equation-label
  references.
* Explanatory prose is original and written as a study guide.
* Any future derivation must reconstruct the calculations independently and cite
  the source equation numbers being explained.
* Source PDFs remain local and untracked; the Korteweg attachment is identified
  by the source-lock ledger rather than copied into this project.

## Source Access

Source PDFs are local-only and are not distributed with this repository.  The
companion records source equation and page anchors in its research ledgers;
readers should consult legally obtained copies of the cited article and book.
Machine-local attachment locations are intentionally excluded from this public
README because they are not portable coauthor instructions.

The companion bibliography is:

* `references/onuki2007_companion.bib`

## Build

```bash
bash scripts/build.sh
```

The generated `main.pdf` is ignored by Git.

## Portable Repository Layer

`REPRODUCIBILITY.md` explains the canonical-source and generated-mirror model.
The reader-facing verification index is `docs/verification-index.md`; concise
tool prerequisites and finite-proof limits are in `docs/`. The root `Makefile`
offers stable commands for the open verification subset, local Wolfram layer,
Lean kernels, manuscript build, and deterministic export. `REUSE_STATUS.md`
records that no reuse license has been selected.

## Derivation Policy

Future derivation passes should follow `research_notes/COMPANION_DERIVATION_PROOF_POLICY.md` and update `research_notes/onuki_companion_section_proof_checklist.csv` when a section changes status.

## Verification

```bash
bash scripts/run_verification.sh
```

The current verification layer checks companion integrity and finite Section
II.A/II.B/II.C/II.D, Appendix A, Appendix B, and Section III estimate identities with
SymPy, Pint, pytest, and Wolfram when available.  A target-local Mathlib project
checks finite component and implication kernels for the Korteweg reconstruction;
it does not prove a continuum equation or model equivalence.  Maxima may be
added later for selected scalar third-witness checks.

For a script-by-script index, see
`research_notes/onuki_companion_code_to_paper_map.csv`. It records each
verification script, the companion section and source-equation anchors it
supports, the generated summary path when applicable, and the proof-scope
limit. This code-to-paper map is the public index. Two specialized row indexes,
`research_notes/visible_derivation_code_to_equation_map.csv` and
`research_notes/source_fidelity_code_to_equation_map.csv`, record the public
derivation links and the highest-risk source-fidelity checks. The scripts check
finite identities and regressions only; they do not reproduce simulations or
prove the physical model.

## Coauthor Review Package

Start with `research_notes/COAUTHOR_READING_GUIDE.md`.  It gives a short
reading order and links the source-equation and verification navigation sheets.
The package keeps the dimensional-source, printed-B3, and unpublished-code
questions separate; it also keeps local flux identities distinct from global
wall and boundary transfer.  Numerical reproduction remains outside the scope
of this companion.
