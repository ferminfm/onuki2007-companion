import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "research_notes" / "COMPANION_DERIVATION_PROOF_POLICY.md"
TEMPLATE = ROOT / "research_notes" / "COMPANION_DERIVATION_AUDIT_TEMPLATE.md"
CHECKLIST = ROOT / "research_notes" / "onuki_companion_section_proof_checklist.csv"

REQUIRED_COLUMNS = {
    "unit_id",
    "file",
    "source_range",
    "current_status",
    "source_anchor_required",
    "typed_objects_status",
    "assumptions_status",
    "step_derivation_status",
    "tool_check_mapping",
    "limitations_status",
    "branch_or_boundary_caveat",
    "next_action",
}

ALLOWED_STATUSES = {
    "NAVIGATION_ONLY",
    "NAVIGATION_ONLY_PENDING_GUIDE",
    "NAVIGATION_ONLY_PENDING_SYNTHESIS",
    "PENDING_DERIVATION",
    "COMPLETED_NEEDS_POLICY_AUDIT",
    "POLICY_AUDITED_COMPLETE",
    "READING_GUIDE_COMPLETED_NEEDS_AUDIT",
    "READING_GUIDE_POLICY_AUDITED",
    "SUPPORT_APPENDIX",
}


def checklist_rows():
    with CHECKLIST.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_policy_and_template_exist_with_required_terms():
    policy = POLICY.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    for phrase in [
        "Source anchor",
        "Typed objects",
        "Tool-check mapping",
        "UNRESOLVED_SOURCE_DEPENDENT",
        "Software checks support finite claims only",
        "Do not copy or closely paraphrase",
    ]:
        assert phrase in policy
    for heading in [
        "## Source Anchors",
        "## Typed Objects",
        "## Verification Mapping",
        "## Limitations",
        "## Audit Decision",
    ]:
        assert heading in template


def test_section_checklist_schema_and_statuses():
    rows = checklist_rows()
    assert rows
    assert set(rows[0].keys()) == REQUIRED_COLUMNS
    statuses = {row["current_status"] for row in rows}
    assert statuses <= ALLOWED_STATUSES
    required_units = {"sec_IIA", "sec_IIB", "sec_IID", "app_A", "app_B", "sec_III_overview"}
    assert required_units <= {row["unit_id"] for row in rows}


def test_checklist_preserves_current_boundaries():
    by_id = {row["unit_id"]: row for row in checklist_rows()}
    assert by_id["sec_I"]["current_status"] == "READING_GUIDE_POLICY_AUDITED"
    for unit_id in ["sec_IIA", "sec_IIB", "sec_IIC", "sec_IID", "app_A", "app_B"]:
        assert by_id[unit_id]["current_status"] == "POLICY_AUDITED_COMPLETE"
    assert "global" in by_id["sec_IID"]["branch_or_boundary_caveat"]
    assert "unpublished" in by_id["app_B"]["branch_or_boundary_caveat"]
    assert by_id["app_C"]["current_status"] == "SUPPORT_APPENDIX"


def test_no_policy_claims_software_proves_physics():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [POLICY, TEMPLATE, CHECKLIST]
    )
    forbidden = [
        "software proves the physical model",
        "software proves physical conclusions",
        "B3 is an official erratum",
        "unpublished simulation-code branch is known",
    ]
    for phrase in forbidden:
        assert phrase not in combined
