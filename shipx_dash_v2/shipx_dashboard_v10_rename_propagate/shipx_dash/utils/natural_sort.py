
import re
from typing import List, Union
_num = re.compile(r"(\d+)")

def natural_key(s: str) -> List[Union[int, str]]:
    parts = _num.split(s.lower())
    out: List[Union[int, str]] = []
    for p in parts:
        if p.isdigit():
            out.append(int(p))
        elif p:
            out.append(p)
    return out
