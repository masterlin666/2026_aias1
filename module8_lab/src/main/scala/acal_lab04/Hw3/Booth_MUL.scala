package acal_lab04.Hw3

import chisel3._
import chisel3.util._

class Booth_MUL(width: Int) extends Module {
  val io = IO(new Bundle {
    val in1 = Input(UInt(width.W))
    val in2 = Input(UInt(width.W))
    val out = Output(UInt((2 * width).W))
  })

  // 將輸入轉為有號數並擴展
  val x_sint = io.in1.asSInt.pad(2 * width)
  val y = Cat(io.in2, 0.U(1.W))

  val num_groups = width / 2
  val partial_products = Wire(Vec(num_groups, SInt((2 * width).W)))

  for (i <- 0 until num_groups) {
    val window = y(2 * i + 2, 2 * i)

    // 修正點：改用 0.asSInt(位元寬度.W) 避開編譯器對 .SInt 的歧義
    partial_products(i) := MuxLookup(window, 0.asSInt((2 * width).W), Seq(
      "b000".U -> 0.asSInt((2 * width).W),
      "b001".U -> x_sint,
      "b010".U -> x_sint,
      "b011".U -> (x_sint << 1),
      "b100".U -> -(x_sint << 1),
      "b101".U -> -x_sint,
      "b110".U -> -x_sint,
      "b111".U -> 0.asSInt((2 * width).W)
    ))
  }

  // 移位並加總
  val shifted_pp = for (i <- 0 until num_groups) yield {
    (partial_products(i) << (2 * i)).asSInt
  }

  io.out := shifted_pp.reduce(_ + _).asUInt
}