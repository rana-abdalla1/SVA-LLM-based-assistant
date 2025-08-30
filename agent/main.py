# -*- coding: utf-8 -*-
import argparse
from pathlib import Path
from prompts import SVA_SYSTEM, SVA_USER_TEMPLATE, SVA_FEWSHOT
from llm import generate_sva, DEFAULT_MODEL
from quality import lint_sva, tighten
from questa import write_bind, write_do, run_questa

def main():
    ap = argparse.ArgumentParser(description="AI SVA Agent (Questa)")
    ap.add_argument("dut", help="Top-level DUT module name (e.g., hello)")
    ap.add_argument("--clk", default="clk")
    ap.add_argument("--rst", default="rst_n")
    ap.add_argument("--signals", default="", help="Comma-separated (e.g., 'valid, ready, data[7:0]')")
    ap.add_argument("--intent", required=True, help="Engineer intent in plain English")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="HF model id")
    ap.add_argument("--no-run", action="store_true", help="Generate only; skip Questa")
    args = ap.parse_args()

    system = SVA_SYSTEM.format(dut=args.dut, clk=args.clk, rst=args.rst)
    user = SVA_USER_TEMPLATE.format(dut=args.dut, clk=args.clk, rst=args.rst,
                                    signals=args.signals, intent=args.intent) + "\n\n" + SVA_FEWSHOT

    sv, note = generate_sva(args.dut, args.clk, args.rst, args.signals, system, user, model_id=args.model)
    sv = tighten(sv)
    issues = lint_sva(sv, args.dut, args.clk, args.rst)
    if issues:
        print("Quality gate failed: " + "; ".join(issues))
    else:
        print("Quality gate passed.")

    out_dir = Path("formal/props")
    out_dir.mkdir(parents=True, exist_ok=True)
    props_path = out_dir / f"{args.dut}_props.sv"
    props_path.write_text(sv, encoding="utf-8")
    bind_path = write_bind(args.dut, args.clk, args.rst, args.signals, out_dir)
    do_path = write_do(args.dut, Path("formal/questa"))
    print(f"Wrote {props_path} and {bind_path} and {do_path}")
    if note:
        print(note)

    if args.no_run:
        print("Skipping Questa (--no-run). To run: vsim -c -do formal\\questa\\run_agent.do")
        return

    rc = run_questa(do_path)
    if rc == -2:
        print("vsim not on PATH. Set PATH then re-run.")
    else:
        print("Questa returned", rc, "— see", Path("formal/questa/run.log"))

if __name__ == "__main__":
    main()
