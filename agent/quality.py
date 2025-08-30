# -*- coding: utf-8 -*-
import re
from typing import List

def lint_sva(sv: str, dut: str, clk: str, rst: str) -> List[str]:
    issues=[]
    if not re.search(rf"\bmodule\s+{re.escape(dut)}_props\b", sv):
        issues.append(f"Module name must be {dut}_props")
    if f"posedge {clk}" not in sv:
        issues.append(f"Missing @(posedge {clk})")
    if f"disable iff(!{rst})" not in sv:
        issues.append(f"Missing disable iff(!{rst})")
    if "assert property" not in sv:
        issues.append("Missing concurrent assert property")
    if "cover property" not in sv:
        issues.append("Missing anti-vacuity cover property")
    if "assume" in sv:
        issues.append("Must not emit assume")
    return issues

def tighten(sv: str) -> str:
    sv = re.sub(r"^\s*//.*$", "", sv, flags=re.M)
    sv = re.sub(r"\n{3,}", "\n\n", sv)
    return sv.strip()
