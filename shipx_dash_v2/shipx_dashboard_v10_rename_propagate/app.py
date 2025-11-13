
from __future__ import annotations
import os, sys
import streamlit as st, pandas as pd

# Prefer local package over any installed one
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shipx_dash.ui.controls import sidebar_load_and_global, panel_controls, sidebar_bulk_rename
from shipx_dash.ui.panels import ensure_panels, add_panel, remove_last_panel, clear_panels
from shipx_dash.ui.plots import plot_overlaid
from shipx_dash.state.cache import folder_fingerprint, cached_load_folder
from shipx_dash.processing.extract import df_for
from shipx_dash.processing.filters import three_point_mean
from shipx_dash.processing.peaks import peak_amplitude
from shipx_dash.io.auto_path import resolve_parameterstudy_root

st.set_page_config(page_title="ShipX Dashboard", layout="wide")
st.title("ShipX Dashboard - Multi-study RAO viewer")

# Sidebar: path + global DOF
studies = st.session_state.get("studies", {})
user_path, load_clicked, dof = sidebar_load_and_global(studies)

# Resolve CASE path -> ParameterStudy/<latest>
resolved = resolve_parameterstudy_root(user_path) if user_path else ""
if user_path:
    st.sidebar.caption(f"Resolved to: `{resolved}`")

# Heavy load only on click
if load_clicked and resolved:
    with st.spinner("Loading folder..."):
        fp = folder_fingerprint(resolved)
        st.session_state["folder_fp"] = fp  # for cache keys if needed
        studies, warnings = cached_load_folder(resolved, fp)
        st.session_state["studies"] = studies
        st.session_state["warnings"] = warnings

studies = st.session_state.get("studies", {})
if st.session_state.get("warnings"):
    for w in st.session_state["warnings"]:
        st.warning(w)

# Study names tool (returns True if renamed)
renamed = sidebar_bulk_rename(studies)
if renamed:
    # refresh local reference and force a clean rerun so widgets are re-keyed with rename_rev
    studies = st.session_state.get("studies", {})
    st.rerun()

# Plot controls
panels = ensure_panels(studies, dof)
with st.sidebar:
    st.markdown("---"); st.subheader("Plots")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Add plot", key="add_plot"):
            add_panel(studies, dof)
    with c2:
        if st.button("Remove last", key="remove_plot"):
            remove_last_panel()
    with c3:
        if st.button("Reset", key="reset_plots"):
            clear_panels(studies, dof)
panels = ensure_panels(studies, dof)

# --- Cached slice helper to speed re-draws ---
@st.cache_data(show_spinner=False)
def df_for_cached(study_name: str, dof: str, heading: float, folder_fp, rename_rev: int) -> pd.DataFrame:
    s = st.session_state["studies"][study_name]
    return df_for(s, dof=dof, heading=heading)

rev = st.session_state.get("rename_rev", 0)

# VERTICAL STACKED PLOTS
st.session_state.setdefault("panels", [])
if len(st.session_state["panels"]) < len(panels):
    st.session_state["panels"].extend([{}] * (len(panels) - len(st.session_state["panels"])))

for i, base_panel in enumerate(panels):
    st.markdown(f"### Plot {i+1}")
    cfg, submitted = panel_controls(base_panel, studies, dof, panel_index=i)

    # Persist latest controls
    st.session_state["panels"][i] = cfg

    if not studies:
        st.info("Load a folder to begin.")
        st.divider()
        continue

    curves, peaks = [], []
    # Use sanitized defaults stored under the rev-aware key, else cfg
    sel_key = f"sel_defaults_{i}_{rev}"
    if sel_key in st.session_state:
        chosen = st.session_state[sel_key]
    else:
        chosen = cfg.selected_studies or list(studies.keys())
    chosen = [x for x in chosen if x in studies]  # hard sanitize

    for name in chosen:
        df = df_for_cached(name, dof, cfg.heading, st.session_state.get("folder_fp"), rev)
        if df is None or df.empty:
            continue
        if cfg.smooth:
            df = three_point_mean(df, cols=[cfg.metric])
        curves.append((name, df))
        if cfg.metric == "amplitude":
            pV, pT = peak_amplitude(df, x_window=cfg.x_window)
        else:
            pV, pT = (None, None)
        peaks.append((name, pT, pV))

    if not curves:
        st.info(f"No data for heading {int(round(cfg.heading))}° and DOF '{dof}'.")
        st.divider()
        continue

    fig = plot_overlaid(
        curves, metric=cfg.metric, x_window=cfg.x_window,
        dof=dof, heading=cfg.heading,
        mark_peaks=peaks if (cfg.metric=='amplitude' and cfg.show_markers) else None
    )
    st.plotly_chart(fig, use_container_width=True, key=f"plot_{i}_{rev}")

    with st.expander("Peak summary (by RAO amplitude) — this DOF & heading"):
        peak_rows = [{"study": nm, "heading_deg": int(round(cfg.heading)), "dof": dof, "peak_amp": pV, "period_s_at_peak": pT} for nm, pT, pV in peaks]
        peak_df = pd.DataFrame(peak_rows)
        st.dataframe(peak_df, use_container_width=True, hide_index=True, key=f"peaks_df_{i}_{rev}")
        csv = peak_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download peaks (CSV)", data=csv, file_name=f"peaks_{dof}_{int(round(cfg.heading))}deg.csv", mime="text/csv", key=f"peaks_dl_{i}_{rev}")

    with st.expander("Show concatenated data"):
        out = []
        for name, df in curves:
            tmp = df.copy(); tmp.insert(0, "study", name); out.append(tmp)
        table = pd.concat(out, ignore_index=True)
        st.dataframe(table, use_container_width=True, hide_index=True, key=f"table_df_{i}_{rev}")
        csv = table.to_csv(index=False).encode("utf-8")
        st.download_button("Download plotted data (CSV)", data=csv, file_name=f"rao_{dof}_{int(round(cfg.heading))}deg.csv", mime="text/csv", key=f"data_dl_{i}_{rev}")

    st.divider()

st.caption("Apply names now replaces old names across the app immediately. "
           "Selections remap, widgets refresh, and defaults are sanitized. "
           "Paste CASE folder; resolver finds ParameterStudy/<latest>. Natural order preserved; stacked plots; optional peak markers.")
