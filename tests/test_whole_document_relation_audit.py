from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "research_notes/equation_relation_provenance_matrix.csv"
QUEUE = ROOT / "research_notes/equation_relation_repair_queue.csv"
REPORT = ROOT / "research_notes/WHOLE_DOCUMENT_RELATION_AUDIT.md"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_task05_report_exists_and_records_residual_scope() -> None:
    text = REPORT.read_text()
    assert "Whole-Document Equation Relation Provenance Audit" in text
    assert "07_literature_source_anchoring" in text
    assert "09_bounded_discrepancy_audit" in text
    assert "official-erratum" in text


def test_task02_rows_are_closed_by_whole_document_review() -> None:
    queue = _rows(QUEUE)
    task02_rows = [
        row for row in queue
        if row["repair_task"] == "02_iia_coexistence_surface_tension"
        and row["bounded_gap"] != "yes"
    ]
    assert task02_rows
    assert {row["queue_status"] for row in task02_rows} == {"CLOSED_TASK05"}
    for row in task02_rows:
        assert row["code_check_status"] == "CODE_PATH_RECORDED"
        assert "section_iia_vdw_baseline_sympy.py" in row["code_paths"]


def test_residual_open_queue_is_closed_after_task09() -> None:
    open_rows = [row for row in _rows(QUEUE) if row["queue_status"].startswith("OPEN")]
    assert open_rows == []


def test_bounded_discrepancies_remain_bounded_after_task05() -> None:
    matrix = {row["relation_id"]: row for row in _rows(MATRIX)}
    for relation_id in ["DISC:Eq2_5_Eq3_9", "DISC:B3Phi", "SRC:APPB-B3"]:
        row = matrix[relation_id]
        assert row["bounded_gap"] == "yes"
        assert "09_bounded_discrepancy_audit" in row["repair_task"]
        assert "FULL_EQUIVALENCE" not in row["provenance_status"]
