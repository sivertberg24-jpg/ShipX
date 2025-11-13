
from __future__ import annotations
from typing import Dict, Tuple, List
import numpy as np, pandas as pd
from shipx_dash.types import Study

def all_headings(studies: Dict[str, Study]) -> List[float]:
    heads: set[float] = set()
    for s in studies.values():
        for h in s.headings:
            heads.add(float(h))
    return sorted(heads)

def df_for(study: Study, dof: str, heading: float, tol: float = 0.01) -> pd.DataFrame:
    if study is None or study.df is None or study.df.empty:
        return pd.DataFrame()
    df = study.df
    h = float(heading)
    mask = (df["dof"] == dof) & (np.abs(df["heading_deg"] - h) <= tol)
    out = df.loc[mask, ["period_s", "amplitude", "phase_deg"]].copy().sort_values("period_s")
    return out

def period_bounds_for(studies: Dict[str, Study], dof: str) -> Tuple[float, float]:
    per_min, per_max = np.inf, -np.inf
    for s in studies.values():
        df = s.df[s.df["dof"] == dof]
        if df.empty: continue
        pmin = df["period_s"].min(skipna=True); pmax = df["period_s"].max(skipna=True)
        if pmin < per_min: per_min = pmin
        if pmax > per_max: per_max = pmax
    if not np.isfinite(per_min) or not np.isfinite(per_max):
        return (3.0, 60.0)
    return float(per_min), float(per_max)
