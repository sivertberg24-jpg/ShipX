
from __future__ import annotations
from typing import List, Tuple
import plotly.graph_objects as go
import pandas as pd

def _y_label(metric: str, dof: str) -> str:
    if metric == "amplitude":
        units = "m/m" if dof in {"Surge","Sway","Heave"} else "deg/m"
        return f"RAO amplitude [{units}]"
    return "Phase [deg]"

def plot_overlaid(curves: List[Tuple[str, pd.DataFrame]], metric: str, x_window: Tuple[float, float], dof: str, heading: float):
    fig = go.Figure()
    x0, x1 = x_window
    for name, df in curves:
        if df is None or df.empty:
            continue
        df_win = df[(df["period_s"] >= x0) & (df["period_s"] <= x1)]
        fig.add_trace(go.Scatter(
            x=df_win["period_s"],
            y=df_win["amplitude" if metric=="amplitude" else "phase_deg"],
            mode="lines+markers",
            name=name,
        ))
    fig.update_layout(
        title=f"{dof} • {('RAO amplitude' if metric=='amplitude' else 'Phase')} vs Period • Heading {heading}°",
        xaxis_title="Period [s]",
        yaxis_title=_y_label(metric, dof),
        legend_title_text="Study",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig
