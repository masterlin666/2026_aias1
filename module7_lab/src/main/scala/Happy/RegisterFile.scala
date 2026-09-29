package Happy

   import chisel3._
   import chisel3.util._

   class RegisterFile(readPorts: Int) extends Module {
     val io = IO(new Bundle {
       val wen   = Input(Bool())
       val waddr = Input(UInt(5.W))
       val wdata = Input(UInt(32.W))
       val raddr = Input(Vec(readPorts, UInt(5.W)))
       val rdata = Output(Vec(readPorts, UInt(32.W)))
     })

     // Initialize all 32 registers to zero
     val regs = RegInit(VecInit(Seq.fill(32)(0.U(32.W))))

     // Write logic
     when(io.wen) { regs(io.waddr) := io.wdata }

     // x0 is hardwired to zero
     regs(0) := 0.U

     // Read logic
     for (i <- 0 until readPorts) {
       io.rdata(i) := regs(io.raddr(i))
     }
   }