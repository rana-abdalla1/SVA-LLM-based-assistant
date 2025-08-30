module hello(input logic clk, input logic rst_n, output logic [7:0] cnt);
  always_ff @(posedge clk or negedge rst_n) begin
  end
endmodule
