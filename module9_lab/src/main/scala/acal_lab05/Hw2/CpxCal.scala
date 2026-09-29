package acal_lab05.Hw2

import chisel3._
import chisel3.util._

class CpxCal extends Module {
  val io = IO(new Bundle {
    val key_in = Input(UInt(5.W))
    val value  = Output(Valid(UInt(32.W)))
  })

  val sStore :: sEqual :: Nil = Enum(2)
  val state = RegInit(sStore)

  val acc      = RegInit(0.U(32.W))
  val mulRes   = RegInit(0.U(32.W))
  val number   = RegInit(0.U(32.W))
  val op       = RegInit(0xA.U(5.W))
  val preOp    = RegInit(0xA.U(5.W))

  val isNeg    = RegInit(false.B)
  val numValid = RegInit(false.B)
  val result   = RegInit(0.U(32.W))

  // 小數點：固定小數 3 位 (x1000)
  val anyDot    = RegInit(false.B)
  val dotSeen   = RegInit(false.B)
  val fracCount = RegInit(0.U(2.W))

  val parenStack = Module(new Stack(8, CpxStackFrame.width))

  val in = io.key_in

  val nextFracCount = fracCount + 1.U
  val nextFracScale = Mux(nextFracCount === 1.U, 100.U(32.W),
                      Mux(nextFracCount === 2.U, 10.U(32.W), 1.U(32.W)))

  val rawNumber = Mux(isNeg, (~number + 1.U), number)
  val scaledInt = Mux(isNeg, (~(number * 1000.U) + 1.U), number * 1000.U)
  val current_val = Mux(anyDot && !dotSeen, scaledInt, rawNumber)

  def mulLevel(lhs: UInt, rhs: UInt): UInt = {
    val l = lhs.asSInt
    val r = rhs.asSInt
    Mux(anyDot, (l * r / 1000.S).asUInt, (l * r).asUInt)
  }

  def divLevel(lhs: UInt, rhs: UInt): UInt = {
    val l = lhs.asSInt
    val r = rhs.asSInt
    Mux(anyDot, (l * 1000.S / r).asUInt, (l / r).asUInt)
  }

  val pushFrame = Wire(new CpxStackFrame)
  pushFrame.acc    := acc
  pushFrame.mulRes := mulRes
  pushFrame.preOp  := preOp
  pushFrame.op     := op

  val popFrame = parenStack.io.deq_val.asTypeOf(new CpxStackFrame)

  parenStack.io.enq_val := pushFrame.asUInt
  parenStack.io.push    := false.B
  parenStack.io.pop     := false.B

  io.value.valid := (state === sEqual)
  io.value.bits  := result

  switch(state) {
    is(sStore) {
      when(in <= 9.U) {
        when(dotSeen) {
          fracCount := nextFracCount
          number := number + in * nextFracScale
        }.otherwise {
          number := (number << 3) + (number << 1) + in
        }
        numValid := true.B
      }.elsewhen(in === 0x10.U) { // '.'
        anyDot := true.B
        when(!dotSeen) {
          dotSeen := true.B
          fracCount := 0.U
          number := number * 1000.U
        }
      }.elsewhen(in === 0xB.U && !numValid) {
        isNeg := true.B
      }.elsewhen(in === 0xD.U) { // '('
        parenStack.io.push := !parenStack.io.full
        acc := 0.U; mulRes := 0.U; op := 0xA.U; preOp := 0xA.U
        numValid := false.B; isNeg := false.B; number := 0.U
        dotSeen := false.B; fracCount := 0.U
      }.elsewhen(in === 0xA.U || in === 0xB.U || in === 0xC.U || in === 0x11.U ||
                 in === 0xF.U || in === 0xE.U) {
        val current_mul_res = Mux(op === 0xC.U, mulLevel(mulRes, current_val),
                             Mux(op === 0x11.U, divLevel(mulRes, current_val), current_val))

        when(in === 0xC.U) {
          mulRes := current_mul_res
          op := 0xC.U
        }.elsewhen(in === 0x11.U) {
          mulRes := current_mul_res
          op := 0x11.U
        }.otherwise {
          val accS = acc.asSInt
          val mulS = current_mul_res.asSInt
          val final_val = Mux(preOp === 0xB.U,
            (accS - mulS).asUInt,
            (accS + mulS).asUInt)

          when(in === 0xF.U) {
            result := final_val
            state := sEqual
          }.elsewhen(in === 0xE.U) {
            parenStack.io.pop := !parenStack.io.empty
            acc := popFrame.acc; mulRes := popFrame.mulRes
            preOp := popFrame.preOp; op := popFrame.op
            number := final_val
            numValid := true.B
            isNeg := false.B
            dotSeen := anyDot
            fracCount := 0.U
          }.otherwise {
            acc := final_val
            preOp := in
            mulRes := 0.U
            op := 0xA.U
          }
        }
        when(in =/= 0xE.U) {
          number := 0.U; numValid := false.B; isNeg := false.B
          dotSeen := false.B; fracCount := 0.U
        }
      }
    }
    is(sEqual) {
      acc := 0.U; mulRes := 0.U; op := 0xA.U; preOp := 0xA.U; number := 0.U
      numValid := false.B; isNeg := false.B
      anyDot := false.B; dotSeen := false.B; fracCount := 0.U
      state := sStore
    }
  }
}
