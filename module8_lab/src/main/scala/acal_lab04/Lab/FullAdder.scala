package acal_lab04.Lab

import chisel3._

class FullAdder extends Module {
  val io = IO(new Bundle {
    val A    = Input(UInt(1.W))
    val B    = Input(UInt(1.W))
    val Cin  = Input(UInt(1.W))
    val Sum  = Output(UInt(1.W))
    val Cout = Output(UInt(1.W))
  })

  // Instantiate two HalfAdders
  val ha1 = Module(new HalfAdder())
  val ha2 = Module(new HalfAdder())

  // HalfAdder 1: add A and B
  ha1.io.A := io.A
  ha1.io.B := io.B

  // HalfAdder 2: add intermediate sum with Cin
  ha2.io.A := ha1.io.Sum
  ha2.io.B := io.Cin

  // Outputs
  io.Sum  := ha2.io.Sum
  io.Cout := ha1.io.Carry | ha2.io.Carry
}