from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean"
INDEX = ROOT / "docs/formal/theorem-index.md"

THEOREMS = [
    "dyadic_gradient_stress_symmetric",
    "finite_stress_contraction_two_dim",
    "capillary_divergence_collection_kernel",
    "density_gradient_coefficient_map",
    "density_hessian_coefficient_map",
    "pressure_to_cauchy_force_bridge",
    "divergence_match_not_literal_tensor_match",
    "dyadic_quadratic_nonnegative",
]


def test_every_public_kernel_has_a_reader_page_and_paper_map_row() -> None:
    module = MODULE.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    mapping = (ROOT / "docs/formal/theorem-to-paper-map.csv").read_text(encoding="utf-8")
    for theorem in THEOREMS:
        assert f"theorem {theorem}" in module
        assert f"`{theorem}`" in index
        assert theorem in mapping


def test_formal_project_is_pinned_and_has_no_project_placeholders() -> None:
    formal = ROOT / "formal/korteweg1901_mathlib"
    assert (formal / "lean-toolchain").read_text(encoding="utf-8").strip() == "leanprover/lean4:v4.29.0"
    assert "8a178386ffc0f5fef0b77738bb5449d50efeea95" in (
        formal / "lake-manifest.json"
    ).read_text(encoding="utf-8")
    source = MODULE.read_text(encoding="utf-8")
    assert "sorry" not in source
    assert "admit" not in source
    assert "\naxiom " not in source


def test_reader_material_keeps_the_finite_scope_boundary() -> None:
    scope = (ROOT / "docs/formal-scope.md").read_text(encoding="utf-8").lower()
    index = INDEX.read_text(encoding="utf-8").lower()
    assert "pde" in scope and "full equivalence" in scope
    assert "does not prove entropy production" in index
    assert "does not construct a stress gauge" in index
