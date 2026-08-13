# device-ai-ivfit

Silicon MOSFET I–V compact-model **baseline**: square-law synthetic data + a tiny
NumPy MLP. Compare the network against the analytic model and report RMSE.

This is an internship modeling repo. It is **not** a foundry PDK dump and
**not** a ferroelectric / carbon-nanotube thesis repo.

`rmse_test` on `data/synthetic.csv` is a **script self-check**, not device accuracy.

## Files

| Path | What |
|------|------|
| `SPEC.md` | Contract and allowlist |
| `src/physics.py` | Square-law Id(Vg,Vd) (teaching model, not BSIM) |
| `src/model.py` | 2→8→1 MLP |
| `src/generate_synthetic.py` | Writes `data/synthetic.csv` |
| `src/fit.py` | Train / RMSE / physics mutant |
| `data/synthetic.csv` | Generated I–V, columns `vg,vd,id` |

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make all
```

Expect: `FIT: PASS`, `PHYSICS CHECK: PASS`, mutant `--vth 1.2` caught, `LEAK CHECK: PASS`.

To fit a real TCAD export later (same columns, not committed here):

```bash
PYTHONPATH=src python3 src/fit.py --csv /path/to/idvg.csv
```

## Evidence (this machine)

- `make all` → `rmse_test ≈ 7.5e-6` on synthetic data (`< 5e-5` gate)
- analytic RMSE on the same CSV is ~1e-11 (CSV **is** the square-law)

## Limitations

- Synthetic square-law ≠ measured silicon ≠ BSIM.
- Do not write "fitted foundry silicon" until a lab CSV is used and that fact is in the README.
- No PDK, no Sentaurus decks, no binary `.plt` in git.

## License

MIT
