package hw6

import chisel3._
import chiseltest._
import chiseltest.RawTester.test
import chiseltest.simulator.WriteVcdAnnotation

object ALUTest extends App {
  test(new ALU, Seq(WriteVcdAnnotation)) { dut =>
    println("Starting ALU tests...")

    def check(s1: Long, s2: Long, f3: Int, f7: Int, expected: Long, msg: String): Unit = {
      dut.io.src1.poke(s1.U)
      dut.io.src2.poke(s2.U)
      dut.io.funct3.poke(f3.U)
      dut.io.funct7.poke(f7.U)
      dut.clock.step(1)
      dut.io.ALUout.expect(expected.U, s"Failed at $msg")
      println(s"  [Pass] $msg")
    }

    // 1. ADD / SUB 區分 (funct3=0, funct7=0 vs 32)
    check(10, 5, 0, 0, 15, "ADD: 10 + 5")
    check(10, 5, 0, 32, 5, "SUB: 10 - 5")

    // 2. SLL (左移)
    check(1, 4, 1, 0, 16, "SLL: 1 << 4")

    // 3. SLT / SLTU (有號與無號比較)
    // -1 (0xFFFFFFFF) < 1 有號應為 true(1), 無號應為 false(0)
    check(0xFFFFFFFFL, 1, 2, 0, 1, "SLT: -1 < 1")
    check(0xFFFFFFFFL, 1, 3, 0, 0, "SLTU: unsigned max < 1")

    // 4. XOR / OR / AND
    check(0xAA, 0x55, 4, 0, 0xFF, "XOR")
    check(0xAA, 0x55, 6, 0, 0xFF, "OR")
    check(0xAA, 0x55, 7, 0, 0x00, "AND")

    // 5. SRL / SRA 區分 (邏輯 vs 算術右移)
    // 0x80000000 右移 1 位，SRL 應為 0x40000000，SRA 應為 0xC0000000
    check(0x80000000L, 1, 5, 0, 0x40000000L, "SRL: Logical Right Shift")
    check(0x80000000L, 1, 5, 32, 0xC0000000L, "SRA: Arithmetic Right Shift")

    // 6. 邊界情況
    check(0, 0, 0, 0, 0, "Zero case")
    // 在最後一個測試案例，數值後加上 'L' 強制轉換為 Long，並正確表示 0xFFFFFFFEL
    check(0x7FFFFFFF, 0x7FFFFFFF, 0, 0, 0xFFFFFFFEL, "Max positive ADD")
  }
  println("\nAll ALU tests passed! VCD generated in test_run_dir.")
}