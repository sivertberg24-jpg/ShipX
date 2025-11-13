
from __future__ import annotations
from pathlib import Path
from typing import Optional
import re
from shipx_dash.utils.natural_sort import natural_key
from shipx_dash.config import PARAM_STUDY_DIR_HINTS, RUN_DIR_REGEX

_run_re = re.compile(RUN_DIR_REGEX, re.IGNORECASE)

def _is_paramstudy_name(name: str) -> bool:
    low = name.lower()
    for hint in PARAM_STUDY_DIR_HINTS:
        if low == hint.lower():
            return True
    # Fallback: names that include both 'parameter' and 'study'
    return ("parameter" in low) and ("study" in low)

def _latest_run_dir(ps: Path) -> Optional[Path]:
    subs = [d for d in ps.iterdir() if d.is_dir()]
    if not subs:
        return None
    candidates = [d for d in subs if _run_re.match(d.name)] or subs
    candidates.sort(key=lambda d: (natural_key(d.name), d.stat().st_mtime))
    return candidates[-1]

def resolve_parameterstudy_root(user_path: str | Path) -> Path:
    p = Path(user_path)

    if p.is_dir():
        # Pasted a ParameterStudy-like folder
        if _is_paramstudy_name(p.name):
            latest = _latest_run_dir(p)
            return latest or p

        # Pasted CASE folder: find a child that looks like ParameterStudy
        try:
            children = [d for d in p.iterdir() if d.is_dir()]
        except Exception:
            children = []
        matches = [d for d in children if _is_paramstudy_name(d.name)]
        if matches:
            matches.sort(key=lambda d: (natural_key(d.name), d.stat().st_mtime))
            ps = matches[-1]
            latest = _latest_run_dir(ps)
            return latest or ps

        # Pasted a run dir already
        if _run_re.match(p.name) and _is_paramstudy_name(p.parent.name):
            return p

    # Fallback: return as-is (loader will try to discover .re1)
    return p
