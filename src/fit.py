#!/usr/bin/env python3
"""提参 + MLP + 外推。退出码才是验收。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from dataclasses import replace

from dataset import load_csv, splits
from extract import compact_id, extract_params
from model import TinyMLP
from physics import TRUE, mosfet_id
from plots import save_figures
from spice_card import write_card

ROOT = Path(__file__).resolve().parents[1]
VTH_ERR_MAX = 0.08
LOG_RMSE_IN_MAX = 0.45
FIG_MIN_BYTES = 2000


def log_rmse(a: np.ndarray, b: np.ndarray) -> float:
    la = np.log10(np.maximum(a, 1e-18))
    lb = np.log10(np.maximum(b, 1e-18))
    return float(np.sqrt(np.mean((la - lb) ** 2)))


def lin_rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=ROOT / "data" / "synthetic.csv")
    p.add_argument("--check-physics", action="store_true")
    p.add_argument("--vth", type=float, default=TRUE.vth)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    if args.check_physics:
        vg = np.array([1.0])
        vd = np.array([1.2])
        i_on = mosfet_id(vg, vd, replace(TRUE, vth=args.vth))[0]
        if i_on <= 1e-8:
            print("PHYSICS CHECK FAIL")
            return 1
        print("PHYSICS CHECK: PASS")
        return 0

    if not args.csv.exists():
        raise SystemExit(f"missing {args.csv}; run generate_synthetic.py first")

    vg, vd, id_true = load_csv(args.csv)
    rng = np.random.default_rng(args.seed)
    tr, te, extra = splits(vg, rng)
    extracted = extract_params(vg[tr], vd[tr], id_true[tr])
    net = TinyMLP(rng)
    net.fit(vg[tr], vd[tr], id_true[tr])

    pred_te = net.predict_id(vg[te], vd[te])
    comp_te = compact_id(vg[te], vd[te], extracted)
    pred_ex = net.predict_id(vg[extra], vd[extra]) if len(extra) else pred_te
    id_ex = id_true[extra] if len(extra) else id_true[te]

    pred_all = net.predict_id(vg, vd)
    comp_all = compact_id(vg, vd, extracted)
    figs = save_figures(vg, vd, id_true, comp_all, pred_all, ROOT / "figs")
    card = ROOT / "models" / "nmos_extracted.inc"
    write_card(card, extracted)

    synthetic = args.csv.name == "synthetic.csv"
    vth_err = abs(extracted.vth - TRUE.vth) if synthetic else None
    payload = {
        "source": str(args.csv.name),
        "dut": (
            "ekv-like generator + 3% log noise (not wafer, not foundry)"
            if synthetic
            else "Sentaurus GettingStarted SOI_IdVg tutorial I-V (Lg=0.2 um SOI nMOS; not wafer, not foundry PDK)"
        ),
        "vth_true": TRUE.vth if synthetic else None,
        "vth_hat": extracted.vth,
        "vth_err": vth_err,
        "ss_mVdec": extracted.ss_mVdec,
        "n_hat": extracted.n,
        "i0_hat": extracted.i0,
        "k_hat": extracted.k,
        "lambda_hat": extracted.lam,
        "log_rmse_mlp_in": log_rmse(pred_te, id_true[te]),
        "log_rmse_compact_in": log_rmse(comp_te, id_true[te]),
        "log_rmse_mlp_extra": log_rmse(pred_ex, id_ex),
        "lin_rmse_mlp_in": lin_rmse(pred_te, id_true[te]),
        "n_train": int(len(tr)),
        "n_test": int(len(te)),
        "n_extra": int(len(extra)),
        "figs": [str(f.name) for f in figs],
    }
    out = ROOT / "reports" / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))

    ok = True
    if synthetic and vth_err is not None and vth_err >= VTH_ERR_MAX:
        print(f"FIT FAIL vth_err={vth_err}")
        ok = False
    if not synthetic:
        ss = payload["ss_mVdec"]
        if not (ss == ss and 40.0 < ss < 200.0):
            print(f"FIT FAIL ss_mVdec={ss}")
            ok = False
        if not (0.05 < extracted.vth < 1.2):
            print(f"FIT FAIL vth_hat={extracted.vth}")
            ok = False
    if payload["log_rmse_mlp_in"] >= LOG_RMSE_IN_MAX:
        print(f"FIT FAIL log_rmse_mlp_in={payload['log_rmse_mlp_in']}")
        ok = False
    for f in figs:
        if f.stat().st_size < FIG_MIN_BYTES:
            print(f"FIT FAIL small fig {f}")
            ok = False
    if payload["log_rmse_mlp_extra"] <= payload["log_rmse_mlp_in"]:
        print("FIT FAIL extra should be worse than in-range")
        ok = False
    if not card.exists():
        print("FIT FAIL missing spice card")
        ok = False
    va = card.with_suffix(".va")
    if not va.exists() or "I(d, s)" not in va.read_text():
        print("FIT FAIL missing Verilog-A compact model")
        ok = False
    if ok:
        print("FIT: PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
