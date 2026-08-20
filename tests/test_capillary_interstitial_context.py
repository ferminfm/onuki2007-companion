from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _flat(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


def test_context_note_keeps_sources_as_future_work_only() -> None:
    text = _flat("research_notes/CAPILLARY_INTERSTITIAL_WORKING_CONTEXT.md")
    required = [
        "does not reinterpret Onuki's equations",
        "preliminary page anchors",
        "NO_FORMULAS_IMPORTED",
        "Direct Korteweg 1901 is source-locked and page-image inspected",
        "They do not supply an Onuki total-energy-flux closure",
    ]
    for phrase in required:
        assert phrase in text


def test_context_source_map_preserves_bounded_korteweg_formula_boundary() -> None:
    with (ROOT / "research_notes/capillary_interstitial_working_source_map.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["source_id"]: row for row in rows}
    assert by_id["dunn_serrin_1985"]["page_equation_anchor_status"] == "PRELIMINARY_PAGE_ANCHORS_ADDED"
    assert by_id["dunn_serrin_1985"]["formula_import_status"] == "NO_FORMULAS_IMPORTED"
    assert by_id["korteweg_1901_original"]["local_status"] == "SOURCE_ATTACHMENT_VERIFIED"
    assert by_id["korteweg_1901_original"]["page_equation_anchor_status"] == "COMPLETE_PAGE_IMAGE_VERIFIED"
    assert by_id["korteweg_1901_original"]["formula_import_status"] == "FINITE_LOCAL_TENSOR_MAP"
    assert all(
        row["formula_import_status"] == "NO_FORMULAS_IMPORTED"
        for row in rows
        if row["source_id"] != "korteweg_1901_original"
    )


def test_open_issues_appendix_mentions_context_without_formula_import() -> None:
    text = _flat("appendices/D_crosswalk_open_issues.tex")
    assert "External capillarity and interstitial-working context" in text
    assert "cited only for contextual comparisons" in text
    assert "does not use them to derive Onuki's equations" in text
    assert "direct Korteweg 1901 source is now page-image" in text


def test_no_external_context_overclaims() -> None:
    combined = "\n".join(
        _flat(path)
        for path in [
            "research_notes/CAPILLARY_INTERSTITIAL_WORKING_CONTEXT.md",
            "appendices/D_crosswalk_open_issues.tex",
        ]
    )
    forbidden = [
        "Onuki derives from Dunn",
        "Dunn--Serrin closes Onuki",
        "Korteweg 1901 establishes full equivalence",
        "global energy flux is closed",
        "PDE well-posedness follows",
    ]
    for phrase in forbidden:
        assert phrase not in combined
