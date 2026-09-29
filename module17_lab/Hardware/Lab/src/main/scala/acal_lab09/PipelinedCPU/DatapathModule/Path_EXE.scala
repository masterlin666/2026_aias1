package acal_lab09.PiplinedCPU.DatapathModule

import chisel3._
import chisel3.util._
import acal_lab09.PiplinedCPU.DatapathModule.DatapathComponent._

class Path_EXE(addrWidth:Int) extends Module {
    val io = IO(new Bundle{
        // datapath
        val EXE_pc_in = Input(UInt(addrWidth.W))
        val EXE_imm_in = Input(UInt(32.W))
        val EXE_rs1_rdata_in = Input(UInt(32.W))
        val EXE_rs2_rdata_in = Input(UInt(32.W))
        
        // Data Forwarding 必要的內部狀態輸入
        val EXE_rs1_addr = Input(UInt(5.W))
        val EXE_rs2_addr = Input(UInt(5.W))
        
        val MEM_rd = Input(UInt(5.W))
        val MEM_RegWEn = Input(Bool())
        val MEM_alu_out = Input(UInt(32.W))
        
        val WB_rd = Input(UInt(5.W))
        val WB_RegWEn = Input(Bool())
        val WB_wdata = Input(UInt(32.W))

        // control signal
        val E_ASel = Input(UInt(2.W))
        val E_BSel = Input(UInt(1.W)) 
        val E_BrUn = Input(Bool())
        val E_ALUSel = Input(UInt(15.W))

        val EXE_target_pc_out = Output(UInt(addrWidth.W))
        val EXE_alu_out = Output(UInt(32.W))
        val EXE_rs2_rdata_out = Output(UInt(32.W))
        val E_BrEq = Output(Bool())
        val E_BrLT = Output(Bool())

        // Test
        val alu_src1 = Output(UInt(32.W))
        val alu_src2 = Output(UInt(32.W))
        val EXE_src1 = Output(UInt(32.W))
        val EXE_src2 = Output(UInt(32.W))
    })
    val alu_src1 = Wire(UInt(32.W))
    val alu_src2 = Wire(UInt(32.W))

    // Forwarding 邏輯實現
    val forwardA = Wire(UInt(2.W))
    val forwardB = Wire(UInt(2.W))

    // ForwardA 偵測
    when(io.MEM_RegWEn && (io.MEM_rd =/= 0.U) && (io.MEM_rd === io.EXE_rs1_addr)) {
        forwardA := 2.U
    }.elsewhen(io.WB_RegWEn && (io.WB_rd =/= 0.U) && (io.WB_rd === io.EXE_rs1_addr)) {
        forwardA := 1.U
    }.otherwise {
        forwardA := 0.U
    }

    // ForwardB 偵測
    when(io.MEM_RegWEn && (io.MEM_rd =/= 0.U) && (io.MEM_rd === io.EXE_rs2_addr)) {
        forwardB := 2.U
    }.elsewhen(io.WB_RegWEn && (io.WB_rd =/= 0.U) && (io.WB_rd === io.EXE_rs2_addr)) {
        forwardB := 1.U
    }.otherwise {
        forwardB := 0.U
    }

    // 依據前推訊號選擇最新正確資料
    val fwd_rs1_data = MuxLookup(forwardA, io.EXE_rs1_rdata_in, Seq(
        0.U -> io.EXE_rs1_rdata_in,
        1.U -> io.WB_wdata,
        2.U -> io.MEM_alu_out
    ))

    val fwd_rs2_data = MuxLookup(forwardB, io.EXE_rs2_rdata_in, Seq(
        0.U -> io.EXE_rs2_rdata_in,
        1.U -> io.WB_wdata,
        2.U -> io.MEM_alu_out
    ))

    //Branch Comparator
    val bc = Module(new BranchComp)
    bc.io.BrUn := io.E_BrUn
    bc.io.src1 := fwd_rs1_data
    bc.io.src2 := fwd_rs2_data
    io.E_BrEq := bc.io.BrEq
    io.E_BrLT := bc.io.BrLT

    //ALU
    val alu = Module(new ALU)
    alu_src1 := MuxLookup(io.E_ASel, fwd_rs1_data, Seq(
        0.U -> fwd_rs1_data,
        1.U -> io.EXE_pc_in,
        2.U -> 0.U(32.W)
    ))
    alu_src2 := MuxLookup(io.E_BSel, fwd_rs2_data, Seq(
        0.U -> fwd_rs2_data,
        1.U -> io.EXE_imm_in,
    ))
    alu.io.src1 := alu_src1
    alu.io.src2 := alu_src2
    alu.io.ALUSel := io.E_ALUSel
    io.EXE_alu_out := alu.io.out

    // other IO
    io.EXE_rs2_rdata_out := fwd_rs2_data
    io.EXE_target_pc_out := alu.io.out(addrWidth-1,0) // pc target from alu out
    io.alu_src1 := alu_src1
    io.alu_src2 := alu_src2
    io.EXE_src1 := fwd_rs1_data
    io.EXE_src2 := fwd_rs2_data
}