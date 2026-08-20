import csv
import importlib.util
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/python/build_coauthor_relation_audit.py"
MATRIX = ROOT / "research_notes/whole_companion_relation_treatment_matrix.csv"
QUEUE = ROOT / "research_notes/coauthor_readiness_derivation_repair_queue.csv"


def load_builder():
    spec = importlib.util.spec_from_file_location("coauthor_relation_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_generator_outputs_are_current_and_unique():
    module = load_builder()
    expected, expected_queue = module.build_matrix()
    actual = rows(MATRIX)
    actual_queue = rows(QUEUE)
    assert actual == expected
    assert actual_queue == expected_queue
    assert len(actual) == len({row["relation_id"] for row in actual})


def test_every_source_row_and_public_equation_label_is_present():
    matrix = rows(MATRIX)
    ids = {row["relation_id"] for row in matrix}
    source = rows(ROOT / "research_notes/onuki2007_canonical_source_equation_inventory.csv")
    assert {f"SRC:{row['canonical_id']}" for row in source} <= ids
    labels = set()
    for path in [*ROOT.joinpath("sections").glob("*.tex"), *ROOT.joinpath("appendices").glob("*.tex")]:
        labels.update(re.findall(r"\\label\{(eq:[^}]+)\}", path.read_text(encoding="utf-8")))
    assert {f"TEX:{label}" for label in labels} <= ids
    source_matrix = [row for row in matrix if row["evidence_scope"] == "SOURCE"]
    assert all(row["mapped_public_relation_ids"] for row in source_matrix)


def test_unlabelled_displays_and_relation_inline_rows_are_exhaustive():
    module = load_builder()
    extracted = module.extract_public_relations()
    matrix_ids = {row["relation_id"] for row in rows(MATRIX)}
    extracted_ids = {row["relation_id"] for row in extracted}
    assert extracted_ids <= matrix_ids
    kinds = Counter(row["relation_kind"] for row in extracted)
    assert kinds["public_unlabelled_display"] > 0
    assert kinds["public_inline_relation"] > 0


def test_terminal_classes_and_repair_routes_are_closed_vocabularies():
    module = load_builder()
    matrix = rows(MATRIX)
    queue = rows(QUEUE)
    assert {row["terminal_treatment_class"] for row in matrix} <= module.TERMINAL_CLASSES
    forbidden = {"covered", "present", "checked", "common knowledge"}
    assert not ({row["terminal_treatment_class"].lower() for row in matrix} & forbidden)
    allowed_tasks = {
        "T03-sections-iia-iic-closure",
        "T04-section-iid-appendix-a-closure",
        "T05-appendix-b-section-iii-closure",
        "T06-public-editorial-korteweg",
        "T07-verification-code-audit",
    }
    assert queue
    assert {row["assigned_task"] for row in queue} <= allowed_tasks
    allowed_statuses = {
        "OPEN_ASSIGNED",
        "CLOSED_T03_VERIFIED",
        "CLOSED_T04_VERIFIED",
        "CLOSED_T05_VERIFIED",
        "CLOSED_T06_VERIFIED",
        "CLOSED_T07_VERIFIED",
    }
    assert {row["status"] for row in queue} <= allowed_statuses


def test_bounded_discrepancies_and_scope_boundaries_remain_separate():
    matrix = {row["relation_id"]: row for row in rows(MATRIX)}
    assert matrix["SRC:II-2_5"]["terminal_treatment_class"] == "BOUNDED_SOURCE_DISCREPANCY"
    assert matrix["SRC:APPB-B3"]["terminal_treatment_class"] == "BOUNDED_SOURCE_DISCREPANCY"
    assert matrix["DISC:B3Phi"]["terminal_treatment_class"] == "BOUNDED_SOURCE_DISCREPANCY"
    assert matrix["DISC:Eq2_5_Eq3_9"]["terminal_treatment_class"] == "BOUNDED_SOURCE_DISCREPANCY"
    assert matrix["LAW:KortewegStressContext"]["terminal_treatment_class"] == "STANDARD_IDENTITY_DERIVED_OR_CITED"
    assert matrix["SRC:INTRO-VDW-GRAD"]["terminal_treatment_class"] == "STANDARD_IDENTITY_DERIVED_OR_CITED"
    assert "restricted" in matrix["LAW:KortewegStressContext"]["terminal_class_reason"].lower()
    assert matrix["DISC:Eq2_5_Eq3_9"]["source_canonical_ids"] == "II-2_5;III-3_9"
    assert matrix["LAW:FourierHeatFlux"]["source_canonical_ids"] == "II-2_39;II-2_45"


def test_first_integrals_are_not_misclassified_as_boundary_conditions():
    matrix = {row["relation_id"]: row for row in rows(MATRIX)}
    assert matrix["TEX:eq:iia-grand-potential-first-integral"]["terminal_treatment_class"] == "VISIBLE_DERIVATION_COMPLETE"
    assert matrix["TEX:eq:iia-grand-potential-excess"]["terminal_treatment_class"] == "VISIBLE_DERIVATION_COMPLETE"


def test_independent_review_classification_corrections_are_preserved():
    matrix = {row["relation_id"]: row for row in rows(MATRIX)}
    assert matrix["TEX:eq:iid-entropy-balance"]["terminal_treatment_class"] == "LAW_OR_POSTULATE_WITH_NAME_AND_SOURCE"
    assert matrix["TEX:eq:iid-gibbs-duhem-246"]["terminal_treatment_class"] == "STANDARD_IDENTITY_DERIVED_OR_CITED"
    assert matrix["TEX:eq:iid-total-energy-density"]["terminal_treatment_class"] == "DEFINITION_WITH_ORIGIN_EXPLAINED"
    assert matrix["TEX:eq:iid-total-energy-density"]["source_canonical_ids"] == "II-2_38"
    assert matrix["SRC:IIB-SIM-SPEC"]["terminal_treatment_class"] == "SIMULATION_SPECIALIZATION_EXPLICIT"
    assert matrix["SRC:III-3_19"]["terminal_treatment_class"] == "DEFINITION_WITH_ORIGIN_EXPLAINED"
    assert matrix["SRC:APPB-B2"]["terminal_treatment_class"] == "VISIBLE_DERIVATION_COMPLETE"
    assert matrix["SRC:APPB-B5"]["terminal_treatment_class"] == "VISIBLE_DERIVATION_COMPLETE"


def test_source_page_and_code_evidence_fields_are_not_silently_empty():
    matrix = rows(MATRIX)
    source_rows = [row for row in matrix if row["evidence_scope"] == "SOURCE"]
    assert all(row["pdf_page"] for row in source_rows)
    assert all(row["source_page_status"] for row in source_rows)
    mechanical = [row for row in source_rows if row["mechanically_checkable"] == "YES"]
    assert mechanical
    assert all(row["code_paths"] for row in mechanical)
