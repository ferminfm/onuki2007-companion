from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / 'research_notes' / 'onuki2007_exhaustive_equation_inventory.csv'
MISS = ROOT / 'research_notes' / 'onuki2007_missing_companion_equations.csv'
REQ = {
    'II-2_1', 'IIA-DP-NDMU', 'IIB-MPRIME', 'IIC-FIRST-INTEGRAL',
    'II-2_44', 'II-2_48', 'II-2_53', 'III-3_1', 'III-3_10',
    'III-3_20', 'APPA-GRADVAR', 'APPB-CONT', 'APPB-B3',
    'REF49-ALPHA', 'REF59-DISCRETIZATION'
}

def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def test_inventory_has_required_columns_and_rows():
    rows = read_csv(INV)
    assert len(rows) >= 100
    required_columns = {
        'inventory_id', 'source_section', 'pdf_page', 'printed_page', 'source_anchor',
        'item_label', 'item_type', 'source_expression_summary', 'source_context_summary',
        'source_derivation_or_procedure', 'companion_location', 'current_companion_status',
        'derivation_needed', 'notes'
    }
    assert required_columns <= set(rows[0])
    ids = {r['inventory_id'] for r in rows}
    assert REQ <= ids

def test_numbered_equation_coverage_boundaries():
    rows = read_csv(INV)
    anchors = {r['source_anchor'] for r in rows}
    for anchor in ['Eq. (2.1)', 'Eq. (2.53)', 'Eq. (3.20)', 'Eq. (A4)', 'Eq. (B6)']:
        assert anchor in anchors

def test_b3_and_future_source_boundaries_are_explicit():
    rows = read_csv(INV)
    b3 = next(r for r in rows if r['inventory_id'] == 'APPB-B3')
    assert 'typographical omission only under dimensional-source derivation' in b3['notes']
    assert 'official erratum' in b3['notes']
    assert 'implementation' in b3['notes']
    intro = next(r for r in rows if r['inventory_id'] == 'INTRO-VDW-GRAD')
    assert 'Korteweg 1901 source locked and conditionally crosswalked' in intro['notes']

def test_missing_queue_parses_and_links_to_inventory():
    rows = read_csv(INV)
    missing = read_csv(MISS)
    ids = {r['inventory_id'] for r in rows}
    assert missing
    assert {r['inventory_id'] for r in missing} <= ids
