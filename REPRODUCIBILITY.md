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

For a public-tree check, use `make verify-source-policy`.  The canonical source
repository alone runs `make verify-clean-export`: that operation needs its
non-public export inventory to construct two independent allowlisted staging
trees and compare their hashes.  Hosted CI covers the standalone portable
Python, Lean, LaTeX, source-policy, and mapping layers; it deliberately does
not claim to run licensed Wolfram software.

After cloning the standalone repository, run `bash scripts/verify_clean_clone.sh`.
The runner validates export metadata when it is present in a local staging tree;
in a fresh Git clone that intentionally excludes `.standalone/`, it instead
checks the Git-tree mode before running the same portable source-policy, Python,
Lean, and LaTeX gates.

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
