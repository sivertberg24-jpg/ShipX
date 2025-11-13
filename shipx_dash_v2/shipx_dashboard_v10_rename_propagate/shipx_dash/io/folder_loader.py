
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
from shipx_dash.types import Study
from shipx_dash.processing.safety import make_demo_study
from shipx_dash.io.re1_reader import read_re1_to_study
from shipx_dash.utils.natural_sort import natural_key

def discover_re1s(base_dir: str | Path) -> List[Tuple[str, Path]]:
    base = Path(base_dir)
    if not base.exists(): return []
    items: List[Tuple[str, Path]] = []

    # Prefer subfolders (ParameterStudy_*/Run_*) in natural numeric order
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    subdirs.sort(key=lambda p: natural_key(p.name))
    for sd in subdirs:
        candidates = list(sd.glob("*.re1")) + list(sd.glob("*.RE1"))
        if not candidates:
            continue
        candidates.sort(key=lambda p: natural_key(p.name))
        items.append((sd.name, candidates[0]))

    # If none found, consider top-level files in natural order
    if not items:
        files = list(base.glob("*.re1")) + list(base.glob("*.RE1"))
        files.sort(key=lambda p: natural_key(p.stem))
        for f in files:
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
            warnings.append(f"Failed to read '{path}': {ex}. Substituted with demo curve.")
            studies[name] = make_demo_study(name, headings=[0,45,90,135,180])
    return studies, warnings
