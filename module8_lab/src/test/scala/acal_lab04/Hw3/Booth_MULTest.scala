package acal_lab04.Hw3

import chisel3._
import chisel3.iotesters.{PeekPokeTester, Driver}
import scala.util.Random

class Booth_MulTest(dut: Booth_MUL) extends PeekPokeTester(dut) {
  val width = 16
  def toSigned(base: Int): Int = if (base >= (1 << (width - 1))) base - (1 << width) else base

  for (i <- 0 until 100) {
    val in1 = Random.nextInt(1 << width)
    val in2 = Random.nextInt(1 << width)
    val s_in1 = toSigned(in1)
    val s_in2 = toSigned(in2)
    val expected = (s_in1.toLong * s_in2.toLong)
    val mask32 = (1L << (2 * width)) - 1
    val expectedUInt = expected & mask32

    poke(dut.io.in1, in1)
    poke(dut.io.in2, in2)
    step(1)
    expect(dut.io.out, expectedUInt)
  }
}

object Booth_MulTest extends App {
  Driver.execute(Array("-td", "./generated", "--backend-name", "verilator"), 
    () => new Booth_MUL(16)) {
    c => new Booth_MulTest(c)
  }
}