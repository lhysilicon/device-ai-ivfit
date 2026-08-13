#!/usr/bin/env python3
"""造合成 I–V CSV。不是实验室测量。"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from physics import square_law_id

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic.csv"


def main() -> None:
    vg = np.linspace(0.0, 1.8, 19)
    vd = np.linspace(0.05, 1.8, 18)
    VG, VD = np.meshgrid(vg, vd, indexing="xy")
    id_ = square_law_id(VG, VD)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vg", "vd", "id"])
        for a, b, c in zip(VG.ravel(), VD.ravel(), id_.ravel()):
            w.writerow([f"{a:.6f}", f"{b:.6f}", f"{c:.12e}"])
    print(f"wrote {OUT} n={VG.size}")


if __name__ == "__main__":
    main()
