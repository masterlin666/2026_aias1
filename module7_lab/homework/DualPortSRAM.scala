package hw6

import chisel3._
import chisel3.util._
import chisel3.util.experimental.loadMemoryFromFileInline

class DualPortSRAM(depth: Int, width: Int) extends Module {
  val io = IO(new Bundle {
    // Read port
    val ren   = Input(Bool())
    val raddr = Input(UInt(log2Ceil(depth).W))
    val rdata = Output(UInt(width.W))

    // Write port
    val wen   = Input(Bool())
    val waddr = Input(UInt(log2Ceil(depth).W))
    val wdata = Input(UInt(width.W))
  })

  // 1. 定義同步記憶體
  val mem = SyncReadMem(depth, UInt(width.W))

  // 2. 初始化記憶體 (檔案需放在 src/main/resource/)
  loadMemoryFromFileInline(mem, "src/main/resource/sram_init.txt")

  // 3. 寫入邏輯
  when(io.wen) {
    mem.write(io.waddr, io.wdata)
  }

  // 4. 同步讀取與閘控邏輯
  // SyncReadMem 在 ren 為高時，下一週期會輸出資料
  val memOut = mem.read(io.raddr, io.ren)
  
  // 為了達成「ren 為低時保持前值」，我們需要一個暫存器來記錄上一次讀到的資料
  val lastRdata = RegNext(memOut)
  val ren_dly = RegNext(io.ren) // 同步讀取的資料會延遲一拍，致能訊號也要對齊

  // 如果上一拍有讀取，輸出新資料；否則維持舊資料
  io.rdata := Mux(ren_dly, memOut, lastRdata)
}