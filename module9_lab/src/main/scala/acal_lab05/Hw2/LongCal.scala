package acal_lab05.Hw2

import chisel3._
import chisel3.util._

class LongCal extends Module {
  val io = IO(new Bundle {
    val key_in = Input(UInt(4.W))
    val value  = Output(Valid(UInt(32.W)))
  })

  // 狀態定義
  val sIdle :: sSrc :: sNegStart :: sEqual :: Nil = Enum(4)
  val state = RegInit(sIdle)

  // 暫存器
  val res      = RegInit(0.U(32.W)) // 累進結果
  val number   = RegInit(0.U(32.W)) // 當前累加的數字
  val op       = RegInit(0.U(2.W))  // 0:+, 1:-, 2:* (依題目 EasyCal 定義)
  val isNeg    = RegInit(false.B)   // 負號旗標
  val hasParen = RegInit(false.B)   // 是否在括號模式中

  val in = io.key_in

  // 預設輸出
  io.value.valid := (state === sEqual)
  io.value.bits  := res

  // 定義執行運算的邏輯
  val current_val = Mux(isNeg, (~number + 1.U), number)
  val next_res = MuxLookup(op, 0.U, Seq(
    0.U -> (res + current_val), // 加法
    1.U -> (res - current_val)  // 減法
  ))

  switch(state) {
    is(sIdle) {
      state := sSrc
    }

    is(sSrc) {
      when(in <= 9.U) {
        number := (number << 3) + (number << 1) + in
      }.elsewhen(in === 0xA.U || in === 0xB.U) { // '+' 或 '-'
        res := next_res
        op := in - 10.U
        number := 0.U
        isNeg := false.B
        state := sSrc
      }.elsewhen(in === 0xD.U) { // '('
        state := sNegStart
      }.elsewhen(in === 0xF.U) { // '='
        res := next_res
        state := sEqual
      }
    }

    is(sNegStart) {
      when(in === 0xB.U) { // '-'
        isNeg := true.B
        state := sSrc // 進入負數累加模式，利用 sSrc 處理數字
      }.elsewhen(in <= 9.U) {
        number := in
        state := sSrc
      }
    }

    is(sEqual) {
      // 輸出 valid 一週期後重置
      res := 0.U
      number := 0.U
      op := 0.U
      isNeg := false.B
      state := sSrc
    }
  }

  // 處理括號結尾 ')' 的邏輯：通常 ')' 後會接運算子或等號
  // 在本設計中，')' 僅作為語法標記，真正的負數轉換在運算時透過 isNeg 觸發
  when(in === 0xE.U) { 
    // 這裡可以選擇不跳轉，因為 number 已經累加，isNeg 已經鎖定
  }
}