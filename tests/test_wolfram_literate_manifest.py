from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_literate_manifest_covers_the_fourteen_wolfram_suites() -> None:
    manifest = json.loads((ROOT / "docs/wolfram-suite-manifest.json").read_text())
    suites = manifest["suites"]
    assert manifest["suite_count"] == 14
    assert len(suites) == 14
    assert len({suite["id"] for suite in suites}) == 14
    for suite in suites:
        assert (ROOT / suite["script"]).is_file()
        assert suite["anchor"]


def test_literate_reader_keeps_finite_scope() -> None:
    text = (ROOT / "docs/wolfram/README.md").read_text().lower()
    assert "expected-nonzero" in text
    assert "erratum" in text
    assert "not" in text and "simulation" in text


def test_suite_guide_gives_each_suite_a_reader_facing_scope() -> None:
    guide = (ROOT / "docs/wolfram/suite-guide.md").read_text()
    manifest = json.loads((ROOT / "docs/wolfram-suite-manifest.json").read_text())
    for suite in manifest["suites"]:
        assert f"`{suite['id']}`" in guide
        assert f"`{Path(suite['script']).name}`" in guide
    assert "not historical influence or full equivalence" in guide
