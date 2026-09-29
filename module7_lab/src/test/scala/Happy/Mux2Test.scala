package Happy

   import chisel3.iotesters.{PeekPokeTester, Driver}

   class Mux2Test(c: Mux2) extends PeekPokeTester(c) {
     val i0 = 0
     val i1 = 1

     for (s <- 0 until 2) {
       poke(c.io.sel, s)
       poke(c.io.in1, i1)
       poke(c.io.in0, i0)
       step(1)

       // Automated check
       expect(c.io.out, if (s == 1) i1 else i0)

       // Manual check with peek
       val result = peek(c.io.out)
       println(s"sel=$s -> out=$result")
     }
   }

   object Mux2Test extends App {
     Driver.execute(args, () => new Mux2) {
       c: Mux2 => new Mux2Test(c)
     }
   }