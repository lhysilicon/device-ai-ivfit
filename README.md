# device-ai-ivfit

End-to-end **MOSFET compact-model extraction + tiny MLP surrogate**.

The DUT is an EKV-like teaching model (subthreshold + square-law) with 3% log-domain noise.
It is **not** wafer data and **not** a foundry PDK. The extractor does not read the hidden parameters.

```
I–V family  →  extract Vth / SS / k / λ  →  compact card
            →  MLP on log10(Id) (train Vg≤1.2 V)
            →  hold out Vg>1.2 V (must get worse)
            →  Id–Vg / Id–Vd / error map
```

## Figures

![Id–Vg](figs/idvg.png)

![Id–Vd](figs/idvd.png)

![MLP error](figs/mlp_error.png)

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make all
```

Expect `FIT: PASS`. Meaning of the gates:

| Gate | Meaning |
|------|---------|
| `vth_err < 0.08` | √Id intercept recovered threshold |
| `log_rmse_mlp_in < 0.45` | surrogate is usable **inside** the train box |
| `log_rmse_mlp_extra > in` | the network is **not** a physical law |

`--check-physics --vth 1.2` must fail (device off).

## Resume lines (honest)

```
• Built an end-to-end MOSFET I–V compact-model flow: extract Vth/SS/k/λ from
  Id–Vg/Id–Vd families, emit a SPICE-like card, and train a tiny MLP surrogate.
• Validated extraction to <80 mV Vth error on a noisy teaching DUT; showed the
  MLP error rising outside the train bias window (no physics extrapolation).
• Published scripts, figures, and the extracted card at
  github.com/lhysilicon/device-ai-ivfit (no PDK, no foundry models).
```

Do **not** replace those lines with “fitted foundry silicon” or a BSIM/PDK claim.

## Files

| Path | What |
|------|------|
| `docs/method.md` | 15-minute talk |
| `src/physics.py` | DUT (hidden params) |
| `src/extract.py` | compact-model extraction |
| `src/model.py` | MLP on log10(Id) |
| `src/fit.py` | orchestration + gates |
| `models/nmos_extracted.inc` | extracted card |
| `data/synthetic.csv` | generated I–V (`vg,vd,id`) |

Later: `python3 src/fit.py --csv your.csv` with the same columns. Lab decks stay off git.

## License

MIT
