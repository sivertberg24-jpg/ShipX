
from __future__ import annotations
from pathlib import Path
from typing import Tuple, List
import pandas as pd, numpy as np
from math import atan2, degrees, pi

try:
    from veres_re1_to_excel import parse_re1, DOF_NAMES_DEFAULT
except Exception as e:
    raise ImportError("veres_re1_to_excel.py must be available next to the app.") from e

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
                ph = degrees(atan2(im_val, re_val))
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
    from ..types import Study
    p = Path(path); name = study_name or p.parent.name or p.stem
    re1 = parse_re1(p)
    df, heads, dof_names = re1_to_tidy_df(re1, speed_index=0, convert_rot_to_deg_per_m=True)
    df.insert(0, "study", name)
    return Study(name=name, re1_path=p, df=df,
                 headings=sorted(list(set(float(h) for h in heads))), dof_names=dof_names)
