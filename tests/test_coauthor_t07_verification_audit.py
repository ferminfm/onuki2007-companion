from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATIONS = ROOT / "research_notes/whole_companion_relation_treatment_matrix.csv"
VERIFY_MAP = ROOT / "research_notes/coauthor_readiness_code_to_paper_map.csv"
TRACE_MAP = ROOT / "research_notes/coauthor_readiness_wolfram_trace_audit.csv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_t07_builders_regenerate_closed_maps() -> None:
    subprocess.run(
        [sys.executable, "scripts/python/build_coauthor_relation_audit.py"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/python/build_coauthor_verification_map.py"],
        cwd=ROOT,
        check=True,
    )
    public = [row for row in read(RELATIONS) if row["evidence_scope"] == "PUBLIC"]
    mapped = read(VERIFY_MAP)
    assert len(public) == 526
    assert len(mapped) == len(public)
    assert {row["relation_id"] for row in mapped} == {
        row["relation_id"] for row in public
    }
    assert sum(row["final_status"] == "VERIFIED_FINITE_EVIDENCE" for row in mapped) == 480
    assert sum(
        row["final_status"] == "VERIFIED_FINITE_EVIDENCE_WITH_BOUNDED_SOURCE_STATUS"
        for row in mapped
    ) == 8
    assert sum(
        row["final_status"] == "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"
        for row in mapped
    ) == 38
    assert not [row for row in mapped if row["final_status"] == "OPEN_VERIFICATION_GAP"]


def test_every_finite_row_has_existing_primary_independent_and_control_paths() -> None:
    finite = [
        row
        for row in read(VERIFY_MAP)
        if row["mechanical_status"] == "MECHANICALLY_CHECKABLE_FINITE"
    ]
    assert finite
    for row in finite:
        assert row["visible_derivation_status"] == "PASS_VISIBLE_LOCATION"
        assert row["wolfram_status"] == "PASS_REPRODUCIBLE_PATH"
        assert row["sympy_status"] == "PASS_REPRODUCIBLE_PATH"
        assert row["negative_control_status"] == "PASS_REPRODUCIBLE_PATH"
        assert row["wolfram_check_ids"]
        assert row["sympy_check_ids"]
        assert row["negative_control_ids"]
        assert "Group-level" not in row["notes"]
        assert row["check_mapping_basis"]
        assert not row["dimensional_status"].startswith("MISSING")
        for path in [part.strip() for part in row["code_paths"].split(";") if part.strip()]:
            assert (ROOT / path).is_file(), (row["relation_id"], path)


def test_check_ids_are_row_specific_not_complete_group_dumps() -> None:
    finite = [
        row
        for row in read(VERIFY_MAP)
        if row["mechanical_status"] == "MECHANICALLY_CHECKABLE_FINITE"
    ]
    assert finite
    for row in finite:
        assert len(row["wolfram_check_ids"].split("; ")) <= 3
        assert len(row["sympy_check_ids"].split("; ")) <= 3
        assert len(row["negative_control_ids"].split("; ")) <= 3
        assert row["check_mapping_basis"].startswith(("wolfram=DIRECT_", "wolfram=ENCLOSING_"))


def test_bounded_source_status_survives_finite_verification() -> None:
    rows = {row["relation_id"]: row for row in read(VERIFY_MAP)}
    bounded = {
        "DISC:B3Phi",
        "DISC:Eq2_5_Eq3_9",
        "LAW:KortewegStressContext",
        "TEX:eq:appb-source-consistent-b3",
        "TEX:eq:appb-b3-bulk-pressure-scale",
        "TEX:eq:appb-b3-grad-square-scale",
        "TEX:eq:appb-b3-laplacian-scale",
        "TEX:eq:appb-b3-dyad-scale",
        "TEX:eq:appb-printed-b3-branch",
        "TEX:eq:appb-b3-branch-residual",
        "TEX:eq:iia-sound-speed",
    }
    assert {relation_id for relation_id, row in rows.items() if row["bounded_gap"] == "yes"} == bounded
    for relation_id in bounded:
        row = rows[relation_id]
        if relation_id != "LAW:KortewegStressContext":
            assert row["source_fidelity_status"] == "BOUNDED_SOURCE_DISCREPANCY"
        else:
            assert row["source_fidelity_status"] == "STANDARD_IDENTITY_DERIVED_OR_CITED"
        assert row["bounded_limitation"] != "NONE"
        if row["mechanical_status"] == "MECHANICALLY_CHECKABLE_FINITE":
            assert row["final_status"] == "VERIFIED_FINITE_EVIDENCE_WITH_BOUNDED_SOURCE_STATUS"
        else:
            assert row["final_status"] == "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"


def test_source_discrepancy_status_always_has_bounded_gap() -> None:
    rows = read(VERIFY_MAP)
    assert not [
        row
        for row in rows
        if row["source_fidelity_status"] == "BOUNDED_SOURCE_DISCREPANCY"
        and row["bounded_gap"] != "yes"
    ]
    by_id = {row["relation_id"]: row for row in rows}
    assert by_id["DISPLAY:11a97ba1fe394278"]["source_fidelity_status"] == "DEFINITION_WITH_ORIGIN_EXPLAINED"
    assert by_id["DISPLAY:1c2e5a2c33689a4a"]["source_fidelity_status"] == "SIMULATION_SPECIALIZATION_EXPLICIT"
    assert by_id["DISPLAY:11a97ba1fe394278"]["wolfram_check_ids"] == "phi_definition; theta_definition; length_scale_squared_relation"
    assert by_id["DISPLAY:11a97ba1fe394278"]["sympy_check_ids"] == "phi_definition; theta_definition; length_scale_squared_relation"
    assert by_id["DISPLAY:1c2e5a2c33689a4a"]["mechanical_status"] == "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"


def test_mixed_section_iii_script_is_detected_as_sympy_and_pint() -> None:
    rows = [
        row
        for row in read(VERIFY_MAP)
        if row["public_location"].startswith("sections/03")
        and row["mechanical_status"] == "MECHANICALLY_CHECKABLE_FINITE"
    ]
    assert rows
    assert all("section_iii_simulation_estimates.py" in row["sympy_evidence"] for row in rows)
    assert all(row["dimensional_status"] == "PASS_DIMENSIONAL_PATH" for row in rows)
    assert all("section_iii_simulation_estimates.py" in row["dimensional_evidence"] for row in rows)


def test_fragile_section_iii_ledgers_have_direct_check_ids() -> None:
    rows = {row["relation_id"]: row for row in read(VERIFY_MAP)}
    expected = {
        "TEX:eq:iii-effective-conductivity-ledger": "effective_conductivity_eq317_definition",
        "TEX:eq:iii-bottom-heat-flux-ledger": "bottom_heat_flux_eq318_definition",
        "TEX:eq:iii-wetting-heat-flux-normalization": "wetting_heat_flux_normalization",
    }
    for relation_id, check_id in expected.items():
        assert check_id in rows[relation_id]["sympy_check_ids"]


def test_all_active_public_wolfram_suites_have_terminal_trace_audit() -> None:
    rows = read(TRACE_MAP)
    assert len(rows) == 14
    assert all(row["audit_status"] == "PASS" for row in rows)
    assert all(row["residual_emitted"] == "YES" for row in rows)
    assert all(row["expected_nonzero_control"] == "YES" for row in rows)
    assert {row["trace_class"] for row in rows} == {
        "EXPLICIT_TRANSITION_TRACE",
        "ATOMIC_NAMED_RESIDUAL_TRACE",
    }


def test_public_lean_names_exist_and_no_project_proof_bypass() -> None:
    lean = (ROOT / "formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean").read_text(encoding="utf-8")
    appendix = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "appendices/C_verification_plan.tex",
            "appendices/E_korteweg_primary_source_crosswalk.tex",
        )
    )
    theorem_names = set(re.findall(r"^theorem\s+([A-Za-z0-9_]+)", lean, re.MULTILINE))
    cited_names = set(re.findall(r"\\path\{([a-z][A-Za-z0-9_]+)\}", appendix))
    cited_theorems = cited_names & theorem_names
    assert cited_theorems
    assert cited_theorems <= theorem_names
    assert not re.search(r"\b(?:sorry|admit)\b|^\s*axiom\b", lean, re.MULTILINE)
    assert "do not prove a continuum PDE" in appendix


def test_obsolete_scaffold_and_generated_artifacts_are_not_public_evidence() -> None:
    runner = (ROOT / "scripts/run_verification.sh").read_text(encoding="utf-8")
    code_map = (ROOT / "research_notes/onuki_companion_code_to_paper_map.csv").read_text(encoding="utf-8")
    assert "onuki2007_planned_checks.wls" not in runner
    assert "onuki2007_planned_checks.wls" not in code_map
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.splitlines()
    forbidden = re.compile(r"(?:^|/)(?:generated|\.lake|__pycache__)(?:/|$)|\.pdf$")
    assert not [path for path in tracked if forbidden.search(path)]
