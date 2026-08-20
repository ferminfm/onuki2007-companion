from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows() -> list[dict[str, str]]:
    with (ROOT / "research_notes/dossier_item_implementation_matrix.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_dossier_matrix_has_required_schema_and_rows() -> None:
    rows = _rows()
    assert len(rows) >= 60
    required_columns = {
        "dossier_part",
        "dossier_file",
        "dossier_item_id",
        "source_equation",
        "dossier_heading",
        "priority",
        "current_companion_file",
        "required_action",
        "page_image_status",
        "visible_derivation_status",
        "code_mirror_status",
        "assigned_task",
        "implementation_status",
        "notes",
    }
    assert set(rows[0]) == required_columns


def test_high_priority_dossier_rows_are_seeded() -> None:
    rows = _rows()
    source_equations = {row["source_equation"] for row in rows}
    required = {
        "Eq. (2.17)",
        "Eq. (2.5)",
        "Eq. (3.9)",
        "Eq. (2.10)",
        "Eq. (2.18)",
        "Eq. (2.41)",
        "Eq. (2.42)",
        "Eq. (2.43)",
        "Eq. (2.44)",
        "Eq. (2.45)",
        "Eq. (2.46)",
        "Eq. (2.51)",
        "Eq. (2.52)",
        "Eq. (2.53)",
        "Eq. (B3)",
    }
    assert required <= source_equations


def test_all_dossier_rows_have_assigned_tasks_and_bounded_statuses() -> None:
    allowed_prefixes = {"02_", "03_", "04_", "05_", "06_", "07_", "08_", "09_"}
    allowed_status_prefixes = {
        "PENDING",
        "IMPLEMENTED_TASK02_VERIFIED",
        "IMPLEMENTED_TASK02_WITH_SOURCE_DISCREPANCY_RECORDED",
        "IMPLEMENTED_TASK03_VERIFIED",
        "IMPLEMENTED_TASK03_EQ217_VERIFIED",
        "IMPLEMENTED_TASK04_VERIFIED",
        "IMPLEMENTED_TASK05_VERIFIED",
        "IMPLEMENTED_TASK06_VERIFIED",
        "IMPLEMENTED_TASK07_VERIFIED",
        "IMPLEMENTED_TASK08_VERIFIED",
        "IMPLEMENTED_TASK09_VERIFIED",
        "CONTEXT_WARNING_CLOSED_TASK10",
    }
    for row in _rows():
        assigned = row["assigned_task"]
        assert assigned
        assert assigned == "04_to_09_by_warning_scope" or any(assigned.startswith(prefix) for prefix in allowed_prefixes)
        assert any(row["implementation_status"].startswith(prefix) for prefix in allowed_status_prefixes)
        assert "GLOBAL_COMPLETE" not in row["implementation_status"]


def test_task02_sound_speed_row_records_source_discrepancy() -> None:
    rows = {row["dossier_item_id"]: row for row in _rows()}
    row = rows["Eq_2_5"]
    assert row["implementation_status"] == "IMPLEMENTED_TASK02_WITH_SOURCE_DISCREPANCY_RECORDED"
    assert "Eq. (3.9)" in row["notes"]
    assert "source-fidelity discrepancy" in row["notes"]


def test_task03_eq217_rows_record_local_equilibrium_derivation() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "03_section_iib_implementation" and row["source_equation"] == "Eq. (2.17)"]
    assert len(rows) == 2
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK03_EQ217_VERIFIED"
        assert "local equilibrium coefficient derivation" in row["notes"]
        assert "factor n" in row["notes"]


def test_task04_section_iic_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "04_section_iic_implementation"]
    assert rows
    required = {f"Eq. (2.{i})" for i in range(21, 35)}
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK04_VERIFIED"
        assert "source badges corrected" in row["notes"]


def test_task05_appendix_a_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "05_appendix_a_implementation"]
    assert rows
    required = {"Eq. (A1)", "Eq. (A2)", "Eq. (A3)", "Eq. (A4)"}
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK05_VERIFIED"
        assert "Appendix A source badges corrected" in row["notes"]


def test_task06_section_iid_balance_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "06_section_iid_balances_entropy"]
    assert rows
    required = {f"Eq. (2.{i})" for i in range(35, 47)}
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK06_VERIFIED"
        assert "Eqs. (2.41)--(2.46) split" in row["notes"]


def test_task07_section_iid_stress_flux_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "07_section_iid_stress_flux_global"]
    assert rows
    required = {"Eqs. (2.47)--(2.48)", "Eq. (2.47)", "Eq. (2.49)", "Eq. (2.50)", "Eq. (2.51)", "Eq. (2.52)", "Eq. (2.53)"}
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK07_VERIFIED"
        assert "Eqs. (2.47)--(2.53) reviewed" in row["notes"]


def test_task08_appendix_b_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "08_appendix_b_implementation"]
    assert rows
    required = {"Eq. (B1)", "Eq. (B2)", "Eq. (B3)", "Eq. (B4)", "Eq. (B5)", "Eq. (B6)"}
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK08_VERIFIED"
        assert "B1--B6 reviewed" in row["notes"]
        assert "simulation-code branch unresolved" in row["notes"]



def test_task09_section_iii_rows_are_verified() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "09_section_iii_implementation"]
    assert rows
    required = {
        "Eqs. (3.1)--(3.11)",
        "Eqs. (3.3)--(3.4)",
        "Eqs. (3.8)--(3.9)",
        "Eq. (3.10)",
        "Eq. (3.11)",
        "Eq. (3.12)",
        "Eq. (3.13)",
        "Eq. (3.14)",
        "Eq. (3.15)",
        "Eq. (3.16)",
        "Eqs. (3.17)--(3.19)",
        "Eq. (3.20)",
    }
    assert required <= {row["source_equation"] for row in rows}
    for row in rows:
        assert row["implementation_status"] == "IMPLEMENTED_TASK09_VERIFIED"
        assert "Section III source pages 036304-6--036304-12 reviewed" in row["notes"]
        assert "no numerical reproduction" in row["notes"]



def test_task10_context_warning_rows_are_closed() -> None:
    rows = [row for row in _rows() if row["assigned_task"] == "04_to_09_by_warning_scope"]
    assert len(rows) == 4
    for row in rows:
        assert row["implementation_status"] == "CONTEXT_WARNING_CLOSED_TASK10"
        assert row["page_image_status"] == "NOT_APPLICABLE_CONTEXT_ROW"
        assert row["visible_derivation_status"] == "NOT_APPLICABLE_CONTEXT_ROW"
        assert row["code_mirror_status"] == "NOT_APPLICABLE_CONTEXT_ROW"
        assert "no standalone source equation" in row["notes"]


def test_matrix_points_to_existing_dossier_files() -> None:
    for row in _rows():
        dossier_file = row["dossier_file"]
        if dossier_file.startswith("/home/"):
            assert Path(dossier_file).exists(), dossier_file
