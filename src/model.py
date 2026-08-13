"""2→16→1 MLP，拟合 log10(Id)。"""

from __future__ import annotations

import numpy as np

LOG_FLOOR = 1e-18


def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


class TinyMLP:
    def __init__(self, rng: np.random.Generator, hidden: int = 16):
        self.w1 = rng.normal(0.0, 0.25, size=(2, hidden))
        self.b1 = np.zeros(hidden)
        self.w2 = rng.normal(0.0, 0.25, size=(hidden, 1))
        self.b2 = np.zeros(1)
        self.x_mean = np.zeros(2)
        self.x_std = np.ones(2)
        self.y_mean = 0.0
        self.y_std = 1.0

    def _x(self, vg: np.ndarray, vd: np.ndarray) -> np.ndarray:
        raw = np.column_stack([np.asarray(vg, float), np.asarray(vd, float)])
        return (raw - self.x_mean) / self.x_std

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, dict]:
        z1 = np.dot(x, self.w1) + self.b1
        h = _relu(z1)
        y = np.dot(h, self.w2) + self.b2
        return y, {"x": x, "z1": z1, "h": h}

    def predict_id(self, vg: np.ndarray, vd: np.ndarray) -> np.ndarray:
        x = self._x(vg, vd)
        y, _ = self.forward(x)
        log_id = y[:, 0] * self.y_std + self.y_mean
        return np.power(10.0, np.clip(log_id, -18.0, 2.0))

    def fit(
        self,
        vg: np.ndarray,
        vd: np.ndarray,
        id_: np.ndarray,
        *,
        steps: int = 5000,
        lr: float = 0.04,
    ) -> list[float]:
        raw = np.column_stack([np.asarray(vg, float), np.asarray(vd, float)])
        self.x_mean = raw.mean(axis=0)
        self.x_std = np.clip(raw.std(axis=0), 1e-6, None)
        x = (raw - self.x_mean) / self.x_std
        log_id = np.log10(np.maximum(id_, LOG_FLOOR))
        self.y_mean = float(log_id.mean())
        self.y_std = float(max(log_id.std(), 1e-3))
        t = ((log_id - self.y_mean) / self.y_std)[:, None]
        losses: list[float] = []
        n = x.shape[0]
        for _ in range(steps):
            y, cache = self.forward(x)
            err = y - t
            loss = float(np.mean(err * err))
            if not np.isfinite(loss):
                raise RuntimeError("training diverged")
            losses.append(loss)
            dy = (2.0 / n) * err
            dw2 = np.dot(cache["h"].T, dy)
            db2 = dy.sum(axis=0)
            dh = np.dot(dy, self.w2.T)
            dz1 = dh * (cache["z1"] > 0.0)
            dw1 = np.dot(cache["x"].T, dz1)
            db1 = dz1.sum(axis=0)
            for arr in (dw1, db1, dw2, db2):
                np.clip(arr, -2.0, 2.0, out=arr)
            self.w2 -= lr * dw2
            self.b2 -= lr * db2
            self.w1 -= lr * dw1
            self.b1 -= lr * db1
        return losses
