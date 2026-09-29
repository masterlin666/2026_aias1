package Happy

   import chisel3.iotesters.{PeekPokeTester, Driver}

   class Mux2_32bTest(c: Mux2_32b) extends PeekPokeTester(c) {
     // Test with several value pairs — use BigInt to avoid sign extension issues
     val testCases = Seq(
       (0, BigInt("12345678", 16), BigInt("ABCDEF01", 16)),
       (1, BigInt("12345678", 16), BigInt("ABCDEF01", 16)),
       (0, BigInt("00000000", 16), BigInt("FFFFFFFF", 16)),
       (1, BigInt("00000000", 16), BigInt("FFFFFFFF", 16))
     )

     for ((sel, in1, in2) <- testCases) {
       poke(c.io.sel, sel)
       poke(c.io.in1, in1)
       poke(c.io.in2, in2)
       step(1)

       val expected = if (sel == 1) in2 else in1
       expect(c.io.out, expected)
       println(f"sel=$sel in1=0x${in1}%08X in2=0x${in2}%08X -> out=0x${peek(c.io.out)}%08X (expected 0x${expected}%08X)")
     }
   }

   object Mux2_32bTest extends App {
     Driver.execute(args, () => new Mux2_32b) {
       c: Mux2_32b => new Mux2_32bTest(c)
     }
   }
