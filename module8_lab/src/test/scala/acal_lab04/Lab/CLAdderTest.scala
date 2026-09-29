package acal_lab04.Lab

import chisel3.iotesters.{PeekPokeTester, Driver}

class CLAdderTest(dut: CLAdder) extends PeekPokeTester(dut) {
  // Exhaustive test: 16 x 16 = 256 combinations
  for (i <- 0 to 15) {
    for (j <- 0 to 15) {
      poke(dut.io.in1, i)
      poke(dut.io.in2, j)
      poke(dut.io.Cin, 0)

      val expectedSum  = (i + j) & 0xF
      val expectedCout = if ((i + j) > 15) 1 else 0

      if (peek(dut.io.Cout) * 16 + peek(dut.io.Sum) != (i + j)) {
        println(s"MISMATCH: $i + $j = ${i + j}, " +
          s"got Cout=${peek(dut.io.Cout)}, Sum=${peek(dut.io.Sum)}")
      }
    }
  }

  // Test with carry-in
  for (i <- 0 to 15) {
    for (j <- 0 to 15) {
      poke(dut.io.in1, i)
      poke(dut.io.in2, j)
      poke(dut.io.Cin, 1)

      val total = i + j + 1
      if (peek(dut.io.Cout) * 16 + peek(dut.io.Sum) != total) {
        println(s"MISMATCH (Cin=1): $i + $j + 1 = $total, " +
          s"got Cout=${peek(dut.io.Cout)}, Sum=${peek(dut.io.Sum)}")
      }
    }
  }

  println("CLAdder test completed!")
}

object CLAdderTest extends App {
  Driver.execute(args, () => new CLAdder) {
    c => new CLAdderTest(c)
  }
}