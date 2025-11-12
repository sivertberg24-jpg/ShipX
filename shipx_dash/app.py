
from __future__ import annotations
import streamlit as st, pandas as pd
from shipx_dash.ui.controls import sidebar_controls
from shipx_dash.ui.plots import plot_overlaid
from shipx_dash.state.cache import folder_fingerprint, cached_load_folder
from shipx_dash.processing.extract import df_for
from shipx_dash.processing.filters import three_point_mean

st.set_page_config(page_title="ShipX RE1 Dashboard", layout="wide")
st.title("ShipX RE1 Dashboard — Multi‑study RAO viewer")

studies = st.session_state.get("studies", {})
base_dir, load_clicked, selected_studies, heading, metric, smooth, x_window, dof = sidebar_controls(studies)

if load_clicked and base_dir:
    with st.spinner("Loading folder..."):
        fp = folder_fingerprint(base_dir)
        studies, warnings = cached_load_folder(base_dir, fp)
        st.session_state["studies"] = studies
        st.session_state["warnings"] = warnings

if st.session_state.get("warnings"):
    for w in st.session_state["warnings"]:
        st.warning(w)

studies = st.session_state.get("studies", {})
if studies:
    if not selected_studies:
        selected_studies = sorted(studies.keys())
    curves, missing = [], []
    for name in selected_studies:
        s = studies.get(name)
        df = df_for(s, dof=dof, heading=heading)
        if df is None or df.empty:
            missing.append(name); continue
        if smooth:
            df = three_point_mean(df, cols=[metric])
        curves.append((name, df))
    if not curves:
        st.info(f"No data found at heading {int(round(heading))}° for DOF '{dof}'. Try a different heading or study set.")
    else:
        fig = plot_overlaid(curves, metric=metric, x_window=x_window, dof=dof, heading=heading)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Show data (concatenated)"):
            out = []
            for name, df in curves:
                tmp = df.copy(); tmp.insert(0, "study", name); out.append(tmp)
            table = pd.concat(out, ignore_index=True)
            st.dataframe(table, use_container_width=True, hide_index=True)
            csv = table.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv, file_name=f"rao_{dof}_{int(round(heading))}deg.csv", mime="text/csv")
    if missing:
        st.caption("Skipped studies without data for the selected heading: " + ", ".join(missing))
else:
    st.info("Load a base folder to begin. The folder should contain subfolders, each with one .re1 file (or .re1 files directly under the folder).")

st.caption("Tip: Rotational RAO amplitudes are converted to deg/m for plotting; translational remain m/m.")
