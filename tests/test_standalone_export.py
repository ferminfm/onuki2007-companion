from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_export_self_check() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/verify_standalone_export.py", "--self-check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "EXPORT_SELF_CHECK_OK" in result.stdout
