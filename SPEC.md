# SPEC — device-ai-ivfit（实习主作品）

从 I–V 家族提取紧凑模型参数，并训练 MLP 作范围内替代；用高 Vg 外推证明网络不能当物理定律。

默认 `make all` 里的合成 DUT 仍是带亚阈的教学解析式 + 3% 对数噪声。另有 `data/tcad_tutorial.csv`：Sentaurus GettingStarted `SOI_IdVg` 教程器件的 I–V（**不是**晶圆、**不是** foundry PDK）。`.plt` / deck 不进 git。

## 完成标准（可机器验证）

1. `make all` 退出 0。
2. 合成路径 `src/fit.py`（默认 CSV）：`vth_err < 0.08`；`log_rmse_mlp_in < 0.45`；`log_rmse_mlp_extra > log_rmse_mlp_in`。
3. TCAD 路径 `src/fit.py --csv data/tcad_tutorial.csv`：不得用合成 `TRUE.vth` 当误差门；`40 < ss_mVdec < 200`；`0.05 < vth_hat < 1.2`；窗内外 MLP 误差门与图门同合成路径。
4. `figs/idvg.png` `figs/idvd.png` `figs/mlp_error.png` 每个 > 2 KB。
5. `models/nmos_extracted.inc` 存在。
6. `--check-physics --vth 1.2` 非零。缺 CSV 列非零。
7. `make leak-check` 退出 0。

## 边界

- 不得把 DUT 写成 foundry 硅片 / BSIM / 已拟合工艺库。
- 不得提交 `.plt` `.tdr` `.lib` `.lef` 或实验室绝对路径。
- 数字仓 P&R 不是本仓完成条件。

## 失败降级

- 无 TCAD CSV：本仓仍是**完整提参流程**，简历必须写 “compact-model-generated DUT”。
- 现有 `data/tcad_tutorial.csv`：可写 “fitted Sentaurus GettingStarted SOI_IdVg tutorial I–V”，仍不得写 foundry PDK / 硅片实测。
