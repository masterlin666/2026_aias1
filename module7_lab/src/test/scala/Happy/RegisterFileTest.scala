package Happy

   import chisel3.iotesters.{PeekPokeTester, Driver}

   class RegisterFileTest(c: RegisterFile) extends PeekPokeTester(c) {
     // Test 1: Verify x0 is always zero
     poke(c.io.wen, 1)
     poke(c.io.waddr, 0)
     poke(c.io.wdata, 0x12345678)
     step(1)
     poke(c.io.wen, 0)
     poke(c.io.raddr(0), 0)
     step(1)
     expect(c.io.rdata(0), 0)
     println(s"x0 after write attempt: ${peek(c.io.rdata(0))} (expected 0)")

     // Test 2: Write to x1 and read back
     poke(c.io.wen, 1)
     poke(c.io.waddr, 1)
     poke(c.io.wdata, 42)
     step(1)
     poke(c.io.wen, 0)
     poke(c.io.raddr(0), 1)
     step(1)
     expect(c.io.rdata(0), 42)
     println(s"x1: ${peek(c.io.rdata(0))} (expected 42)")

     // Test 3: Simultaneous read from two ports
     poke(c.io.wen, 1)
     poke(c.io.waddr, 5)
     poke(c.io.wdata, 100)
     step(1)
     poke(c.io.wen, 0)
     poke(c.io.raddr(0), 1)
     poke(c.io.raddr(1), 5)
     step(1)
     expect(c.io.rdata(0), 42)
     expect(c.io.rdata(1), 100)
     println(s"x1: ${peek(c.io.rdata(0))}, x5: ${peek(c.io.rdata(1))}")

     println("RegisterFile test completed!")
   }

   object RegisterFileTest extends App {
     Driver.execute(args, () => new RegisterFile(2)) {
       c: RegisterFile => new RegisterFileTest(c)
     }
   }