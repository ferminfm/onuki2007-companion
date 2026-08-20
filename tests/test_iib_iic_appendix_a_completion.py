from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_IDS = {
    "II-2_12", "II-2_13", "II-2_14", "II-2_15", "II-2_16", "II-2_17",
    "II-2_18", "IIB-MPRIME", "II-2_20", "II-2_21", "II-2_22",
    "II-2_24", "II-2_25", "IIC-FIRST-INTEGRAL", "II-2_28", "II-2_29",
    "II-2_30", "II-2_31", "II-2_32", "II-2_34", "IIC-STOT-ETOT",
    "APPA-A1", "APPA-A2", "APPA-A3", "APPA-A4", "APPA-GRADVAR",
}


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_completion_matrix_covers_required_iib_iic_appendix_a_rows() -> None:
    with (ROOT / "research_notes/onuki_iib_iic_appendix_a_completion_matrix.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["inventory_id"]: row for row in rows}
    assert REQUIRED_IDS <= set(by_id)
    for inventory_id in REQUIRED_IDS:
        row = by_id[inventory_id]
        assert row["completion_status"] == "CLOSED_EXPLICIT_DERIVATION"
        assert row["verification_support"]
        assert row["limitation"]


def test_companion_sections_record_source_procedure_closure() -> None:
    checks = {
        "sections/02b_gradient_entropy_energy.tex": "Source-Procedure Closure for Section II.B",
        "sections/02c_equilibrium_conditions.tex": "Source-Procedure Closure for Section II.C",
        "appendices/A_reversible_stress_plan.tex": "Source-Procedure Closure for Appendix A",
    }
    for path, phrase in checks.items():
        text = _read(path)
        assert phrase in text
        assert "does not" in text


def test_completion_note_preserves_bounded_gaps() -> None:
    text = _read("research_notes/SECTION_IIB_IIC_APPENDIX_A_COMPLETION.md")
    required = [
        "local/procedural",
        "Dynamic global entropy",
        "Appendix-B B3",
        "unpublished simulation-code branch remains unresolved",
        "Korteweg 1901 remains pending",
    ]
    for phrase in required:
        assert phrase in text
    forbidden = [
        "official erratum is established",
        "simulation-code branch is known",
        "global entropy closure is proved",
        "PDE well-posedness is proved",
    ]
    for phrase in forbidden:
        assert phrase not in text
