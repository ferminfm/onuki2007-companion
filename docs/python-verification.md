# Python Verification Reader Guide

The Python layer mirrors finite hand calculations with SymPy and checks selected
dimensions with Pint. It is installed as a small package so a reader can list
and run the existing transparent scripts without discovering local paths.

## Fresh Environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
onuki2007-check list
onuki2007-check topic section-iid
onuki2007-check dimensions
python -m pytest -q tests/test_python_package_cli.py
```

`onuki2007-check run b-b3` runs the B3 dimensional-source scaling check, and
`onuki2007-check show b-b3` prints its topic, source script, and finite scope.
The complete `onuki2007-check python-all` route runs the public Python scripts
in a stable manifest order.

## Topics and Limits

The CLI IDs cover the local van der Waals baseline, gradient and wall terms,
reversible stress, hydrodynamic balance bookkeeping, Appendix-B scaling,
Section-III estimates, and the bounded Korteweg crosswalk. Expected-nonzero
controls are deliberately changed finite inputs: they verify that a named
factor, sign, or premise matters. They do not prove author intent, unpublished
simulation behavior, a physical model, continuum well-posedness, or full model
equivalence.

The original `scripts/python/*.py` files remain the primary reader-visible
implementations. The package adds a portable index and command interface; it
does not hide or replace their mathematical expressions.

The canonical repository's full test suite additionally checks private
research-note ledgers and source-audit records that are intentionally excluded
from the standalone mirror. Run that complete suite in the canonical repository.
The standalone gate is the package CLI test plus the exposed finite scripts.
The `scaffold` check is consequently labelled `canonical_only`; it is visible
for traceability but is not included in `python-all`.

Some finite scripts add a stronger canonical-ledger regression after their
algebra. When that ledger is absent from the standalone mirror, they report
`SKIPPED_CANONICAL_LEDGER` and retain the finite result; the corresponding
canonical invocation still requires the ledger and preserves the stronger check.
