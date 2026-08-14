"""把提取参数写成教学卡片 + Verilog-A。不是 BSIM，不是 foundry 模型。"""

from __future__ import annotations

from pathlib import Path

from extract import Extracted
from physics import VT


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
    write_veriloga(path.with_suffix(".va"), e)


def write_veriloga(path: Path, e: Extracted) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""// Teaching NMOS compact model (subthreshold + square-law). Not BSIM.
`include "disciplines.vams"
module nmos_extracted(d, g, s);
    inout d, g, s;
    electrical d, g, s;
    parameter real vth = {e.vth:.8f};
    parameter real nfac = {e.n:.8f};
    parameter real i0 = {e.i0:.8e};
    parameter real k = {e.k:.8e};
    parameter real lam = {e.lam:.8f};
    localparam real vt = {VT:.8f};
    real vgs, vds, vov, id_lin, id_sat, id_strong, id_sub;
    analog begin
        vgs = V(g,s);
        vds = V(d,s);
        if (vds < 1.0e-6) vds = 1.0e-6;
        vov = vgs - vth;
        id_sub = 0.0;
        id_strong = 0.0;
        if (vov < 0.0) begin
            id_sub = i0 * exp(vov / (nfac * vt)) * (1.0 - exp(-vds / vt));
            if (id_sub < 0.0) id_sub = 0.0;
        end else begin
            id_lin = k * (vov * vds - 0.5 * vds * vds);
            id_sat = 0.5 * k * vov * vov * (1.0 + lam * vds);
            if (vds > vov) id_strong = id_sat;
            else if (id_lin > 0.0) id_strong = id_lin;
            else id_strong = 0.0;
        end
        I(d, s) <+ id_sub + id_strong;
    end
endmodule
"""
    )
