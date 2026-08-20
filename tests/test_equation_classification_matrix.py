from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'research_notes' / 'onuki2007_equation_classification_matrix.csv'
QUEUE = ROOT / 'research_notes' / 'onuki2007_derivation_required_queue.csv'
POLICY = ROOT / 'research_notes' / 'ONUKI2007_EQUATION_CLASSIFICATION_POLICY.md'

def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def test_classification_matrix_covers_inventory_and_vocab():
    rows = read_csv(MATRIX)
    assert len(rows) >= 100
    allowed = {
        'DEFINITION','EQUATION_OF_STATE_OR_STATE_FUNCTION','THERMODYNAMIC_IDENTITY',
        'CONSERVATION_LAW','BALANCE_LAW','CONSTITUTIVE_LAW','SOURCE_ASSUMPTION',
        'BOUNDARY_CONDITION','SCALING_DEFINITION_OR_NONDIMENSIONAL_EQUATION',
        'VARIATIONAL_IDENTITY','DERIVED_IDENTITY','ESTIMATE','DIAGNOSTIC_BRANCH',
        'SOURCE_DISCREPANCY','SOURCE_MISSING_ITEM','SOURCE_CONTEXT'
    }
    assert {r['classification'] for r in rows} <= allowed
    assert {r['derivation_decision'] for r in rows} <= {'REQUIRED','OPTIONAL','NOT_REQUIRED','OUT_OF_SCOPE'}

def test_priority_queue_contains_required_central_rows():
    queue = read_csv(QUEUE)
    ids = {r['inventory_id'] for r in queue}
    for inv_id in ['IIA-DP-NDMU','II-2_48','APPB-B3','II-2_53','REF49-ALPHA']:
        assert inv_id in ids
    ranks = [int(r['queue_rank']) for r in queue]
    assert ranks == list(range(1, len(queue)+1))

def test_source_boundaries_are_preserved():
    rows = read_csv(MATRIX)
    b3 = next(r for r in rows if r['inventory_id'] == 'APPB-B3')
    assert b3['classification'] == 'SOURCE_DISCREPANCY'
    assert 'no official erratum' in b3['claim_boundary']
    intro = next(r for r in rows if r['inventory_id'] == 'INTRO-VDW-GRAD')
    assert intro['classification'] == 'SOURCE_MISSING_ITEM'
    assert intro['derivation_decision'] == 'OUT_OF_SCOPE'
    text = POLICY.read_text()
    assert 'blackboard calculation' in text
    assert 'avoid article-facing' in text
