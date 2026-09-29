package hw6

import chisel3._
import chisel3.util._

class ALUIO extends Bundle {
  val src1    = Input(UInt(32.W))
  val src2    = Input(UInt(32.W))
  val funct3  = Input(UInt(3.W))
  val funct7  = Input(UInt(7.W))
  val ALUout  = Output(UInt(32.W))
}

class ALU extends Module {
  val io = IO(new ALUIO)

  // 定義 funct3 具名常數
  val F3_ADD_SUB = "b000".U
  val F3_SLL     = "b001".U
  val F3_SLT     = "b010".U
  val F3_SLTU    = "b011".U
  val F3_XOR     = "b100".U
  val F3_SR_LA   = "b101".U
  val F3_OR      = "b110".U
  val F3_AND     = "b111".U

  val f7_bit5 = io.funct7(5)
  val shamt   = io.src2(4, 0)

  // 確保 MuxLookup 參數在同一個括號內，且移除多餘的 .io
  io.ALUout := MuxLookup(io.funct3, 0.U, Seq(
    F3_ADD_SUB -> Mux(f7_bit5, io.src1 - io.src2, io.src1 + io.src2),
    F3_SLL     -> (io.src1 << shamt),
    F3_SLT     -> (io.src1.asSInt < io.src2.asSInt).asUInt,
    F3_SLTU    -> (io.src1 < io.src2).asUInt,
    F3_XOR     -> (io.src1 ^ io.src2),
    F3_SR_LA   -> Mux(f7_bit5, (io.src1.asSInt >> shamt).asUInt, io.src1 >> shamt),
    F3_OR      -> (io.src1 | io.src2),
    F3_AND     -> (io.src1 & io.src2)
  ))
}