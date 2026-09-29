package acal_lab04.Hw2

import chisel3.iotesters.{PeekPokeTester, Driver}

class Add_SuberTest(dut: Add_Suber) extends PeekPokeTester(dut) {
  
  // 遍歷所有可能的 4-bit 輸入組合 (0-15)
  for (op <- 0 to 1) { // 0: ADD, 1: SUB
    val opName = if (op == 0) "ADD" else "SUB"
    println(s"Starting $opName tests...")
    
    for (i <- 0 to 15) {
      for (j <- 0 to 15) {
        poke(dut.io.in_1, i)
        poke(dut.io.in_2, j)
        poke(dut.io.op, op)
        step(1)

        // 將 UInt 轉為 Scala 的有號整數進行預期值計算
        // 4位元有號數轉換：若值 > 7 則減去 16 (例如 1111 是 15，15-16 = -1)
        val s_i = if (i > 7) i - 16 else i
        val s_j = if (j > 7) j - 16 else j
        
        // 根據 op 計算數學結果
        val res = if (op == 0) s_i + s_j else s_i - s_j
        
        // 判斷是否溢位 (範圍應在 -8 到 +7 之間)
        val expectedOF = if (res > 7 || res < -8) 1 else 0
        
        // 計算預期輸出 (4-bit 位元向量)
        // 使用 & 0xF 確保只取低 4 位，模擬硬體溢位行為
        val expectedOut = (if (res < 0) res + 16 else res) & 0xF

        // 驗證結果
        expect(dut.io.out, expectedOut)
        expect(dut.io.o_f, expectedOF)

        // 若發生錯誤，印出詳細資訊方便除錯
        if (peek(dut.io.out) != expectedOut || peek(dut.io.o_f) != expectedOF) {
          println(s"Error at $s_i $opName $s_j:")
          println(s"Expected: out=$expectedOut, o_f=$expectedOF")
          println(s"Got:      out=${peek(dut.io.out)}, o_f=${peek(dut.io.o_f)}")
        }
      }
    }
  }
  println("Add_Suber tests completed!")
}

object Add_SuberTest extends App {
  Driver.execute(Array("-td", "./generated", "--backend-name", "verilator"), 
    () => new Add_Suber()) {
    c => new Add_SuberTest(c)
  }
}