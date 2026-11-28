"""Guard against committing raw or large data files.

The repository may contain small synthetic examples, but not the BAF raw files,
the processed evaluation frame, or row-level parquet outputs.
"""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_no_raw_data_files_are_tracked():
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git is not available in this environment")

    tracked = [Path(p) for p in result.stdout.splitlines() if p.strip()]
    forbidden = [
        p
        for p in tracked
        if p.parts[0] == "data"
        or p.name in {"Base.csv", "Variant.csv"}
        or p.name.startswith("Variant")
        and p.suffix in {".csv", ".parquet"}
        or p.suffix == ".parquet"
    ]
    assert forbidden == []
