"""教学用 NMOS：亚阈指数 + 强反型平方律。不是 BSIM，不是硅片测量。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

VT = 0.02585  # kT/q at 300 K
EPS = 1e-18


@dataclass(frozen=True)
class DutParams:
    vth: float = 0.42
    k: float = 2.0e-4
    lam: float = 0.05
    n: float = 1.40
    i0: float = 6.0e-8


TRUE = DutParams()


def mosfet_id(
    vg: np.ndarray,
    vd: np.ndarray,
    p: DutParams = TRUE,
) -> np.ndarray:
    vg = np.asarray(vg, dtype=float)
    vd = np.clip(np.asarray(vd, dtype=float), 1e-6, None)
    vov = vg - p.vth
    id_lin = p.k * (vov * vd - 0.5 * vd * vd)
    id_sat = 0.5 * p.k * np.maximum(vov, 0.0) ** 2 * (1.0 + p.lam * vd)
    sat = vd > np.maximum(vov, 0.0)
    strong = np.where(sat, id_sat, id_lin)
    strong = np.where(vov <= 0.0, 0.0, np.maximum(strong, 0.0))
    sub = p.i0 * np.exp(vov / (p.n * VT)) * (1.0 - np.exp(-vd / VT))
    sub = np.clip(sub, 0.0, None)
    sub = np.where(vov < 0.0, sub, 0.0)
    return strong + sub
