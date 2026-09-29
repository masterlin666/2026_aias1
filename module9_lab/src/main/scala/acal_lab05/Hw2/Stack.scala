package acal_lab05.Hw2

import chisel3._
import chisel3.util._

class Stack(val depth: Int, val width: Int) extends Module {
  val io = IO(new Bundle {
    val push    = Input(Bool())
    val pop     = Input(Bool())
    val enq_val = Input(UInt(width.W))
    val deq_val = Output(UInt(width.W))
    val empty   = Output(Bool())
    val full    = Output(Bool())
  })

  val stack_mem = Reg(Vec(depth, UInt(width.W)))
  val sp        = RegInit(0.U(log2Ceil(depth + 1).W))

  io.deq_val := 0.U
  io.empty   := sp === 0.U
  io.full    := sp === depth.U

  when(io.push && !io.full) {
    stack_mem(sp) := io.enq_val
    sp := sp + 1.U
  }.elsewhen(io.pop && !io.empty) {
    sp := sp - 1.U
    io.deq_val := stack_mem(sp - 1.U)
  }
}

// CpxCal 括號堆疊每一層儲存的運算狀態
class CpxStackFrame extends Bundle {
  val acc    = UInt(32.W)
  val mulRes = UInt(32.W)
  val preOp  = UInt(5.W)
  val op     = UInt(5.W)
}

object CpxStackFrame {
  val width: Int = 74
}
