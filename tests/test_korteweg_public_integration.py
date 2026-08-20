from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_public_companion_uses_inspected_source_with_bounded_scope() -> None:
    paths = [
        "sections/01_introduction_navigation.tex",
        "sections/02a_vdw_baseline.tex",
        "sections/02d_hydrodynamic_equations.tex",
        "appendices/D_crosswalk_open_issues.tex",
        "appendices/E_korteweg_primary_source_crosswalk.tex",
    ]
    combined = "\n".join(_text(path) for path in paths)
    assert "direct Korteweg 1901 primary source is still missing locally" not in combined
    assert "direct Korteweg 1901 primary source remains missing locally" not in combined
    assert "conditional local" in combined
    assert "full model" in combined or "full-PDE" in combined
    assert "historical-influence" in combined or "historical derivation" in combined


def test_appendix_exposes_verified_formula_and_residual() -> None:
    appendix = _text("appendices/E_korteweg_primary_source_crosswalk.tex")
    required = [
        r"\label{eq:korteweg-capillary-tensor}",
        r"\label{eq:korteweg-capillary-divergence}",
        r"\label{eq:korteweg-onuki-map}",
        r"\label{eq:korteweg-onuki-residual}",
        r"\frac{nK}{T}(\grad n\cdot\grad T)\delta_{ij}",
        "KT01--KT14",
        "KO01--KO11",
        "unpublished simulation code",
    ]
    for item in required:
        assert item in appendix


def test_public_verification_paths_and_lean_theorems_exist() -> None:
    appendix_c = _text("appendices/C_verification_plan.tex")
    appendix_e = _text("appendices/E_korteweg_primary_source_crosswalk.tex")
    for path in [
        "scripts/wolfram/korteweg1901_tensor_trace.wls",
        "scripts/wolfram/korteweg_onuki_crosswalk_checks.wls",
        "scripts/python/korteweg1901_tensor_sympy.py",
        "scripts/python/korteweg1901_tensor_units.py",
        "scripts/python/korteweg_onuki_crosswalk_sympy.py",
        "formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean",
    ]:
        assert (ROOT / path).is_file()
        assert path in appendix_c + appendix_e

    lean = _text("formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean")
    for theorem in [
        "dyadic_gradient_stress_symmetric",
        "finite_stress_contraction_two_dim",
        "capillary_divergence_collection_kernel",
        "pressure_to_cauchy_force_bridge",
        "divergence_match_not_literal_tensor_match",
    ]:
        assert f"theorem {theorem}" in lean
        assert theorem in appendix_c + appendix_e


def test_active_provenance_maps_no_longer_mark_korteweg_missing() -> None:
    lineage = {row["lineage_id"]: row for row in _rows("research_notes/onuki_companion_literature_lineage_map.csv")}
    row = lineage["korteweg_primary"]
    assert row["local_source_status"] == "SOURCE_ATTACHMENT_VERIFIED_COMPLETE_PAGE_IMAGE_VERIFIED"
    assert row["formula_import_status"] == "FINITE_LOCAL_TENSOR_MAP"

    provenance = {row["relation_id"]: row for row in _rows("research_notes/equation_relation_provenance_matrix.csv")}
    law = provenance["LAW:KortewegStressContext"]
    assert law["provenance_status"] == "PRIMARY_SOURCE_PAGE_AUDITED_T07"
    assert law["code_check_status"] == "CODE_PATH_RECORDED"
    assert law["bounded_gap"] == "yes"


def test_b3_and_noncomparable_objects_remain_separate() -> None:
    crosswalk = {row["row_id"]: row for row in _rows("research_notes/korteweg_onuki_equation_crosswalk.csv")}
    assert crosswalk["KOX-014"]["tensor_status"] == "NOT_COMPARABLE"
    assert crosswalk["KOX-014"]["boundary_status"] == "UNPUBLISHED_CODE_UNRESOLVED"
    for row_id in ["KOX-009", "KOX-010", "KOX-011", "KOX-012", "KOX-015"]:
        assert crosswalk[row_id]["tensor_status"] in {"SOURCE_OBJECT_MISSING", "NOT_COMPARABLE"}
