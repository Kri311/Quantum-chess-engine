"""Backward-compatible command for the reproducible 3×3 comparison."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.compare_3x3_systems import main


# ---------------------------------------------------------------------------
# Compatibility entry point
# ---------------------------------------------------------------------------
# Preserve the old command path while routing execution through the current
# reproducible comparison implementation.
if __name__ == "__main__":
    main()
