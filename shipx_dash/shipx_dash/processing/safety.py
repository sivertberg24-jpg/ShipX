
from __future__ import annotations
from pathlib import Path
from typing import List
import numpy as np, pandas as pd
from ..types import Study

def demo_roll_curve(heading_deg: float, n: int = 120) -> pd.DataFrame:
    periods = np.linspace(4.0, 20.0, n)
    peak = 9.0 + 2.0 * np.cos(np.radians(heading_deg))
    width = 1.6 + 0.4 * np.sin(np.radians(heading_deg))
    amp_scale = 0.9 + 0.3 * np.cos(np.radians(heading_deg))
    amplitude = 0.1 + amp_scale * np.exp(-0.5 * ((periods - peak) / width) ** 2)
    phase_deg = 20 + 30 * np.sin(periods / 3 + np.radians(heading_deg) / 2)
    return pd.DataFrame({
        "period_s": periods,
        "amplitude": amplitude,
        "phase_deg": phase_deg,
        "heading_deg": float(heading_deg),
        "dof": "Roll",
        "omega_rad_s": (2.0 * np.pi) / periods,
        "freq_hz": 1.0 / periods,
    })

def make_demo_study(name: str, headings: List[float]) -> Study:
    frames = [demo_roll_curve(h) for h in headings]
    df = pd.concat(frames, ignore_index=True)
    df.insert(0, "study", name)
    return Study(
        name=name,
        re1_path=Path(f"{name}/(demo)"),
        df=df,
        headings=sorted(list(set(float(h) for h in headings))),
        dof_names=["Surge","Sway","Heave","Roll","Pitch","Yaw"],
        warnings=["This is a demo study generated due to parse/load failure."],
        errors=[]
    )
