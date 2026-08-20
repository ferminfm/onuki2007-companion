from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _rows() -> list[dict[str, str]]:
    with (ROOT / "research_notes/korteweg_onuki_equation_crosswalk.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 16
    assert all(None not in row for row in rows)
    return rows


def test_sympy_crosswalk_residuals_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/korteweg_onuki_crosswalk_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Korteweg--Onuki crosswalk SymPy checks" in result.stdout
    assert "general_nonisothermal_tensor_residual" in result.stdout
    assert "expected_nonzero_general_force_residual" in result.stdout


def test_exact_rows_name_restrictions_and_both_anchors() -> None:
    rows = _rows()
    exact = [row for row in rows if row["tensor_status"] == "EXACT_UNDER_RESTRICTED_BRANCH"]
    assert len(exact) == 3
    for row in exact:
        assert row["korteweg_anchor"]
        assert row["onuki_anchor"]
        assert row["assumptions"]
        assert row["coefficient_map"]


def test_general_residual_and_hessian_limit_are_explicit() -> None:
    rows = {row["row_id"]: row for row in _rows()}
    assert rows["KOX-003"]["tensor_status"] == "DISCREPANCY_MIXED_GRADIENT_RESIDUAL"
    assert "nK/T" in rows["KOX-003"]["onuki_expression"]
    assert rows["KOX-007"]["tensor_status"] == "KORTEWEG_FAMILY_STRICTLY_BROADER"
    assert "delta_K=0" in rows["KOX-007"]["coefficient_map"]


def test_energy_entropy_wall_and_b3_boundaries_remain_bounded() -> None:
    rows = {row["row_id"]: row for row in _rows()}
    for row_id in ("KOX-009", "KOX-010", "KOX-011", "KOX-012", "KOX-015"):
        assert rows[row_id]["tensor_status"] == "SOURCE_OBJECT_MISSING"
    assert rows["KOX-014"]["tensor_status"] == "NOT_COMPARABLE"
    assert rows["KOX-014"]["boundary_status"] == "UNPUBLISHED_CODE_UNRESOLVED"


def test_decision_is_partial_local_embedding_not_full_equivalence() -> None:
    decision = (ROOT / "research_notes/KORTEWEG_ONUKI_EQUIVALENCE_DECISION.md").read_text(
        encoding="utf-8"
    )
    assert "PARTIAL_CONDITIONAL_LOCAL_STRESS_EMBEDDING" in decision
    assert "not unrestricted equation equality" in decision
    assert "unpublished implementation behavior is unknown" in decision


def test_dependency_map_records_t05_boundary() -> None:
    dependency = (ROOT / "research_notes/ONUKI2007_EQUATION_DEPENDENCY_GRAPH.md").read_text(
        encoding="utf-8"
    )
    assert "T05 Korteweg--Onuki Crosswalk" in dependency
    assert "mixed density--temperature-gradient residual" in dependency
