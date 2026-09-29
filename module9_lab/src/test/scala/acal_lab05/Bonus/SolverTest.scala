package acal_lab05.Bonus

import chisel3.iotesters.{Driver,PeekPokeTester}
import scala.language.implicitConversions

class SolverTest(dut:Solver) extends PeekPokeTester(dut) {

    implicit def bigint2boolean(b:BigInt):Boolean = if (b>0) true else false

    //always set ready to High

    val ans_seq = Seq(1,3,6,9)

    while(!peek(dut.io.finish)){
        poke(dut.io.ready,true)
        step(1)
        poke(dut.io.ready,false)

        while(!peek(dut.io.s_valid)){step(1)}

        println(peek(dut.io.guess(3)).toString+" "
               +peek(dut.io.guess(2)).toString+" "
               +peek(dut.io.guess(1)).toString+" "
               +peek(dut.io.guess(0)).toString)

        val guess_seq = for (i <- 0 until 4) yield peek(dut.io.guess(3-i)).toInt
        var ans_mutable = collection.mutable.ArrayBuffer(ans_seq: _*)
        var guess_mutable = collection.mutable.ArrayBuffer(guess_seq: _*)

        var A = 0
        var B = 0
        
        for (i <- (0 until 4).reverse) {
            if (ans_mutable(i) == guess_mutable(i)) {
                A += 1
                ans_mutable.remove(i)
                guess_mutable.remove(i)
            }
        }

        for (guess_num <- guess_mutable) {
            val found_index = ans_mutable.indexOf(guess_num)
            if (found_index != -1) {
                B += 1
                ans_mutable.remove(found_index)
            }
        }

        println("A = " + A.toString)
        println("B = " + B.toString)

        //computation time in NumGuess
        step(16)

        poke(dut.io.A,A)
        poke(dut.io.B,B)
        poke(dut.io.g_valid,true)
        step(1)
        poke(dut.io.g_valid,false)
    }

}

object SolverTest extends App{
    Driver.execute(args,()=>new Solver){
        dut:Solver => new SolverTest(dut)
    }
}
