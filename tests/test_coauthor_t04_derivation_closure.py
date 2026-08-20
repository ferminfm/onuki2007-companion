import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_notes/coauthor_readiness_derivation_repair_queue.csv"
CLOSURE = ROOT / "research_notes/coauthor_readiness_task_closure_evidence.csv"


def read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_all_t04_rows_have_relation_level_closure_evidence():
    queue = [row for row in read(QUEUE) if row["assigned_task"] == "T04-section-iid-appendix-a-closure"]
    closure = {
        row["relation_id"]: row
        for row in read(CLOSURE)
        if row["task_id"] == "T04-section-iid-appendix-a-closure"
    }
    assert queue
    assert set(closure) == {row["relation_id"] for row in queue}
    assert all(row["status"] == "CLOSED_T04_VERIFIED" for row in queue)
    assert all(row["closure_status"] == "CLOSED_T04_VERIFIED" for row in closure.values())
    assert all(row["source_page_evidence"] for row in closure.values())
    assert all(row["visible_derivation_evidence"] for row in closure.values())
    assert all(row["mechanical_check_evidence"] for row in closure.values())
    assert all(row["negative_control_evidence"] for row in closure.values())
    assert all(row["dimensional_evidence"] for row in closure.values())
    assert all("PASS" in row["independent_review_evidence"] for row in closure.values())


def test_t04_public_derivations_expose_dossier_required_steps():
    iid = (ROOT / "sections/02d_hydrodynamic_equations.tex").read_text(encoding="utf-8")
    appa = (ROOT / "appendices/A_reversible_stress_plan.tex").read_text(encoding="utf-8")

    for token in (
        r"eq:iid-local-entropy-time-variation",
        r"eq:iid-entropy-flux-before-gradient-combination",
        r"eq:iid-entropy-flux-mass-balance-combination",
        r"D_tn+n\grad\cdot v",
        "boundary heat",
        "surface-energy",
    ):
        assert token in iid

    for token in (
        r"eq:app-a-material-density-gradient",
        r"eq:app-a-material-gradient-variation",
        r"eq:app-a-material-gradient-ibp",
        r"eq:app-a-material-gradient-scalar-bulk",
        r"C_c^2(\Omega;\mathbb{R}^d)",
        "wall-touching",
    ):
        assert token in appa


def test_t04_code_mirrors_negative_controls_and_units_are_explicit():
    paths = [
        "scripts/python/section_iid_hydrodynamic_balance_sympy.py",
        "scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls",
        "scripts/python/section_iid_hydrodynamic_balance_units.py",
        "scripts/python/appendix_a_reversible_stress_sympy.py",
        "scripts/wolfram/appendix_a_reversible_stress_checks.wls",
        "tests/test_section_iid_hydrodynamic_balances.py",
        "tests/test_appendix_a_reversible_stress.py",
    ]
    assert all((ROOT / path).is_file() for path in paths)
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    assert "entropy_flux_reconstruction_eq_249" in combined
    assert "expected_nonzero_entropy_flux_without_number_balance" in combined
    assert "material_gradient_ibp_with_boundary_A3" in combined
    assert "expected_nonzero_omitted_material_gradient_boundary" in combined
    assert "PASS_DIMENSIONAL" in combined


def test_t04_preserves_local_global_and_variation_boundaries():
    iid = (ROOT / "sections/02d_hydrodynamic_equations.tex").read_text(encoding="utf-8")
    appa = (ROOT / "appendices/A_reversible_stress_plan.tex").read_text(encoding="utf-8")
    assert "not obtained from the local flux identity alone" in iid
    assert "boundary heat" in iid and "surface-energy" in iid
    assert "wall-touching" in appa
    assert "does not manufacture that global" in appa
