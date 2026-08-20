from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _flat(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


def test_task07_named_law_rows_are_closed_with_bounded_statuses() -> None:
    matrix = {row["relation_id"]: row for row in _rows("research_notes/equation_relation_provenance_matrix.csv")}
    assert matrix["LAW:Gibbs-Duhem"]["provenance_status"] == "SOURCE_ANCHORED_TASK07"
    assert matrix["LAW:Gibbs-Duhem"]["code_check_status"] == "CODE_PATH_RECORDED"
    assert "section_iid_hydrodynamic_balance_sympy.py" in matrix["LAW:Gibbs-Duhem"]["code_paths"]

    fourier = matrix["LAW:FourierHeatFlux"]
    assert fourier["provenance_status"] == "SOURCE_MODEL_INPUT_ANCHORED_TASK07"
    assert fourier["derivation_logic_status"] == "CONSTITUTIVE_MODEL_INPUT_STATUS_EXPLICIT"
    assert "section_iii_simulation_estimates.py" in fourier["code_paths"]

    korteweg = matrix["LAW:KortewegStressContext"]
    assert korteweg["provenance_status"] == "PRIMARY_SOURCE_PAGE_AUDITED_T07"
    assert korteweg["bounded_gap"] == "yes"
    assert "FINITE_LOCAL_TENSOR_MAP" in korteweg["derivation_logic_status"]


def test_repair_queue_after_task09_has_no_open_rows() -> None:
    open_rows = [row for row in _rows("research_notes/equation_relation_repair_queue.csv") if row["queue_status"].startswith("OPEN")]
    assert open_rows == []


def test_public_text_states_source_literature_boundaries() -> None:
    combined = "\n".join(
        _flat(path)
        for path in [
            "sections/01_introduction_navigation.tex",
            "sections/02d_hydrodynamic_equations.tex",
            "sections/03e_steady_heat_conduction.tex",
            "appendices/D_crosswalk_open_issues.tex",
        ]
    )
    required = [
        "direct Korteweg 1901 source has now been page-image inspected",
        "Fourier-type conductive branch",
        "source-stated model inputs",
        "does not derive the conductive law",
        "source-stated local Gibbs--Duhem differential",
        "Other external formulas remain excluded",
    ]
    for phrase in required:
        assert phrase in combined


def test_external_context_imports_only_audited_korteweg_tensor_map() -> None:
    rows = _rows("research_notes/external_capillary_source_anchor_map.csv")
    assert rows
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
    assert korteweg
    assert "SOURCE_RECONSTRUCTED_T04_CROSSWALKED_T05" in {
        row["current_use_status"] for row in korteweg
    }



def test_task09_bounded_discrepancies_are_page_audited_and_closed() -> None:
    queue = {row["relation_id"]: row for row in _rows("research_notes/equation_relation_repair_queue.csv")}
    for relation_id in ["SRC:APPB-B3", "DISC:B3Phi", "DISC:Eq2_5_Eq3_9"]:
        row = queue[relation_id]
        assert row["repair_task"] == "09_bounded_discrepancy_audit"
        assert row["queue_status"] == "CLOSED_TASK09_PAGE_AUDITED"
        assert row["provenance_status"] == "BOUNDED_DISCREPANCY_PAGE_AUDITED_TASK09"
        assert row["bounded_gap"] == "yes"


def test_literature_anchor_note_records_no_formula_import_policy() -> None:
    text = _flat("research_notes/TASK07_LITERATURE_SOURCE_ANCHORING.md")
    assert "External sources are cited only where the prose is explicitly contextual" in text
    assert "Direct Korteweg 1901 primary material remains missing locally" in text
    assert "does not import any external formula" in text
    current = _flat("research_notes/KORTEWEG1901_SOURCE_LOCK.md")
    assert "SOURCE_ATTACHMENT_VERIFIED" in current
