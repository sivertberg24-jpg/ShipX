# shipx_dash/ui/plots.py
from __future__ import annotations
from typing import List, Tuple, Optional, Dict
import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd


# A long qualitative palette so names have stable, matching colors
PALETTE = (
    pc.qualitative.Plotly
    + pc.qualitative.Dark24
    + pc.qualitative.Safe
    + pc.qualitative.Set3
    + pc.qualitative.Pastel
)


def _y_label(metric: str, dof: str) -> str:
    """Axis label that adapts to metric and DOF."""
    if metric == "amplitude":
        units = "m/m" if dof in {"Surge", "Sway", "Heave"} else "deg/m"
        return f"RAO amplitude [{units}]"
    return "Phase [deg]"


def _make_color_map(names: List[str]) -> Dict[str, str]:
    """Deterministic mapping: first appearance gets a palette color."""
    return {nm: PALETTE[i % len(PALETTE)] for i, nm in enumerate(names)}


def plot_overlaid(
    curves: List[Tuple[str, pd.DataFrame]],
    metric: str,
    x_window: Tuple[float, float],
    dof: str,
    heading: float,
    mark_peaks: Optional[List[Tuple[str, float, float]]] = None,
    show_samples: bool = False,              # optional; default is lines without circles
    color_map: Optional[Dict[str, str]] = None,
):
    """
    curves: [(study_name, df_with_period_amp_phase), ...]
            df columns: period_s, amplitude, phase_deg
    metric: 'amplitude' or 'phase_deg'
    x_window: (x0, x1) in seconds (Period)
    dof: for labeling units
    heading: for plot title
    mark_peaks: optional list of (study_name, period_at_peak, amp_at_peak) for amplitude plots
    show_samples: if True, draw small markers on the line samples
    """
    fig = go.Figure()
    x0, x1 = x_window

    # Build a consistent color map so line, cross and label share the same color
    names = [name for name, _ in curves]
    cmap = color_map or _make_color_map(names)

    # --- Curves (default: lines only; no circles) ---
    for name, df in curves:
        if df is None or df.empty:
            continue
        df_win = df[(df["period_s"] >= x0) & (df["period_s"] <= x1)]
        color = cmap.get(name, "#1f77b4")

        fig.add_trace(
            go.Scatter(
                x=df_win["period_s"],
                y=df_win["amplitude" if metric == "amplitude" else "phase_deg"],
                mode="lines+markers" if show_samples else "lines",
                name=name,
                line=dict(color=color, width=2),
                marker=(dict(size=5, color=color) if show_samples else None),
                hovertemplate=(
                    f"{name}<br>"
                    "Period: %{x:.3g}s<br>"
                    + ("RAO amp: %{y:.3g}" if metric == "amplitude" else "Phase: %{y:.3g}°")
                    + "<extra></extra>"
                ),
            )
        )

    # --- Peak overlay (X marker + right-side label in same color) ---
    # Only plotted when mark_peaks is provided (e.g. when 'Show peak markers' is checked
    # and metric=='amplitude' in your app code).
    if mark_peaks:
        for label, pT, pV in mark_peaks:
            if pT is None or pV is None:
                continue
            color = cmap.get(label, "#000000")
            fig.add_trace(
                go.Scatter(
                    x=[pT],
                    y=[pV],
                    mode="markers+text",
                    marker=dict(
                        size=8,
                        symbol="x",
                        color=color,
                        line=dict(width=2, color=color),
                    ),
                    text=[label],
                    textposition="middle right",
                    textfont=dict(color=color, size=12),
                    showlegend=False,  # keep legend from duplicating entries
                    hovertemplate=f"{label}<br>Peak: {pV:.3g}<br>Period: {pT:.3g}s<extra></extra>",
                    name=f"{label} peak",
                )
            )

    fig.update_layout(
        title=f"{dof} • {('RAO amplitude' if metric=='amplitude' else 'Phase')} vs Period • Heading {int(round(heading))}°",
        xaxis_title="Period [s]",
        yaxis_title=_y_label(metric, dof),
        legend_title_text="Study",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=50, r=30, t=60, b=40),
    )
    return fig
