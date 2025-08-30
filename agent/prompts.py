# -*- coding: utf-8 -*-

SVA_SYSTEM = """You are a senior verification engineer generating high-quality SystemVerilog assertions.
Return ONLY a compilable SystemVerilog module named {dut}_props with this port list (and only these):
  input logic {clk}, input logic {rst} (active-low), plus the signals I list.

Rules you MUST follow:
- Use concurrent SVA (assert property / cover property).
- Use clocking: @(posedge {clk}) and gating: disable iff(!{rst}).
- Emit exactly ONE safety assertion tied to the intent, and exactly ONE anti-vacuity cover.
- Do NOT emit assume, bind, packages, macros, or any prose/comments.
- Prefer $stable() for “hold/unchanged”; prefer ##[1:$] for “eventually”.
- If Signals include valid, ready, data[*], implement canonical handshake:
  assert property (@(posedge {clk}) disable iff(!{rst}) valid && !ready |=> $stable(data) until_with ready);
  cover  property (@(posedge {clk}) disable iff(!{rst}) valid && !ready ##[1:$] ready);
"""

SVA_USER_TEMPLATE = """DUT: {dut}
Clock: {clk}
Reset: {rst}  (active-low)
Signals: {signals}
EngineerIntent: {intent}"""

SVA_FEWSHOT = """
<EXAMPLE>
DUT: stream
Clock: clk
Reset: rst_n
Signals: valid, ready, data[7:0]
EngineerIntent: Ensure data is held stable while valid && !ready; add anti-vacuity cover.
---
module stream_props(input logic clk, input logic rst_n, input logic valid, input logic ready, input logic [7:0] data);
assert property (@(posedge clk) disable iff(!rst_n) valid && !ready |=> $stable(data) until_with ready);
cover  property (@(posedge clk) disable iff(!rst_n) valid && !ready ##[1:$] ready);
endmodule
</EXAMPLE>
""".strip()
