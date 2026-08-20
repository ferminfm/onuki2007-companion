from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "research_notes/equation_relation_provenance_matrix.csv"
QUEUE = ROOT / "research_notes/equation_relation_repair_queue.csv"
FINAL_QA = ROOT / "research_notes/PROVENANCE_READABILITY_FINAL_QA.md"
HANDOFF = ROOT / "research_notes/PROVENANCE_READABILITY_LAYER1_HANDOFF.md"
PROMPT = ROOT / "research_notes/LAYER1_PROVENANCE_READABILITY_REVIEW_PROMPT.txt"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_final_qa_artifacts_exist_and_state_bounded_gaps() -> None:
    for path in [FINAL_QA, HANDOFF, PROMPT]:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        assert "B3" in text
        assert "Eq. (2.5)/(3.9)" in text
        assert "Korteweg 1901" in text
        assert "unpublished" in text
        assert "numerical" in text.lower()


def test_repair_queue_is_closed_after_task09() -> None:
    rows = _rows(QUEUE)
    assert rows
    assert [row for row in rows if row["queue_status"].startswith("OPEN")] == []


def test_no_ambiguous_review_required_statuses_remain() -> None:
    rows = _rows(MATRIX)
    forbidden = {"TEXT_LOGIC_REVIEW_REQUIRED", "CODE_REVIEW_REQUIRED"}
    for row in rows:
        assert row["derivation_logic_status"] not in forbidden, row["relation_id"]
        assert row["code_check_status"] not in forbidden, row["relation_id"]


def test_bounded_discrepancy_and_context_rows_are_explicit() -> None:
    matrix = {row["relation_id"]: row for row in _rows(MATRIX)}
    for relation_id in ["DISC:Eq2_5_Eq3_9", "DISC:B3Phi", "SRC:APPB-B3"]:
        row = matrix[relation_id]
        assert row["provenance_status"] == "BOUNDED_DISCREPANCY_PAGE_AUDITED_TASK09"
        assert row["bounded_gap"] == "yes"
    for relation_id in [
        "SRC:APPB-EULER",
        "SRC:IIIA-2D-LATTICE",
        "SRC:IIIA-T-BC",
        "SRC:REF59-DISCRETIZATION",
        "SRC:IIB-SIM-SPEC",
        "SRC:CONCL-LANGEVIN",
    ]:
        row = matrix[relation_id]
        assert row["derivation_logic_status"] == "SOURCE_CONTEXT_OR_ASSUMPTION_ROW_NO_DERIVATION_REQUIRED"
        assert row["code_check_status"] == "NO_FINITE_CHECK_SOURCE_CONTEXT_ROW"
