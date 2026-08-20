import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "research_notes"


def test_final_package_files_exist_and_are_substantive():
    required = [
        "COAUTHOR_READING_GUIDE.md",
        "COAUTHOR_READINESS_CHANGE_SUMMARY.md",
        "COAUTHOR_SOURCE_EQUATION_NAVIGATION.md",
        "COAUTHOR_VERIFICATION_NAVIGATION.md",
        "COAUTHOR_READINESS_REMAINING_QUESTIONS.md",
        "COAUTHOR_READINESS_FINAL_QA.md",
        "LAYER1_COAUTHOR_READINESS_REVIEW_PROMPT.txt",
    ]
    for name in required:
        text = (NOTES / name).read_text(encoding="utf-8")
        assert len(text.splitlines()) >= 8, name


def test_issue_ledger_has_no_stale_open_rows():
    with (NOTES / "COAUTHOR_READINESS_ISSUE_LEDGER.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert rows
    assert not [row for row in rows if row["status"] == "OPEN"]
    deferred = {row["stable_id"] for row in rows if row["status"] == "FROZEN_DEFERRED"}
    assert {"CR-014", "CR-022", "CR-023", "CR-024", "CR-025", "CR-026"} <= deferred


def test_package_preserves_bounded_scientific_questions():
    combined = "\n".join(
        (NOTES / name).read_text(encoding="utf-8")
        for name in [
            "COAUTHOR_READING_GUIDE.md",
            "COAUTHOR_READINESS_REMAINING_QUESTIONS.md",
            "COAUTHOR_READINESS_FINAL_QA.md",
        ]
    )
    required = [
        "unpublished",
        "local",
        "global",
        "B3",
        "Korteweg",
        "numerical reproduction",
    ]
    for phrase in required:
        assert phrase in combined
    forbidden = [
        "full Korteweg--Onuki equivalence is established",
        "the simulations are reproduced",
        "is an official erratum",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_independent_reader_claim_labels_are_bounded():
    scope = (ROOT / "sections/00_companion_scope.tex").read_text(encoding="utf-8")
    iia = (ROOT / "sections/02a_vdw_baseline.tex").read_text(encoding="utf-8")
    iii = (ROOT / "sections/03a_method_scaled_equations.tex").read_text(encoding="utf-8")
    appb = (ROOT / "appendices/B_scaled_equations_plan.tex").read_text(encoding="utf-8")
    navigation = (NOTES / "COAUTHOR_VERIFICATION_NAVIGATION.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert 'badge beginning with ``Companion\'\'' in scope
    assert "companionbranchbadge{derived 2.5 branch}" in iia
    assert "companionbranchbadge{scaled from 2.47--2.48}" in appb
    assert "not an independent derivation of the denominator" in iii
    assert "high-confidence typographical-omission candidate" in appb
    assert "Contextual or nonalgebraic rows" in navigation
    assert "../Fukagawa2021/references/" not in readme
