# Spectre 对照（本机，不进 PDK）

`nmos_extracted.va` 是教学 Verilog-A，方程与 `src/physics.py` 的紧凑模型相同，**不是 BSIM**。

在已 source Cadence 环境的 WSL ext4 上：

```bash
cd <repo>/flow/spectre
mkdir -p out
spectre tb_idvg.scs
```

对照：同一偏置下 Python `compact_id` 与 Spectre `I(Vds)` 应对得上（数量级与拐点）。`.raw` 在 `flow/spectre/out/`，已 gitignore。
