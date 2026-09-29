package hw6

import chisel3._
import chiseltest._
import chiseltest.RawTester.test
import chiseltest.simulator.WriteVcdAnnotation

object DualPortSRAMTest extends App {
  test(new DualPortSRAM(32, 32), Seq(WriteVcdAnnotation)) { dut =>
    println("Starting DualPortSRAM tests...")

    // --- 1. 讀取從檔案載入的初始值 ---
    dut.io.ren.poke(true.B)
    dut.io.raddr.poke(0.U)
    dut.clock.step(1) // 同步讀取需要一週期
    dut.io.rdata.expect("hdeadbeef".U)
    
    dut.io.raddr.poke(1.U)
    dut.clock.step(1)
    dut.io.rdata.expect("hcafebabe".U)
    println("  [Pass] Initial memory load")

    // --- 2. 寫入並回讀 (1 週期延遲) ---
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(10.U)
    dut.io.wdata.poke("hBBBBCCCC".U)
    dut.clock.step(1)
    
    dut.io.wen.poke(false.B)
    dut.io.ren.poke(true.B)
    dut.io.raddr.poke(10.U)
    dut.clock.step(1) // 第一步：地址送入
    dut.io.rdata.expect("hBBBBCCCC".U)
    println("  [Pass] Write and sync read")

    // --- 3. 讀取啟用閘控 (Gating) ---
    // 目前 rdata 應該是 hBBBBCCCC
    dut.io.ren.poke(false.B)
    dut.io.raddr.poke(0.U) // 試圖讀取別的位址
    dut.clock.step(1)
    dut.io.rdata.expect("hBBBBCCCC".U) // 因為 ren=0，rdata 應保持舊值
    println("  [Pass] Read enable gating (hold value)")

    // --- 4. 同時讀寫不同位址 ---
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(15.U)
    dut.io.wdata.poke("h55AA55AA".U)
    
    dut.io.ren.poke(true.B)
    dut.io.raddr.poke(2.U) // 讀取初始值 0x12345678
    
    dut.clock.step(1)
    dut.io.rdata.expect("h12345678".U) // 讀取正確
    
    // 驗證剛才寫入的 15 號位址
    dut.io.ren.poke(true.B)
    dut.io.raddr.poke(15.U)
    dut.clock.step(1)
    dut.io.rdata.expect("h55AA55AA".U)
    println("  [Pass] Simultaneous read and write")
  }
}