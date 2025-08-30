module hello_props(input logic clk, input logic rst_n);
assert property (@(posedge clk) disable iff(!rst_n) 1'b1 |=> 1'b1);
cover  property (@(posedge clk) disable iff(!rst_n) 1'b1 ##1 1'b1);
endmodule