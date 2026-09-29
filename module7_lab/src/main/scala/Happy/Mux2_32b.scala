package Happy

   import chisel3._
   import chisel3.util._

   class Mux2_32b extends Module {
     val io = IO(new Bundle {
       val sel = Input(Bool())
       val in1 = Input(UInt(32.W))
       val in2 = Input(UInt(32.W))
       val out = Output(UInt(32.W))
     })

     // --- Method 1: when/otherwise ---
     // Uncomment to use:
     // when(~io.sel) {
     //   io.out := io.in1
     // }.otherwise {
     //   io.out := io.in2
     // }

     // --- Method 2: Custom generic MUX function ---
     // def myMux[T <: Data](sel: Bool, in1: T, in2: T): T = {
     //   val x = WireDefault(in1)
     //   when(sel) { x := in2 }
     //   x
     // }
     // io.out := myMux(io.sel, io.in1, io.in2)

     // --- Method 3: Chisel built-in Mux ---
     io.out := Mux(io.sel, io.in2, io.in1)
   }