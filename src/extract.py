"""从 I–V 提 Vth / SS / k / lambda。提取器看不到 DUT 真值。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics import VT, DutParams, mosfet_id


@dataclass
class Extracted:
    vth: float
    ss_mVdec: float
    k: float
    lam: float
    n: float
    i0: float


def _slice(vg: np.ndarray, vd: np.ndarray, id_: np.ndarray, vd_target: float):
    mask = np.abs(vd - vd_target) <= (np.min(np.abs(vd - vd_target)) + 1e-12)
    g = vg[mask]
    i = np.maximum(id_[mask], 0.0)
    order = np.argsort(g)
    return g[order], i[order]


def extract_params(vg: np.ndarray, vd: np.ndarray, id_: np.ndarray) -> Extracted:
    vg = np.asarray(vg, float)
    vd = np.asarray(vd, float)
    id_ = np.asarray(id_, float)

    g_lin, i_lin = _slice(vg, vd, id_, float(np.min(vd)))
    # SS in subthreshold: low current, still rising exponentially
    sub = (i_lin > 1e-13) & (i_lin < 1e-6)
    if np.count_nonzero(sub) >= 4:
        slope = np.polyfit(g_lin[sub], np.log10(i_lin[sub]), 1)[0]
        ss = float(1000.0 / slope) if slope > 1e-6 else float("nan")
    else:
        ss = float("nan")

    # Vth: saturation √Id vs Vg intercept (classic teaching method)
    g_sat, i_sat = _slice(vg, vd, id_, float(np.max(vd)))
    on = (i_sat > 1e-6) & (g_sat > (g_sat.min() + 0.2))
    if np.count_nonzero(on) >= 5:
        s = np.sqrt(i_sat[on])
        a, b = np.polyfit(g_sat[on], s, 1)  # s = a*Vg + b, intercept Vg=-b/a
        vth = float(-b / a) if abs(a) > 1e-12 else 0.4
    else:
        vth = 0.4
    vth = float(np.clip(vth, 0.05, 1.2))

    on2 = (vg > vth + 0.15) & (id_ > 1e-8)
    vov = vg[on2] - vth
    vds = vd[on2]
    ids = id_[on2]
    sat = vds > vov
    a = np.column_stack([0.5 * vov[sat] ** 2, 0.5 * vov[sat] ** 2 * vds[sat]])
    if a.shape[0] >= 4:
        coef, *_ = np.linalg.lstsq(a, ids[sat], rcond=None)
        k_hat = max(float(coef[0]), 1e-8)
        lam_hat = max(float(coef[1] / k_hat), 0.0) if k_hat > 0 else 0.05
    else:
        k_hat, lam_hat = 1e-4, 0.05
    n_hat = float(ss / (1000.0 * VT * np.log(10))) if ss == ss and ss > 20 else 1.4
    n_hat = float(np.clip(n_hat, 1.0, 2.5))
    sub_pts = (vg < vth - 0.05) & (id_ > 1e-13) & (id_ < 1e-7)
    if np.count_nonzero(sub_pts) >= 4:
        denom = np.exp((vg[sub_pts] - vth) / (n_hat * VT)) * (1.0 - np.exp(-np.clip(vd[sub_pts], 1e-6, None) / VT))
        i0_hat = float(np.median(id_[sub_pts] / np.clip(denom, 1e-18, None)))
        i0_hat = float(np.clip(i0_hat, 1e-12, 1e-5))
    else:
        i0_hat = 5e-8
    return Extracted(vth=vth, ss_mVdec=ss, k=k_hat, lam=lam_hat, n=n_hat, i0=i0_hat)


def compact_id(vg: np.ndarray, vd: np.ndarray, e: Extracted) -> np.ndarray:
    p = DutParams(vth=e.vth, k=e.k, lam=e.lam, n=e.n, i0=e.i0)
    return mosfet_id(vg, vd, p)
