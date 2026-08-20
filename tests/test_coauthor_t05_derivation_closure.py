import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_notes/coauthor_readiness_derivation_repair_queue.csv"
CLOSURE = ROOT / "research_notes/coauthor_readiness_task_closure_evidence.csv"


def read(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_all_t05_rows_have_relation_level_closure_evidence():
    queue = [row for row in read(QUEUE) if row["assigned_task"] == "T05-appendix-b-section-iii-closure"]
    closure = {
        row["relation_id"]: row
        for row in read(CLOSURE)
        if row["task_id"] == "T05-appendix-b-section-iii-closure"
    }
    assert queue
    assert set(closure) == {row["relation_id"] for row in queue}
    assert all(row["status"] == "CLOSED_T05_VERIFIED" for row in queue)
    assert all(row["closure_status"] == "CLOSED_T05_VERIFIED" for row in closure.values())
    assert all(row["source_page_evidence"] for row in closure.values())
    assert all(row["visible_derivation_evidence"] for row in closure.values())
    assert all(row["mechanical_check_evidence"] for row in closure.values())
    assert all(row["negative_control_evidence"] for row in closure.values())
    assert all(row["dimensional_evidence"] for row in closure.values())
    assert all("PASS" in row["independent_review_evidence"] for row in closure.values())


def test_t05_public_scaling_and_scenario_boundaries_are_explicit():
    appendix_b = (ROOT / "appendices/B_scaled_equations_plan.tex").read_text(encoding="utf-8")
    section_iii = (ROOT / "sections/03_numerical_results_overview.tex").read_text(encoding="utf-8")
    assert "appendix\\_b\\_transition\\_trace.wls" in appendix_b
    assert "source object, substitution, intermediate" in appendix_b
    assert "dimensional-source scaling gives" in appendix_b
    assert "unpublished numerical implementation" in appendix_b
    assert "section\\_iii\\_simulation\\_estimates\\_checks.wls" in section_iii
    assert "does not validate the numerical results" in section_iii
    assert "does not reconstruct the simulation code" in section_iii


def test_t05_code_mirrors_controls_and_dimensions_are_explicit():
    paths = [
        "scripts/python/appendix_b_scaling_definitions_sympy.py",
        "scripts/python/appendix_b_energy_boundary_sympy.py",
        "scripts/python/appendix_b_scaling_definitions_units.py",
        "scripts/python/appendix_b_energy_boundary_units.py",
        "scripts/wolfram/appendix_b_transition_trace.wls",
        "scripts/python/section_iii_simulation_estimates.py",
        "scripts/wolfram/section_iii_simulation_estimates_checks.wls",
    ]
    assert all((ROOT / path).is_file() for path in paths)
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    for token in (
        "wrong-coordinate-derivative",
        "missing-kinetic-density",
        "wrong-gravity-sign",
        "mixed-velocity",
        "PASS_DIMENSIONAL",
        "UNRESOLVED_SOURCE_DEPENDENT",
        "NOT_REPRODUCED",
    ):
        assert token in combined
