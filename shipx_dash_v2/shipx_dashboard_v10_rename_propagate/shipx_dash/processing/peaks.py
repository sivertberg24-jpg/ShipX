
from __future__ import annotations
from typing import Optional
import pandas as pd

def peak_amplitude(df: pd.DataFrame, x_window: tuple[float, float] | None = None) -> tuple[Optional[float], Optional[float]]:
    if df is None or df.empty or "amplitude" not in df or "period_s" not in df:
        return None, None
    sub = df
    if x_window is not None:
        x0, x1 = x_window
        sub = sub[(sub["period_s"] >= x0) & (sub["period_s"] <= x1)]
    if sub.empty:
        return None, None
    idx = sub["amplitude"].astype(float).idxmax()
    return float(sub.loc[idx, "amplitude"]), float(sub.loc[idx, "period_s"])
