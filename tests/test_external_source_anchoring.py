from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _flat(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


def test_external_anchor_map_keeps_only_audited_korteweg_formula_import() -> None:
    rows = _read_csv("research_notes/external_capillary_source_anchor_map.csv")
    assert rows
    by_id = {row["source_id"] for row in rows}
    required = {
        "dunn_serrin_1985",
        "slemrod_1983",
        "freistuehler_kotschote_2016",
        "freistuehler_kotschote_2017_arxiv",
        "kotschote_2014",
        "vdw_rowlinson_1979_external",
        "korteweg_1901_original",
    }
    assert required <= by_id
    finite_maps = [row for row in rows if row["formula_import_status"] == "FINITE_LOCAL_TENSOR_MAP"]
    assert len(finite_maps) == 1
    assert finite_maps[0]["source_id"] == "korteweg_1901_original"
    assert finite_maps[0]["anchor_type"] == "definitive_capillary_stress"
    assert all(
        row["formula_import_status"] == "NO_FORMULAS_IMPORTED"
        for row in rows
        if row not in finite_maps
    )
    korteweg = [row for row in rows if row["source_id"] == "korteweg_1901_original"]
    assert len(korteweg) >= 4
    assert {row["current_use_status"] for row in korteweg} == {
        "INSPECTED_PRIMARY_CONTEXT",
        "SOURCE_RECONSTRUCTED_T04_CROSSWALKED_T05",
    }
    assert {row["pdf_pages"] for row in korteweg} == {"24"}


def test_context_source_map_reports_only_audited_korteweg_formula_import() -> None:
    rows = _read_csv("research_notes/capillary_interstitial_working_source_map.csv")
    by_id = {row["source_id"]: row for row in rows}
    assert by_id["dunn_serrin_1985"]["page_equation_anchor_status"] == "PRELIMINARY_PAGE_ANCHORS_ADDED"
    assert by_id["slemrod_1983"]["page_equation_anchor_status"] == "PRELIMINARY_PAGE_ANCHORS_ADDED"
    assert by_id["korteweg_1901_original"]["page_equation_anchor_status"] == "COMPLETE_PAGE_IMAGE_VERIFIED"
    assert by_id["korteweg_1901_original"]["formula_import_status"] == "FINITE_LOCAL_TENSOR_MAP"
    assert all(
        row["formula_import_status"] == "NO_FORMULAS_IMPORTED"
        for row in rows
        if row["source_id"] != "korteweg_1901_original"
    )


def test_notes_and_appendix_state_formula_use_boundary() -> None:
    combined = "\n".join(
        _flat(path)
        for path in [
            "research_notes/EXTERNAL_SOURCE_ANCHORING_UPDATE.md",
            "research_notes/CAPILLARY_INTERSTITIAL_WORKING_CONTEXT.md",
            "appendices/D_crosswalk_open_issues.tex",
        ]
    )
    required = [
        "preliminary page anchors",
        "NO_FORMULAS_IMPORTED",
        "source-locked and page-image inspected",
        "cited only for contextual comparisons",
        "does not use them to derive Onuki's equations",
    ]
    for phrase in required:
        assert phrase in combined


def test_external_anchor_overclaim_phrases_absent() -> None:
    combined = "\n".join(
        _flat(path)
        for path in [
            "research_notes/EXTERNAL_SOURCE_ANCHORING_UPDATE.md",
            "research_notes/CAPILLARY_INTERSTITIAL_WORKING_CONTEXT.md",
            "research_notes/external_capillary_source_anchor_map.csv",
            "appendices/D_crosswalk_open_issues.tex",
        ]
    )
    forbidden = [
        "Onuki derives from Dunn",
        "Dunn--Serrin closes Onuki",
        "Korteweg 1901 establishes full equivalence",
        "global energy flux is closed",
        "PDE well-posedness follows",
        "historical influence established",
    ]
    for phrase in forbidden:
        assert phrase not in combined
