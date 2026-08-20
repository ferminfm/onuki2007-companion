# Environment Matrix

| Layer | Entry point | Expected result | Scope limit |
|---|---|---|---|
| Python | `make verify-open` | deterministic finite residual and regression checks | no continuum or numerical validation |
| Wolfram | `make verify-wolfram` | transition traces and negative controls | local licensed tool only |
| Lean | `make verify-lean` | pinned finite kernel build | no PDE or constitutive proof |
| LaTeX | `make manuscript` | `main.pdf` | source document build only |
| Export | `make export OUT=...` | manifest, hashes, origin map | staging tree, not remote publication |
