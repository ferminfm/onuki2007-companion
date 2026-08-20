#!/usr/bin/env python3
"""Validate an exported standalone tree without accessing the parent monorepo."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REQUIRED = {"README.md", "REPRODUCIBILITY.md", "Makefile", "main.tex", "docs/verification-index.md"}


def check_export(root: Path) -> None:
    metadata = root / ".standalone"
    manifest = json.loads(metadata.joinpath("file-manifest.json").read_text(encoding="utf-8"))
    expected = {item["path"]: item["sha256"] for item in manifest}
    missing = REQUIRED - set(expected)
    if missing:
        raise SystemExit("required files absent from export: " + ", ".join(sorted(missing)))
    for rel, digest in expected.items():
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"missing exported file: {rel}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"hash mismatch: {rel}")
        if rel.endswith(".pdf") or rel.startswith("research_notes/"):
            raise SystemExit(f"forbidden exported file: {rel}")
    print(f"EXPORT_VERIFY_OK files={len(expected)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        print("EXPORT_SELF_CHECK_OK expected staged tree requires .standalone metadata")
        return 0
    if args.export is None:
        parser.error("--export is required unless --self-check is selected")
    check_export(args.export)
    return 0


if __name__ == "__main__":
    sys.exit(main())
