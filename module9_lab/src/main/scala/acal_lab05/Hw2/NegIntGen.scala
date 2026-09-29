package acal_lab05.Hw2

import chisel3._
import chisel3.util._

class NegIntGen extends Module {
  val io = IO(new Bundle {
    val key_in = Input(UInt(4.W))
    val value  = Output(Valid(UInt(32.W)))
  })

  // 簡化狀態：只保留核心狀態
  val sAccept :: sNegAccept :: sEqual :: Nil = Enum(3)
  val state = RegInit(sAccept)

  val number = RegInit(0.U(32.W))
  val isNeg  = RegInit(false.B)

  val in = io.key_in 

  // 組合邏輯輸出：這是最穩定的輸出方式
  io.value.valid := (state === sEqual)
  io.value.bits  := Mux(isNeg, (~number + 1.U), number)

  switch(state) {
    is(sAccept) {
      when(in <= 9.U) {
        number := (number << 3) + (number << 1) + in
      }.elsewhen(in === 0xD.U) { // '('
        // 看到左括號，保持在 Accept 但預備偵測負號
        // 這裡不跳轉，讓下一拍直接在 sAccept 判定
      }.elsewhen(in === 0xB.U) { // '-'
        // 只有在看到負號時才切換模式
        isNeg := true.B
        state := sNegAccept
      }.elsewhen(in === 0xF.U) { // '='
        state := sEqual
      }
    }

    is(sNegAccept) {
      when(in <= 9.U) {
        number := (number << 3) + (number << 1) + in
      }.elsewhen(in === 0xE.U) { // ')'
        state := sAccept // 數字收完，回去等 '='
      }
    }

    is(sEqual) {
      // 輸出完畢，全部歸零
      number := 0.U
      isNeg  := false.B
      state  := sAccept
    }
  }
}