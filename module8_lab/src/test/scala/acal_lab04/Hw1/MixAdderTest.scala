package acal_lab04.Hw1

import chisel3._
import chisel3.iotesters.{PeekPokeTester, Driver, ChiselFlatSpec}
import scala.util.Random

// 1. 保留原本的 Tester 邏輯
class MixAdderTester(dut: MixAdder) extends PeekPokeTester(dut) {
  val n = 8
  val testCount = 100
  val mask = BigInt("FFFFFFFF", 16)

  // 隨機測試
  for (i <- 0 until testCount) {
    val in1 = BigInt(32, Random)
    val in2 = BigInt(32, Random)
    val cin = Random.nextInt(2)

    poke(dut.io.In1, in1)
    poke(dut.io.In2, in2)
    poke(dut.io.Cin, cin)
    step(1)

    val total = in1 + in2 + cin
    expect(dut.io.Sum, total & mask)
    expect(dut.io.Cout, if (total > mask) 1 else 0)
  }

  // 邊界測試
  poke(dut.io.In1, mask)
  poke(dut.io.In2, 1)
  poke(dut.io.Cin, 0)
  step(1)
  expect(dut.io.Sum, 0)
  expect(dut.io.Cout, 1)
}

// 2. 關鍵修正：繼承 ChiselFlatSpec 讓 sbt 能夠偵測到這是一個測試案例
class MixAdderTest extends ChiselFlatSpec {
  "MixAdder" should "correctly add 32-bit numbers with carry-in" in {
    // 這裡調用 Driver 來執行上面的 Tester
    Driver.execute(Array("--backend-name", "verilator"), () => new MixAdder(8)) {
      c => new MixAdderTester(c)
    } should be (true)
  }
}