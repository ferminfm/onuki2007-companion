import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "research_notes/coauthor_readiness_derivation_repair_queue.csv"
CLOSURE = ROOT / "research_notes/coauthor_readiness_task_closure_evidence.csv"


def read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_all_t03_rows_have_relation_level_closure_evidence():
    queue = [row for row in read(QUEUE) if row["assigned_task"] == "T03-sections-iia-iic-closure"]
    closure = {
        row["relation_id"]: row
        for row in read(CLOSURE)
        if row["task_id"] == "T03-sections-iia-iic-closure"
    }
    assert queue
    assert set(closure) == {row["relation_id"] for row in queue}
    assert all(row["status"] == "CLOSED_T03_VERIFIED" for row in queue)
    assert all(row["closure_status"] == "CLOSED_T03_VERIFIED" for row in closure.values())
    assert all(row["source_page_evidence"] for row in closure.values())
    assert all(row["visible_derivation_evidence"] for row in closure.values())
    assert all(row["mechanical_check_evidence"] for row in closure.values())
    assert all(row["negative_control_evidence"] for row in closure.values())


def test_t03_public_sections_expose_dossier_required_steps():
    iia = (ROOT / "sections/02a_vdw_baseline.tex").read_text(encoding="utf-8")
    iib = (ROOT / "sections/02b_gradient_entropy_energy.tex").read_text(encoding="utf-8")
    iic = (ROOT / "sections/02c_equilibrium_conditions.tex").read_text(encoding="utf-8")

    for token in (
        r"\left(\frac{\partial T}{\partial n}\right)_s",
        r"\dd p=n\,\dd\mu",
        r"[M n_x\eta]_{\partial}",
        r"\mu_{\rm cx}",
        r"\omega-\omega_{\rm cx}",
        "monotone",
        r"eq:iia-surface-tension-density-change",
    ):
        assert token in iia

    for token in (
        r"\hat e_\varepsilon=\hat e+\varepsilon\xi",
        r"M_n|_T",
        r"\grad M=M_n|_T\,\grad n+M_T|_n\,\grad T",
        r"\int_{\partial\Omega}",
        "fixed density variation",
        "global entropy/energy",
    ):
        assert token in iib

    for token in (
        r"T=\frac{1}{k_B\beta}",
        r"\hat\mu=k_B T\lambda_N=\mathrm{constant}",
        r"\left(\frac{\partial f_s}{\partial n}\right)_T",
        r"M\nu\cdot\grad n-a_s+b_s(n-n_c)=0",
        "so the constant is zero",
        "monotone interface",
    ):
        assert token in iic


def test_t03_code_mirrors_and_negative_controls_are_explicit():
    paths = [
        "scripts/python/section_iia_vdw_baseline_sympy.py",
        "scripts/wolfram/section_iia_vdw_baseline_checks.wls",
        "scripts/python/section_iib_gradient_entropy_sympy.py",
        "scripts/wolfram/section_iib_gradient_entropy_checks.wls",
        "scripts/python/section_iic_equilibrium_wall_sympy.py",
        "scripts/wolfram/section_iic_equilibrium_wall_checks.wls",
        "tests/test_section_iia_vdw_baseline.py",
        "tests/test_section_iib_gradient_entropy.py",
        "tests/test_section_iic_equilibrium_wall.py",
    ]
    assert all((ROOT / path).is_file() for path in paths)
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
    assert "expected_nonzero" in combined.lower() or "negative" in combined.lower()
    assert "surface_tension_monotone_density_change" in combined
    assert "surface_tension_wrong_orientation_negative_control" in combined
    assert "formal erratum" in (ROOT / "sections/02a_vdw_baseline.tex").read_text(encoding="utf-8").lower()
