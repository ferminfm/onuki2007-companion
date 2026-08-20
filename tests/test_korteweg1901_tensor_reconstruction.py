from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(None not in row for row in rows)
    return rows


def test_sympy_tensor_reconstruction_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/korteweg1901_tensor_sympy.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Korteweg 1901 tensor SymPy checks" in result.stdout
    assert "divergence_x_collected" in result.stdout
    assert "expected_nonzero_wrong_sign_force" in result.stdout


def test_pint_tensor_dimensions_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/korteweg1901_tensor_units.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Korteweg 1901 tensor Pint checks" in result.stdout
    assert "stress_divergence_force_density" in result.stdout


def test_reconstruction_steps_and_trace_are_complete() -> None:
    steps = _rows("research_notes/korteweg1901_reconstruction_steps.csv")
    assert len(steps) >= 15
    assert {row["status"] for row in steps} >= {
        "SOURCE_TRANSCRIBED",
        "BLACKBOARD_TRACE_COMPLETE",
        "FINITE_KERNEL_VERIFIED",
        "EXPECTED_NONZERO_CONTROL",
    }
    trace = _rows("research_notes/korteweg1901_wolfram_trace_ledger.csv")
    assert [row["trace_id"] for row in trace] == [f"KT{i:02d}" for i in range(1, 15)]
    script = (ROOT / "scripts/wolfram/korteweg1901_tensor_trace.wls").read_text(encoding="utf-8")
    for row in trace:
        assert f'"{row["trace_id"]}"' in script


def test_source_and_modern_conventions_remain_distinct() -> None:
    text = (ROOT / "research_notes/KORTEWEG1901_MODERN_TENSOR_RECONSTRUCTION.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "pressure-positive sign convention" in text
    assert "sigma_ij = -p_ij" in text
    assert "does not identify this four-function family with Onuki" in text
    assert "It is not automatic in this reconstruction" in flat
    registry = {row["registry_id"]: row for row in _rows("research_notes/korteweg1901_sign_convention_registry.csv")}
    assert registry["KSC-001"]["status"] == "EXACT_SIGN_MAP"
    assert registry["KSC-007"]["status"] == "CONDITIONAL_ONLY"
    assert registry["KSC-008"]["status"] == "DIVERGENCE_EQUIVALENT_ONLY"


def test_formal_project_has_only_bounded_kernels_and_no_proof_gaps() -> None:
    source = (ROOT / "formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean").read_text(encoding="utf-8")
    lowered = source.lower()
    assert not re.search(r"\b(sorry|admit|axiom)\b", lowered)
    required = [
        "dyadic_gradient_stress_symmetric",
        "finite_stress_contraction_two_dim",
        "capillary_divergence_collection_kernel",
        "pressure_to_cauchy_force_bridge",
        "divergence_match_not_literal_tensor_match",
        "dyadic_quadratic_nonnegative",
    ]
    for theorem in required:
        assert f"theorem {theorem}" in source
    assessment = (ROOT / "research_notes/KORTEWEG1901_FORMAL_VERIFICATION_ASSESSMENT.md").read_text(encoding="utf-8")
    assert "does not define or differentiate a continuum tensor field" in " ".join(assessment.split())


def test_no_full_model_or_energy_retrofit_claim() -> None:
    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            "research_notes/KORTEWEG1901_MODERN_TENSOR_RECONSTRUCTION.md",
            "research_notes/KORTEWEG1901_FORMAL_VERIFICATION_ASSESSMENT.md",
        ]
    )
    forbidden = [
        "Korteweg's model is formally verified",
        "Onuki equivalence is proved",
        "Korteweg derived interstitial working",
        "full PDE equivalence",
    ]
    for phrase in forbidden:
        assert phrase not in combined
