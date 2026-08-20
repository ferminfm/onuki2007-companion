# Korteweg 1901 finite Mathlib kernels

This pinned target-local project checks eight finite algebraic and logical
kernels used by the modern tensor reconstruction. It does not formalize a
continuum field, Korteweg PDE, boundary-value problem, constitutive law, or
Onuki equivalence.

From this formal-project directory, build with:

```bash
lake build
```

From the repository root, `bash scripts/verify_formal_project.sh` runs the same
build and scans for `sorry`, `admit`, and custom `axiom`
declarations before rebuilding. `lean-toolchain` pins Lean 4.29.0 and
`lake-manifest.json` pins Mathlib. Reader-facing declarations, hand proofs,
and scope limits are in `docs/formal/theorem-index.md`.
