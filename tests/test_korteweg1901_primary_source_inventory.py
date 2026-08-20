import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
NOTES = PROJECT / "research_notes"
INVENTORY = NOTES / "korteweg1901_equation_inventory.csv"
PAGES = NOTES / "korteweg1901_page_anchor_map.csv"
GLOSSARY = NOTES / "korteweg1901_translation_glossary.csv"
LOCK = NOTES / "KORTEWEG1901_SOURCE_LOCK.md"
SUMMARY = NOTES / "KORTEWEG1901_PRIMARY_SOURCE_INVENTORY.md"
UNCERTAINTIES = NOTES / "KORTEWEG1901_TRANSCRIPTION_UNCERTAINTIES.md"


def read_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, f"{path.name} must not be empty"
    assert all(None not in row for row in rows), f"malformed CSV row in {path.name}"
    return rows


def test_every_page_is_ordered_and_image_checked():
    pages = read_rows(PAGES)
    assert [int(row["pdf_page"]) for row in pages] == list(range(1, 25))
    assert [int(row["printed_page"]) for row in pages] == list(range(1, 25))
    assert {row["source_id"] for row in pages} == {"korteweg_1901_original"}
    assert all(row["page_image_status"] == "IMAGE_CHECKED" for row in pages)
    assert all(row["math_readability"] == "READABLE" for row in pages)


def test_numbered_equations_one_through_fifty_eight_are_unique():
    rows = read_rows(INVENTORY)
    numbered = [row for row in rows if row["row_id"].startswith("K1901-E")]
    assert len(numbered) == 58
    assert [row["row_id"] for row in numbered] == [
        f"K1901-E{number:03d}" for number in range(1, 59)
    ]
    assert [row["source_equation"] for row in numbered] == [
        f"({number})" for number in range(1, 59)
    ]
    assert len({row["row_id"] for row in rows}) == len(rows)


def test_inventory_has_unnumbered_logic_and_separate_layers():
    rows = read_rows(INVENTORY)
    unnumbered = [row for row in rows if row["row_id"].startswith("K1901-U")]
    assert len(unnumbered) >= 20
    required = {
        "source_transcription",
        "audit_translation",
        "modern_notation",
        "derivation_instruction",
        "hypotheses",
        "scope",
    }
    assert required.issubset(rows[0])
    assert all(row["source_transcription"] for row in rows)
    assert all(row["audit_translation"] for row in rows)
    assert all(row["modern_notation"] for row in rows)
    assert all(row["image_checked"] == "YES" for row in rows)
    assert all(1 <= int(row["pdf_page"]) <= 24 for row in rows)
    assert all(row["confidence"] in {"HIGH", "MEDIUM"} for row in rows)


def test_source_fingerprint_and_inventory_boundary_are_stable():
    lock = LOCK.read_text(encoding="utf-8")
    summary = SUMMARY.read_text(encoding="utf-8")
    uncertainties = UNCERTAINTIES.read_text(encoding="utf-8")
    assert "d2b73e9aac955b145a64ea8b5e92f512a469bcd4355055107689a01d644ec4f4" in lock
    assert "COMPLETE_PAGE_IMAGE_VERIFIED" in summary
    assert "does not assert equivalence to Onuki" in summary
    assert "NO_CRITICAL_UNRESOLVED_TRANSCRIPTION" in uncertainties
    assert "not source notation" in summary


def test_glossary_is_explicit_about_source_and_modern_symbols():
    rows = read_rows(GLOSSARY)
    assert len(rows) >= 20
    assert all(row["source_symbol"] and row["modern_notation"] for row in rows)
    density = next(row for row in rows if row["source_symbol"] == "ρ")
    assert density["source_term"] == "densité"
    stress = next(row for row in rows if row["source_symbol"] == "p_xx etc.")
    assert "pressure-positive" in stress["limitation"]
