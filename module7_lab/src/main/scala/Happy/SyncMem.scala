package Happy

   import chisel3._
   import chisel3.util._
   import chisel3.util.experimental.loadMemoryFromFile

   class SyncMem extends Module {
     val io = IO(new Bundle {
       val raddr = Input(UInt(5.W))
       val rdata = Output(UInt(32.W))
       val wen   = Input(Bool())
       val waddr = Input(UInt(5.W))
       val wdata = Input(UInt(32.W))
     })

     // Synchronous read memory (sync read, sync write)
     val memory = SyncReadMem(32, UInt(32.W))

     // Load initial values from file
     loadMemoryFromFile(memory, "./src/main/resource/value.txt")

     // Read and write wiring
     io.rdata := memory(io.raddr)
     when(io.wen) { memory(io.waddr) := io.wdata }
   }