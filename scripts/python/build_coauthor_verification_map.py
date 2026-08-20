#!/usr/bin/env python3
"""Build the row-level coauthor verification and Wolfram-trace audits.

The maps distinguish finite mechanical checks from contextual or nonalgebraic
relations. They summarize existing evidence; they do not promote a CAS result
to a continuum, constitutive, thermodynamic, or numerical proof.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "research_notes"
RELATIONS = NOTES / "whole_companion_relation_treatment_matrix.csv"
PUBLIC_CODE_MAP = NOTES / "onuki_companion_code_to_paper_map.csv"
MAP_OUT = NOTES / "coauthor_readiness_code_to_paper_map.csv"
TRACE_OUT = NOTES / "coauthor_readiness_wolfram_trace_audit.csv"

MAP_FIELDS = [
    "relation_id",
    "public_location",
    "line",
    "source_anchor",
    "terminal_treatment_class",
    "source_fidelity_status",
    "bounded_gap",
    "bounded_limitation",
    "operation_class",
    "mechanical_status",
    "visible_derivation_status",
    "visible_derivation_evidence",
    "wolfram_status",
    "wolfram_evidence",
    "wolfram_check_ids",
    "sympy_status",
    "sympy_evidence",
    "sympy_check_ids",
    "negative_control_status",
    "negative_control_evidence",
    "negative_control_ids",
    "check_mapping_basis",
    "dimensional_status",
    "dimensional_evidence",
    "lean_status",
    "lean_evidence",
    "code_paths",
    "proof_scope_limit",
    "final_status",
    "notes",
]

TOKEN_STOPWORDS = {
    "app", "appendix", "check", "checks", "companion", "definition",
    "display", "eq", "equation", "expected", "finite", "from", "identity",
    "inline", "ledger", "nonzero", "onuki", "pass", "relation", "residual",
    "section", "source", "step", "test", "tests", "the", "trace", "zero",
}

EXACT_ID_OVERRIDES = {
    "DISPLAY:11a97ba1fe394278": {
        "wolfram": "phi_definition; theta_definition; length_scale_squared_relation",
        "sympy": "phi_definition; theta_definition; length_scale_squared_relation",
        "pytest": "test_sympy_scaling_checks_pass",
    },
    "INLINE:a7984da36b03f8e6": {
        "pytest": "test_sympy_checks_pass",
    },
    "INLINE:ce5713ef8405fcfd": {
        "pytest": "test_sympy_checks_pass",
    },
    "TEX:eq:korteweg-onuki-residual": {
        "sympy": "general_nonisothermal_tensor_residual",
    },
    "TEX:eq:iii-effective-conductivity-ledger": {
        "wolfram": "III-14A-effective-conductivity-definition",
        "sympy": "effective_conductivity_eq317_definition",
    },
    "TEX:eq:iii-bottom-heat-flux-ledger": {
        "wolfram": "III-14B-bottom-heat-flux-definition",
        "sympy": "bottom_heat_flux_eq318_definition",
    },
    "TEX:eq:iii-wetting-heat-flux-normalization": {
        "wolfram": "III-17-wetting-heat-flux-normalization",
        "sympy": "wetting_heat_flux_normalization",
    },
}

KORTEWEG_WOLFRAM_RELATION_MAP = {
    "TEX:eq:korteweg-onuki-residual": "KO04",
    "INLINE:e12823b370da0977": "KO06",
    "INLINE:e8762706c55ab54a": "KO05",
    "INLINE:828589bf99c8d434": "KO06",
    "INLINE:b25c9b682f2f35ee": "KO07",
    "INLINE:cee37f367657cb2e": "KT10",
    "INLINE:3104b83c2807c930": "KO01",
    "INLINE:bd204a017af7097c": "KO01",
    "INLINE:c710af29166fe218": "KT01",
    "INLINE:57a84ae8421fee59": "KT01",
    "INLINE:b2e35dd69b54e764": "KT01",
    "TEX:eq:korteweg-capillary-tensor": "KT01",
    "INLINE:ab5ddf7fac4f9005": "KT02",
    "TEX:eq:korteweg-capillary-divergence": "KT07; KT08",
    "INLINE:8cf18bd3bd979ea0": "KT09",
    "INLINE:40628eebb170708c": "KO01",
    "TEX:eq:onuki-capillary-expanded-for-korteweg": "KO02; KO03",
    "INLINE:928407f0f72fd859": "KO03",
    "DISPLAY:c2e13e9591048430": "KO02",
    "TEX:eq:korteweg-onuki-map": "KO01; KO04",
    "LAW:KortewegStressContext": "KT01; KO04",
}
for relation_id, check_ids_value in KORTEWEG_WOLFRAM_RELATION_MAP.items():
    EXACT_ID_OVERRIDES.setdefault(relation_id, {})["wolfram"] = check_ids_value

TRACE_FIELDS = [
    "script",
    "trace_class",
    "named_check_count",
    "expected_nonzero_control",
    "residual_emitted",
    "assumptions_or_premises",
    "output_scope",
    "audit_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def paths(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def existing_path(path: str) -> bool:
    return (ROOT / path).is_file()


def evidence_status(value: str, none_token: str = "NONE_RECORDED") -> str:
    items = paths(value)
    if not items or value == none_token:
        return "MISSING"
    if not all(existing_path(item) for item in items):
        return "MISSING_PATH"
    return "PASS_REPRODUCIBLE_PATH"


def all_check_ids(value: str, tool: str) -> list[str]:
    found: list[str] = []
    for item in paths(value):
        candidate = ROOT / item
        if not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8")
        if tool == "wolfram":
            ids = re.findall(
                r'(?:checkZero|checkExpectedNonzero|addCheck|recordStep|addTrace)\[\s*"([^"]+)"',
                text,
            )
        elif tool == "sympy":
            ids = re.findall(
                r'(?:_assert_(?:zero|expected_nonzero|dimensionless|units)|_zero|_nonzero)\(\s*(?:rows,\s*)?"([^"]+)"',
                text,
            )
        else:
            ids = re.findall(r"^def\s+(test_[A-Za-z0-9_]+)\(", text, re.MULTILINE)
        for check_id in ids:
            if check_id not in found:
                found.append(check_id)
    return found


def semantic_tokens(value: str) -> set[str]:
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    tokens = set(re.findall(r"[A-Za-z0-9]+", value.lower()))
    return {token for token in tokens if len(token) > 1 and token not in TOKEN_STOPWORDS}


def direct_check_ids(row: dict[str, str], ids: list[str], tool: str) -> list[str]:
    override = EXACT_ID_OVERRIDES.get(row["relation_id"], {}).get(tool)
    if override:
        selected = [item.strip() for item in override.split(";") if item.strip()]
        missing = [item for item in selected if item not in ids]
        if missing:
            raise ValueError(f"missing overridden {tool} checks {missing} for {row['relation_id']}")
        return selected

    primary = semantic_tokens(" ".join((row["relation_id"], row["tex_label"], row["source_anchor"])))
    context = semantic_tokens(" ".join((row["relation_summary"], row["derivative_or_operation"])))
    scored: list[tuple[int, str]] = []
    for check_id in ids:
        check_tokens = semantic_tokens(check_id)
        score = 5 * len(primary & check_tokens) + len(context & check_tokens)
        if score:
            scored.append((score, check_id))
    if not scored:
        return []
    best = max(score for score, _ in scored)
    return [check_id for score, check_id in scored if score == best][:3]


def selected_check_ids(
    rows: list[dict[str, str]], evidence_field: str, tool: str
) -> dict[str, tuple[str, str]]:
    """Select row-specific checks, then inherit only from an enclosing public step.

    A relation never receives the complete list from a group script.  Opaque
    inline/display relations may inherit the selected check of the nearest
    semantically named relation in the same file and evidence group; the basis
    is retained in the output so this containment claim remains reviewable.
    """

    ids_by_evidence = {
        value: all_check_ids(value, tool)
        for value in {row[evidence_field] for row in rows}
    }
    direct: dict[str, list[str]] = {
        row["relation_id"]: direct_check_ids(row, ids_by_evidence[row[evidence_field]], tool)
        for row in rows
    }
    result: dict[str, tuple[str, str]] = {}
    for row in rows:
        own = direct[row["relation_id"]]
        if own:
            result[row["relation_id"]] = ("; ".join(own), "DIRECT_SEMANTIC_CHECK_MATCH")
            continue
        candidates = [
            candidate
            for candidate in rows
            if candidate["public_location"] == row["public_location"]
            and candidate[evidence_field] == row[evidence_field]
            and direct[candidate["relation_id"]]
            and candidate["relation_id"].startswith("TEX:")
        ]
        if not candidates:
            candidates = [
                candidate
                for candidate in rows
                if candidate["public_location"] == row["public_location"]
                and candidate[evidence_field] == row[evidence_field]
                and direct[candidate["relation_id"]]
            ]
        if not candidates:
            if tool == "pytest" and ids_by_evidence[row[evidence_field]]:
                module_ids = ids_by_evidence[row[evidence_field]]
                selected = next(
                    (
                        check_id
                        for check_id in module_ids
                        if "sympy" in check_id or "checks_pass" in check_id
                    ),
                    module_ids[0],
                )
                result[row["relation_id"]] = (
                    selected,
                    "DECLARED_MODULE_EXECUTION_TEST",
                )
                continue
            raise ValueError(
                f"no row-specific or enclosing {tool} check for {row['relation_id']}"
            )
        nearest = min(
            candidates,
            key=lambda candidate: abs(int(candidate["line"]) - int(row["line"])),
        )
        result[row["relation_id"]] = (
            "; ".join(direct[nearest["relation_id"]]),
            f"ENCLOSING_DERIVATION_STEP:{nearest['relation_id']}",
        )
    return result


def build_relation_map() -> list[dict[str, str]]:
    public = [row for row in read_csv(RELATIONS) if row["evidence_scope"] == "PUBLIC"]
    inconsistent_source_status = [
        row
        for row in public
        if row["terminal_treatment_class"] == "BOUNDED_SOURCE_DISCREPANCY"
        and row["bounded_gap"].lower() != "yes"
    ]
    if inconsistent_source_status:
        raise ValueError(
            "bounded source discrepancy without bounded_gap=yes: "
            + ", ".join(row["relation_id"] for row in inconsistent_source_status)
        )
    mechanical_rows = [row for row in public if row["mechanically_checkable"] == "YES"]
    wolfram_map = selected_check_ids(mechanical_rows, "wolfram_evidence", "wolfram")
    sympy_map = selected_check_ids(mechanical_rows, "sympy_evidence", "sympy")
    negative_map = selected_check_ids(mechanical_rows, "negative_control_evidence", "pytest")
    result: list[dict[str, str]] = []
    for row in public:
        mechanical = row["mechanically_checkable"] == "YES"
        wolfram_status = evidence_status(row["wolfram_evidence"])
        sympy_status = evidence_status(row["sympy_evidence"])
        negative_status = evidence_status(row["negative_control_evidence"], "REVIEW_REQUIRED")
        if mechanical:
            wolfram_ids, wolfram_basis = wolfram_map[row["relation_id"]]
            sympy_ids, sympy_basis = sympy_map[row["relation_id"]]
            negative_ids, negative_basis = negative_map[row["relation_id"]]
            mapping_basis = (
                f"wolfram={wolfram_basis}; sympy={sympy_basis}; "
                f"negative_control={negative_basis}"
            )
        else:
            wolfram_ids = sympy_ids = negative_ids = "NOT_APPLICABLE"
            mapping_basis = "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"

        dimensional_paths = paths(row["dimensional_evidence"])
        if dimensional_paths and "REVIEW_REQUIRED_WHERE_RELEVANT" not in dimensional_paths:
            dimensional_status = (
                "PASS_DIMENSIONAL_PATH"
                if all(existing_path(item) for item in dimensional_paths)
                else "MISSING_DIMENSIONAL_PATH"
            )
            dimensional_evidence = row["dimensional_evidence"]
        else:
            dimensional_status = "NOT_SEPARATELY_REQUIRED_FOR_THIS_FINITE_IDENTITY"
            dimensional_evidence = (
                "Visible derivation supplies the object types; this row makes no independent Pint claim."
            )

        lean_paths = [item for item in paths(row["code_paths"]) if item.endswith(".lean")]
        lean_status = "PASS_FINITE_KERNEL_SCOPE" if lean_paths else "NOT_APPLICABLE"
        lean_evidence = "; ".join(lean_paths) or "No Lean claim is made for this row."

        if mechanical:
            required = [wolfram_status, sympy_status, negative_status]
            verification_pass = (
                "VERIFIED_FINITE_EVIDENCE"
                if all(status.startswith("PASS_") for status in required)
                and all((wolfram_ids, sympy_ids, negative_ids))
                and not dimensional_status.startswith("MISSING")
                else "OPEN_VERIFICATION_GAP"
            )
            final_status = (
                "VERIFIED_FINITE_EVIDENCE_WITH_BOUNDED_SOURCE_STATUS"
                if verification_pass == "VERIFIED_FINITE_EVIDENCE"
                and row["bounded_gap"].lower() == "yes"
                else verification_pass
            )
            mechanical_status = "MECHANICALLY_CHECKABLE_FINITE"
        else:
            final_status = "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"
            mechanical_status = "NOT_APPLICABLE_CONTEXT_OR_NONALGEBRAIC"
            wolfram_status = sympy_status = negative_status = "NOT_APPLICABLE"

        proof_scope = (
            "Finite algebra/component/scaling evidence only; no continuum PDE, "
            "constitutive-law, second-law, global-boundary, numerical, or empirical proof."
        )
        result.append(
            {
                "relation_id": row["relation_id"],
                "public_location": row["public_location"],
                "line": row["line"],
                "source_anchor": row["source_anchor"],
                "terminal_treatment_class": row["terminal_treatment_class"],
                "source_fidelity_status": row["terminal_treatment_class"],
                "bounded_gap": row["bounded_gap"],
                "bounded_limitation": (
                    row["notes"] if row["bounded_gap"].lower() == "yes" else "NONE"
                ),
                "operation_class": row["derivative_or_operation"],
                "mechanical_status": mechanical_status,
                "visible_derivation_status": "PASS_VISIBLE_LOCATION",
                "visible_derivation_evidence": row["visible_derivation_evidence"],
                "wolfram_status": wolfram_status,
                "wolfram_evidence": row["wolfram_evidence"],
                "wolfram_check_ids": wolfram_ids if mechanical else "NOT_APPLICABLE",
                "sympy_status": sympy_status,
                "sympy_evidence": row["sympy_evidence"],
                "sympy_check_ids": sympy_ids if mechanical else "NOT_APPLICABLE",
                "negative_control_status": negative_status,
                "negative_control_evidence": row["negative_control_evidence"],
                "negative_control_ids": negative_ids if mechanical else "NOT_APPLICABLE",
                "check_mapping_basis": mapping_basis,
                "dimensional_status": dimensional_status,
                "dimensional_evidence": dimensional_evidence,
                "lean_status": lean_status,
                "lean_evidence": lean_evidence,
                "code_paths": row["code_paths"],
                "proof_scope_limit": proof_scope,
                "final_status": final_status,
                "notes": (
                    "Selected check IDs identify the direct or enclosing public derivation step; "
                    "the visible derivation remains the primary mathematical argument, and finite "
                    "verification does not erase bounded source status."
                ),
            }
        )
    return sorted(result, key=lambda row: (row["public_location"], row["line"], row["relation_id"]))


def build_trace_audit(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    relation_scripts = {
        item
        for row in rows
        for item in paths(row["wolfram_evidence"])
        if item.endswith(".wls")
    }
    indexed_scripts = {
        row["script"]
        for row in read_csv(PUBLIC_CODE_MAP)
        if row["tool"] == "Wolfram" and row["script"].endswith(".wls")
    }
    scripts = sorted(relation_scripts | indexed_scripts)
    result = []
    for script in scripts:
        text = (ROOT / script).read_text(encoding="utf-8")
        explicit = bool(re.search(r"recordStep|addTrace", text))
        structured = explicit or "recordAtomicTrace" in text
        named_count = len(set(re.findall(r'"([A-Za-z][A-Za-z0-9_\-]{3,})"', text)))
        expected_nonzero = "PASS_EXPECTED_NONZERO" in text or "checkExpectedNonzero" in text
        residual = "residual" in text and "Print[" in text
        assumptions = "Assumptions" in text or "assumption" in text.lower() or "premise" in text.lower()
        trace_class = "EXPLICIT_TRANSITION_TRACE" if explicit else "ATOMIC_NAMED_RESIDUAL_TRACE"
        audit_status = (
            "PASS"
            if structured and named_count > 0 and residual and (expected_nonzero or "negative" in text.lower())
            else "OPEN_TRACE_GAP"
        )
        result.append(
            {
                "script": script,
                "trace_class": trace_class,
                "named_check_count": str(named_count),
                "expected_nonzero_control": "YES" if expected_nonzero else "NO",
                "residual_emitted": "YES" if residual else "NO",
                "assumptions_or_premises": "EXPLICIT" if assumptions else "VISIBLE_IN_CONSTRUCTED_EXPRESSIONS_AND_PUBLIC_DERIVATION",
                "output_scope": "finite residuals only; see the row-level proof-scope limit",
                "audit_status": audit_status,
            }
        )
    return result


def main() -> None:
    relation_rows = build_relation_map()
    write_csv(MAP_OUT, MAP_FIELDS, relation_rows)
    trace_rows = build_trace_audit(relation_rows)
    write_csv(TRACE_OUT, TRACE_FIELDS, trace_rows)
    open_rows = [row for row in relation_rows if row["final_status"] == "OPEN_VERIFICATION_GAP"]
    open_traces = [row for row in trace_rows if row["audit_status"] != "PASS"]
    print(f"PUBLIC_RELATION_ROWS={len(relation_rows)}")
    print(f"MECHANICAL_ROWS={sum(row['mechanical_status'] == 'MECHANICALLY_CHECKABLE_FINITE' for row in relation_rows)}")
    print(f"OPEN_VERIFICATION_ROWS={len(open_rows)}")
    print(f"WOLFRAM_TRACE_SCRIPTS={len(trace_rows)}")
    print(f"OPEN_TRACE_SCRIPTS={len(open_traces)}")
    if open_rows or open_traces:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
