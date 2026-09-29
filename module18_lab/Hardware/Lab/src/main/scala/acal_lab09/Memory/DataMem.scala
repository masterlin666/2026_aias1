package acal_lab09.Memory

import chisel3._
import chisel3.util._
import chisel3.util.experimental.loadMemoryFromFile
import acal_lab09.PiplinedCPU.wide._

class DataMem(bits: Int) extends Module {
  val io = IO(new Bundle {
    val Length       = Input(UInt(4.W))

    // Read interface
    val raddr        = Input(UInt(bits.W))
    val rdata        = Output(UInt(32.W))

    // Write interface
    val wen          = Input(Bool())
    val waddr        = Input(UInt(bits.W))
    val wdata        = Input(UInt(32.W))
  })

  val memory = Mem(1 << bits, UInt(8.W))
  loadMemoryFromFile(memory, "./src/main/resource/data.hex")

  val byte0 = memory(io.raddr)
  val byte1 = memory((io.raddr & ~(1.U(bits.W))) + 1.U)
  val byte2 = memory((io.raddr & ~(3.U(bits.W))) + 2.U)
  val byte3 = memory((io.raddr & ~(3.U(bits.W))) + 3.U)

  val readDataComb = Wire(UInt(32.W))

  readDataComb := MuxLookup(io.Length, 0.U(32.W), Seq(
    Byte  -> byte0.asSInt.pad(32).asUInt,
    Half  -> Cat(byte1, byte0).asSInt.pad(32).asUInt,
    Word  -> Cat(byte3, byte2, byte1, byte0).asSInt.pad(32).asUInt,
    UByte -> Cat(0.U(24.W), byte0).asSInt.pad(32).asUInt,
    UHalf -> Cat(0.U(16.W), byte1, byte0).asSInt.pad(32).asUInt
  ))

  val raAligned = MuxLookup(io.Length, io.raddr, Seq(
    Byte -> io.raddr,
    Half -> (io.raddr & ~(1.U(bits.W))),
    Word -> (io.raddr & ~(3.U(bits.W)))
  ))

  // Align write address per length
  val wa = MuxLookup(io.Length, io.waddr, Seq(
    Byte -> io.waddr,
    Half -> (io.waddr & ~(1.U(bits.W))),
    Word -> (io.waddr & ~(3.U(bits.W)))
  ))

  val wd = MuxLookup(io.Length, io.wdata, Seq(
    Byte -> io.wdata(7, 0),
    Half -> io.wdata(15, 0),
    Word -> io.wdata
  ))

  when (io.wen && (wa === raAligned)) {
    readDataComb := wd
  }

  io.rdata := readDataComb

  when(io.wen) {
    switch(io.Length) {
      is(Byte) {
        memory(wa) := wd(7,0)
      }
      is(Half) {
        memory(wa)       := wd(7,0)
        memory(wa + 1.U) := wd(15,8)
      }
      is(Word) {
        memory(wa)       := wd(7,0)
        memory(wa + 1.U) := wd(15,8)
        memory(wa + 2.U) := wd(23,16)
        memory(wa + 3.U) := wd(31,24)
      }
    }
  }
}