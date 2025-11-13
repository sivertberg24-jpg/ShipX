
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple
import pandas as pd

@dataclass
class Study:
    name: str
    re1_path: Path
    df: pd.DataFrame
    headings: List[float]
    dof_names: List[str]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class PanelConfig:
    selected_studies: list[str]
    heading: float
    metric: str                  # "amplitude" or "phase_deg"
    smooth: bool
    x_window: Tuple[float, float]
    show_markers: bool = False
