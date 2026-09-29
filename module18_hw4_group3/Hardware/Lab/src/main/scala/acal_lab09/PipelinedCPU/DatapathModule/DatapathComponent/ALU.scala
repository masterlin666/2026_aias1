package acal_lab09.PiplinedCPU.DatapathModule.DatapathComponent

import chisel3._
import chisel3.util._

import acal_lab09.PiplinedCPU.opcode_map._
import acal_lab09.PiplinedCPU.alu_op_map._

class ALUIO extends Bundle{
  val src1    = Input(UInt(32.W))
  val src2    = Input(UInt(32.W))
  val ALUSel  = Input(UInt(15.W))
  val out  = Output(UInt(32.W))
}

class ALU extends Module{
  val io = IO(new ALUIO)
  io.out := 0.U

  // RISC-V bit operations use only the low five bits as the shift/bit index.
  val shamt = io.src2(4,0)
  val rolRightShamt = (32.U(6.W) - Cat(0.U(1.W), shamt))(4,0)
  switch(io.ALUSel){
    // Base RV32I ALU operations.
    is(ADD ){ io.out := io.src1 + io.src2 }
    is(SLL ){io.out := io.src1 << shamt}
    is(SLT ){io.out := Mux(io.src1.asSInt < io.src2.asSInt,1.U,0.U)}
    is(SLTU){io.out := Mux(io.src1 < io.src2              ,1.U,0.U)}
    is(XOR ){io.out := io.src1^io.src2}
    is(SRL ){io.out := io.src1 >> shamt}
    is(OR  ){io.out := io.src1|io.src2}
    is(AND ){io.out := io.src1&io.src2}
    is(SUB ){io.out := io.src1-io.src2}
    is(SRA ){io.out := (io.src1.asSInt >> shamt).asUInt}

    // Zba: shifted-add address generation.
    is(SH1ADD){ io.out := (io.src1 << 1.U) + io.src2 }
    is(SH3ADD){ io.out := (io.src1 << 3.U) + io.src2 }

    is(SH2ADD){io.out := (io.src1 << 2.U) + io.src2}

    // Zbb: basic bit-manipulation operations.
    is(ANDN){io.out := io.src1 & ~io.src2}
    is(CLZ){io.out := Mux(io.src1 === 0.U, 32.U, PriorityEncoder(Reverse(io.src1)))}
    is(MAX){io.out := Mux(io.src1.asSInt > io.src2.asSInt, io.src1, io.src2)}
    is(ROL){io.out := (io.src1 << shamt) | (io.src1 >> rolRightShamt)}
    is(ORC_B){io.out := Cat(
      Mux(io.src1(31,24).orR, "hff".U(8.W), 0.U(8.W)),
      Mux(io.src1(23,16).orR, "hff".U(8.W), 0.U(8.W)),
      Mux(io.src1(15,8).orR, "hff".U(8.W), 0.U(8.W)),
      Mux(io.src1(7,0).orR, "hff".U(8.W), 0.U(8.W))
    )}
    is(MAXU){io.out := Mux(io.src1.asUInt < io.src2.asUInt, io.src2.asUInt, io.src1.asUInt)}
    
    is(CPOP){io.out := PopCount(io.src1)}
    
    is(SEXT_H){
    val sign_bit = io.src1(15)
    io.out := Cat(Fill(16, sign_bit), io.src1(15, 0))
    }
    
    is(RORI , ROR){
      // 32 位元循環右移邏輯
      val roriLeftShamt = (32.U(6.W) - Cat(0.U(1.W), shamt))(4,0)
      io.out := (io.src1 >> shamt) | (io.src1 << roriLeftShamt)
    }

    is(ORN){io.out := io.src1 | ~io.src2}
    is(CTZ){io.out := Mux(io.src1 === 0.U, 32.U, PriorityEncoder(io.src1))}
    is(MIN){io.out := Mux(io.src1.asSInt < io.src2.asSInt, io.src1, io.src2)}
    //is(ROR){io.out := (io.src1 >> shamt) | (io.src1 << rolRightShamt)}
    is(BINV){io.out := io.src1 ^ (1.U(32.W) << shamt)}
    is(XNOR){io.out := ~(io.src1 ^ io.src2)}
    is(MINU){io.out := Mux(io.src1 < io.src2, io.src1, io.src2)}
    is(SEXT_B){io.out := Cat(Fill(24, io.src1(7)), io.src1(7,0))}
    is(ZEXT_H){io.out := Cat(Fill(16, 0.U), io.src1(15,0))}
    is(REV8){io.out := Cat(io.src1(7,0), io.src1(15,8), io.src1(23,16), io.src1(31,24))}

    // Zbs: single-bit operations. bclri reuses this operation with an
    // immediate bit index already selected onto src2.
    is(BCLR){io.out := io.src1 & ~(1.U(32.W) << shamt)}
    is(BSET){io.out := io.src1 | (1.U(32.W) << shamt)}
    is(BEXT){io.out := (io.src1 >> shamt) & 1.U}
  }
}

