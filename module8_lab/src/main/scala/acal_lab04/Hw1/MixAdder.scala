package acal_lab04.Hw1

import chisel3._
import chisel3.util._
import acal_lab04.Lab._

class MixAdder(n: Int) extends Module {
  val io = IO(new Bundle {
    val Cin  = Input(UInt(1.W))
    val In1  = Input(UInt((4 * n).W))
    val In2  = Input(UInt((4 * n).W))
    val Sum  = Output(UInt((4 * n).W))
    val Cout = Output(UInt(1.W))
  })

  // 1. 使用 Array.fill 進行硬體產生，產生 n 個 CLAdder
  val clas = Array.fill(n)(Module(new CLAdder()).io)

  // 2. 用於收集各區塊 Sum 的 Vec
  val sumVec = Wire(Vec(n, UInt(4.W)))

  // 3. 進行接線 (For Loop)
  for (i <- 0 until n) {
    // 修正點：根據錯誤訊息，CLAdder 的輸入應為小寫 in1, in2
    clas(i).in1 := io.In1(4 * i + 3, 4 * i)
    clas(i).in2 := io.In2(4 * i + 3, 4 * i)
    
    if (i == 0) {
      clas(i).Cin := io.Cin
    } else {
      clas(i).Cin := clas(i - 1).Cout
    }

    sumVec(i) := clas(i).Sum
  }

  // 4. 組合輸出
  io.Sum  := sumVec.asUInt
  io.Cout := clas(n - 1).Cout
}