package acal_lab04.Hw2

import chisel3._
import acal_lab04.Lab._  // 確保載入 Lab 中的 FullAdder

class Add_Suber extends Module {
  val io = IO(new Bundle {
    val in_1 = Input(UInt(4.W))
    val in_2 = Input(UInt(4.W))
    val op   = Input(Bool())      // 0: ADD, 1: SUB
    val out  = Output(UInt(4.W))
    val o_f  = Output(Bool())     // overflow flag
  })

  // 1. 宣告 4 個 FullAdder 實例
  val fas = Array.fill(4)(Module(new FullAdder()).io)

  // 2. 宣告進位線 (包含內部的進位與最終的進位)
  val carry = Wire(Vec(5, Bool()))

  // 3. 初始進位 Cin = op (加法時為 0, 減法時為 1 提供 +1)
  carry(0) := io.op

  // 4. 使用迴圈進行接線
  val sumBits = Wire(Vec(4, Bool()))

  for (i <- 0 until 4) {
    fas(i).A    := io.in_1(i)
    // 當 op 為 1 時，B 需要反轉 (~B)
    fas(i).B    := io.in_2(i) ^ io.op
    fas(i).Cin  := carry(i)
    
    sumBits(i)  := fas(i).Sum
    carry(i + 1) := fas(i).Cout
  }

  // 5. 組合輸出
  io.out := sumBits.asUInt

  /* * 6. 溢位偵測 (Overflow Detection):
   * 根據題目規則：當進入 MSB 的進位 (C_3) 與離開 MSB 的進位 (C_4) 不同時，發生溢位。
   * C_3 是 carry(3), C_4 是 carry(4)
   */
  io.o_f := carry(3) ^ carry(4)
}