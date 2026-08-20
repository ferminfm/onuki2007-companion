from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_task07_reports_exist() -> None:
    assert (ROOT / "research_notes/EQUATION_INVENTORY_VERIFICATION_COMPLETION.md").exists()
    assert (ROOT / "research_notes/article_facing_wording_cleanup_log.csv").exists()


def test_completed_derivation_regression_is_mapped() -> None:
    path = ROOT / "research_notes/onuki_companion_code_to_paper_map.csv"
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_script = {row["script"]: row for row in rows}
    row = by_script["tests/test_iid_appendix_b_section_iii_completion.py"]
    assert "Section II.D" in row["companion_location"]
    assert "Appendix B" in row["companion_location"]
    assert "Section III" in row["companion_location"]
    assert "prose regression" in row["proof_scope_limit"].lower()


def test_article_facing_files_avoid_private_workflow_metaphor() -> None:
    public_files = [
        "README.md",
        "main.tex",
        "appendices/C_verification_plan.tex",
        "appendices/B_scaled_equations_plan.tex",
        "sections/01_introduction_navigation.tex",
        "sections/02d_hydrodynamic_equations.tex",
        "sections/03_numerical_results_overview.tex",
    ]
    forbidden = [
        "blackboard calculation",
        "blackboard derivation",
        "blackboard_code_to_derivation_map.csv",
        "is an official erratum",
        "official erratum is established",
        "author intent is established",
        "simulation-code branch is identified",
    ]
    for path in public_files:
        lowered = _read(path).lower().replace(r"\_", "_")
        for phrase in forbidden:
            assert phrase not in lowered, (path, phrase)


def test_b3_claim_remains_strong_but_bounded() -> None:
    appendix_b = " ".join(
        _read("appendices/B_scaled_equations_plan.tex").lower().split()
    )
    assert "high-confidence typographical-omission candidate" in appendix_b
    assert "under the dimensional-source derivation" in appendix_b
    assert "not an official erratum" in appendix_b
    assert "not evidence about the unpublished numerical implementation" in appendix_b
