import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "lab"
A4 = Path(__file__).resolve().parents[2] / "modulo-a4" / "lab"
for p in (LAB, A4):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# testes A8/A9/A10 no mesmo pytest devem poder desligar o adapter; A5 não força.
os.environ.setdefault("TRILHA_A5_TESTE", "1")
