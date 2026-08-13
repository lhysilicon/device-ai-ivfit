# SPEC — device-ai-ivfit（实习主作品，非课题仓）

硅基 MOSFET I–V → Python 拟合/小网络预测。本仓不包含铁电/碳基课题内容。

## 北极星

一份**公开、可 clone、面试 15 分钟能讲完**的器件建模作品：曲线从哪来、怎么拟合、误差怎么报、以后怎么换成 TCAD CSV。数字仓 `stream-pe-asic` 是工具链识字件，不是本仓。

## 完成标准（可机器验证）

1. `python3 src/fit.py` 退出码 0，写出 `reports/metrics.json`，且 `rmse_test < 5e-5`（合成平方律数据）。
2. `python3 src/fit.py --check-physics --vth 1.2` 必须非零退出且 stdout 含 `PHYSICS CHECK FAIL`。
3. `src/` 无 Sentaurus `*.plt`、无 PDK、无课题关键词。
4. 输入只认 CSV 列 `vg,vd,id`。缺列非零退出。

## 边界 / 禁止

- 不得把实验室 deck、PDK、许可证路径写进已跟踪文件。
- 不得把本仓写成 CIM / 铁电 / 碳基博士课题。
- 不得用「PINN 复现某篇铁电论文」当实习句；本仓是平方律基线 + 小 MLP，诚实写局限。
- 公开 `git ls-files` 只允许：`README.md` `LICENSE` `SPEC.md` `Makefile` `requirements.txt` `src/*` `data/synthetic.csv` `reports/.gitkeep` `.gitignore` `scripts/leak_check.py` `.github/workflows/*.yml`。`data/tcad_raw/`、`reports/metrics.json`、`STATE.md` 永不进 git。

## 失败降级

- 没有 TCAD CSV：合成数据可跑通脚本，简历写「合成基线 + 本机 TCAD 替换接口」，不写「已拟合 foundry 硅片」。
- 没有 numpy：本仓不算完成。
- 公开泄漏 PDK/deck：删库重建，不改 private 当没发生。

## 命令含义

| 命令 | 含义 |
|---|---|
| `python3 src/generate_synthetic.py` | 用平方律**造** Id(Vg,Vd)，不是测真实器件 |
| `python3 src/fit.py` | 训练小 MLP，对照解析模型算 RMSE |
| `python3 src/fit.py --csv path.csv` | 同一套脚本吃 TCAD 导出的 `vg,vd,id`；导出在实验室做，不进本仓 |
