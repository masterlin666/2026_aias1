`timescale 1ns/1ps

module tb_v2_sequential;
    reg clk, a;
    wire [3:0] q;
    integer pass_count, fail_count;

    top_module uut (.clk(clk), .a(a), .q(q));

    /* Clock generation: 10ns period */
    initial clk = 0;
    always #5 clk = ~clk;

    task check_at_posedge;
        input [3:0] expected_q;
        begin
            @(posedge clk);
            #1; /* small delay after posedge to let output settle */
            if (q === expected_q) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: at time %0t, a=%0b, expected q=%0d, got q=%0d",
                         $time, a, expected_q, q);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        pass_count = 0;
        fail_count = 0;

        /* Reset: a=0 for a couple cycles */
        a = 0;
        check_at_posedge(4'd0); /* cycle 1: a=0 -> q=0 */
        check_at_posedge(4'd0); /* cycle 2: a=0 -> q=0 */

        /* Count up: a=1 for 5 cycles */
        a = 1;
        check_at_posedge(4'd1); /* cycle 3: a=1 -> q=1 */
        check_at_posedge(4'd2); /* cycle 4: a=1 -> q=2 */
        check_at_posedge(4'd3); /* cycle 5: a=1 -> q=3 */
        check_at_posedge(4'd4); /* cycle 6: a=1 -> q=4 */
        check_at_posedge(4'd5); /* cycle 7: a=1 -> q=5 */

        /* Reset again */
        a = 0;
        check_at_posedge(4'd0); /* cycle 8: a=0 -> q=0 */

        /* Count again */
        a = 1;
        check_at_posedge(4'd1); /* cycle 9: a=1 -> q=1 */
        check_at_posedge(4'd2); /* cycle 10: a=1 -> q=2 */
        check_at_posedge(4'd3); /* cycle 11: a=1 -> q=3 */

        /* Reset mid-count */
        a = 0;
        check_at_posedge(4'd0); /* cycle 12: a=0 -> q=0 */

        /* One more count */
        a = 1;
        check_at_posedge(4'd1); /* cycle 13: a=1 -> q=1 */

        $display("RESULTS: %0d passed, %0d failed out of %0d tests",
                 pass_count, fail_count, pass_count + fail_count);
        if (fail_count == 0)
            $display("ALL_PASS");
        else
            $display("SOME_FAIL");
        $finish;
    end
endmodule
