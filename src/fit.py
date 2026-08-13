#!/usr/bin/env python3
"""拟合合成（或 CSV）I–V。退出码才是验收，不要只看打印。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from model import TinyMLP
from physics import VTH, square_law_id

ROOT = Path(__file__).resolve().parents[1]
RMSE_MAX = 5e-5


def load_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with path.open() as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"empty csv: {path}")
    need = {"vg", "vd", "id"}
    if set(rows[0].keys()) < need:
        raise SystemExit(f"csv must have columns vg,vd,id; got {list(rows[0].keys())}")
    vg = np.array([float(r["vg"]) for r in rows])
    vd = np.array([float(r["vd"]) for r in rows])
    id_ = np.array([float(r["id"]) for r in rows])
    return vg, vd, id_


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=ROOT / "data" / "synthetic.csv")
    p.add_argument("--check-physics", action="store_true")
    p.add_argument("--vth", type=float, default=VTH, help="故意改错应非零退出，例如 --vth 1.2")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    if args.check_physics:
        vg = np.array([1.0])
        vd = np.array([1.2])
        i_on = square_law_id(vg, vd, vth=args.vth)[0]
        # 正确 VTH≈0.4 时 Id 应明显大于 1e-6；改成 1.2 则器件关断
        if i_on <= 1e-6:
            print("PHYSICS CHECK FAIL")
            return 1
        print("PHYSICS CHECK: PASS")
        return 0

    if not args.csv.exists():
        raise SystemExit(f"missing {args.csv}; run generate_synthetic.py first")

    vg, vd, id_true = load_csv(args.csv)
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(vg))
    n_train = int(0.8 * len(idx))
    tr, te = idx[:n_train], idx[n_train:]

    net = TinyMLP(rng)
    net.fit(vg[tr], vd[tr], id_true[tr])
    pred = net.predict_id(vg[te], vd[te])
    analytic = square_law_id(vg[te], vd[te])
    m_rmse = rmse(pred, id_true[te])
    a_rmse = rmse(analytic, id_true[te])

    out = ROOT / "reports" / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "rmse_test": m_rmse,
        "analytic_rmse_test": a_rmse,
        "n_test": int(len(te)),
        "csv": str(args.csv),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    if m_rmse >= RMSE_MAX:
        print(f"FIT FAIL rmse_test={m_rmse} >= {RMSE_MAX}")
        return 1
    print("FIT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
