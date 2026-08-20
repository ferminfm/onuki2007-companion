from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "research_notes/equation_relation_provenance_matrix.csv"
QUEUE = ROOT / "research_notes/equation_relation_repair_queue.csv"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_provenance_matrix_schema_and_size() -> None:
    rows = _rows(MATRIX)
    assert len(rows) >= 250
    assert set(rows[0]) == {
        "relation_id",
        "relation_kind",
        "public_location",
        "tex_label",
        "source_anchor",
        "source_page",
        "printed_page",
        "relation_summary",
        "provenance_status",
        "provenance_detail",
        "derivation_logic_status",
        "code_check_status",
        "code_paths",
        "repair_task",
        "repair_reason",
        "bounded_gap",
        "notes",
    }


def test_all_rows_have_status_and_repair_task() -> None:
    for row in _rows(MATRIX):
        assert row["relation_id"], row
        assert row["public_location"], row["relation_id"]
        assert row["provenance_status"], row["relation_id"]
        assert row["derivation_logic_status"], row["relation_id"]
        assert row["code_check_status"], row["relation_id"]
        assert row["repair_task"], row["relation_id"]
        assert "FULL_EQUIVALENCE" not in row["provenance_status"]


def test_high_priority_source_rows_are_present() -> None:
    ids = {row["relation_id"] for row in _rows(MATRIX)}
    required = {
        "SRC:II-2_5",
        "SRC:II-2_10",
        "SRC:II-2_17",
        "SRC:II-2_18",
        "SRC:APPB-B3",
        "DISC:Eq2_5_Eq3_9",
        "DISC:B3Phi",
        "LAW:CoexistenceMuPressure",
        "LAW:SurfaceTensionFirstIntegral",
        "LAW:Gibbs-Duhem",
        "LAW:KortewegStressContext",
    }
    assert required <= ids


def test_repair_queue_contains_named_layer1_concerns() -> None:
    queue = _rows(QUEUE)
    ids = {row["relation_id"] for row in queue}
    required = {
        "DISC:Eq2_5_Eq3_9",
        "DISC:B3Phi",
        "LAW:CoexistenceMuPressure",
        "LAW:SurfaceTensionFirstIntegral",
        "TERM:EquilibriumProfile",
        "LAW:KortewegStressContext",
        "LAW:NewtonianViscousStress",
    }
    assert required <= ids


def test_bounded_discrepancies_remain_bounded() -> None:
    rows = {row["relation_id"]: row for row in _rows(MATRIX)}
    for relation_id in ["DISC:Eq2_5_Eq3_9", "DISC:B3Phi"]:
        row = rows[relation_id]
        assert row["provenance_status"] == "BOUNDED_DISCREPANCY_PAGE_AUDITED_TASK09"
        assert row["bounded_gap"] == "yes"
        assert "09_bounded_discrepancy_audit" in row["repair_task"]


def test_no_placeholder_rows_in_task01_outputs() -> None:
    joined = "\n".join(
        ",".join(row.values()) for row in _rows(MATRIX) + _rows(QUEUE)
    ).lower()
    forbidden = ["todo only", "placeholder only", "tbd"]
    for needle in forbidden:
        assert needle not in joined
