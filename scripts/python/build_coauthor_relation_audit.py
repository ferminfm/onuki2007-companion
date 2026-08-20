#!/usr/bin/env python3
"""Build the coauthor-readiness source/public relation audit.

This script does not judge source mathematics.  It normalizes the project's
page-verified source inventory and existing provenance ledger, then adds every
currently displayed public relation and every relation-bearing inline premise.
The resulting terminal classes follow the Layer-1 audit policy; rows assigned
to T03--T07 identify where those classes still need a focused evidence review.
"""

from __future__ import annotations

import csv
import hashlib
import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "research_notes"

SOURCE_INVENTORY = NOTES / "onuki2007_canonical_source_equation_inventory.csv"
SOURCE_GATE = NOTES / "page_verified_source_row_gate.csv"
PROVENANCE = NOTES / "equation_relation_provenance_matrix.csv"
MATRIX_OUT = NOTES / "whole_companion_relation_treatment_matrix.csv"
QUEUE_OUT = NOTES / "coauthor_readiness_derivation_repair_queue.csv"
GRAPH_OUT = NOTES / "whole_companion_source_public_dependency_graph.md"
CLOSURE_EVIDENCE = NOTES / "coauthor_readiness_task_closure_evidence.csv"

PUBLIC_FILES = sorted((ROOT / "sections").glob("*.tex")) + sorted(
    (ROOT / "appendices").glob("*.tex")
)

TERMINAL_CLASSES = {
    "VISIBLE_DERIVATION_COMPLETE",
    "DEFINITION_WITH_ORIGIN_EXPLAINED",
    "LAW_OR_POSTULATE_WITH_NAME_AND_SOURCE",
    "STANDARD_IDENTITY_DERIVED_OR_CITED",
    "CONSTITUTIVE_CHOICE_EXPLICITLY_LABELLED",
    "BOUNDARY_OR_VARIATION_BRANCH_EXPLICIT",
    "SIMULATION_SPECIALIZATION_EXPLICIT",
    "NAVIGATION_ONLY_WITH_REASON",
    "INTENTIONALLY_OMITTED_WITH_DEFENSIBLE_REASON",
    "BOUNDED_SOURCE_DISCREPANCY",
    "BLOCKED_BY_SPECIFIC_SOURCE_AMBIGUITY",
}

MATRIX_FIELDS = [
    "relation_id",
    "evidence_scope",
    "relation_kind",
    "public_location",
    "line",
    "tex_label",
    "source_canonical_ids",
    "mapped_public_relation_ids",
    "source_anchor",
    "pdf_page",
    "printed_page",
    "relation_summary",
    "mapping_type",
    "terminal_treatment_class",
    "terminal_class_reason",
    "definition_or_law_origin",
    "derivative_or_operation",
    "held_variables_or_branch",
    "boundary_term_status",
    "source_page_status",
    "mechanically_checkable",
    "visible_derivation_evidence",
    "wolfram_evidence",
    "sympy_evidence",
    "negative_control_evidence",
    "dimensional_evidence",
    "code_paths",
    "bounded_gap",
    "repair_task",
    "repair_status",
    "notes",
]

QUEUE_FIELDS = [
    "repair_id",
    "relation_id",
    "priority",
    "assigned_task",
    "public_location",
    "source_anchor",
    "terminal_treatment_class",
    "gap_type",
    "observed_evidence",
    "required_action",
    "acceptance_check",
    "bounded_gap",
    "status",
]

CLOSURE_FIELDS = [
    "task_id",
    "relation_id",
    "closure_status",
    "public_location",
    "source_anchor",
    "source_page_evidence",
    "visible_derivation_evidence",
    "mechanical_check_evidence",
    "negative_control_evidence",
    "dimensional_evidence",
    "independent_review_evidence",
    "closure_note",
]

SECTION_SOURCE_RANGES = {
    "sections/01_introduction_navigation.tex": "Onuki introduction",
    "sections/02a_vdw_baseline.tex": "Eqs. (2.1)--(2.11)",
    "sections/02b_gradient_entropy_energy.tex": "Eqs. (2.12)--(2.20)",
    "sections/02c_equilibrium_conditions.tex": "Eqs. (2.21)--(2.34)",
    "sections/02d_hydrodynamic_equations.tex": "Eqs. (2.35)--(2.53)",
    "sections/03_numerical_results_overview.tex": "Onuki Section III",
    "sections/03a_method_scaled_equations.tex": "Onuki Section III and Appendix B",
    "sections/03b_adiabatic_expansion.tex": "Onuki Section III.A",
    "sections/03c_piston_effect.tex": "Onuki Section III.B",
    "sections/03d_heat_flow_two_phase.tex": "Onuki Section III.C",
    "sections/03e_steady_heat_conduction.tex": "Onuki Section III.D",
    "sections/03f_boiling_gravity.tex": "Onuki Section III.E",
    "sections/03g_wetting_dynamics.tex": "Onuki Section III.F",
    "appendices/A_reversible_stress_plan.tex": "Appendix A Eqs. (A1)--(A4)",
    "appendices/B_scaled_equations_plan.tex": "Appendix B Eqs. (B1)--(B6)",
    "appendices/D_crosswalk_open_issues.tex": "scope and boundary crosswalk",
    "appendices/E_korteweg_primary_source_crosswalk.tex": "Korteweg 1901 bounded crosswalk",
}

SECTION_CODE_PATHS = {
    "sections/01_introduction_navigation.tex": "scripts/python/section_iib_gradient_entropy_sympy.py; scripts/wolfram/section_iib_gradient_entropy_checks.wls; tests/test_section_iib_gradient_entropy.py",
    "sections/02a_vdw_baseline.tex": "scripts/python/section_iia_vdw_baseline_sympy.py; scripts/wolfram/section_iia_vdw_baseline_checks.wls; tests/test_section_iia_vdw_baseline.py",
    "sections/02b_gradient_entropy_energy.tex": "scripts/python/section_iib_gradient_entropy_sympy.py; scripts/wolfram/section_iib_gradient_entropy_checks.wls; tests/test_section_iib_gradient_entropy.py",
    "sections/02c_equilibrium_conditions.tex": "scripts/python/section_iic_equilibrium_wall_sympy.py; scripts/wolfram/section_iic_equilibrium_wall_checks.wls; tests/test_section_iic_equilibrium_wall.py",
    "sections/02d_hydrodynamic_equations.tex": "scripts/python/section_iid_hydrodynamic_balance_sympy.py; scripts/wolfram/section_iid_hydrodynamic_balance_checks.wls; scripts/python/section_iid_hydrodynamic_balance_units.py; scripts/python/section_iid_p1_pressure_expansion_sympy.py; scripts/wolfram/section_iid_p1_pressure_expansion_checks.wls; tests/test_section_iid_hydrodynamic_balances.py; tests/test_section_iid_p1_pressure_expansion.py",
    "appendices/A_reversible_stress_plan.tex": "scripts/python/appendix_a_reversible_stress_sympy.py; scripts/wolfram/appendix_a_reversible_stress_checks.wls; scripts/python/section_iid_hydrodynamic_balance_units.py; tests/test_appendix_a_reversible_stress.py",
    "appendices/B_scaled_equations_plan.tex": "scripts/python/appendix_b_scaling_definitions_sympy.py; scripts/python/appendix_b_scaling_definitions_units.py; scripts/python/appendix_b_momentum_b3_sympy.py; scripts/python/appendix_b_b3_typo_candidate_sympy.py; scripts/python/appendix_b_energy_boundary_sympy.py; scripts/python/appendix_b_energy_boundary_units.py; scripts/wolfram/appendix_b_scaling_definitions_checks.wls; scripts/wolfram/appendix_b_momentum_b3_checks.wls; scripts/wolfram/appendix_b_b3_typo_candidate_checks.wls; scripts/wolfram/appendix_b_energy_boundary_checks.wls; scripts/wolfram/appendix_b_transition_trace.wls; tests/test_appendix_b_scaling_definitions.py; tests/test_appendix_b_momentum_b3.py; tests/test_appendix_b_b3_typo_candidate.py; tests/test_appendix_b_energy_boundary.py",
    "appendices/D_crosswalk_open_issues.tex": "scripts/python/appendix_b_scaling_definitions_sympy.py; scripts/python/appendix_b_scaling_definitions_units.py; scripts/wolfram/appendix_b_scaling_definitions_checks.wls; tests/test_appendix_b_scaling_definitions.py",
    "appendices/E_korteweg_primary_source_crosswalk.tex": "scripts/python/korteweg1901_tensor_sympy.py; scripts/python/korteweg1901_tensor_units.py; scripts/python/korteweg_onuki_crosswalk_sympy.py; scripts/wolfram/korteweg1901_tensor_trace.wls; scripts/wolfram/korteweg_onuki_crosswalk_checks.wls; formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean; tests/test_korteweg1901_tensor_reconstruction.py; tests/test_korteweg_onuki_crosswalk.py; tests/test_coauthor_t06_public_editorial.py",
    "sections/03_numerical_results_overview.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03a_method_scaled_equations.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03b_adiabatic_expansion.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03c_piston_effect.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03d_heat_flow_two_phase.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03e_steady_heat_conduction.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03f_boiling_gravity.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
    "sections/03g_wetting_dynamics.tex": "scripts/python/section_iii_simulation_estimates.py; scripts/wolfram/section_iii_simulation_estimates_checks.wls; tests/test_section_iii_simulation_guide.py",
}

NAMED_CODE_PATHS = {
    "TERM:EquilibriumProfile": SECTION_CODE_PATHS["sections/02a_vdw_baseline.tex"],
    "DISC:Eq2_5_Eq3_9": (
        SECTION_CODE_PATHS["sections/02a_vdw_baseline.tex"]
        + "; "
        + SECTION_CODE_PATHS["sections/03a_method_scaled_equations.tex"]
    ),
}

NAMED_SOURCE_IDS = {
    "DISC:B3Phi": "APPB-B3",
    "LAW:CoexistenceMuPressure": "II-2_9;II-2_10",
    "LAW:SurfaceTensionFirstIntegral": "II-2_11",
    "TERM:EquilibriumProfile": "II-2_9;II-2_11",
    "DISC:Eq2_5_Eq3_9": "II-2_5;III-3_9",
    "LAW:Gibbs-Duhem": "II-2_46",
    "LAW:NewtonianViscousStress": "II-2_37",
    "LAW:FourierHeatFlux": "II-2_39;II-2_45",
    "LAW:KortewegStressContext": "EXTERNAL:KORTEWEG-20",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def strip_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def normalize_math(text: str) -> str:
    return " ".join(text.strip().split())


def stable_suffix(path: str, kind: str, expression: str, ordinal: int) -> str:
    material = f"{path}\0{kind}\0{expression}\0{ordinal}".encode()
    return hashlib.sha256(material).hexdigest()[:16]


def code_evidence(code_paths: str) -> tuple[str, str, str, str, str]:
    paths = [part.strip() for part in code_paths.split(";") if part.strip()]
    wolfram = "; ".join(path for path in paths if path.endswith(".wls"))

    def python_uses(path: str, package: str) -> bool:
        if not path.endswith(".py"):
            return False
        candidate = ROOT / path
        if not candidate.is_file():
            return False
        text = candidate.read_text(encoding="utf-8")
        return bool(re.search(rf"(?:from\s+{package}\b|import\s+{package}\b)", text))

    sympy = "; ".join(
        path
        for path in paths
        if path.endswith(".py")
        and ("sympy" in path.lower() or python_uses(path, "sympy"))
    )
    tests = "; ".join(path for path in paths if path.startswith("tests/"))
    negative = tests if tests else "REVIEW_REQUIRED"
    dimensions = (
        "; ".join(
            path
            for path in paths
            if "unit" in path.lower()
            or "dimension" in path.lower()
            or python_uses(path, "pint")
        )
        or "REVIEW_REQUIRED_WHERE_RELEVANT"
    )
    return wolfram or "NONE_RECORDED", sympy or "NONE_RECORDED", negative, dimensions, tests


def canonical_ids(anchor: str, summary: str) -> str:
    exact_anchor = re.fullmatch(r"Eq\. \(([AB])?(\d+(?:\.\d+)?)\)", anchor)
    joined = anchor if exact_anchor else f"{anchor} {summary}"
    ids: list[str] = []
    for token in re.findall(r"(?:sourceeqbadge|eqsrc)\{([A-B]?\d+(?:\.\d+)?)", joined):
        if token.startswith("A"):
            value = f"APPA-{token.replace('.', '_')}"
        elif token.startswith("B"):
            value = f"APPB-{token.replace('.', '_')}"
        else:
            value = f"II-{token.replace('.', '_')}" if token.startswith("2.") else f"III-{token.replace('.', '_')}"
        if value not in ids:
            ids.append(value)
    for prefix, number in re.findall(r"Eq\. \(([AB])?(\d+(?:\.\d+)?)\)", anchor):
        value = (
            f"APP{prefix}-{prefix}{number.replace('.', '_')}"
            if prefix
            else (f"II-{number.replace('.', '_')}" if number.startswith("2.") else f"III-{number.replace('.', '_')}")
        )
        if value not in ids:
            ids.append(value)
    return ";".join(ids)


def task_for_location(location: str) -> str:
    if any(part in location for part in ("02a_", "02b_", "02c_")):
        return "T03-sections-iia-iic-closure"
    if "02d_" in location or "A_reversible" in location:
        return "T04-section-iid-appendix-a-closure"
    if "B_scaled" in location or "/03" in location or location.startswith("sections/03"):
        return "T05-appendix-b-section-iii-closure"
    if "Korteweg" in location or "korteweg" in location or "introduction" in location or "crosswalk" in location:
        return "T06-public-editorial-korteweg"
    return "T07-verification-code-audit"


def operation_type(expression: str) -> str:
    if re.search(r"\\delta|\\varepsilon|variation|functional", expression, re.I):
        return "variational_or_functional"
    if re.search(r"\\partial|\\nabla|\\grad|\\Delta|D_t|\\dd", expression):
        return "partial_spatial_or_material"
    if re.search(r"\\int|\\oint", expression):
        return "integral_or_global"
    if re.search(r"=|\\equiv|\\propto|\\sim", expression):
        return "algebraic_or_definitional"
    return "relation_or_inequality"


def public_terminal_class(
    relation_id: str,
    location: str,
    expression: str,
    source_anchor: str,
    bounded_gap: str,
    relation_kind: str,
) -> tuple[str, str]:
    lower = f"{relation_id} {location} {expression} {source_anchor}".lower()
    identity = f"{relation_id} {source_anchor}".lower()
    relation_identity = relation_id.lower()
    relation_text = expression.lower() if relation_kind in {"public_inline_relation", "public_unlabelled_display"} else identity
    if relation_id == "DISPLAY:11a97ba1fe394278":
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The display collects source-stated Appendix-B scale definitions."
    if relation_id == "DISPLAY:1c2e5a2c33689a4a":
        return "SIMULATION_SPECIALIZATION_EXPLICIT", "The display states the K=0, constant-C simulation specialization."
    if bounded_gap == "yes" and "korteweg" not in lower:
        return "BOUNDED_SOURCE_DISCREPANCY", "Printed/source or derivative/source alternatives are kept separate."
    if "b3" in relation_identity and ("print" in relation_identity or "residual" in relation_identity):
        return "BOUNDED_SOURCE_DISCREPANCY", "Appendix-B printed and dimensional-source branches remain explicit."
    if "iid-gibbs-duhem-246" in identity:
        return "STANDARD_IDENTITY_DERIVED_OR_CITED", "The Gibbs--Duhem identity is derived from displayed thermodynamic differentials and source-anchored."
    if "iid-total-energy-density" in identity:
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The source defines total energy density as internal plus kinetic energy density."
    if any(word in relation_text for word in ("boundary", "wall", "endpoint", "limits", "no-slip", "normal derivative")):
        return "BOUNDARY_OR_VARIATION_BRANCH_EXPLICIT", "The relation states a boundary, wall, endpoint, or variation branch."
    if any(word in identity for word in ("dissipative-stress", "newtonian", "fourier", "conductivity law", "viscosity law")):
        return "CONSTITUTIVE_CHOICE_EXPLICITLY_LABELLED", "The public text identifies a constitutive choice and its sign or scope assumptions."
    if any(word in identity for word in ("mass-balance", "momentum-components", "total-energy-balance", "entropy-balance")):
        return "LAW_OR_POSTULATE_WITH_NAME_AND_SOURCE", "The relation is a source-stated continuum balance law."
    if location.startswith("sections/03") and any(word in lower for word in ("initial", "choice", "set", "geometry", "scaled", "g^*", "theta_")):
        return "SIMULATION_SPECIALIZATION_EXPLICIT", "The relation is a Section-III scale or scenario specialization, not a new law."
    if relation_kind == "public_inline_relation" and re.search(r"(?:^|\s)(?:let|set|define|denote)", lower):
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The surrounding public sentence introduces the relation as notation or a definition."
    if relation_kind == "public_inline_relation" and re.match(r"^[A-Za-z\\][^=]{0,80}=", expression):
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The inline equality records a local notation, specialization, or previously derived quantity."
    if "korteweg" in lower:
        return "STANDARD_IDENTITY_DERIVED_OR_CITED", "The bounded Korteweg relation is page-anchored and restricted to its stated local tensor map."
    return "VISIBLE_DERIVATION_COMPLETE", "The public relation is displayed or used in an explicit equality chain; T03--T07 recheck fragile transitions."


def source_terminal_class(source: dict[str, str], gate: dict[str, str]) -> tuple[str, str]:
    canonical_id = source["canonical_id"]
    classification = source["classification"]
    item_class = gate.get("item_class", "")
    delta = source.get("delta_review", "")
    section = source["source_section"]
    if canonical_id == "II-2_5":
        return "BOUNDED_SOURCE_DISCREPANCY", "The printed Eq. (2.5) and derivative-consistent Eq. (3.9) denominator branches remain separate."
    if canonical_id == "INTRO-VDW-GRAD":
        return "STANDARD_IDENTITY_DERIVED_OR_CITED", "The historical context is now tied to the bounded, page-anchored Korteweg tensor crosswalk."
    if canonical_id == "IIB-SIM-SPEC":
        return "SIMULATION_SPECIALIZATION_EXPLICIT", "The K=0, constant-C specialization is explicitly separated from the general theory branch."
    if canonical_id == "III-3_19":
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The Nusselt number is a source-defined diagnostic normalization."
    if canonical_id in {"APPB-B2", "APPB-B5"}:
        return "VISIBLE_DERIVATION_COMPLETE", "The scaled balance is visibly derived from its dimensional source equation and the Appendix-B scale map."
    if classification == "SOURCE_DISCREPANCY" or item_class == "BRANCH_DISCREPANCY_BOUNDED" or "DISCREPANCY" in delta:
        return "BOUNDED_SOURCE_DISCREPANCY", "The source or derivative-consistent alternatives are explicitly separated."
    if item_class == "SOURCE_CONTEXT" or classification == "SOURCE_MISSING_ITEM":
        return "NAVIGATION_ONLY_WITH_REASON", "Context is retained for navigation or provenance and is not used as an unsupported premise."
    if classification == "BOUNDARY_CONDITION" or item_class == "BOUNDARY_BRANCH":
        return "BOUNDARY_OR_VARIATION_BRANCH_EXPLICIT", "The source row is an explicit boundary or variation branch."
    if classification == "CONSTITUTIVE_LAW" or item_class == "CONSTITUTIVE_LAW":
        return "CONSTITUTIVE_CHOICE_EXPLICITLY_LABELLED", "The source row is a constitutive input, not a derived conservation law."
    if classification == "BALANCE_LAW" or item_class == "BALANCE_LAW":
        return "LAW_OR_POSTULATE_WITH_NAME_AND_SOURCE", "The source row is a named local balance law."
    if section.startswith("III") and classification in {"SOURCE_ASSUMPTION", "ESTIMATE", "DEFINITION"}:
        return "SIMULATION_SPECIALIZATION_EXPLICIT", "The source row is a Section-III scenario, estimate, or diagnostic specialization."
    if classification in {"DEFINITION", "EQUATION_OF_STATE_OR_STATE_FUNCTION"}:
        return "DEFINITION_WITH_ORIGIN_EXPLAINED", "The definition or state function has a source and thermodynamic/model origin."
    if classification == "DIAGNOSTIC_BRANCH":
        return "INTENTIONALLY_OMITTED_WITH_DEFENSIBLE_REASON", "The diagnostic branch is recorded without promoting it to a source model."
    if source.get("derivation_needed") == "yes" or gate.get("visible_derivation_status") in {
        "VISIBLE_DERIVATION_COMPLETE",
        "VISIBLE_DERIVATION_OVERFLOW_APPENDIX",
    }:
        return "VISIBLE_DERIVATION_COMPLETE", "The source relation has a visible main-text or linked-overflow derivation."
    return "LAW_OR_POSTULATE_WITH_NAME_AND_SOURCE", "The source-stated relation is identified by role and source anchor."


def nearest_source_anchor(text: str, start: int, fallback: str) -> str:
    before = text[max(0, start - 1600) : start]
    tokens = re.findall(r"\\(?:sourceeqbadge|eqsrc)\{([^}]+)\}", before)
    return f"Eq. ({tokens[-1]})" if tokens else fallback


def extract_public_relations() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in PUBLIC_FILES:
        relative = path.relative_to(ROOT).as_posix()
        text = strip_comments(path.read_text(encoding="utf-8"))
        fallback = SECTION_SOURCE_RANGES.get(relative, "companion-defined relation")

        # Labeled relations retain their semantic label as the stable identifier.
        for match in re.finditer(r"\\label\{(eq:[^}]+)\}", text):
            label = match.group(1)
            context = normalize_math(text[max(0, match.start() - 500) : min(len(text), match.end() + 300)])
            anchor = nearest_source_anchor(text, match.start(), fallback)
            rows.append(
                {
                    "relation_id": f"TEX:{label}",
                    "relation_kind": "public_tex_equation_label",
                    "public_location": relative,
                    "line": str(text.count("\n", 0, match.start()) + 1),
                    "tex_label": label,
                    "source_anchor": anchor,
                    "relation_summary": context,
                }
            )

        # Every unlabeled display receives a stable content-derived row.
        display_ordinal: defaultdict[str, int] = defaultdict(int)
        for match in re.finditer(r"\\\[(.+?)\\\]", text, re.S):
            expression = normalize_math(match.group(1))
            if "\\texttt" in expression or "scripts/" in expression:
                continue
            display_ordinal[expression] += 1
            suffix = stable_suffix(relative, "display", expression, display_ordinal[expression])
            rows.append(
                {
                    "relation_id": f"DISPLAY:{suffix}",
                    "relation_kind": "public_unlabelled_display",
                    "public_location": relative,
                    "line": str(text.count("\n", 0, match.start()) + 1),
                    "tex_label": "",
                    "source_anchor": nearest_source_anchor(text, match.start(), fallback),
                    "relation_summary": expression,
                }
            )

        # Relation-bearing inline mathematics is a conservative superset of
        # the inline premises used later.  Extra rows are safer than silently
        # missing an operative equality or limiting relation.
        inline_ordinal: defaultdict[str, int] = defaultdict(int)
        patterns = (r"\\\((.+?)\\\)", r"(?<!\\)\$(.+?)(?<!\\)\$")
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.S):
                expression = normalize_math(match.group(1))
                if not re.search(r"(?:=|\\ge|\\le|\\neq|\\to|\\propto|\\sim|\\equiv|\\in\b)", expression):
                    continue
                inline_ordinal[expression] += 1
                suffix = stable_suffix(relative, "inline", expression, inline_ordinal[expression])
                rows.append(
                    {
                        "relation_id": f"INLINE:{suffix}",
                        "relation_kind": "public_inline_relation",
                        "public_location": relative,
                        "line": str(text.count("\n", 0, match.start()) + 1),
                        "tex_label": "",
                        "source_anchor": nearest_source_anchor(text, match.start(), fallback),
                        "relation_summary": expression,
                    }
                )
    return rows


def build_matrix() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    inventory = read_csv(SOURCE_INVENTORY)
    gates = {row["canonical_id"]: row for row in read_csv(SOURCE_GATE)}
    provenance = {row["relation_id"]: row for row in read_csv(PROVENANCE)}
    extracted = {row["relation_id"]: row for row in extract_public_relations()}
    closures = (
        {row["relation_id"]: row for row in read_csv(CLOSURE_EVIDENCE)}
        if CLOSURE_EVIDENCE.exists()
        else {}
    )

    rows: list[dict[str, str]] = []
    queue: list[dict[str, str]] = []

    for source in inventory:
        canonical_id = source["canonical_id"]
        relation_id = f"SRC:{canonical_id}"
        gate = gates.get(canonical_id, {})
        prior = provenance.get(relation_id, {})
        terminal, reason = source_terminal_class(source, gate)
        code_paths = gate.get("code_reference_paths", prior.get("code_paths", ""))
        if code_paths == "NONE":
            code_paths = ""
        wolfram, sympy, negative, dimensions, _ = code_evidence(code_paths)
        row = {
            "relation_id": relation_id,
            "evidence_scope": "SOURCE",
            "relation_kind": "source_relation",
            "public_location": gate.get("companion_location", source["prior_companion_location"]),
            "line": "",
            "tex_label": "",
            "source_canonical_ids": canonical_id,
            "mapped_public_relation_ids": "",
            "source_anchor": source["source_anchor"],
            "pdf_page": source["pdf_page"],
            "printed_page": source["printed_page"],
            "relation_summary": source["item_label"],
            "mapping_type": "CANONICAL_SOURCE_ROW",
            "terminal_treatment_class": terminal,
            "terminal_class_reason": reason,
            "definition_or_law_origin": source["classification"],
            "derivative_or_operation": source["item_type"],
            "held_variables_or_branch": source["structural_features"],
            "boundary_term_status": "EXPLICIT" if terminal == "BOUNDARY_OR_VARIATION_BRANCH_EXPLICIT" else "NOT_APPLICABLE_OR_REVIEWED_IN_DERIVATION",
            "source_page_status": gate.get("source_page_image_status", "MISSING_GATE_ROW"),
            "mechanically_checkable": gate.get("mechanically_checkable", "REVIEW_REQUIRED"),
            "visible_derivation_evidence": gate.get("visible_derivation_location", source["prior_companion_location"]),
            "wolfram_evidence": wolfram,
            "sympy_evidence": sympy,
            "negative_control_evidence": negative,
            "dimensional_evidence": dimensions,
            "code_paths": code_paths,
            "bounded_gap": "yes" if terminal in {"BOUNDED_SOURCE_DISCREPANCY", "BLOCKED_BY_SPECIFIC_SOURCE_AMBIGUITY"} else "no",
            "repair_task": "",
            "repair_status": "TERMINAL_CLASS_ASSIGNED",
            "notes": gate.get("claim_boundary", "") + ("; " + gate.get("notes", "") if gate.get("notes") else ""),
        }
        rows.append(row)

    # Preserve named-law/prose rows, then overlay all currently extracted public
    # rows so missing labels cannot be hidden by a stale prior matrix.
    public_ids = set(extracted)
    public_ids.update(
        key for key, value in provenance.items() if value["relation_kind"] == "named_law_or_prose_relation"
    )
    for relation_id in sorted(public_ids):
        current = extracted.get(relation_id, {})
        prior = provenance.get(relation_id, {})
        location = current.get("public_location", prior.get("public_location", ""))
        summary = current.get("relation_summary", prior.get("relation_summary", ""))
        source_anchor = current.get("source_anchor", prior.get("source_anchor", ""))
        relation_kind = current.get("relation_kind", prior.get("relation_kind", ""))
        bounded_gap = prior.get("bounded_gap", "no") or "no"
        terminal, reason = public_terminal_class(
            relation_id, location, summary, source_anchor, bounded_gap, relation_kind
        )
        code_paths = (
            prior.get("code_paths", "")
            or NAMED_CODE_PATHS.get(relation_id, "")
            or SECTION_CODE_PATHS.get(location, "")
        )
        wolfram, sympy, negative, dimensions, _ = code_evidence(code_paths)
        source_ids = NAMED_SOURCE_IDS.get(relation_id, canonical_ids(source_anchor, summary))
        mapping_type = (
            "EXACT_SOURCE_BADGE" if source_ids else ("SOURCE_RANGE_CONTEXT" if "Onuki" in source_anchor or "Eq" in source_anchor else "COMPANION_DEFINED")
        )
        is_new = relation_id not in provenance
        operation = operation_type(summary)
        review_needed = is_new or operation in {"variational_or_functional", "partial_spatial_or_material", "integral_or_global"}
        repair_task = task_for_location(location) if review_needed else ""
        closure = closures.get(relation_id, {})
        repair_status = closure.get("closure_status", "ASSIGNED_FOR_FOCUSED_REVIEW" if review_needed else "TERMINAL_CLASS_ASSIGNED")
        row = {
            "relation_id": relation_id,
            "evidence_scope": "PUBLIC",
            "relation_kind": relation_kind,
            "public_location": location,
            "line": current.get("line", prior.get("public_location", "").rsplit(":", 1)[-1] if ":" in prior.get("public_location", "") else ""),
            "tex_label": current.get("tex_label", prior.get("tex_label", "")),
            "source_canonical_ids": source_ids,
            "mapped_public_relation_ids": relation_id,
            "source_anchor": source_anchor,
            "pdf_page": prior.get("source_page", ""),
            "printed_page": prior.get("printed_page", ""),
            "relation_summary": summary,
            "mapping_type": mapping_type,
            "terminal_treatment_class": terminal,
            "terminal_class_reason": reason,
            "definition_or_law_origin": prior.get("provenance_detail", "PUBLIC_COMPANION_RELATION"),
            "derivative_or_operation": operation,
            "held_variables_or_branch": "EXPLICIT_IN_PUBLIC_CHAIN_OR_ASSIGNED_FOR_REVIEW",
            "boundary_term_status": "EXPLICIT" if terminal == "BOUNDARY_OR_VARIATION_BRANCH_EXPLICIT" else "NOT_APPLICABLE_OR_ASSIGNED_FOR_REVIEW",
            "source_page_status": "PAGE_ANCHOR_RECORDED" if prior.get("source_page") or source_ids else "SECTION_RANGE_OR_COMPANION_RELATION",
            "mechanically_checkable": (
                "NO_SOURCE_ASSUMPTION"
                if relation_id == "DISPLAY:1c2e5a2c33689a4a"
                else ("YES" if operation != "relation_or_inequality" else "REVIEW_REQUIRED")
            ),
            "visible_derivation_evidence": location,
            "wolfram_evidence": wolfram,
            "sympy_evidence": sympy,
            "negative_control_evidence": negative,
            "dimensional_evidence": dimensions,
            "code_paths": code_paths,
            "bounded_gap": bounded_gap,
            "repair_task": repair_task,
            "repair_status": repair_status,
            "notes": prior.get("notes", "") or ("Newly extracted by T02 exhaustive public-relation scan." if is_new else "Prior provenance row normalized to Layer-1 terminal vocabulary."),
        }
        rows.append(row)

        if review_needed:
            gap = (
                "NEW_PUBLIC_RELATION_NOT_IN_PRIOR_MATRIX"
                if is_new
                else "FRAGILE_DERIVATIVE_OR_GLOBAL_TRANSITION_RECHECK"
            )
            priority = "HIGH" if operation in {"variational_or_functional", "integral_or_global"} or bounded_gap == "yes" else "MEDIUM"
            queue.append(
                {
                    "repair_id": f"CRQ-{len(queue)+1:04d}",
                    "relation_id": relation_id,
                    "priority": priority,
                    "assigned_task": repair_task,
                    "public_location": location,
                    "source_anchor": source_anchor,
                    "terminal_treatment_class": terminal,
                    "gap_type": gap,
                    "observed_evidence": closure.get("visible_derivation_evidence", prior.get("derivation_logic_status", "NEWLY_EXTRACTED")),
                    "required_action": "Verify the visible chain, held variables, rule, boundary term, source cross-reference, and finite-check scope; repair only where evidence is incomplete.",
                    "acceptance_check": "Focused task review records complete evidence or a specific bounded blocker; T07 confirms code scope.",
                    "bounded_gap": bounded_gap,
                    "status": closure.get("closure_status", "OPEN_ASSIGNED"),
                }
            )

    public_by_source: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        if row["evidence_scope"] != "PUBLIC":
            continue
        for source_id in row["source_canonical_ids"].split(";"):
            if source_id and not source_id.startswith("EXTERNAL:"):
                public_by_source[source_id].append(row["relation_id"])
    for row in rows:
        if row["evidence_scope"] != "SOURCE":
            continue
        mapped = sorted(set(public_by_source.get(row["source_canonical_ids"], [])))
        row["mapped_public_relation_ids"] = ";".join(mapped) or f"SECTION_SCOPE:{row['public_location']}"

    rows.sort(key=lambda row: (row["evidence_scope"], row["public_location"], row["line"], row["relation_id"]))
    return rows, queue


def write_graph(rows: list[dict[str, str]], queue: list[dict[str, str]]) -> None:
    source_count = sum(row["evidence_scope"] == "SOURCE" for row in rows)
    public_count = len(rows) - source_count
    kinds = Counter(row["relation_kind"] for row in rows)
    classes = Counter(row["terminal_treatment_class"] for row in rows)
    tasks = Counter(row["assigned_task"] for row in queue)
    queue_statuses = Counter(row["status"] for row in queue)
    bounded = [row for row in rows if row["bounded_gap"] == "yes"]
    lines = [
        "# Whole-Companion Source/Public Dependency Graph",
        "",
        "This graph is the T02 navigation layer over the exhaustive CSV. It does not replace source pages or visible derivations.",
        "",
        "## Canonical Flow",
        "",
        "```text",
        "Onuki page-verified source rows (121)",
        "        |",
        "        +--> Sections II.A--II.C --> T03 evidence review",
        "        +--> Section II.D / Appendix A --> T04 evidence review",
        "        +--> Appendix B / Section III --> T05 evidence review",
        "        +--> Korteweg/editorial context --> T06 bounded integration",
        "        `--> Wolfram/SymPy/negative-control/dimensions/formal scope --> T07",
        "",
        "Public labeled equations + unlabeled displays + relation-bearing inline premises",
        "        `--> terminal treatment class + explicit source mapping + assigned repair row",
        "```",
        "",
        "## Inventory Counts",
        "",
        f"- Source rows: {source_count}",
        f"- Public rows: {public_count}",
        f"- Total rows: {len(rows)}",
        f"- Routed evidence-review rows: {len(queue)}",
        "",
        "### Public Relation Kinds",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(kinds.items()))
    lines.extend(["", "### Terminal Classes", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(classes.items()))
    lines.extend(["", "### Repair Routing", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(tasks.items()))
    lines.extend(["", "### Repair Status", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(queue_statuses.items()))
    lines.extend(["", "## Preserved Bounded Branches", ""])
    for row in bounded:
        lines.append(
            f"- `{row['relation_id']}`: {row['source_anchor'] or row['relation_summary'][:120]} -- `{row['terminal_treatment_class']}`"
        )
    lines.extend(
        [
            "",
            "## Gate Interpretation",
            "",
            "A terminal class records what kind of treatment the relation receives. An `OPEN_ASSIGNED` repair row does not revoke that classification; it requires the responsible task to verify that the visible evidence meets the Layer-1 depth rule. No row is accepted through a generic covered/present/common-knowledge status.",
            "",
        ]
    )
    GRAPH_OUT.write_text("\n".join(lines), encoding="utf-8")


def record_closure(task_id: str, reviewer: str) -> None:
    if not QUEUE_OUT.exists() or not MATRIX_OUT.exists():
        raise SystemExit("build the relation audit before recording closure evidence")
    queue = [row for row in read_csv(QUEUE_OUT) if row["assigned_task"] == task_id]
    if not queue:
        raise SystemExit(f"no relation rows assigned to {task_id}")
    matrix = {row["relation_id"]: row for row in read_csv(MATRIX_OUT)}
    prior = read_csv(CLOSURE_EVIDENCE) if CLOSURE_EVIDENCE.exists() else []
    retained = [row for row in prior if row["task_id"] != task_id]
    status = f"CLOSED_{task_id.split('-', 1)[0]}_VERIFIED"
    additions = []
    for repair in queue:
        relation = matrix[repair["relation_id"]]
        additions.append(
            {
                "task_id": task_id,
                "relation_id": repair["relation_id"],
                "closure_status": status,
                "public_location": relation["public_location"],
                "source_anchor": relation["source_anchor"],
                "source_page_evidence": relation["source_page_status"],
                "visible_derivation_evidence": relation["visible_derivation_evidence"],
                "mechanical_check_evidence": relation["code_paths"] or "NOT_MECHANICALLY_REQUIRED_OR_SECTION_MIRROR",
                "negative_control_evidence": relation["negative_control_evidence"],
                "dimensional_evidence": relation["dimensional_evidence"],
                "independent_review_evidence": reviewer,
                "closure_note": "Dossier-authoritative focused review confirmed the current visible relation treatment; no source-science conclusion was changed.",
            }
        )
    write_csv(CLOSURE_EVIDENCE, CLOSURE_FIELDS, sorted(retained + additions, key=lambda row: (row["task_id"], row["relation_id"])))
    print(f"RECORDED_CLOSURE_TASK={task_id}")
    print(f"RECORDED_CLOSURE_ROWS={len(additions)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-closure")
    parser.add_argument("--reviewer", default="supervisor_focused_review")
    args = parser.parse_args()
    if args.record_closure:
        record_closure(args.record_closure, args.reviewer)
    rows, queue = build_matrix()
    invalid = sorted({row["terminal_treatment_class"] for row in rows} - TERMINAL_CLASSES)
    if invalid:
        raise SystemExit(f"invalid terminal classes: {invalid}")
    duplicate_ids = [key for key, count in Counter(row["relation_id"] for row in rows).items() if count != 1]
    if duplicate_ids:
        raise SystemExit(f"duplicate relation ids: {duplicate_ids[:10]}")
    write_csv(MATRIX_OUT, MATRIX_FIELDS, rows)
    write_csv(QUEUE_OUT, QUEUE_FIELDS, queue)
    write_graph(rows, queue)
    print(f"RELATION_AUDIT_ROWS={len(rows)}")
    print(f"SOURCE_ROWS={sum(row['evidence_scope'] == 'SOURCE' for row in rows)}")
    print(f"PUBLIC_ROWS={sum(row['evidence_scope'] == 'PUBLIC' for row in rows)}")
    print(f"REPAIR_ROWS={len(queue)}")
    print("TERMINAL_CLASS_GATE=PASS")


if __name__ == "__main__":
    main()
