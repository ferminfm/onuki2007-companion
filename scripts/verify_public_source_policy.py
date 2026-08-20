#!/usr/bin/env python3
"""Check public-export hygiene from the canonical companion checkout.

This is a repository-policy check, not a scientific verifier.  It rejects
tracked source PDFs, generated PDFs, common credentials, and build caches so a
clean export cannot depend on private or machine-local material.
"""

from __future__ import annotations

import re
import subprocess
import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATH = re.compile(r"(^|/)(generated|\.lake|\.venv|__pycache__)(/|$)|\.pdf$|\.(aux|log|bbl|blg)$")
SECRET = re.compile(r"(BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|WOLFRAM_APP_ID\s*=)")


def tracked_files() -> list[Path]:
    if subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).returncode == 0:
        output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
        return [ROOT / item for item in output.splitlines()]
    manifest = ROOT / ".standalone" / "file-manifest.json"
    if not manifest.is_file():
        raise SystemExit("requires a Git checkout or an exported .standalone/file-manifest.json")
    return [ROOT / item["path"] for item in json.loads(manifest.read_text(encoding="utf-8"))]


def main() -> int:
    violations: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        if FORBIDDEN_PATH.search(relative):
            violations.append(f"forbidden tracked path: {relative}")
            continue
        if path.is_file() and SECRET.search(path.read_text(encoding="utf-8", errors="ignore")):
            violations.append(f"possible secret in tracked text: {relative}")
    if violations:
        raise SystemExit("\n".join(violations))
    print("PUBLIC_SOURCE_POLICY_OK tracked_files=" + str(len(tracked_files())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
