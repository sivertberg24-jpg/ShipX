
from __future__ import annotations
from pathlib import Path
from typing import Tuple, List
import streamlit as st
from shipx_dash.io.folder_loader import load_folder

def folder_fingerprint(base_dir: str | Path) -> Tuple[str, Tuple[Tuple[str, float, int], ...]]:
    base = Path(base_dir)
    if not base.exists():
        return (str(base), tuple())
    fp_rows: List[Tuple[str, float, int]] = []
    for p in sorted(list(base.glob("*.re1")) + list(base.glob("*.RE1"))):
        try:
            stat = p.stat()
            fp_rows.append((str(p), stat.st_mtime, stat.st_size))
        except Exception:
            continue
    for sd in sorted([p for p in base.iterdir() if p.is_dir()]):
        for p in sorted(list(sd.glob("*.re1")) + list(sd.glob("*.RE1"))):
            try:
                stat = p.stat()
                fp_rows.append((str(p), stat.st_mtime, stat.st_size))
            except Exception:
                continue
    return (str(base.resolve()), tuple(fp_rows))

@st.cache_data(show_spinner=False)
def cached_load_folder(base_dir: str | Path, fingerprint: Tuple[str, Tuple[Tuple[str, float, int], ...]]):
    studies, warnings = load_folder(base_dir)
    return studies, warnings
