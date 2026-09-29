/*
 * Prerequisite Assessment — Verilog Problem 1: Combinational Circuit
 *
 * Design a combinational circuit that implements the following
 * truth table (from the given waveform/simulation):
 *
 *   a[2:0]  |  q[15:0]
 *   --------|----------
 *    3'd0   |  16'd2
 *    3'd1   |  16'd7
 *    3'd2   |  16'd15
 *    3'd3   |  16'd22
 *    3'd4   |  16'd24
 *    3'd5   |  16'd29
 *    3'd6   |  16'd32
 *    3'd7   |  16'd44
 *
 * Instructions:
 *   - Implement the logic inside the module below
 *   - Do NOT change the module name or port list
 */
module top_module (
    input  [2:0] a,
    output [15:0] q
);
    // TODO: Implement this module
    assign q = (a == 3'd0) ? 16'd2  :                
               (a == 3'd1) ? 16'd7  :
               (a == 3'd2) ? 16'd15 :
               (a == 3'd3) ? 16'd22 :
               (a == 3'd4) ? 16'd24 :
               (a == 3'd5) ? 16'd29 :
               (a == 3'd6) ? 16'd32 :
               (a == 3'd7) ? 16'd44 : 16'd0; // 預設值

endmodule
