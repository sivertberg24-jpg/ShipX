
from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import streamlit as st
from ..types import Study
from ..processing.extract import all_headings, period_bounds_for
from ..config import DEFAULT_DOF, PERIOD_WINDOW_DEFAULT
try:
    from veres_re1_to_excel import DOF_NAMES_DEFAULT as _DOF_NAMES_DEFAULT
    DOF_NAMES = tuple(_DOF_NAMES_DEFAULT)
except Exception:
    DOF_NAMES = ("Surge","Sway","Heave","Roll","Pitch","Yaw")

def sidebar_controls(studies: Dict[str, Study]) -> tuple[str, bool, List[str], float, str, bool, tuple[float,float], str]:
    with st.sidebar:
        st.header("Load folder")
        base_dir = st.text_input("Base folder path", value=st.session_state.get("base_dir", ""))
        load_clicked = st.button("Load folder")
        if load_clicked:
            st.session_state["base_dir"] = base_dir
        st.markdown("---")
        st.header("Plot options")
        dof = st.selectbox("Degree of freedom", options=list(DOF_NAMES), index=list(DOF_NAMES).index(DEFAULT_DOF) if DEFAULT_DOF in DOF_NAMES else 3)
        metric = st.radio("Y-axis", options=["RAO amplitude", "Phase [deg]"], index=0, horizontal=True)
        metric_key = "amplitude" if metric.startswith("RAO") else "phase_deg"
        smooth = st.checkbox("Apply 3-point rolling mean (per study)", value=False)

        if studies:
            sel_studies = st.multiselect("Studies", options=sorted(studies.keys()), default=sorted(studies.keys()))
            heads = all_headings({k: studies[k] for k in sel_studies}) if sel_studies else all_headings(studies)
            if not heads: heads = [0.0]
            default_idx = heads.index(90.0) if 90.0 in heads else 0
            heading = st.selectbox("Heading (deg)", options=heads, index=default_idx, format_func=lambda x: f"{int(round(x))}°")
            pmin, pmax = period_bounds_for({k: studies[k] for k in sel_studies} if sel_studies else studies, dof=dof)
        else:
            sel_studies = []
            heading = 90.0
            pmin, pmax = PERIOD_WINDOW_DEFAULT

        x_window = st.slider("Period window [s]", min_value=float(max(0.1, pmin)), max_value=float(max(pmin+0.1, pmax)), value=(float(pmin), float(pmax)), step=0.1)

    return base_dir, load_clicked, sel_studies, float(heading), metric_key, bool(smooth), (float(x_window[0]), float(x_window[1])), dof
