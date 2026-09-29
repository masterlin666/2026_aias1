package hw6

import chisel3._
import chiseltest._
import chiseltest.RawTester.test
import chiseltest.simulator.WriteVcdAnnotation 

object MuxNTest extends App {

  // --- 測試 1：4 輸入 MUX，測試所有選擇值 ---
  println("Step 1: Testing 4-input MuxN (All selection values)...")
  test(new MuxN(4, 32), Seq(WriteVcdAnnotation)) { dut =>
    // 使用非平凡的資料值 (Non-trivial values)
    val testValues = Seq("hAAAA_BBBB".U(32.W), "h1234_5678".U(32.W), "h5555_6666".U(32.W), "h8765_4321".U(32.W))
    
    // 灌入測試資料
    for (i <- 0 until 4) {
      dut.io.in(i).poke(testValues(i))
    }

    // 逐一檢查所有 4 個選擇值 (0, 1, 2, 3)
    for (i <- 0 until 4) {
      dut.io.sel.poke(i.U)
      dut.clock.step(1)
      dut.io.out.expect(testValues(i))
      println(s"  Selected index $i: expected ${testValues(i).litValue.toString(16)}, got ${dut.io.out.peek().litValue.toString(16)}")
    }
  }

  // --- 測試 2：8 輸入 MUX，測試邊界選擇值 (0 和 n-1) ---
  println("\nStep 2: Testing 8-input MuxN (Boundary values)...")
  test(new MuxN(8, 32), Seq(WriteVcdAnnotation)) { dut =>
    // 定義邊界測試用的非平凡資料
    val firstVal = "hDEAD_BEEF".U(32.W)
    val lastVal  = "hCAFE_BABE".U(32.W)
    val otherVal = "h0000_1111".U(32.W)

    // 初始化所有輸入，並給予邊界特定的值
    for (i <- 0 until 8) {
      if (i == 0) dut.io.in(i).poke(firstVal)
      else if (i == 7) dut.io.in(i).poke(lastVal)
      else dut.io.in(i).poke(otherVal)
    }

    // 測試邊界 0
    dut.io.sel.poke(0.U)
    dut.clock.step(1)
    dut.io.out.expect(firstVal)
    println(s"  Boundary 0: expected ${firstVal.litValue.toString(16)}, passed!")

    // 測試邊界 n-1 (即 index 7)
    dut.io.sel.poke(7.U)
    dut.clock.step(1)
    dut.io.out.expect(lastVal)
    println(s"  Boundary 7: expected ${lastVal.litValue.toString(16)}, passed!")
  }

  println("\nAll HW 7-1 requirements satisfied!")
}