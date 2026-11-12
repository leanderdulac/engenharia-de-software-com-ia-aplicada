import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "lab"
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))
