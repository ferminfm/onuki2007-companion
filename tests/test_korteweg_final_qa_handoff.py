from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_final_korteweg_review_package_exists_and_is_bounded() -> None:
    qa = _text("research_notes/KORTEWEG_PRIMARY_SOURCE_FINAL_QA.md")
    handoff = _text("research_notes/KORTEWEG_PRIMARY_SOURCE_LAYER1_HANDOFF.md")
    prompt = _text("research_notes/LAYER1_KORTEWEG_PRIMARY_SOURCE_REVIEW_PROMPT.txt")

    assert "READY_FOR_LAYER1_REVIEW_WITH_BOUNDED_GAPS" in qa
    assert "conditional local" in qa.lower()
    assert "does not establish energy, entropy" in qa
    assert "does not self-reference its own commit SHA" in handoff
    assert "Do not merge" in prompt


def test_final_package_preserves_source_and_formal_boundaries() -> None:
    text = "\n".join(
        [
            _text("research_notes/KORTEWEG_PRIMARY_SOURCE_FINAL_QA.md"),
            _text("research_notes/KORTEWEG_PRIMARY_SOURCE_LAYER1_HANDOFF.md"),
            _text("research_notes/LAYER1_KORTEWEG_PRIMARY_SOURCE_REVIEW_PROMPT.txt"),
        ]
    )
    for required in (
        "B3",
        "unpublished",
        "Wolfram",
        "SymPy",
        "Pint",
        "Lean",
        "full model equivalence",
    ):
        assert required in text
    for forbidden in (
        "full Korteweg--Onuki equivalence is established",
        "Korteweg influenced Onuki",
        "simulation code used the",
        "the continuum PDE is formally verified",
    ):
        assert forbidden not in text


def test_adversarial_review_repairs_active_anchor_and_verification_paths() -> None:
    crosswalk = _text("research_notes/KORTEWEG_ONUKI_EQUATION_CROSSWALK.md")
    integration = _text("research_notes/KORTEWEG_PUBLIC_COMPANION_INTEGRATION.md")
    code_map = _text("research_notes/onuki_companion_code_to_paper_map.csv")
    source_ledger = _text("research_notes/ONUKI2007_SOURCE_EQUATION_LEDGER.csv")

    assert "Eqs. (2.47)--(2.48), PRE page 036304-4" in crosswalk
    assert "korteweg1901_tensor_trace.wls" in integration
    assert "korteweg1901_tensor_sympy.py" in integration
    assert "korteweg1901_tensor_reconstruction_checks.wls" not in integration
    assert "korteweg1901_tensor_reconstruction_sympy.py" not in integration
    assert "generated/python/korteweg1901_tensor_sympy_summary.tsv" in code_map
    for equation in ("(2.47)", "(2.48)", "(2.49)", "(2.50)"):
        row = next(line for line in source_ledger.splitlines() if line.startswith(f'"{equation}"'))
        assert ',4,"036304-4",' in row
