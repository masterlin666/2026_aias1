package acal_lab04.Lab

import chisel3.iotesters.{PeekPokeTester, Driver}

class RCAdderTest(dut: RCAdder) extends PeekPokeTester(dut) {
  // Selective test cases using zip
  val in1 = Array(5, 32, 1, 77, 34, 55, 12)
  val in2 = Array(3456, 89489, 78, 5216, 4744, 8, 321)

  (in1 zip in2).foreach {
    case (i, j) =>
      poke(dut.io.In1, i)
      poke(dut.io.In2, j)
      poke(dut.io.Cin, 0)
      expect(dut.io.Sum, i + j)
  }

  // Edge cases
  poke(dut.io.In1, 0)
  poke(dut.io.In2, 0)
  poke(dut.io.Cin, 0)
  expect(dut.io.Sum, 0)
  expect(dut.io.Cout, 0)

  // Max value test (overflow)
  val maxVal = (1L << 32) - 1  // 0xFFFFFFFF for 32-bit
  poke(dut.io.In1, maxVal)
  poke(dut.io.In2, 1)
  poke(dut.io.Cin, 0)
  expect(dut.io.Sum, 0)
  expect(dut.io.Cout, 1)

  println("RCAdder test completed!")
}

object RCAdderTest extends App {
  Driver.execute(args, () => new RCAdder(32)) {
    c => new RCAdderTest(c)
  }
}