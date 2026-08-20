import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MAP = PROJECT / "research_notes" / "korteweg_historical_lineage_map.csv"
NOTE = PROJECT / "research_notes" / "KORTEWEG_VDW_ONUKI_LINEAGE_MAP.md"


def rows():
    with MAP.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))
    assert data
    assert all(None not in row for row in data)
    return data


def test_claim_types_and_anchors_are_bounded():
    data = rows()
    allowed = {
        "EXPLICIT_PRIMARY_SOURCE",
        "EXPLICIT_LATER_ATTRIBUTION",
        "RETROSPECTIVE_MODERN_TERMINOLOGY",
        "MATHEMATICALLY_SUPPORTED_LINEAGE",
        "UNRESOLVED_HISTORICAL_INFLUENCE",
    }
    assert {row["claim_type"] for row in data} == allowed
    assert all(row["source_id"] and row["pdf_page"] and row["claim_text"] for row in data)
    assert {row["formula_import_status"] for row in data} == {
        "NO_FORMULA_EQUIVALENCE_IMPORTED"
    }


def test_onuki_citation_and_korteweg_scope_are_separate():
    data = {row["claim_id"]: row for row in rows()}
    assert data["KHL-011"]["claim_type"] == "EXPLICIT_LATER_ATTRIBUTION"
    assert data["KHL-011"]["printed_page_or_section"] == "036304-1"
    assert data["KHL-006"]["claim_type"] == "EXPLICIT_PRIMARY_SOURCE"
    assert data["KHL-006"]["printed_page_or_section"] == "12"
    assert data["KHL-014"]["influence_status"] == "UNRESOLVED"


def test_modern_terminology_is_not_attributed_to_korteweg():
    text = NOTE.read_text(encoding="utf-8")
    assert "retrospective labels" in text
    assert "not represented as Korteweg's own terminology" in text
    assert "No row establishes equation-by-equation equivalence" in text
    assert "which particular Korteweg equations influenced" in text
