package acal_lab04.Lab

import chisel3.iotesters.{PeekPokeTester, Driver}

class HalfAdderTest(dut: HalfAdder) extends PeekPokeTester(dut) {
  for (a <- 0 until 2) {
    for (b <- 0 until 2) {
      poke(dut.io.A, a)
      poke(dut.io.B, b)

      expect(dut.io.Sum, a ^ b)
      expect(dut.io.Carry, a & b)
      step(1)
    }
  }
  println("HalfAdder test completed!")
}

object HalfAdderTest extends App {
  Driver.execute(Array("-td", "./generated"),
    () => new HalfAdder()) {
    c => new HalfAdderTest(c)
  }
}
