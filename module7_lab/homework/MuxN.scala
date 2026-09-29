package hw6

import chisel3._
import chisel3.util._

class MuxN(n: Int, w: Int = 32) extends Module {
  require(n > 0 && (n & (n - 1)) == 0, "n must be a power of 2")
  val io = IO(new Bundle {
    val sel = Input(UInt(log2Ceil(n).W))
    val in  = Input(Vec(n, UInt(w.W)))
    val out = Output(UInt(w.W))
  })

  // 使用 MuxLookup 實作
  // 構造一個 Seq[(UInt, UInt)] 的對照表
  io.out := MuxLookup(io.sel, 0.U(w.W), (0 until n).map(i => i.U -> io.in(i)))
}