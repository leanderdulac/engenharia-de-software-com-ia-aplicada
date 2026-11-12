import os
import sys
from pathlib import Path

os.environ.setdefault("TRILHA_PI_SFT", "0")

LAB = Path(__file__).resolve().parents[1] / "lab"
A2 = Path(__file__).resolve().parents[2] / "modulo-a2" / "lab"
A5 = Path(__file__).resolve().parents[2] / "modulo-a5" / "lab"
for p in (LAB, A2, A5):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
