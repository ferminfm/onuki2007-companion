from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_korteweg_provenance_matrix_is_closed_and_page_anchored() -> None:
    rows = _rows("research_notes/korteweg_primary_source_provenance_matrix.csv")
    assert len(rows) == 20
    assert all(row["source_anchor"] for row in rows)
    assert all(row["page_image_status"] for row in rows)
    assert all(row["final_status"].startswith("CLOSED_") for row in rows)


def test_t07_repair_queue_has_no_open_row() -> None:
    rows = _rows("research_notes/korteweg_primary_source_repair_queue.csv")
    assert rows
    assert {row["status"] for row in rows} == {"CLOSED"}


def test_onuki_crosswalk_uses_page_four_for_pressure_tensor_rows() -> None:
    rows = {row["row_id"]: row for row in _rows("research_notes/korteweg_onuki_equation_crosswalk.csv")}
    for row_id in ("KOX-002", "KOX-003", "KOX-004", "KOX-005", "KOX-006", "KOX-007"):
        assert "036304-4" in rows[row_id]["onuki_anchor"]
    assert rows["KOX-011"]["onuki_anchor"].endswith("036304-4")
    assert rows["KOX-014"]["boundary_status"] == "UNPUBLISHED_CODE_UNRESOLVED"


def test_public_korteweg_context_has_exact_static_and_thin_layer_anchors() -> None:
    appendix = _text("appendices/E_korteweg_primary_source_crosswalk.tex")
    assert "(57)--(58)" in appendix
    assert "printed page 17" in appendix
    assert "pages 23--24" in appendix
    assert "restricted structural comparisons" in appendix


def test_every_public_korteweg_wolfram_script_has_complete_trace() -> None:
    rows = _rows("research_notes/korteweg_wolfram_trace_classification.csv")
    assert len(rows) == 2
    assert {row["classification"] for row in rows} == {"BLACKBOARD_TRACE_COMPLETE"}
    assert {row["status"] for row in rows} == {"PASS"}
    for row in rows:
        assert (ROOT / row["script"]).is_file()
        assert (ROOT / row["sympy_mirror"]).is_file()
        for field in ("anchor", "input", "transformation", "assumptions", "output", "residual", "status"):
            assert field in row["trace_fields"]

    crosswalk = _text("scripts/wolfram/korteweg_onuki_crosswalk_checks.wls")
    for token in ("recordStep", '"KO01"', '"KO11"', "traceHeaders", "premise", "transformation"):
        assert token in crosswalk


def test_lean_theorem_map_matches_built_module_and_has_no_placeholders() -> None:
    rows = _rows("research_notes/korteweg_lean_theorem_to_paper_map.csv")
    lean = _text("formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean")
    assert len(rows) == 8
    for row in rows:
        assert f'theorem {row["theorem_name"]}' in lean
        assert row["build_status"] == "BUILD_PASS"
        assert row["scope_limit"]
    assert not re.search(r"\b(sorry|admit)\b", lean)
    assert not re.search(r"(?m)^\s*axiom\s", lean)


def test_public_formal_and_trace_claims_are_bounded_and_exact() -> None:
    public = _text("appendices/C_verification_plan.tex") + _text(
        "appendices/E_korteweg_primary_source_crosswalk.tex"
    )
    assert "KO01--KO11" in public
    assert "complete transition rows" in public or "explicit transition traces" in public
    assert "formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean" in public
    assert "do not prove a continuum PDE" in public


def test_tensor_map_does_not_encode_historical_influence_or_full_equality() -> None:
    figure = _text("figures/tikz/korteweg_onuki_tensor_map.tex")
    appendix = _text("appendices/E_korteweg_primary_source_crosswalk.tex")
    assert r"\draw[arrow] (k) -- (schema)" in figure
    assert r"\draw[arrow] (o) -- (schema)" in figure
    assert r"\draw[darrow] (schema) -- (restricted)" in figure
    assert "historical influence nor unrestricted equality" in appendix
    assert "full-PDE" in appendix or "continuum PDE" in appendix


def test_bounded_onuki_discrepancies_remain_separate() -> None:
    audit = _text("research_notes/KORTEWEG_PRIMARY_SOURCE_PROVENANCE_AUDIT.md")
    assert "typographical omission only under the dimensional-source" in audit
    assert "No official erratum" in audit
    assert "Eqs. (2.5)/(3.9)" in audit
    assert "unpublished simulation-code branch remains unresolved" in audit
