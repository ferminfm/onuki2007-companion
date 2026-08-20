# Reproducibility Guide

The canonical authoring source is the `Onuki2007Companion` subtree in
`ferminfm/latex`. A future `ferminfm/onuki2007-companion` repository is a
generated one-way mirror, not an independently edited fork.

## Quick start

```bash
make help
make verify-open
make manuscript
```

`make verify-open` runs the exported Python/SymPy/Pint checks and their
portable package, export, Wolfram-manifest, formal-documentation, and
clean-export regression tests.  The canonical full historical research-note
regression suite remains `bash scripts/run_verification.sh`; it is deliberately
not an input to the standalone mirror. `make
verify-wolfram` is a local optional layer that requires an installed
WolframKernel. `make verify-lean` builds the finite Mathlib kernels. None of
these commands reproduces simulations or proves the continuum model.

For a packaging check, use `make verify-source-policy` and `make
verify-clean-export`.  The latter produces two independent allowlisted staging
trees and compares their hashes.  Hosted CI covers the portable Python, Lean,
LaTeX, source-policy, and mapping layers; it deliberately does not claim to run
licensed Wolfram software.

## Deterministic export

Create a temporary standalone staging tree outside this source tree:

```bash
python3 scripts/export_standalone.py --output /tmp/onuki2007-companion-export
python3 scripts/verify_standalone_export.py --export /tmp/onuki2007-companion-export
```

The exporter writes a sorted file manifest, hashes, origin map, exclusion
report, and tree digest. It rejects unclassified tracked files, local paths,
source PDFs, generated PDFs, caches, and credentials. The generated mirror
inherits the source at the recorded commit and must not be edited directly.

## Scope

The companion documents hand derivations and finite checks. Its retained
limitations are listed in `docs/bounded-limitations.md`. The source article and
historically cited literature are not distributed here.
