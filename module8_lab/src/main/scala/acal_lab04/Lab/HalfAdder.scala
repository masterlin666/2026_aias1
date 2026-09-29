package acal_lab04.Lab

import chisel3._

class HalfAdder extends Module {
  val io = IO(new Bundle {
    val A     = Input(UInt(1.W))
    val B     = Input(UInt(1.W))
    val Sum   = Output(UInt(1.W))
    val Carry = Output(UInt(1.W))
  })

  io.Sum   := io.A ^ io.B
  io.Carry := io.A & io.B
}