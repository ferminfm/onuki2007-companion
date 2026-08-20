from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_navigation_figure_files_exist() -> None:
    required = [
        "figures/tikz/source_section_navigation.tex",
        "figures/tikz/section_ii_dependency_flow.tex",
        "figures/tikz/appendix_b_b3_branch_map.tex",
        "figures/tikz/section_iii_scenario_navigation.tex",
        "figures/tikz/coexistence_profile_navigation.tex",
        "figures/tikz/source_to_companion_provenance_map.tex",
    ]
    for path in required:
        text = _read(path)
        assert "\\begin{tikzpicture}" in text
        assert "\\end{tikzpicture}" in text


def test_navigation_figures_are_included_with_bounded_captions() -> None:
    combined = "\n".join(
        [
            _read("sections/00_companion_scope.tex"),
            _read("sections/01_introduction_navigation.tex"),
            _read("sections/02_theory_overview.tex"),
            _read("sections/02a_vdw_baseline.tex"),
            _read("sections/03_numerical_results_overview.tex"),
            _read("appendices/B_scaled_equations_plan.tex"),
        ]
    )
    required = [
        "fig:source-section-navigation",
        "fig:section-ii-dependency-flow",
        "fig:section-iii-scenario-navigation",
        "fig:appendix-b-b3-branch-map",
        "fig:source-to-companion-provenance-map",
        "fig:coexistence-profile-navigation",
        "does not reproduce",
        "unpublished simulation-code branch is not inferred",
        "wall-transfer branch",
    ]
    for phrase in required:
        assert phrase in combined


def test_b3_figure_preserves_branch_boundaries() -> None:
    text = _read("figures/tikz/appendix_b_b3_branch_map.tex")
    assert "Dimensional-source branch" in text
    assert "Printed B3 branch" in text
    assert "Unpublished simulation-code branch" in text
    assert "not inferred" in text


def test_task06_figures_do_not_overclaim() -> None:
    profile = _read("figures/tikz/coexistence_profile_navigation.tex")
    provenance = _read("figures/tikz/source_to_companion_provenance_map.tex")
    sections = "\n".join([
        _read("sections/00_companion_scope.tex"),
        _read("sections/02a_vdw_baseline.tex"),
    ])
    assert "not a sharp jump" in profile
    assert "not a time trajectory" in sections
    assert "sharp-interface" in sections
    assert "jump condition" in sections
    assert "bounded gaps" in provenance
    assert "bounded gaps rather than completed" in sections
    assert "simulation code is known" not in sections.lower()
