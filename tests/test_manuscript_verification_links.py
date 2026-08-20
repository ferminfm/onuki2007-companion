"""Regression checks for the tag-pinned manuscript verification complement."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "link-manifest.json"
OUTPUT = ROOT / "generated" / "manuscript_verification_links.tex"


def test_manifest_has_stable_tag_and_required_topics() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["repository"] == "ferminfm/onuki2007-companion"
    assert data["tag"] == "v0.1.0"
    expected = {
        "iia", "iib", "iic", "iid-balances", "iid-pressure", "appendix-a",
        "appendix-b", "section-iii", "appendix-e", "verification-index",
        "bounded-limitations", "formal-scope",
    }
    assert {topic["topic"] for topic in data["topics"]} == expected
    for topic in data["topics"]:
        assert (ROOT / topic["source"]).is_file()


def test_generated_macros_are_tag_pinned() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_manuscript_link_macros.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "MANUSCRIPT_LINK_MACROS_OK topics=12 tag=v0.1.0" in result.stdout
    generated = OUTPUT.read_text(encoding="utf-8")
    assert "/blob/v0.1.0/" in generated
    assert "batch/" not in generated
    assert "/home/" not in generated


def test_each_required_article_link_is_present_once() -> None:
    sources = {
        "OnukiLinkIIA": "sections/02a_vdw_baseline.tex",
        "OnukiLinkIIB": "sections/02b_gradient_entropy_energy.tex",
        "OnukiLinkIIC": "sections/02c_equilibrium_conditions.tex",
        "OnukiLinkIIDBalances": "sections/02d_hydrodynamic_equations.tex",
        "OnukiLinkIIDPressure": "sections/02d_hydrodynamic_equations.tex",
        "OnukiLinkAppendixA": "appendices/A_reversible_stress_plan.tex",
        "OnukiLinkAppendixB": "appendices/B_scaled_equations_plan.tex",
        "OnukiLinkSectionIII": "sections/03_numerical_results_overview.tex",
        "OnukiLinkAppendixE": "appendices/E_korteweg_primary_source_crosswalk.tex",
        "OnukiLinkVerificationIndex": "sections/00_companion_scope.tex",
        "OnukiLinkFormalScope": "sections/00_companion_scope.tex",
        "OnukiLinkBoundedLimitations": "sections/04_summary_navigation.tex",
    }
    for macro, relpath in sources.items():
        assert (ROOT / relpath).read_text(encoding="utf-8").count(f"\\{macro}") == 1
