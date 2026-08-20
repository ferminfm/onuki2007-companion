from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


PUBLIC_FILES = [
    ROOT / "main.tex",
    ROOT / "README.md",
    *sorted((ROOT / "sections").glob("*.tex")),
    *sorted((ROOT / "appendices").glob("*.tex")),
    *sorted((ROOT / "figures/tikz").glob("*.tex")),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_abstract_and_readme_match_actual_coverage():
    abstract = read(ROOT / "main.tex")
    readme = read(ROOT / "README.md")
    assert "Section II.A equilibrium baseline" in abstract
    assert "Appendix E reconstructs" in abstract
    assert "Section II.A derives" in readme
    assert "II.A/II.B/II.C/II.D" in readme


def test_public_files_do_not_expose_internal_workflow_language():
    combined = "\n".join(read(path) for path in PUBLIC_FILES).lower()
    for forbidden in (
        "batch-internal",
        "for maintainers",
        "repair queue",
        "blackboard-level",
        "copyright-boundary",
        "scanner/distributor provenance",
        "future-work support only",
    ):
        assert forbidden not in combined


def test_korteweg_partial_derivative_and_restrictions_are_typed():
    appendix = read(ROOT / "appendices/E_korteweg_primary_source_crosswalk.tex")
    figure = read(ROOT / "figures/tikz/korteweg_onuki_tensor_map.tex")
    assert r"M_n|_T:=\left(\frac{\partial M}{\partial n}\right)_T" in appendix
    assert "thermodynamic partial derivative at fixed temperature" in appendix
    assert "not a constitutive model branch" in appendix
    assert "sufficient source-supported restrictions" in figure


def test_scientific_boundaries_remain_explicit():
    appendix = read(ROOT / "appendices/E_korteweg_primary_source_crosswalk.tex")
    crosswalk = read(ROOT / "appendices/D_crosswalk_open_issues.tex")
    for token in (
        "not the whole Korteweg family",
        "does not establish an integrated balance or historical",
        "unpublished simulation code",
    ):
        assert token in appendix
    assert "source-branch discrepancy rather than an official erratum" in crosswalk
    assert "unpublished simulation-code branch remains unresolved" in crosswalk
    assert "Local flux-gauge identities do not imply integrated balance equalities" in crosswalk
