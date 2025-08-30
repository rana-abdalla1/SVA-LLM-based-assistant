# -*- coding: utf-8 -*-
import shutil, subprocess
from pathlib import Path

def _split_signals(signals: str):
    out=[]
    for s in [x.strip() for x in (signals or "").split(",") if x.strip()]:
        if "[" in s and "]" in s:
            name=s.split("[",1)[0]; width="["+s.split("[",1)[1]
            out.append((name,width))
        else:
            out.append((s,""))
    return out

def write_bind(dut: str, clk: str, rst: str, signals: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    sigs = _split_signals(signals)
    port_map = [f".{clk}({clk})", f".{rst}({rst})"] + [f".{n}({n})" for n,_ in sigs]
    bind = f"""bind {dut} {dut}_props props_i (
  {', '.join(port_map)}
);
"""
    p = out_dir / f"{dut}_bind.sv"
    p.write_text(bind, encoding="utf-8")
    return p

def write_do(dut: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    # compile any local rtl if present
    if Path("hello.sv").exists(): files.append("hello.sv")
    if Path("rtl").exists(): files += [str(p) for p in Path("rtl").glob("*.sv")]
    # props and bind
    files.append(str(Path("formal/props")/f"{dut}_props.sv"))
    files.append(str(Path("formal/props")/f"{dut}_bind.sv"))
    # TB optional
    top = f"work.{dut}"
    if Path("tb_hello.sv").exists():
        files.append("tb_hello.sv")
        top = "work.tb_hello"
    vlog_line = "vlog -sv " + " ".join(files)
    do = f"""vlib work
vmap work work
{vlog_line}
vsim -c {top} -do "run -all; report -assertions -verbose; quit -f"
"""
    p = out_dir / "run_agent.do"
    p.write_text(do, encoding="utf-8")
    return p

def run_questa(do_path: Path) -> int:
    vsim = shutil.which("vsim")
    if not vsim:
        return -2
    res = subprocess.run([vsim, "-c", "-do", str(do_path)],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (do_path.parent/"run.log").write_text(res.stdout, encoding="utf-8")
    return res.returncode
