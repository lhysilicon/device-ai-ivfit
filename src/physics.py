"""硅 NMOS 平方律 Id(Vg, Vd)。教学解析式，不是 BSIM。"""

from __future__ import annotations

import numpy as np

K = 2.0e-4  # A/V^2
VTH = 0.40
LAMBDA = 0.05
EPS = 1e-15


def square_law_id(vg: np.ndarray, vd: np.ndarray, vth: float = VTH) -> np.ndarray:
    vg = np.asarray(vg, dtype=float)
    vd = np.asarray(vd, dtype=float)
    vov = vg - vth
    id_lin = K * (vov * vd - 0.5 * vd * vd)
    id_sat = 0.5 * K * vov * vov * (1.0 + LAMBDA * vd)
    sat = vd > np.maximum(vov, 0.0)
    off = vov <= 0.0
    out = np.where(sat, id_sat, id_lin)
    out = np.where(off, 0.0, np.maximum(out, 0.0))
    return out
