# Wolfram Trace Reader

The fourteen `.wls` suites are executable companions to visible derivation
steps. Run them from the repository root with `make verify-wolfram` or the
individual `WolframKernel -script` command listed in the suite manifest.

Each topic page names the source and companion anchor, premises, assumptions,
trace and negative-control IDs, expected residual class, and scope limit. Read
the hand calculation first; the compact per-suite entries are in
[`suite-guide.md`](suite-guide.md). A symbolic pass establishes only the displayed
finite algebraic or component identity under the named assumptions.

`scripts/wolfram/generate_literate_notebook.wl` writes a small uncached
Mathematica notebook expression from the committed suite manifest. It has no
hidden initialization, local paths, or source-document content; evaluate cells
top to bottom in a fresh kernel.

Designed expected-nonzero controls are sensitivity checks. They demonstrate that
an altered sign, factor, branch, or omitted premise is detectable; they are not
evidence of an erratum, author intent, implementation behavior, simulation
behavior, or a physical-model failure.
