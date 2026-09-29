package acal_lab04.Lab

import chisel3.iotesters.{PeekPokeTester, Driver}

class FullAdderTest(fa: FullAdder) extends PeekPokeTester(fa) {
  for (a <- 0 until 2) {
    for (b <- 0 until 2) {
      for (c <- 0 until 2) {
        poke(fa.io.A, a)
        poke(fa.io.B, b)
        poke(fa.io.Cin, c)

        val expectedSum  = a ^ b ^ c
        val expectedCout = (a & b) | ((a ^ b) & c)

        expect(fa.io.Sum, expectedSum)
        expect(fa.io.Cout, expectedCout)
        step(1)
      }
    }
  }
  println("FullAdder test completed!")
}

object FullAdderTest extends App {
  Driver.execute(Array("-td", "./generated"),
    () => new FullAdder()) {
    c => new FullAdderTest(c)
  }
}
