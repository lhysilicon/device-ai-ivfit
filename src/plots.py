"""Id–Vg / Id–Vd / 误差图。Agg 后端，不弹窗。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save_figures(
    vg: np.ndarray,
    vd: np.ndarray,
    id_true: np.ndarray,
    id_comp: np.ndarray,
    id_mlp: np.ndarray,
    out_dir: Path,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    vd_lin = float(np.min(vd))
    m = np.isclose(vd, vd_lin, atol=1e-6)
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.semilogy(vg[m], np.maximum(id_true[m], 1e-16), "k.", label="DUT", markersize=4)
    ax.semilogy(vg[m], np.maximum(id_comp[m], 1e-16), "C0-", label="extracted compact", lw=1.4)
    ax.semilogy(vg[m], np.maximum(id_mlp[m], 1e-16), "C1--", label="MLP", lw=1.4)
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("Id (A)")
    ax.set_title(f"Id–Vg at Vd={vd_lin:.3f} V")
    ax.legend(frameon=False)
    ax.grid(True, which="both", ls=":", alpha=0.5)
    p = out_dir / "idvg.png"
    fig.tight_layout()
    fig.savefig(p, dpi=140)
    plt.close(fig)
    written.append(p)

    vg_on = float(np.quantile(vg, 0.8))
    # nearest vg slice
    g_uniq = np.unique(np.round(vg, 4))
    g_pick = g_uniq[np.argmin(np.abs(g_uniq - vg_on))]
    m2 = np.isclose(vg, g_pick, atol=6e-4)
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    order = np.argsort(vd[m2])
    ax.plot(vd[m2][order], id_true[m2][order], "k.", label="DUT", markersize=4)
    ax.plot(vd[m2][order], id_comp[m2][order], "C0-", label="extracted compact", lw=1.4)
    ax.plot(vd[m2][order], id_mlp[m2][order], "C1--", label="MLP", lw=1.4)
    ax.set_xlabel("Vd (V)")
    ax.set_ylabel("Id (A)")
    ax.set_title(f"Id–Vd at Vg={g_pick:.2f} V")
    ax.legend(frameon=False)
    ax.grid(True, ls=":", alpha=0.5)
    p = out_dir / "idvd.png"
    fig.tight_layout()
    fig.savefig(p, dpi=140)
    plt.close(fig)
    written.append(p)

    err = np.abs(np.log10(np.maximum(id_mlp, 1e-18)) - np.log10(np.maximum(id_true, 1e-18)))
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    sc = ax.scatter(vg, vd, c=err, s=18, cmap="magma", vmin=0.0, vmax=max(float(np.quantile(err, 0.95)), 0.2))
    fig.colorbar(sc, ax=ax, label="|Δ log10 Id| (MLP vs DUT)")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("Vd (V)")
    ax.set_title("MLP error map")
    p = out_dir / "mlp_error.png"
    fig.tight_layout()
    fig.savefig(p, dpi=140)
    plt.close(fig)
    written.append(p)
    return written
