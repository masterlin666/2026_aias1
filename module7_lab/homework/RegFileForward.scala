package hw6

import chisel3._
import chisel3.util._

class RegFileForward(readPorts: Int) extends Module {
  val io = IO(new Bundle {
    val wen   = Input(Bool())
    val waddr = Input(UInt(5.W))
    val wdata = Input(UInt(32.W))
    val raddr = Input(Vec(readPorts, UInt(5.W)))
    val rdata = Output(Vec(readPorts, UInt(32.W)))
  })

  // 實作 32 個 32-bit 暫存器，並初始化為 0
  val regs = RegInit(VecInit(Seq.fill(32)(0.U(32.W))))

  // 寫入邏輯：waddr 為 0 時不寫入
  when(io.wen && io.waddr =/= 0.U) {
    regs(io.waddr) := io.wdata
  }

  // 讀取邏輯 + Forwarding
  for (i <- 0 until readPorts) {
    // 判斷條件：
    // 1. 正在寫入 (wen)
    // 2. 寫入位址等於目前讀取位址 (waddr == raddr)
    // 3. 位址不是 x0 (waddr != 0)
    val do_forward = io.wen && (io.waddr === io.raddr(i)) && (io.waddr =/= 0.U)
    
    // 基礎讀取值：x0 恆為 0
    val raw_rdata = Mux(io.raddr(i) === 0.U, 0.U, regs(io.raddr(i)))
    
    // 如果符合 Forwarding 條件則輸出 wdata，否則輸出原本從暫存器讀到的值
    io.rdata(i) := Mux(do_forward, io.wdata, raw_rdata)
  }
}