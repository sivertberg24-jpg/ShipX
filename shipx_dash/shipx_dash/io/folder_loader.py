
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import traceback
from ..types import Study
from ..processing.safety import make_demo_study
from .re1_reader import read_re1_to_study

def discover_re1s(base_dir: str | Path) -> List[Tuple[str, Path]]:
    base = Path(base_dir)
    if not base.exists(): return []
    items: List[Tuple[str, Path]] = []
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    for sd in sorted(subdirs):
        candidates = list(sd.glob("*.re1")) + list(sd.glob("*.RE1"))
        if not candidates: continue
        items.append((sd.name, sorted(candidates)[0]))
    if not items:
        for f in sorted(list(base.glob("*.re1")) + list(base.glob("*.RE1"))):
            items.append((f.stem, f))
    return items

def load_folder(base_dir: str | Path) -> Tuple[Dict[str, Study], List[str]]:
    warnings: List[str] = []
    studies: Dict[str, Study] = {}
    pairs = discover_re1s(base_dir)
    if not pairs:
        warnings.append(f"No .re1 files found in '{base_dir}'. Expect one per subfolder or directly under the folder.")
        return studies, warnings
    for name, path in pairs:
        try:
            study = read_re1_to_study(path, study_name=name)
            studies[name] = study
        except Exception as ex:
            warn = f"Failed to read '{path}': {ex}. Substituted with demo curve."
            warnings.append(warn)
            studies[name] = make_demo_study(name, headings=[0,45,90,135,180])
    return studies, warnings
