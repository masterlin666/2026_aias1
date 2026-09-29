/*
 * Prerequisite Assessment — Verilog Problem 2: Sequential Circuit
 *
 * Design a sequential circuit with the following behavior:
 *   - On each rising edge of clk:
 *     - If a == 1: increment q by 1
 *     - If a == 0: reset q to 0
 *   - q is a 4-bit output (wraps around at 15)
 *
 * Instructions:
 *   - Implement the logic inside the module below
 *   - Do NOT change the module name or port list
 *   - Use posedge clk for sequential logic
 */
module top_module (
    input clk,
    input a,
    output reg [3:0] q
);
    // TODO: Implement this module
    always @(posedge clk) begin
        if (a) begin
            q <= q + 1'b1;
        end else begin
            q <= 4'b0000;
        end
    end
endmodule
