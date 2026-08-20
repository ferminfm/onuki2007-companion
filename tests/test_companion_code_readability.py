from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_code_to_paper_map_is_present_and_complete() -> None:
    path = ROOT / "research_notes/onuki_companion_code_to_paper_map.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) >= 20
    required_columns = {
        "script",
        "tool",
        "companion_location",
        "source_equation_anchor",
        "checked_identity_or_guard",
        "summary_output",
        "proof_scope_limit",
    }
    assert set(rows[0]) == required_columns

    scripts = {row["script"] for row in rows}
    required_scripts = {
        "scripts/run_verification.sh",
        "scripts/python/section_iid_hydrodynamic_balance_sympy.py",
        "scripts/python/appendix_b_b3_typo_candidate_sympy.py",
        "scripts/python/section_iii_simulation_estimates.py",
        "scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls",
        "tests/test_iid_appendix_b_section_iii_completion.py",
    }
    assert required_scripts <= scripts
    for row in rows:
        assert (ROOT / row["script"]).exists(), row["script"]
        assert row["proof_scope_limit"]


def test_runner_and_appendix_point_to_code_map() -> None:
    runner = _read("scripts/run_verification.sh")
    appendix = _read("appendices/C_verification_plan.tex")
    readme = _read("README.md")

    assert "onuki_companion_code_to_paper_map.csv" in runner
    assert r"research\_notes/" in appendix
    assert r"onuki\_companion\_code\_to\_paper\_map.csv" in appendix
    assert "onuki_companion_code_to_paper_map.csv" in readme


def test_source_fidelity_code_map_tracks_corrected_rows() -> None:
    path = ROOT / "research_notes/source_fidelity_code_to_equation_map.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    required_columns = {
        "source_row",
        "source_anchor",
        "companion_location",
        "correction_or_risk",
        "primary_mirror",
        "secondary_mirror",
        "pytest_regression",
        "runner_coverage",
        "status",
        "proof_scope_limit",
    }
    assert set(rows[0]) == required_columns

    by_row = {row["source_row"]: row for row in rows}
    for source_row in ["II-2_10", "II-2_17", "APPB-B3", "APPB-B4", "APPB-B5", "APPB-B6"]:
        assert source_row in by_row

    assert by_row["II-2_17"]["status"] == "MIRRORED_PASS_ZERO"
    assert "source_eq_2_17_factor_n" in by_row["II-2_17"]["primary_mirror"]
    assert by_row["APPB-B3"]["status"] == "SOURCE_BRANCH_DISCREPANCY_BOUNDED"
    assert "no official erratum" in by_row["APPB-B3"]["proof_scope_limit"]
    assert by_row["APPB-B5"]["status"] == "MIRRORED_EXPECTED_NONZERO_BOUNDARY_GAP"

    appendix = _read("appendices/C_verification_plan.tex")
    readme = _read("README.md")
    assert "source_fidelity_code_to_equation_map.csv" in readme
    assert "source_fidelity_code_to_equation_map.csv" in appendix


def test_script_headers_preserve_proof_scope_limits() -> None:
    checked_files = [
        "scripts/python/check_companion_scaffold.py",
        "scripts/python/appendix_b_energy_boundary_sympy.py",
        "scripts/python/appendix_b_energy_boundary_units.py",
        "scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls",
        "scripts/wolfram/appendix_b_energy_boundary_checks.wls",
    ]
    combined = " ".join("\n".join(_read(path)[:900] for path in checked_files).split())
    required = [
        "not a scientific verification layer",
        "do not reproduce simulations",
        "do not validate any numerical run",
        "author intent",
        "global balances",
    ]
    for phrase in required:
        assert phrase in combined


def test_blackboard_code_to_derivation_map_is_present_and_current() -> None:
    path = ROOT / "research_notes/blackboard_code_to_derivation_map.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) >= 14
    required_columns = {
        "task_number",
        "derivation_group",
        "companion_location",
        "source_anchor",
        "expanded_display_or_calculation",
        "primary_code_mirror",
        "secondary_code_mirror",
        "pytest_regression",
        "status",
        "proof_scope_limit",
    }
    assert set(rows[0]) == required_columns

    by_group = {row["derivation_group"]: row for row in rows}
    for group in [
        "IIB M coefficient identity",
        "IID p1 pressure expansion",
        "Appendix B diagonal factor proof",
        "Section III finite estimates",
    ]:
        assert group in by_group

    for row in rows:
        primary = row["primary_code_mirror"]
        if primary != "none":
            assert (ROOT / primary).exists(), primary
        pytest_path = row["pytest_regression"]
        if pytest_path != "none":
            assert (ROOT / pytest_path).exists(), pytest_path
        limit = row["proof_scope_limit"].lower()
        assert limit
        assert "full equivalence" not in limit
        assert "validated simulation" not in limit


def test_public_files_use_neutral_detailed_derivation_wording() -> None:
    runner = _read("scripts/run_verification.sh")
    appendix = _read("appendices/C_verification_plan.tex")
    readme = _read("README.md")
    for text in [runner, appendix.replace(r"\_", "_"), readme]:
        lowered = text.lower()
        assert "blackboard calculation" not in lowered
        assert "blackboard derivation" not in lowered
        assert "blackboard_code_to_derivation_map.csv" not in lowered
    assert "code-to-paper map is the public index" in readme
    assert "public verification index" in appendix
