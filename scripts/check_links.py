"""Check relative Markdown links in the repository.

Usage:
    python scripts/check_links.py

Exits non-zero if a relative link target does not exist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}


def main() -> int:
    root = Path(".")
    missing: list[tuple[str, str]] = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                missing.append((str(path), target))
    for path, target in missing:
        print(f"{path}: {target}")
    print(f"{len(missing)} missing link(s)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
