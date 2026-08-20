"""Regression checks for T07's public-export and CI interface."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reproducibility_manifest_declares_open_and_local_layers() -> None:
    data = json.loads((ROOT / "docs/reproducibility-manifest.json").read_text(encoding="utf-8"))
    assert "make verify-open" in data["portable_gates"]
    assert data["local_optional_gate"]["command"] == "make verify-wolfram"
    assert "continuum-model validity" in data["scope_limit"]


def test_make_help_explains_portable_and_licensed_layers() -> None:
    result = subprocess.run(["make", "help"], cwd=ROOT, text=True, capture_output=True, check=True)
    assert "WolframKernel is a licensed local optional layer" in result.stdout
    assert "verify-clean-export" in result.stdout


def test_source_policy_and_export_self_check() -> None:
    policy = subprocess.run(
        [sys.executable, "scripts/verify_public_source_policy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PUBLIC_SOURCE_POLICY_OK" in policy.stdout
