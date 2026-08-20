from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def _flat(path: str) -> str:
    return " ".join(_read(path).split())


def test_section_iii_estimate_checks_pass() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/python/section_iii_simulation_estimates.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "PASS: Section III simulation-estimate checks" in result.stdout
    required = [
        "section_iii_sigma_forms",
        "transport_density_ratio_1p70_over_0p27",
        "sound_As_eq39_denominator",
        "acoustic_traversal_time_scale",
        "capillary_wave_eq311_scaling",
        "inverse_compressibility_eq312",
        "adiabatic_coefficient_eq314_d2",
        "latent_heat_velocity_gradient_branch",
        "one_phase_nusselt_no_convection",
        "adiabatic_gradient_order_eq320",
        "heat_flux_normalization_q0_units",
        "section_iii_no_numerical_reproduction_gate",
        "section_iii_b3_simulation_code_branch",
    ]
    for check_id in required:
        assert check_id in result.stdout


def test_section_iii_overview_declares_no_reproduction() -> None:
    text = _flat("sections/03_numerical_results_overview.tex")
    required = [
        "reading guide",
        "source-described numerical example, not a reproduced run",
        "does not reconstruct the simulation code",
        "unpublished simulation-code branch",
        "does not validate the numerical results",
        "companion estimate checks",
    ]
    for phrase in required:
        assert phrase in text
    assert "scripts/wolfram/section\\_iii\\_simulation\\_estimates\\_checks.wls" in text
    assert (ROOT / "scripts/wolfram/section_iii_simulation_estimates_checks.wls").is_file()


def test_all_section_iii_files_are_substantive_guides() -> None:
    files = [
        "sections/03a_method_scaled_equations.tex",
        "sections/03b_adiabatic_expansion.tex",
        "sections/03c_piston_effect.tex",
        "sections/03d_heat_flow_two_phase.tex",
        "sections/03e_steady_heat_conduction.tex",
        "sections/03f_boiling_gravity.tex",
        "sections/03g_wetting_dynamics.tex",
    ]
    forbidden = ["will plan", "Planned derivations", "Planned verification checks"]
    for path in files:
        text = _flat(path)
        assert "Reading Guide" in text or "Typed Simulation Objects" in text
        assert "Limitations" in text or "Open Issues" in text
        for phrase in forbidden:
            assert phrase not in text


def test_scenario_map_preserves_source_boundaries() -> None:
    with (ROOT / "research_notes/onuki_section_iii_scenario_map.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    by_id = {row["scenario_id"]: row for row in rows}
    assert by_id["III-A-method"]["companion_status"] == "READING_GUIDE_POLICY_AUDITED"
    assert "B3 simulation-code branch unresolved" in by_id["III-A-method"]["open_issue"]
    assert "No bubble dynamics reproduced" in by_id["III-F-boiling-gravity"]["no_reproduction_note"]
    assert "No spreading law" in by_id["III-G-wetting-dynamics"]["no_reproduction_note"]


def test_research_note_states_copyright_and_no_numerics() -> None:
    text = _flat("research_notes/SECTION_III_SIMULATION_READING_GUIDE.md")
    assert "does not reproduce figures" in text
    assert "does not validate the numerical scheme" in text
    assert "does not reproduce source text" in text
    assert "The original article remains required reading" in text

def test_task06_audit_artifacts_exist_and_mark_no_reproduction() -> None:
    audit = _flat("research_notes/SECTION_III_SCENARIO_PROOF_AUDIT.md")
    assert "not a reproduction project" in audit
    assert "READING_GUIDE_POLICY_AUDITED" in audit
    public_audit = _flat("research_notes/SECTION_III_PUBLIC_PASS_AUDIT.md")
    assert "COMPLETE_VERIFIED" in public_audit
    assert "not a numerical reproduction" in public_audit
    assert "unpublished simulation-code branch remains unresolved" in public_audit
    with (ROOT / "research_notes/section_iii_scenario_proof_matrix.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    assert {row["policy_audit_status"] for row in rows} == {"READING_GUIDE_POLICY_AUDITED"}
    assert all(row["no_reproduction_status"] == "PASS" for row in rows)


def test_public_pass_estimate_displays_are_source_labeled() -> None:
    combined = "\n".join(
        [
            _flat("sections/03a_method_scaled_equations.tex"),
            _flat("sections/03b_adiabatic_expansion.tex"),
            _flat("sections/03c_piston_effect.tex"),
            _flat("sections/03d_heat_flow_two_phase.tex"),
            _flat("sections/03e_steady_heat_conduction.tex"),
            _flat("sections/03f_boiling_gravity.tex"),
            _flat("sections/03g_wetting_dynamics.tex"),
        ]
    )
    required = [
        r"\sourceeqbadge{3.5--3.6}",
        r"\sourceeqbadge{3.12}",
        r"\sourceeqbadge{3.13}",
        r"\sourceeqbadge{3.15}",
        r"\sourceeqbadge{3.16}",
        r"\sourceeqbadge{3.17}",
        r"\sourceeqbadge{3.18}",
        r"\sourceeqbadge{3.19}",
        r"\sourceeqbadge{3.20}",
        "Estimate Ledger",
        "branch data",
        "boundary objects",
        "not validations of the computed acoustic response",
        "not the flow field itself",
        "No steady heat-conduction solution",
        "does not determine a boiling threshold",
    ]
    for phrase in required:
        assert phrase in combined


def test_linebyline_task05_estimate_detail_audit_exists() -> None:
    text = _flat("research_notes/SECTION_III_ESTIMATE_DETAIL_AUDIT.md")
    required = [
        "COMPLETE_VERIFIED",
        "finite estimate ledgers",
        "does not reproduce numerical data",
        "unpublished simulation-code branch remains unresolved",
        "Any numerical reproduction requires a separate authorization",
    ]
    for phrase in required:
        assert phrase in text



def test_task09_dossier_derivations_are_visible() -> None:
    method = _flat("sections/03a_method_scaled_equations.tex")
    adiabatic = _flat("sections/03b_adiabatic_expansion.tex")
    piston = _flat("sections/03c_piston_effect.tex")
    conduction = _flat("sections/03e_steady_heat_conduction.tex")
    gravity = _flat("sections/03f_boiling_gravity.tex")
    wetting = _flat("sections/03g_wetting_dynamics.tex")

    required_by_file = {
        "method": [
            "Transport Ratio from Density-Proportional Coefficients",
            "Sound Scale, Eq. (3.9), and the Eq. (2.5) Denominator",
            "Acoustic Traversal and Damping Estimates",
            "Capillary-Wave Frequency Estimate",
            r"\sourceeqbadge{3.9}",
            r"\sourceeqbadge{3.10}",
            r"\sourceeqbadge{3.11}",
            "not a statement about the unpublished numerical code",
        ],
        "adiabatic": [
            r"\sourceeqbadge{3.12}",
            "spinodal-temperature definition gives",
            "not integrated over the cell",
        ],
        "piston": [
            r"\sourceeqbadge{3.13}",
            r"\sourceeqbadge{3.14}",
            r"\sourceeqbadge{3.15}",
            r"\sourceeqbadge{3.16}",
            "far-field heat-flux branch",
        ],
        "conduction": [
            "one-phase no-convection estimate",
            r"\sourceeqbadge{3.19}",
            "not a calculation of the two-phase convective state",
        ],
        "gravity": [
            r"\sourceeqbadge{3.20}",
            "scale estimate, not an exact equality",
            "does not determine a boiling threshold",
        ],
        "wetting": [
            "Q_0",
            "heat-flux units",
            "not a new boundary law",
        ],
    }
    texts = {
        "method": method,
        "adiabatic": adiabatic,
        "piston": piston,
        "conduction": conduction,
        "gravity": gravity,
        "wetting": wetting,
    }
    for label, phrases in required_by_file.items():
        for phrase in phrases:
            assert phrase in texts[label], (label, phrase)
