# Spectre 对照（无 PDK）

`nmos_extracted.va` 是教学 Verilog-A，方程与 `src/physics.py` 的紧凑模型相同，**不是 BSIM**。

`make all` 在 Mac 上就能跑，不需要 Spectre。Cadence Spectre 装在 EDA 机的 Linux/WSL 上，**不是** Mac 笔记本。不要把实验室绝对路径写进本仓。

在已 source Cadence 环境的 WSL ext4 上：

```bash
cd <repo>/flow/spectre
mkdir -p out
spectre tb_idvg.scs
```

对照：同一偏置下 Python `compact_id` 与 Spectre `I(Vds)` 应对得上（数量级与拐点）。`.raw` 在 `flow/spectre/out/`，已 gitignore。
