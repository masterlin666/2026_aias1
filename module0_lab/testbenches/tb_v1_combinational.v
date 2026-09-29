`timescale 1ns/1ps

module tb_v1_combinational;
    reg  [2:0] a;
    wire [15:0] q;
    integer pass_count, fail_count;

    top_module uut (.a(a), .q(q));

    task check;
        input [2:0] test_a;
        input [15:0] expected_q;
        begin
            a = test_a;
            #10;
            if (q === expected_q) begin
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL: a=%0d, expected q=%0d, got q=%0d", test_a, expected_q, q);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        pass_count = 0;
        fail_count = 0;

        check(3'd0, 16'd2);
        check(3'd1, 16'd7);
        check(3'd2, 16'd15);
        check(3'd3, 16'd22);
        check(3'd4, 16'd24);
        check(3'd5, 16'd29);
        check(3'd6, 16'd32);
        check(3'd7, 16'd44);

        $display("RESULTS: %0d passed, %0d failed out of %0d tests",
                 pass_count, fail_count, pass_count + fail_count);
        if (fail_count == 0)
            $display("ALL_PASS");
        else
            $display("SOME_FAIL");
        $finish;
    end
endmodule
