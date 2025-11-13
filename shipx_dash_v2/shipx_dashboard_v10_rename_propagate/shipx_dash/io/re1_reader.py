
from __future__ import annotations
from pathlib import Path
from typing import Tuple, List
import pandas as pd, numpy as np
from math import degrees, pi

# Import the parser if available; otherwise fall back to demo data
try:
    from veres_re1_to_excel import parse_re1, DOF_NAMES_DEFAULT
    HAS_PARSER = True
except Exception:
    HAS_PARSER = False
    DOF_NAMES_DEFAULT = ["Surge","Sway","Heave","Roll","Pitch","Yaw"]

def re1_to_tidy_df(re1, speed_index: int = 0, convert_rot_to_deg_per_m: bool = True) -> Tuple[pd.DataFrame, List[float], List[str]]:
    speed = re1.speeds[speed_index]
    heads = speed.heads
    omegas = speed.freqs  # rad/s
    records = []
    dof_names = DOF_NAMES_DEFAULT[:]
    ndof = re1.header.ndof
    for ih, head in enumerate(heads):
        for ifr, omega in enumerate(omegas):
            period_s = (2.0 * np.pi) / omega if omega != 0 else np.nan
            freq_hz = omega / (2.0 * np.pi) if omega != 0 else np.nan
            for i in range(ndof):
                re_val, im_val = speed.rao_re_im[ih][ifr][i]
                amp = (re_val * re_val + im_val * im_val) ** 0.5
                ph = degrees(np.arctan2(im_val, re_val))
                ph = ((ph + 180.0) % 360.0) - 180.0
                if i >= 3 and convert_rot_to_deg_per_m:
                    amp *= (180.0 / pi)  # rad/m -> deg/m
                records.append({
                    "heading_deg": float(head),
                    "dof": dof_names[i] if i < len(dof_names) else f"DOF{i+1}",
                    "omega_rad_s": omega,
                    "freq_hz": freq_hz,
                    "period_s": period_s,
                    "amplitude": amp,
                    "phase_deg": ph,
                })
    df = pd.DataFrame.from_records(records)
    return df, heads, dof_names[:ndof]

def read_re1_to_study(path: str | Path, study_name: str | None = None) -> "Study":
    from shipx_dash.types import Study
    from shipx_dash.processing.safety import make_demo_study
    p = Path(path); name = study_name or p.parent.name or p.stem

    if not HAS_PARSER:
        demo = make_demo_study(name, headings=[0,45,90,135,180])
        demo.warnings.append("veres_re1_to_excel.py not found; showing demo data. Place it next to app.py for real .re1 parsing.")
        return demo

    re1 = parse_re1(p)
    df, heads, dof_names = re1_to_tidy_df(re1, speed_index=0, convert_rot_to_deg_per_m=True)
    df.insert(0, "study", name)
    return Study(name=name, re1_path=p, df=df,
                 headings=sorted(list(set(float(h) for h in heads))), dof_names=dof_names)
