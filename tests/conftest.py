"""Load reference solutions when AGENTSTACK_PEEK=1."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

if os.environ.get("AGENTSTACK_PEEK") == "1":
    import peek

    peek.install()
