from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def _tex_text(path: str) -> str:
    return _read(path).replace(r"\_", "_")


def _split_paths(paths: str) -> list[str]:
    return [part.strip() for part in paths.split(";") if part.strip()]


def test_visible_derivation_map_covers_mechanically_checkable_rows() -> None:
    with (ROOT / "research_notes/code_mirror_gap_queue.csv").open(newline="") as handle:
        queue_rows = [row for row in csv.DictReader(handle) if row["mechanically_checkable"] == "YES"]

    with (ROOT / "research_notes/visible_derivation_code_to_equation_map.csv").open(newline="") as handle:
        map_rows = list(csv.DictReader(handle))

    required_columns = {
        "canonical_id",
        "source_anchor",
        "companion_location",
        "mechanically_checkable",
        "code_paths",
        "article_reference_status",
        "assigned_task",
        "source_row_status",
        "proof_scope_limit",
        "notes",
    }
    assert set(map_rows[0]) == required_columns

    queue_ids = {row["canonical_id"] for row in queue_rows}
    map_ids = {row["canonical_id"] for row in map_rows}
    assert queue_ids == map_ids

    for row in map_rows:
        assert row["mechanically_checkable"] == "YES"
        assert row["article_reference_status"] == "ARTICLE_REFERENCE_PRESENT"
        assert row["source_row_status"].startswith("CLOSED_TASK"), row
        assert "PDE-model proof" in row["proof_scope_limit"]
        paths = _split_paths(row["code_paths"])
        assert paths, row
        for path in paths:
            assert path != "NONE"
            assert (ROOT / path).exists(), path


def test_public_derivation_groups_name_exact_code_paths() -> None:
    checks = {
        "sections/02a_vdw_baseline.tex": [
            "scripts/python/section_iia_vdw_baseline_sympy.py",
            "scripts/wolfram/section_iia_vdw_baseline_checks.wls",
        ],
        "sections/02b_gradient_entropy_energy.tex": [
            "scripts/python/section_iib_gradient_entropy_sympy.py",
            "scripts/wolfram/section_iib_gradient_entropy_checks.wls",
        ],
        "sections/02c_equilibrium_conditions.tex": [
            "scripts/python/section_iic_equilibrium_wall_sympy.py",
            "scripts/wolfram/section_iic_equilibrium_wall_checks.wls",
        ],
        "appendices/A_reversible_stress_plan.tex": [
            "scripts/python/appendix_a_reversible_stress_sympy.py",
            "scripts/wolfram/appendix_a_reversible_stress_checks.wls",
        ],
        "sections/02d_hydrodynamic_equations.tex": [
            "scripts/python/section_iid_hydrodynamic_balance_sympy.py",
            "scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls",
            "scripts/python/section_iid_p1_pressure_expansion_sympy.py",
            "scripts/wolfram/section_iid_p1_pressure_expansion_checks.wls",
        ],
        "appendices/B_scaled_equations_plan.tex": [
            "scripts/python/appendix_b_scaling_definitions_sympy.py",
            "scripts/python/appendix_b_momentum_b3_sympy.py",
            "scripts/python/appendix_b_b3_typo_candidate_sympy.py",
            "scripts/python/appendix_b_energy_boundary_sympy.py",
            "scripts/wolfram/appendix_b_energy_boundary_checks.wls",
        ],
        "sections/03_numerical_results_overview.tex": [
            "scripts/python/section_iii_simulation_estimates.py",
            "tests/test_section_iii_simulation_guide.py",
        ],
    }
    for article_path, code_paths in checks.items():
        text = _tex_text(article_path)
        for code_path in code_paths:
            assert code_path in text, (article_path, code_path)


def test_visible_code_map_is_advertised_by_public_verification_text() -> None:
    appendix_c = _tex_text("appendices/C_verification_plan.tex")
    readme = _read("README.md")
    runner = _read("scripts/run_verification.sh")
    for text in [appendix_c, readme, runner]:
        assert "visible_derivation_code_to_equation_map.csv" in text


def test_visible_derivation_gate_test_is_in_public_code_map() -> None:
    with (ROOT / "research_notes/onuki_companion_code_to_paper_map.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_script = {row["script"]: row for row in rows}
    row = by_script["tests/test_visible_derivation_code_gate.py"]
    assert "visible derivation" in row["checked_identity_or_guard"].lower()
    assert "ledger and prose regression" in row["proof_scope_limit"].lower()
