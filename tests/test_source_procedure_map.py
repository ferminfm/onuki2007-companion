from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'research_notes' / 'onuki2007_source_procedure_map.csv'
ALT = ROOT / 'research_notes' / 'onuki2007_alternative_derivation_needed.csv'
MATRIX = ROOT / 'research_notes' / 'onuki2007_equation_classification_matrix.csv'
GRAPH = ROOT / 'research_notes' / 'onuki2007_equation_dependency_graph_full.md'

def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def test_procedure_map_has_key_source_routes():
    rows = read_csv(PROC)
    ids = {r['inventory_id'] for r in rows}
    for inv_id in ['IIA-DP-NDMU','II-2_48','APPB-B3','II-2_53','REF49-ALPHA']:
        assert inv_id in ids
    b3 = next(r for r in rows if r['inventory_id'] == 'APPB-B3')
    assert b3['source_operation_type'] == 'NONDIMENSIONALIZATION_WITH_SOURCE_BRANCH_RESIDUAL'
    assert 'Eqs. (2.47)--(2.48)' in b3['source_dependencies']

def test_alternative_rows_preserve_bounded_gaps():
    rows = read_csv(ALT)
    ids = {r['inventory_id'] for r in rows}
    assert {'APPB-B3','II-2_48','II-2_53'} <= ids
    b3 = next(r for r in rows if r['inventory_id'] == 'APPB-B3')
    assert 'preserve both' in b3['alternative_reason']
    assert 'no official erratum' in b3['claim_boundary']

def test_metadata_corrections_are_present():
    rows = read_csv(MATRIX)
    p1 = next(r for r in rows if r['inventory_id'] == 'II-2_48')
    first = next(r for r in rows if r['inventory_id'] == 'IIC-FIRST-INTEGRAL')
    assert p1['classification'] == 'DERIVED_IDENTITY'
    assert first['classification'] == 'DERIVED_IDENTITY'

def test_dependency_graph_mentions_major_chains():
    text = GRAPH.read_text()
    assert 'Section II.A thermodynamic baseline' in text
    assert 'Appendix A' in text
    assert 'B3 remains a typographical omission only under the dimensional-source derivation' in text
