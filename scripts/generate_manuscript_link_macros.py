#!/usr/bin/env python3
"""Generate tag-pinned manuscript link macros from docs/link-manifest.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "generated" / "manuscript_verification_links.tex",
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / "docs" / "link-manifest.json").read_text(encoding="utf-8"))
    base = f"https://github.com/{manifest['repository']}"
    tag = manifest["tag"]
    lines = [
        "% Generated from docs/link-manifest.json; do not edit manually.",
        f"\\newcommand{{\\OnukiVerificationRepositoryURL}}{{{base}}}",
        f"\\newcommand{{\\OnukiVerificationTag}}{{\\texttt{{{tag}}}}}",
        "\\newcommand{\\OnukiVerificationRepository}{\\url{\\OnukiVerificationRepositoryURL}}",
    ]
    for topic in manifest["topics"]:
        url = f"{base}/blob/{tag}/{topic['source']}"
        lines.append(f"\\newcommand{{\\{topic['macro']}}}[1]{{\\href{{{url}}}{{#1}}}}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"MANUSCRIPT_LINK_MACROS_OK topics={len(manifest['topics'])} tag={tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
