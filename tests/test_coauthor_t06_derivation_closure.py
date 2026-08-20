import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_notes/coauthor_readiness_derivation_repair_queue.csv"
CLOSURE = ROOT / "research_notes/coauthor_readiness_task_closure_evidence.csv"
TASK = "T06-public-editorial-korteweg"


def read(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_all_t06_rows_have_relation_level_closure_evidence():
    queue = [row for row in read(QUEUE) if row["assigned_task"] == TASK]
    closure = {
        row["relation_id"]: row
        for row in read(CLOSURE)
        if row["task_id"] == TASK
    }
    assert queue
    assert set(closure) == {row["relation_id"] for row in queue}
    assert all(row["status"] == "CLOSED_T06_VERIFIED" for row in queue)
    assert all(row["closure_status"] == "CLOSED_T06_VERIFIED" for row in closure.values())
    assert all(row["source_page_evidence"] for row in closure.values())
    assert all(row["visible_derivation_evidence"] for row in closure.values())
    assert all(row["mechanical_check_evidence"] for row in closure.values())
    assert all(row["negative_control_evidence"] for row in closure.values())
    assert all(row["dimensional_evidence"] for row in closure.values())
    assert all("PASS" in row["independent_review_evidence"] for row in closure.values())
