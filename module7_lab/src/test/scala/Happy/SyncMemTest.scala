package Happy

   import chisel3.iotesters.{PeekPokeTester, Driver}

   class SyncMemTest(c: SyncMem) extends PeekPokeTester(c) {
     // Test 1: Read initial values (note: sync read has 1-cycle latency)
     poke(c.io.wen, 0)
     for (addr <- 0 until 8) {
       poke(c.io.raddr, addr)
       step(1)  // Wait one cycle for sync read
       val data = peek(c.io.rdata)
       println(s"mem[$addr] = $data (expected $addr)")
     }

     // Test 2: Write a value and read it back
     poke(c.io.wen, 1)
     poke(c.io.waddr, 10)
     poke(c.io.wdata, 0xDEADBEEFL)
     step(1)

     poke(c.io.wen, 0)
     poke(c.io.raddr, 10)
     step(1)
     val readBack = peek(c.io.rdata)
     println(s"mem[10] after write = 0x${readBack.toString(16)} (expected 0xDEADBEEF)")

     println("SyncMem test completed!")
   }

   object SyncMemTest extends App {
     Driver.execute(args, () => new SyncMem) {
       c: SyncMem => new SyncMemTest(c)
     }
   }