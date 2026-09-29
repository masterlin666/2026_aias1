package Happy

   import chisel3._
   import chisel3.util._
   import chisel3.stage.ChiselStage

   class Mux2 extends Module {
     val io = IO(new Bundle {
       val sel = Input(UInt(1.W))
       val in0 = Input(UInt(1.W))
       val in1 = Input(UInt(1.W))
       val out = Output(UInt(1.W))
     })

     io.out := (io.sel & io.in1) | (~io.sel & io.in0)
   }