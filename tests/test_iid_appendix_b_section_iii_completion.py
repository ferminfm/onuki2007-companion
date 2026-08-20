from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def _flat(path: str) -> str:
    return " ".join(_read(path).split())


def _matrix() -> dict[str, dict[str, str]]:
    with (ROOT / "research_notes/onuki_iid_appendix_b_section_iii_completion_matrix.csv").open(
        newline=""
    ) as handle:
        return {row["inventory_id"]: row for row in csv.DictReader(handle)}


def test_completion_matrix_covers_task06_priority_rows() -> None:
    rows = _matrix()
    required = {
        "II-2_35",
        "II-2_36",
        "II-2_40",
        "II-2_48",
        "II-2_53",
        "APPB-B1",
        "APPB-CONT",
        "APPB-B2",
        "APPB-B3",
        "APPB-B4",
        "APPB-B5",
        "APPB-B6",
        "III-3_1",
        "III-3_2",
        "III-3_6",
        "III-3_12",
        "III-3_14",
        "III-3_16",
        "III-3_18",
        "III-3_20",
    }
    missing = sorted(required.difference(rows))
    assert missing == []
    assert rows["APPB-B3"]["completion_status"] == "CLOSED_BOUNDED_SOURCE_BRANCH"
    assert "no official erratum" in rows["APPB-B3"]["limitation"]
    assert rows["II-2_53"]["completion_status"] == "CLOSED_BOUNDED_BOUNDARY_STATUS"
    assert "boundary" in rows["II-2_53"]["limitation"]
    assert rows["III-3_16"]["completion_status"] == "CLOSED_SCENARIO_ESTIMATE_NO_REPRODUCTION"


def test_public_sections_declare_task06_completion_boundaries() -> None:
    iid = _flat("sections/02d_hydrodynamic_equations.tex")
    appendix_b = _flat("appendices/B_scaled_equations_plan.tex")
    section_iii = _flat("sections/03_numerical_results_overview.tex")
    assert "Source-Procedure Completion Status" in iid
    assert "integrated energy/entropy closure remains boundary dependent" in iid
    assert "Source-Procedure Completion Status" in appendix_b
    assert "No unpublished numerical implementation branch is inferred" in appendix_b
    assert "Source-Procedure Completion Status" in section_iii
    assert "Published figures, time traces, boiling transitions" in section_iii
    assert "does not reproduce or validate them" in section_iii


def test_task06_completion_note_preserves_scientific_boundaries() -> None:
    text = _flat("research_notes/SECTION_IID_APPENDIX_B_SECTION_III_COMPLETION.md")
    required = [
        "No numerical reproduction",
        "unpublished implementation inference",
        "source method assumptions, boundary branches",
        "typographical omission under that dimensional-source derivation only",
        "global entropy statement remains a boundary and wall-transfer issue",
    ]
    for phrase in required:
        assert phrase in text
    forbidden = [
        "official erratum is established",
        "author intended",
        "simulation code used",
        "numerical impact is proven",
        "full global closure is proved",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_no_article_facing_blackboard_wording_in_task06_files() -> None:
    article_files = [
        "sections/02d_hydrodynamic_equations.tex",
        "appendices/B_scaled_equations_plan.tex",
        "sections/03_numerical_results_overview.tex",
        "sections/03a_method_scaled_equations.tex",
        "sections/03b_adiabatic_expansion.tex",
        "sections/03c_piston_effect.tex",
        "sections/03d_heat_flow_two_phase.tex",
        "sections/03e_steady_heat_conduction.tex",
        "sections/03f_boiling_gravity.tex",
        "sections/03g_wetting_dynamics.tex",
    ]
    for path in article_files:
        assert "blackboard calculation" not in _read(path).lower()
        assert "blackboard derivation" not in _read(path).lower()
