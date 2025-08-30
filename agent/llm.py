# -*- coding: utf-8 -*-
from typing import Tuple
from huggingface_hub import InferenceClient

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"  # light & usually available

def _joined_prompt(system: str, user: str) -> str:
    return f"<<SYS>>\n{system}\n<</SYS>>\n<<USER>>\n{user}\n<</USER>>\n<<ASSISTANT>>\n"

def call_hf(system: str, user: str, model_id: str = DEFAULT_MODEL,
            max_new_tokens: int = 600, temperature: float = 0.2) -> str:
    client = InferenceClient(model=model_id, timeout=60)
    prompt = _joined_prompt(system, user)
    return client.text_generation(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        return_full_text=False,
        repetition_penalty=1.05,
    ).strip()

def _split(siglist: str):
    return [s.strip() for s in (siglist or "").split(",") if s.strip()]

def fallback_template(dut: str, clk: str, rst: str, signals: str, intent: str) -> str:
    """Safe ‘always-compiles’ concurrent SVA when HF is unavailable.
       Handshake if (valid,ready,data) exist; otherwise, a tautology assert to keep the demo flowing."""
    sigs = _split(signals)
    names = [s.split("[", 1)[0] for s in sigs]
    has_vr = {"valid", "ready"}.issubset(set(names))
    has_data = "data" in names
    if has_vr and has_data:
        body = [
            f"assert property (@(posedge {clk}) disable iff(!{rst}) valid && !ready |=> $stable(data) until_with ready);",
            f"cover  property (@(posedge {clk}) disable iff(!{rst}) valid && !ready ##[1:$] ready);",
        ]
    else:
        body = [
            f"assert property (@(posedge {clk}) disable iff(!{rst}) 1'b1 |=> 1'b1);",
            f"cover  property (@(posedge {clk}) disable iff(!{rst}) 1'b1 ##1 1'b1);",
        ]

    port_items = [f"input logic {clk}", f"input logic {rst}"]
    for raw in sigs:
        if "[" in raw and "]" in raw:
            name = raw.split("[", 1)[0]
            width = "[" + raw.split("[", 1)[1]
            port_items.append(f"input logic {width} {name}")
        else:
            port_items.append(f"input logic {raw}")
    port_block = ", ".join(port_items)
    return f"module {dut}_props({port_block});\n" + "\n".join(body) + "\nendmodule\n"

def generate_sva(dut: str, clk: str, rst: str, signals: str, system: str, user: str,
                 model_id: str = DEFAULT_MODEL) -> Tuple[str, str]:
    explanation = ""
    try:
        sv = call_hf(system, user, model_id=model_id)
        if "module" not in sv or f"{dut}_props" not in sv:
            raise RuntimeError("LLM returned unexpected text; falling back.")
    except Exception as e:
        explanation = f"// HF fallback: {e}"
        sv = fallback_template(dut, clk, rst, signals, user)
    return sv.strip(), explanation
