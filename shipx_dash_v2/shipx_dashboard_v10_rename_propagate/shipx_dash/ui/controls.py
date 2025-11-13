
"""UI controls for the ShipX Dashboard."""

from __future__ import annotations
from typing import Dict, List
import streamlit as st
from shipx_dash.types import Study, PanelConfig
from shipx_dash.processing.extract import all_headings, period_bounds_for
from shipx_dash.config import DEFAULT_DOF, PERIOD_WINDOW_DEFAULT

try:
    from veres_re1_to_excel import DOF_NAMES_DEFAULT as _DOF_NAMES_DEFAULT
    DOF_NAMES = tuple(_DOF_NAMES_DEFAULT)
except Exception:
    DOF_NAMES = ("Surge", "Sway", "Heave", "Roll", "Pitch", "Yaw")


def sidebar_load_and_global(studies: Dict[str, Study]) -> tuple[str, bool, str]:
    """Sidebar controls for loading folder and global options."""
    with st.sidebar:
        st.header("Load folder")
        base_dir = st.text_input(
            "Folder Path ParameterStudy",
            value=st.session_state.get("base_dir", "")
        )
        load_clicked = st.button("Load folder", key="load_btn")
        if load_clicked:
            st.session_state["base_dir"] = base_dir

        st.markdown("---")
        st.header("Global options")
        dof = st.selectbox(
            "Degree of freedom",
            options=list(DOF_NAMES),
            index=list(DOF_NAMES).index(DEFAULT_DOF) if DEFAULT_DOF in DOF_NAMES else 3,
            key="global_dof"
        )
    return base_dir, load_clicked, dof


def _sanitize_defaults(options: List[str], defaults: List[str]) -> List[str]:
    """Ensure defaults are valid given current options."""
    if not options:
        return []
    if not defaults:
        return list(options)
    valid = [x for x in defaults if x in options]
    return valid if valid else list(options)


def sidebar_bulk_rename(studies: Dict[str, Study]) -> bool:
    """Sidebar control for renaming multiple studies at once."""
    renamed = False
    with st.sidebar.expander("Study Names", expanded=False):
        st.caption("Paste names from Excel (one per line). They replace current study names in folder order (natural numeric).")
        old_order = list(studies.keys())
        if old_order:
            st.write("Current order:")
            st.code("\n".join(old_order), language=None)
        pasted = st.text_area(
            "Names (one per line)",
            value="",
            height=140,
            placeholder="Run A\nRun B\nRun C",
            key="bulk_names"
        )
        apply = st.button("Apply names", key="apply_names")
        if apply:
            names = [ln.strip() for ln in pasted.splitlines() if ln.strip()]
            if len(names) != len(old_order):
                st.warning(f"Got {len(names)} names but there are {len(old_order)} studies. Provide exactly one name per study.")
                return False

            # Make unique names
            seen = set()
            uniq = []
            for nm in names:
                base = nm
                i = 1
                while nm in seen:
                    i += 1
                    nm = f"{base} ({i})"
                seen.add(nm)
                uniq.append(nm)

            # Build mapping old->new and rekey studies
            mapping = dict(zip(old_order, uniq))
            new_studies: Dict[str, Study] = {}
            for old, new in zip(old_order, uniq):
                s = studies[old]
                s.name = new
                if "study" in s.df.columns:
                    s.df.loc[:, "study"] = new
                new_studies[new] = s

            st.session_state["studies"] = new_studies

            # Bump rename revision to force fresh widget keys
            st.session_state["rename_rev"] = st.session_state.get("rename_rev", 0) + 1

            # Remap panel selections and clear stale widget state
            panels = st.session_state.get("panels", [])
            for idx, panel in enumerate(panels or []):
                sel = panel.selected_studies or old_order
                sel_remapped = [mapping.get(x, x) for x in sel if mapping.get(x, x) in new_studies]
                if not sel_remapped:
                    sel_remapped = list(new_studies.keys())
                panel.selected_studies = sel_remapped
                panels[idx] = panel

            st.session_state["panels"] = panels

            # Purge any old selection widget keys to avoid stale defaults
            for k in list(st.session_state.keys()):
                if k.startswith("sel_defaults_") or k.startswith("sel_ms_"):
                    del st.session_state[k]

            st.success("Study names updated; selections remapped and UI refreshed.")
            renamed = True
    return renamed


def _form_select(options: List[str], defaults: List[str], panel_index: int) -> tuple[list[str], bool]:
    """
    Display study selection widget with Select All/None/Apply buttons.
    
    Button actions must update session state BEFORE the widget is created.
    We use a separate action key to trigger changes before widget initialization.
    
    Args:
        options: List of available study names
        defaults: Default selected studies
        panel_index: Index of the panel (for unique widget keys)
    
    Returns:
        tuple: (selected_studies, submitted)
    """
    rev = st.session_state.get("rename_rev", 0)
    ms_key = f"sel_ms_{panel_index}_{rev}"
    sel_key = f"sel_defaults_{panel_index}_{rev}"  # Key used by app.py to read selections
    action_key = f"sel_action_{panel_index}_{rev}"
    
    # Initialize multiselect session state on first run
    if ms_key not in st.session_state:
        st.session_state[ms_key] = _sanitize_defaults(options, defaults)
    
    # Check if we need to apply an action BEFORE creating the widget
    if action_key in st.session_state:
        action = st.session_state[action_key]
        if action == "all":
            st.session_state[ms_key] = list(options)
        elif action == "none":
            st.session_state[ms_key] = []
        # Clear the action after applying it
        del st.session_state[action_key]
        st.rerun()
    
    # Display the multiselect widget
    # It reads from and writes to st.session_state[ms_key]
    chosen = st.multiselect(
        "Selected studies",
        options=options,
        default=st.session_state[ms_key],
        key=ms_key
    )
    
    # Display buttons in columns
    col1, col2, col3 = st.columns(3)
    submitted = False
    
    with col1:
        if st.button("Select all", key=f"all_btn_{panel_index}_{rev}"):
            # Set action to be applied on next render, BEFORE widget creation
            st.session_state[action_key] = "all"
            st.rerun()
    
    with col2:
        if st.button("Select none", key=f"none_btn_{panel_index}_{rev}"):
            # Set action to be applied on next render, BEFORE widget creation
            st.session_state[action_key] = "none"
            st.rerun()
    
    with col3:
        if st.button("Apply to plot", key=f"apply_btn_{panel_index}_{rev}"):
            # Save the current selection to sel_key so app.py reads it for the plot
            st.session_state[sel_key] = st.session_state[ms_key]
            submitted = True
    
    # Return the current multiselect value
    return st.session_state[ms_key], submitted


def panel_controls(panel: PanelConfig, studies: Dict[str, Study], dof: str, panel_index: int) -> tuple[PanelConfig, bool]:
    """Display all controls for a single plot panel."""
    heads = all_headings(studies) if studies else [90.0]
    if not heads:
        heads = [90.0]
    
    pmin, pmax = period_bounds_for(studies, dof=dof) if studies else (PERIOD_WINDOW_DEFAULT[0], PERIOD_WINDOW_DEFAULT[1])
    rev = st.session_state.get("rename_rev", 0)

    st.subheader("Plot settings")
    
    # Get selected studies
    options = list(studies.keys())
    sel, submitted = _form_select(options, panel.selected_studies or options, panel_index)

    # Heading selector
    default_idx = heads.index(90.0) if 90.0 in heads else 0
    heading_idx = default_idx if panel.heading not in heads else heads.index(panel.heading)
    heading = st.selectbox(
        "Heading (deg)",
        options=heads,
        index=heading_idx,
        format_func=lambda x: f"{int(round(x))}°",
        key=f"heading_{panel_index}_{rev}"
    )
    
    # Metric selector
    metric_lbl = st.radio(
        "Y-axis",
        options=["RAO amplitude", "Phase [deg]"],
        index=(0 if panel.metric == 'amplitude' else 1),
        horizontal=True,
        key=f"metric_{panel_index}_{rev}"
    )
    metric_key = "amplitude" if metric_lbl.startswith("RAO") else "phase_deg"
    
    # Smoothing checkbox
    smooth = st.checkbox(
        "Apply 3-point rolling mean",
        value=bool(panel.smooth),
        key=f"smooth_{panel_index}_{rev}"
    )
    
    # Peak markers checkbox
    show_markers = st.checkbox(
        "Show peak markers on chart",
        value=bool(getattr(panel, "show_markers", False)),
        key=f"showmarkers_{panel_index}_{rev}"
    )
    
    # Period window slider
    xwin = st.slider(
        "Period window [s]",
        min_value=float(max(0.1, pmin)),
        max_value=float(max(pmin + 0.1, pmax)),
        value=(
            float(panel.x_window[0]) if panel.x_window else float(pmin),
            float(panel.x_window[1]) if panel.x_window else float(pmax)
        ),
        step=0.1,
        key=f"xwin_{panel_index}_{rev}"
    )

    # Create and return configuration
    cfg = PanelConfig(
        selected_studies=sel,
        heading=float(heading),
        metric=metric_key,
        smooth=bool(smooth),
        x_window=(float(xwin[0]), float(xwin[1])),
        show_markers=bool(show_markers),
    )
    return cfg, submitted
