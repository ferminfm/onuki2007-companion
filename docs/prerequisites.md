# Prerequisites

Required for the open verification subset: Python 3, `pytest`, `sympy`, and
`pint`. Install the declared reader environment with
`python -m pip install -e '.[dev]'`; this exposes `onuki2007-check` without
changing the legacy script paths. Required for the manuscript: a PDFLaTeX and BibTeX compatible LaTeX
installation. Required for the finite formal project: Lean and Lake matching
`formal/korteweg1901_mathlib/lean-toolchain`.

WolframKernel is optional for a complete local symbolic run. Hosted CI must not
claim Wolfram execution unless a separately configured licensed kernel exists.
No command requires a source PDF, network fetch, or a parent repository path.
