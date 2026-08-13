"""把提取参数写成可粘进网表的教学卡片，不是 foundry 模型。"""

from __future__ import annotations

from pathlib import Path

from extract import Extracted


def write_card(path: Path, e: Extracted) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""* Extracted teaching compact model (not BSIM, not foundry PDK)
* Vth={e.vth:.4f} V  SS={e.ss_mVdec:.1f} mV/dec  n={e.n:.3f}  i0={e.i0:.3e} A
* k={e.k:.4e} A/V^2  lambda={e.lam:.4f} 1/V
.param vthx={e.vth:.6f}
.param nx={e.n:.6f}
.param i0x={e.i0:.8e}
.param kx={e.k:.8e}
.param lamx={e.lam:.6f}
"""
    )
