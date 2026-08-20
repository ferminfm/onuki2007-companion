import csv
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
CATALOG = PROJECT / "research_notes" / "onuki_companion_reference_catalog.csv"
MISSING = PROJECT / "research_notes" / "onuki_companion_missing_sources.csv"
BIB = PROJECT / "references" / "onuki2007_companion.bib"
KORTEWEG_LEDGER = PROJECT / "research_notes" / "korteweg1901_source_ledger.csv"


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def by_id(items):
    return {row["source_id"]: row for row in items}


def test_catalog_is_parseable_and_nonempty():
    catalog = rows(CATALOG)
    missing = rows(MISSING)
    assert len(catalog) >= 10
    assert len(missing) >= 1
    assert all(row["source_id"] and row["inspected_status"] for row in catalog)


def test_required_primary_and_external_sources_are_classified():
    catalog = by_id(rows(CATALOG))
    assert catalog["onuki_pre_2007"]["inspected_status"] == "LOCAL_PRIMARY_INSPECTED_METADATA"
    assert catalog["dunn_serrin_1985"]["inspected_status"] == "LOCAL_PRIMARY_INSPECTED_METADATA"
    assert catalog["teshigawara_onuki_2008"]["inspected_status"] == "EXTERNAL_LOCAL_PRIMARY_INSPECTED_METADATA"
    assert catalog["vdw_rowlinson_1979_external"]["inspected_status"] == "EXTERNAL_LOCAL_PRIMARY_INSPECTED_METADATA"
    assert catalog["landau_lifshitz_fluid_mechanics_external"]["inspected_status"] == "EXTERNAL_LOCAL_REFERENCE_INSPECTED_METADATA"
    assert "not Fluid Mechanics" in catalog["landau_lifshitz_mechanics_local_non_target"]["notes"]


def test_korteweg_direct_primary_attachment_is_locked():
    catalog = by_id(rows(CATALOG))
    missing = by_id(rows(MISSING))
    ledger = by_id(rows(KORTEWEG_LEDGER))
    source = catalog["korteweg_1901_original"]
    lock = ledger["korteweg_1901_original"]
    assert source["inspected_status"] == "LOCAL_PRIMARY_ATTACHMENT_INSPECTED"
    assert source["page_count"] == "24"
    assert "korteweg_1901_original" not in missing
    assert lock["zotero_item_key"] == "TDFUJKVC"
    assert lock["parent_item_status"] == "ABSENT_ORPHAN_ATTACHMENT"
    assert lock["source_identity_status"] == "SOURCE_ATTACHMENT_VERIFIED"
    assert lock["sha256"] == "d2b73e9aac955b145a64ea8b5e92f512a469bcd4355055107689a01d644ec4f4"


def test_bibliography_notes_match_catalog_boundaries():
    text = BIB.read_text(encoding="utf-8")
    assert "Local PDF cataloged for later companion context" in text
    assert "Local 24-page French primary-source scan inspected" in text
    assert "scanner and repository provenance are unresolved" in text
    entry = text[
        text.index("@article{Korteweg1901") :
        text.index("@article{FukagawaFujitani2012")
    ].lower()
    assert "doi =" not in entry
