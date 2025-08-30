module stream_props(input logic clk, input logic rst_n, input logic valid, input logic ready, input logic [7:0] data);
assert property (@(posedge clk) disable iff(!rst_n) valid && !ready |=> $stable(data) until_with ready);
cover  property (@(posedge clk) disable iff(!rst_n) valid && !ready ##[1:$] ready);
endmodule