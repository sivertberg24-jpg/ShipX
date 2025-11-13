
from __future__ import annotations
from typing import Dict
import streamlit as st
from shipx_dash.types import Study, PanelConfig
from shipx_dash.processing.extract import all_headings, period_bounds_for

DEFAULT_PANELS_KEY = "panels"

def _default_panel(studies: Dict[str, Study], dof: str) -> PanelConfig:
    heads = all_headings(studies) if studies else [90.0]
    heading = 90.0 if 90.0 in heads else (heads[0] if heads else 90.0)
    pmin, pmax = period_bounds_for(studies, dof=dof) if studies else (3.0, 60.0)
    return PanelConfig(
        selected_studies=list(studies.keys()) if studies else [],
        heading=float(heading),
        metric="amplitude",
        smooth=False,
        x_window=(float(pmin), float(pmax)),
        show_markers=False,
    )

def ensure_panels(studies: Dict[str, Study], dof: str) -> list[PanelConfig]:
    if DEFAULT_PANELS_KEY not in st.session_state or not st.session_state[DEFAULT_PANELS_KEY]:
        st.session_state[DEFAULT_PANELS_KEY] = [_default_panel(studies, dof)]
    out: list[PanelConfig] = []
    for p in st.session_state[DEFAULT_PANELS_KEY]:
        keep = [s for s in (p.selected_studies or []) if s in studies]
        if not keep and studies:
            keep = list(studies.keys())
        out.append(PanelConfig(
            selected_studies=keep,
            heading=float(p.heading),
            metric=p.metric if p.metric in ("amplitude", "phase_deg") else "amplitude",
            smooth=bool(p.smooth),
            x_window=(float(p.x_window[0]), float(p.x_window[1])) if p.x_window else (3.0, 60.0),
            show_markers=bool(getattr(p, "show_markers", False)),
        ))
    st.session_state[DEFAULT_PANELS_KEY] = out
    return out

def add_panel(studies: Dict[str, Study], dof: str):
    panels = ensure_panels(studies, dof)
    base = panels[-1] if panels else _default_panel(studies, dof)
    st.session_state[DEFAULT_PANELS_KEY].append(PanelConfig(
        selected_studies=list(base.selected_studies),
        heading=float(base.heading),
        metric=str(base.metric),
        smooth=bool(base.smooth),
        x_window=(float(base.x_window[0]), float(base.x_window[1])),
        show_markers=bool(base.show_markers),
    ))

def remove_last_panel():
    if DEFAULT_PANELS_KEY in st.session_state and len(st.session_state[DEFAULT_PANELS_KEY]) > 1:
        st.session_state[DEFAULT_PANELS_KEY].pop()

def clear_panels(studies: Dict[str, Study], dof: str):
    st.session_state[DEFAULT_PANELS_KEY] = [_default_panel(studies, dof)]
