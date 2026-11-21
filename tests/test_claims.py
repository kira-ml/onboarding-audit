import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_headline_numbers_match_committed_artifacts():
    spec = importlib.util.spec_from_file_location(
        "check_claims", ROOT / "scripts" / "check_claims.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == 0
