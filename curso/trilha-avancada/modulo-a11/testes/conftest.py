from __future__ import annotations

import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "lab"
A2 = Path(__file__).resolve().parents[2] / "modulo-a2" / "lab"
for p in (LAB, A2):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
