import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "lab"
A5 = Path(__file__).resolve().parents[2] / "modulo-a5" / "lab"
A4 = Path(__file__).resolve().parents[2] / "modulo-a4" / "lab"
for p in (LAB, A5, A4):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

os.environ.setdefault("TRILHA_A6_TESTE", "1")
