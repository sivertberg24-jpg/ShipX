
import pandas as pd
def three_point_mean(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if df is None or df.empty: return df
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].rolling(window=3, center=True, min_periods=1).mean()
    return out
