import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = ROOT / "scripts/python/check_companion_scaffold.py"


spec = importlib.util.spec_from_file_location("check_companion_scaffold", CHECK_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_required_files_exist():
    module.test_required_files_exist()


def test_ledger_schema_and_rows():
    module.test_ledger_schema_and_rows()


def test_no_source_pdfs_tracked_in_companion():
    module.test_no_source_pdfs_tracked_in_companion()


def test_policy_declares_original_companion():
    module.test_policy_declares_original_companion()
