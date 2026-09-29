// 測試 CpxCal 的新表達式
package acal_lab05.Hw2

import chisel3.iotesters.{Driver,PeekPokeTester}
import scala.language.implicitConversions

class CpxCalTest2(dut:CpxCal) extends PeekPokeTester(dut){

    val dict = Map(
      '0' -> 0,
      '1' -> 1,
      '2' -> 2,
      '3' -> 3,
      '4' -> 4,
      '5' -> 5,
      '6' -> 6,
      '7' -> 7,
      '8' -> 8,
      '9' -> 9,
      '+' -> 10,
      '-' -> 11,
      '*' -> 12,
      '(' -> 13,
      ')' -> 14,
      '=' -> 15,
      '.' -> 16,
      '/' -> 17
    )

    // 新增的複雜測試表達式
    val golden = Seq(
      ("((-87)*((-21)+4*3-2)*5+(18-(-13)))*(((-3)-5)*((-4)+2))=", 77056),
      ("(6+2)*(9-4*7)+((-5)*(8+(-2)*(6+11)-9)*((4+6)-5))=", 723),
      ("((((((((7-2)*3-5)*(4-3)*2-1)*4+3)*2-1)*3+2)*2+5)*3+7)*5-1357924680*864213579-(-135799246)*(553311779-22446688990)*1029384756=", 2091663100),
      ("((-2.5+0.8)/4.0)-3.6*1.5=", -5825)
    )

    golden.zipWithIndex.foreach{ case((input,expectedOutput),index)=>
        input.foreach{ ch =>
            if(dict.contains(ch)) {
                poke(dut.io.key_in, dict(ch))
            } else {
                println(s"Warning: unsupported character '$ch'")
            }
            step(1)
        }
        
        // 等待結果有效
        var waitCount = 0
        while(peek(dut.io.value.valid) == 0 && waitCount < 100) {
            step(1)
            waitCount += 1
        }
        
        val result = peek(dut.io.value.bits).toInt
        println("Question "+(index+1).toString + ": " + input)
        println("Module output: " + result)
        println("Expected: " + expectedOutput)
        println(if(result == expectedOutput) "✓ PASS" else "✗ FAIL")
        println("=" * 60)
        step(1)
    }
}

object CpxCalTest2 extends App{
    Driver.execute(args,()=>new CpxCal){
        c:CpxCal => new CpxCalTest2(c)
    }
}
