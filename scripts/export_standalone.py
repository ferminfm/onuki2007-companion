#!/usr/bin/env python3
"""Create a deterministic standalone staging tree from the canonical subtree.

This tool only copies paths whose public role is recorded by T02 or by the
small repository-root scaffold declared below. It never publishes a repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


TOOL_VERSION = "1"
SCAFFOLD_PATHS = {
    ".editorconfig",
    ".gitattributes",
    ".github/workflows/verify-open.yml",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "Makefile",
    "REPRODUCIBILITY.md",
    "REUSE_STATUS.md",
    "SOURCE_USE_POLICY.md",
    "docs/bounded-limitations.md",
    "docs/canonical-sync.md",
    "docs/check-map.csv",
    "docs/environment-matrix.md",
    "docs/expected-results.json",
    "docs/reproducibility-manifest.json",
    "docs/formal-scope.md",
    "docs/formal/README.md",
    "docs/formal/theorem-index.md",
    "docs/formal/theorem-to-paper-map.csv",
    "docs/hand-calculation-standard.md",
    "docs/link-manifest.json",
    "docs/prerequisites.md",
    "docs/python-verification.md",
    "docs/verification-index.md",
    "pyproject.toml",
    "docs/wolfram-check-schema.json",
    "docs/wolfram-suite-manifest.json",
    "scripts/export_standalone.py",
    "scripts/generate_manuscript_link_macros.py",
    "scripts/verify_formal_project.sh",
    "scripts/verify_clean_clone.sh",
    "scripts/reproduce_clean_export.sh",
    "scripts/verify_public_source_policy.py",
    "scripts/verify_standalone_export.py",
    "scripts/wolfram/generate_literate_notebook.wl",
    "tests/test_standalone_export.py",
    "tests/test_python_package_cli.py",
    "tests/test_formal_reproducibility.py",
    "tests/test_clean_clone_reproducibility.py",
    "tests/test_wolfram_literate_manifest.py",
    "tests/test_manuscript_verification_links.py",
}
SCAFFOLD_PREFIXES = ("docs/topics/", "docs/wolfram/", "src/onuki2007_companion/")
POST_INVENTORY_LOCAL_ONLY = {
    "research_notes/REPRODUCIBLE_REPOSITORY_BOUNDED_GAP_LEDGER.md",
    "research_notes/REPRODUCIBLE_REPOSITORY_ROADMAP.md",
    "research_notes/reproducible_repository_bounded_gap_ledger.csv",
    "research_notes/standalone_public_export_inventory.csv",
    "research_notes/standalone_public_export_manifest.yaml",
    "research_notes/STANDALONE_REPOSITORY_SCAFFOLD_QA.md",
    "research_notes/WOLFRAM_MATHEMATICA_REPRODUCIBILITY_QA.md",
    "research_notes/PYTHON_REPRODUCIBILITY_QA.md",
    "research_notes/LEAN_MATHLIB_REPRODUCIBILITY_QA.md",
    "research_notes/CLEAN_CLONE_REPRODUCIBILITY_QA.md",
    "research_notes/MANUSCRIPT_VERIFICATION_LINK_QA.md",
    "research_notes/REPRODUCIBLE_REPOSITORY_RESUME.md",
}


def run_git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_inventory(root: Path) -> dict[str, str]:
    inventory = root / "research_notes" / "standalone_public_export_inventory.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        return {row["path"]: row["export_status"] for row in csv.DictReader(stream)}


def selected_paths(root: Path) -> list[str]:
    roles = role_inventory(root)
    tracked = set(run_git(root, "ls-files").splitlines())
    scaffold = SCAFFOLD_PATHS | {path for path in tracked if path.startswith(SCAFFOLD_PREFIXES)}
    unclassified = tracked - set(roles) - scaffold - POST_INVENTORY_LOCAL_ONLY
    if unclassified:
        raise SystemExit("unclassified tracked files: " + ", ".join(sorted(unclassified)))
    selected = {path for path, role in roles.items() if role == "include_or_generate"}
    selected |= scaffold
    forbidden = [
        path
        for path in selected
        if path.endswith(".pdf")
        or path.startswith(("generated/", "research_notes/"))
        or "/.lake/" in path
    ]
    if forbidden:
        raise SystemExit("forbidden public export paths: " + ", ".join(sorted(forbidden)))
    return sorted(selected)


def export(root: Path, output: Path, allow_dirty: bool) -> None:
    if output.resolve() == root.resolve() or root.resolve() in output.resolve().parents:
        raise SystemExit("output must be outside the canonical source tree")
    if output.exists() and any(output.iterdir()):
        raise SystemExit("output directory must be absent or empty")
    status = run_git(root, "status", "--porcelain")
    if status and not allow_dirty:
        raise SystemExit("canonical source is dirty; commit or use --allow-dirty for a local preview")
    output.mkdir(parents=True, exist_ok=True)
    files = selected_paths(root)
    rows = []
    for rel in files:
        source = root / rel
        if not source.is_file():
            raise SystemExit(f"declared export file is missing: {rel}")
        destination = output / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        rows.append({"path": rel, "sha256": sha256(source), "origin": rel})
    metadata = output / ".standalone"
    metadata.mkdir()
    tree_digest = hashlib.sha256(
        "".join(f"{row['sha256']}  {row['path']}\n" for row in rows).encode()
    ).hexdigest()
    metadata.joinpath("file-manifest.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metadata.joinpath("origin-map.json").write_text(
        json.dumps({row["path"]: row["origin"] for row in rows}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    metadata.joinpath("export-metadata.json").write_text(
        json.dumps(
            {
                "canonical_repository": "ferminfm/latex",
                "canonical_subtree": "papers/edu/Onuki2007Companion",
                "source_commit": run_git(root, "rev-parse", "HEAD"),
                "source_tree_dirty": bool(status),
                "export_tool_version": TOOL_VERSION,
                "file_count": len(rows),
                "tree_digest": tree_digest,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    metadata.joinpath("exclusion-report.json").write_text(
        json.dumps(
            {
                "excluded_count": len(role_inventory(root)) - len(rows),
                "policy": "T02 export inventory plus explicit public scaffold allowlist",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"EXPORT_OK files={len(rows)} digest={tree_digest}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    export(Path(__file__).resolve().parents[1], args.output, args.allow_dirty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
