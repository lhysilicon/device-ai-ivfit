"""CSV 与划分。外推集 = 训练时没见过的高 Vg。"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

VG_TRAIN_MAX = 1.20


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


def splits(
    vg: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    in_box = np.flatnonzero(vg <= VG_TRAIN_MAX)
    extra = np.flatnonzero(vg > VG_TRAIN_MAX)
    perm = rng.permutation(in_box)
    n_te = max(int(0.2 * len(perm)), 8)
    te = perm[:n_te]
    tr = perm[n_te:]
    return tr, te, extra
