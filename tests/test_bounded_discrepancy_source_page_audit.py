from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> dict[str, dict[str, str]]:
    with (ROOT / path).open(newline="") as handle:
        return {row["relation_id"]: row for row in csv.DictReader(handle)}


def test_task09_audit_note_records_source_pages_and_caveats() -> None:
    note = (ROOT / "research_notes/TASK09_BOUNDED_DISCREPANCY_SOURCE_PAGE_AUDIT.md").read_text()
    assert "Eq. (2.5)" in note and "036304-2" in note
    assert "Eq. (3.9)" in note and "036304-7" in note
    assert "Eq. (B3)" in note and "036304-14" in note
    assert "Eqs. (2.47)--(2.48)" in note and "036304-4" in note
    for phrase in [
        "not a formal erratum",
        "does not claim an official erratum",
        "author intent",
        "unpublished simulation-code behavior",
        "No numerical reproduction is opened",
    ]:
        assert phrase in note


def test_open_bounded_discrepancy_rows_are_closed_by_task09() -> None:
    queue = _rows("research_notes/equation_relation_repair_queue.csv")
    for relation_id in [
        "DISC:Eq2_5_Eq3_9",
        "SRC:APPB-B3",
        "TEX:eq:appb-source-consistent-b3",
        "TEX:eq:appb-printed-b3-branch",
        "TEX:eq:appb-b3-branch-residual",
        "DISC:B3Phi",
    ]:
        row = queue[relation_id]
        assert row["queue_status"] == "CLOSED_TASK09_PAGE_AUDITED"
        assert row["provenance_status"] == "BOUNDED_DISCREPANCY_PAGE_AUDITED_TASK09"
        assert row["bounded_gap"] == "yes"


def test_page_anchors_are_recorded_for_discrepancy_rows() -> None:
    matrix = _rows("research_notes/equation_relation_provenance_matrix.csv")
    eq_row = matrix["DISC:Eq2_5_Eq3_9"]
    assert eq_row["source_page"] == "2;7"
    assert eq_row["printed_page"] == "036304-2;036304-7"
    b3_row = matrix["DISC:B3Phi"]
    assert b3_row["source_page"] == "4;14"
    assert b3_row["printed_page"] == "036304-4;036304-14"


def test_korteweg_and_simulation_code_remain_bounded() -> None:
    matrix = _rows("research_notes/equation_relation_provenance_matrix.csv")
    korteweg = matrix["LAW:KortewegStressContext"]
    assert korteweg["provenance_status"] == "PRIMARY_SOURCE_PAGE_AUDITED_T07"
    note = (ROOT / "research_notes/TASK09_BOUNDED_DISCREPANCY_SOURCE_PAGE_AUDIT.md").read_text()
    assert "unpublished Onuki simulation-code branch remains `UNRESOLVED_SOURCE_DEPENDENT`" in note
    assert "No numerical reproduction is opened" in note
