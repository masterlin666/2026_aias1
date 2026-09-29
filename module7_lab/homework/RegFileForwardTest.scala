package hw6

import chisel3._
import chiseltest._
import chiseltest.RawTester.test
import chiseltest.simulator.WriteVcdAnnotation

object RegFileForwardTest extends App {
  // 建立一個 2 讀取埠的 RegFile 進行測試
  test(new RegFileForward(2), Seq(WriteVcdAnnotation)) { dut =>
    println("Starting RegFileForward tests...")

    // --- 1. 基本寫入與回讀 (Non-forwarding) ---
    // 週期 1: 寫入 x1
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(1.U)
    dut.io.wdata.poke(0xABCD.U)
    dut.clock.step(1)
    
    // 週期 2: 停止寫入，讀取 x1
    dut.io.wen.poke(false.B)
    dut.io.raddr(0).poke(1.U)
    dut.clock.step(1)
    dut.io.rdata(0).expect(0xABCD.U, "Basic read/write failed")
    println("  [Pass] Basic read/write")

    // --- 2. Read-after-write forwarding ---
    // 同時寫入 x5 並讀取 x5
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(5.U)
    dut.io.wdata.poke(0x1234.U)
    dut.io.raddr(0).poke(5.U)
    // 應該立即看到 0x1234，而不是舊值 0
    dut.io.rdata(0).expect(0x1234.U)
    dut.clock.step(1)
    println("  [Pass] Read-after-write forwarding on x5")

    // --- 3. x0 forwarding 抑制 ---
    // 嘗試寫入 x0 並讀取 x0
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(0.U)
    dut.io.wdata.poke(0x9999.U)
    dut.io.raddr(0).poke(0.U)
    // 輸出必須恆為 0
    dut.io.rdata(0).expect(0.U)
    dut.clock.step(1)
    println("  [Pass] x0 forwarding suppression")

    // --- 4. 雙讀取埠混合測試 ---
    // 一個埠發生 forwarding (讀取目前寫入的 x10)，另一個埠讀取已存在的舊值 (x1)
    dut.io.wen.poke(true.B)
    dut.io.waddr.poke(10.U)
    dut.io.wdata.poke(0x7777.U)
    
    dut.io.raddr(0).poke(10.U) // Forwarding
    dut.io.raddr(1).poke(1.U)  // Normal read
    
    dut.io.rdata(0).expect(0x7777.U)
    dut.io.rdata(1).expect(0xABCD.U)
    dut.clock.step(1)
    println("  [Pass] Dual port mixed forwarding")
  }
  println("\nAll RegFile tests passed! Waveform generated.")
}