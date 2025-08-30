`timescale 1ns/1ps
module tb_hello;
  logic clk = 0; always #5 clk = ~clk;
  logic rst_n = 0;
  logic [7:0] cnt;

  // DUT
  hello dut(.clk(clk), .rst_n(rst_n), .cnt(cnt));

  // Simple stimulus: release reset after a few cycles, then run
  initial begin
    repeat (3) @(posedge clk);  // keep reset low for 3 cycles
    rst_n = 1;
    repeat (40) @(posedge clk);
    $display("CNT=%0d", cnt);
    $finish;
  end
endmodule
