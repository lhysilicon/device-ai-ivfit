#!/usr/bin/env python3
"""造 DUT I–V。隐藏参数在 physics.TRUE；提取器不得读这个文件的真值以外的捷径。"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from physics import TRUE, mosfet_id

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "synthetic.csv"


def main() -> None:
    rng = np.random.default_rng(1)
    vg = np.linspace(0.0, 1.80, 37)
    vd = np.concatenate([[0.05], np.linspace(0.10, 1.80, 18)])
    VG, VD = np.meshgrid(vg, vd, indexing="xy")
    id_ = mosfet_id(VG, VD, TRUE)
    # 3% log-domain noise：提取/拟合都不是背答案
    id_ = id_ * np.exp(rng.normal(0.0, 0.03, size=id_.shape))
    id_ = np.clip(id_, 1e-18, None)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vg", "vd", "id"])
        for a, b, c in zip(VG.ravel(), VD.ravel(), id_.ravel()):
            w.writerow([f"{a:.6f}", f"{b:.6f}", f"{c:.12e}"])
    print(f"wrote {OUT} n={VG.size} vth_true={TRUE.vth}")


if __name__ == "__main__":
    main()
